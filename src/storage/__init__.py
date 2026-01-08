"""
Ambient Wi-Fi Monitor - Storage Module
Handles persistence of raw data, normalized data, baselines, and metadata.
"""

import json
import os
import csv
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path


class RawDataStore:
    """
    Stores raw command outputs with timestamps.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize raw data store.
        
        Args:
            config: Application configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger('ambient_wifi_monitor.storage.raw')
        self.storage_path = self._get_storage_path()
    
    def _get_storage_path(self) -> str:
        """Get the base storage path for raw data."""
        storage = self.config.get('storage', {})
        base_dir = storage.get('data_dir', 'data')
        raw_dir = storage.get('raw_dir', 'raw')
        return os.path.join(base_dir, raw_dir)
    
    def save(self, collection_data: Dict) -> str:
        """
        Save raw collection data to disk.
        
        Args:
            collection_data: Raw collection dictionary
        
        Returns:
            Path to saved file
        """
        timestamp = collection_data.get('collection_timestamp', datetime.now().isoformat())
        
        # Create timestamped filename
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        filename = f"raw_{dt.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.storage_path, filename)
        
        # Ensure directory exists
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Save to JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(collection_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Saved raw data to {filepath}")
        return filepath
    
    def load(self, filepath: str) -> Dict:
        """
        Load raw collection data from file.
        
        Args:
            filepath: Path to raw data file
        
        Returns:
            Raw collection dictionary
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data
    
    def list_files(self, limit: Optional[int] = None) -> List[str]:
        """
        List raw data files, newest first.
        
        Args:
            limit: Maximum number of files to return
        
        Returns:
            List of file paths
        """
        files = []
        if os.path.exists(self.storage_path):
            files = [
                os.path.join(self.storage_path, f)
                for f in os.listdir(self.storage_path)
                if f.startswith('raw_') and f.endswith('.json')
            ]
            files.sort(reverse=True)
        
        if limit:
            files = files[:limit]
        
        return files


class NormalizedDataStore:
    """
    Stores normalized, structured data.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize normalized data store.
        
        Args:
            config: Application configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger('ambient_wifi_monitor.storage.normalized')
        self.storage_path = self._get_storage_path()
    
    def _get_storage_path(self) -> str:
        """Get the base storage path for normalized data."""
        storage = self.config.get('storage', {})
        base_dir = storage.get('data_dir', 'data')
        norm_dir = storage.get('normalized_dir', 'normalized')
        return os.path.join(base_dir, norm_dir)
    
    def save(self, normalized_data: Dict) -> str:
        """
        Save normalized data to disk.
        
        Args:
            normalized_data: Normalized data dictionary
        
        Returns:
            Path to saved file
        """
        timestamp = normalized_data.get('timestamp', datetime.now().isoformat())
        
        # Create timestamped filename
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        filename = f"normalized_{dt.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.storage_path, filename)
        
        # Ensure directory exists
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Save to JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(normalized_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Saved normalized data to {filepath}")
        
        # Also save to CSV for easy analysis
        self._save_bssids_csv(normalized_data, dt)
        
        return filepath
    
    def _save_bssids_csv(self, normalized_data: Dict, timestamp: datetime) -> None:
        """
        Save BSSID data to CSV for easy analysis.
        
        Args:
            normalized_data: Normalized data dictionary
            timestamp: Observation timestamp
        """
        networks = normalized_data.get('wlan_networks', {})
        bssids = networks.get('bssids', [])
        
        if not bssids:
            return
        
        csv_path = os.path.join(self.storage_path, 'bssids_history.csv')
        file_exists = os.path.exists(csv_path)
        
        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            fieldnames = ['timestamp', 'ssid', 'bssid', 'signal', 'channel', 'radio_type', 'authentication', 'encryption']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            for bssid in bssids:
                writer.writerow({
                    'timestamp': timestamp.isoformat(),
                    'ssid': bssid.get('ssid', ''),
                    'bssid': bssid.get('bssid', ''),
                    'signal': bssid.get('signal', ''),
                    'channel': bssid.get('channel', ''),
                    'radio_type': bssid.get('radio_type', ''),
                    'authentication': bssid.get('authentication', ''),
                    'encryption': bssid.get('encryption', '')
                })
    
    def load(self, filepath: str) -> Dict:
        """
        Load normalized data from file.
        
        Args:
            filepath: Path to normalized data file
        
        Returns:
            Normalized data dictionary
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data
    
    def list_files(self, limit: Optional[int] = None) -> List[str]:
        """
        List normalized data files, newest first.
        
        Args:
            limit: Maximum number of files to return
        
        Returns:
            List of file paths
        """
        files = []
        if os.path.exists(self.storage_path):
            files = [
                os.path.join(self.storage_path, f)
                for f in os.listdir(self.storage_path)
                if f.startswith('normalized_') and f.endswith('.json')
            ]
            files.sort(reverse=True)
        
        if limit:
            files = files[:limit]
        
        return files
    
    def load_recent(self, count: int) -> List[Dict]:
        """
        Load the most recent normalized observations.
        
        Args:
            count: Number of observations to load
        
        Returns:
            List of normalized data dictionaries
        """
        files = self.list_files(limit=count)
        observations = []
        
        for filepath in files:
            try:
                data = self.load(filepath)
                observations.append(data)
            except Exception as e:
                self.logger.error(f"Error loading {filepath}: {e}")
        
        return observations


class BaselineStore:
    """
    Stores baseline models and statistics.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize baseline store.
        
        Args:
            config: Application configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger('ambient_wifi_monitor.storage.baseline')
        self.storage_path = self._get_storage_path()
    
    def _get_storage_path(self) -> str:
        """Get the base storage path for baselines."""
        storage = self.config.get('storage', {})
        base_dir = storage.get('data_dir', 'data')
        baseline_dir = storage.get('baselines_dir', 'baselines')
        return os.path.join(base_dir, baseline_dir)
    
    def save(self, baseline: Dict, name: str = 'current') -> str:
        """
        Save baseline model to disk.
        
        Args:
            baseline: Baseline model dictionary
            name: Baseline identifier
        
        Returns:
            Path to saved file
        """
        filename = f"baseline_{name}.json"
        filepath = os.path.join(self.storage_path, filename)
        
        # Ensure directory exists
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Save to JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(baseline, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Saved baseline '{name}' to {filepath}")
        return filepath
    
    def load(self, name: str = 'current') -> Optional[Dict]:
        """
        Load baseline model from disk.
        
        Args:
            name: Baseline identifier
        
        Returns:
            Baseline model dictionary or None if not found
        """
        filename = f"baseline_{name}.json"
        filepath = os.path.join(self.storage_path, filename)
        
        if not os.path.exists(filepath):
            self.logger.warning(f"Baseline '{name}' not found at {filepath}")
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            baseline = json.load(f)
        
        return baseline
    
    def exists(self, name: str = 'current') -> bool:
        """
        Check if a baseline exists.
        
        Args:
            name: Baseline identifier
        
        Returns:
            True if baseline exists, False otherwise
        """
        filename = f"baseline_{name}.json"
        filepath = os.path.join(self.storage_path, filename)
        return os.path.exists(filepath)


class MetadataStore:
    """
    Stores application metadata and observation counters.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize metadata store.
        
        Args:
            config: Application configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger('ambient_wifi_monitor.storage.metadata')
        self.filepath = self._get_filepath()
    
    def _get_filepath(self) -> str:
        """Get the metadata file path."""
        storage = self.config.get('storage', {})
        base_dir = storage.get('data_dir', 'data')
        return os.path.join(base_dir, 'metadata.json')
    
    def load(self) -> Dict:
        """
        Load metadata from disk.
        
        Returns:
            Metadata dictionary
        """
        if not os.path.exists(self.filepath):
            return self._initialize_metadata()
        
        with open(self.filepath, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        return metadata
    
    def save(self, metadata: Dict) -> None:
        """
        Save metadata to disk.
        
        Args:
            metadata: Metadata dictionary
        """
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def _initialize_metadata(self) -> Dict:
        """
        Create initial metadata structure.
        
        Returns:
            Initial metadata dictionary
        """
        return {
            'initialized': datetime.now().isoformat(),
            'observation_count': 0,
            'last_observation': None,
            'baseline_initialized': False,
            'baseline_observation_count': 0
        }
    
    def increment_observation(self) -> int:
        """
        Increment observation counter.
        
        Returns:
            New observation count
        """
        metadata = self.load()
        metadata['observation_count'] += 1
        metadata['last_observation'] = datetime.now().isoformat()
        self.save(metadata)
        return metadata['observation_count']


class StorageOrchestrator:
    """
    Orchestrates all storage operations.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize storage orchestrator.
        
        Args:
            config: Application configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger('ambient_wifi_monitor.storage')
        
        # Initialize stores
        self.raw_store = RawDataStore(config)
        self.normalized_store = NormalizedDataStore(config)
        self.baseline_store = BaselineStore(config)
        self.metadata_store = MetadataStore(config)
    
    def save_observation(self, raw_data: Dict, normalized_data: Dict) -> int:
        """
        Save a complete observation (raw + normalized).
        
        Args:
            raw_data: Raw collection data
            normalized_data: Normalized data
        
        Returns:
            Observation number
        """
        # Save raw data
        self.raw_store.save(raw_data)
        
        # Save normalized data
        self.normalized_store.save(normalized_data)
        
        # Increment observation counter
        obs_num = self.metadata_store.increment_observation()
        
        self.logger.info(f"Saved observation #{obs_num}")
        
        return obs_num

"""
Ambient Wi-Fi Monitor - Environmental Fingerprinting Module
Creates reproducible fingerprints of Wi-Fi environments for comparison.
"""

import logging
import hashlib
import numpy as np
from typing import Dict, List, Optional


class EnvironmentalFingerprint:
    """
    Creates and compares Wi-Fi environmental fingerprints.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize environmental fingerprinting system.
        
        Args:
            config: Application configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger('ambient_wifi_monitor.analysis.fingerprint')
        
        # Configuration
        fingerprint_config = config.get('fingerprint', {})
        self.features = fingerprint_config.get('features', [
            'bssid_count', 'ssid_count', 'rssi_mean', 'rssi_std',
            'channel_diversity', 'signal_stability'
        ])
        self.similarity_threshold = fingerprint_config.get('similarity_threshold', 0.85)
    
    def generate(self, observation: Dict) -> Dict:
        """
        Generate environmental fingerprint from observation.
        
        Args:
            observation: Normalized observation dictionary
        
        Returns:
            Fingerprint dictionary
        """
        self.logger.info("Generating environmental fingerprint")
        
        networks = observation.get('wlan_networks', {})
        summary = networks.get('summary', {})
        bssids = networks.get('bssids', [])
        
        # Extract features
        features = {}
        
        # BSSID count
        if 'bssid_count' in self.features:
            features['bssid_count'] = summary.get('bssid_count', 0)
        
        # SSID count
        if 'ssid_count' in self.features:
            features['ssid_count'] = len(summary.get('ssids', []))
        
        # Signal statistics (using signal percentage)
        signals = [b.get('signal') for b in bssids if b.get('signal') is not None]
        if signals:
            if 'rssi_mean' in self.features:
                features['rssi_mean'] = float(np.mean(signals))
            
            if 'rssi_std' in self.features:
                features['rssi_std'] = float(np.std(signals))
            
            if 'signal_stability' in self.features:
                # Lower std = more stable = higher score
                if np.mean(signals) > 0:
                    cv = np.std(signals) / np.mean(signals)
                    features['signal_stability'] = float(max(0, 1 - cv))
                else:
                    features['signal_stability'] = 0.0
        
        # Channel diversity
        if 'channel_diversity' in self.features:
            channels = [b.get('channel') for b in bssids if b.get('channel') is not None]
            if channels:
                unique_channels = len(set(channels))
                # Normalize by typical number of channels (assume max 14 for 2.4GHz + channels for 5GHz)
                features['channel_diversity'] = float(unique_channels / 14.0)
            else:
                features['channel_diversity'] = 0.0
        
        # Generate hash
        fingerprint_hash = self._compute_hash(features)
        
        return {
            'timestamp': observation.get('timestamp'),
            'hash': fingerprint_hash,
            'features': features,
            'observation_count': 1
        }
    
    def _compute_hash(self, features: Dict) -> str:
        """
        Compute a hash from feature values.
        
        Args:
            features: Feature dictionary
        
        Returns:
            8-character hex hash
        """
        # Round features to avoid minor variations
        rounded = {}
        for key, value in features.items():
            if isinstance(value, float):
                rounded[key] = round(value, 1)
            else:
                rounded[key] = value
        
        # Create deterministic string
        feature_str = "|".join(f"{k}:{v}" for k, v in sorted(rounded.items()))
        
        # Hash
        hash_obj = hashlib.sha256(feature_str.encode())
        return hash_obj.hexdigest()[:8]
    
    def compare(self, fingerprint1: Dict, fingerprint2: Dict) -> Dict:
        """
        Compare two environmental fingerprints.
        
        Args:
            fingerprint1: First fingerprint
            fingerprint2: Second fingerprint
        
        Returns:
            Comparison results dictionary
        """
        features1 = fingerprint1.get('features', {})
        features2 = fingerprint2.get('features', {})
        
        # Compute similarity for each feature
        feature_similarities = {}
        for feature in self.features:
            if feature in features1 and feature in features2:
                val1 = features1[feature]
                val2 = features2[feature]
                
                # Compute normalized difference
                if val1 == 0 and val2 == 0:
                    similarity = 1.0
                elif val1 == 0 or val2 == 0:
                    similarity = 0.0
                else:
                    max_val = max(abs(val1), abs(val2))
                    diff = abs(val1 - val2)
                    similarity = max(0.0, 1.0 - (diff / max_val))
                
                feature_similarities[feature] = similarity
        
        # Overall similarity (average of feature similarities)
        if feature_similarities:
            overall_similarity = np.mean(list(feature_similarities.values()))
        else:
            overall_similarity = 0.0
        
        # Match status
        is_match = overall_similarity >= self.similarity_threshold
        
        return {
            'overall_similarity': float(overall_similarity),
            'is_match': is_match,
            'feature_similarities': feature_similarities,
            'hash_match': fingerprint1.get('hash') == fingerprint2.get('hash'),
            'interpretation': self._interpret_comparison(overall_similarity, is_match)
        }
    
    def aggregate_fingerprints(self, fingerprints: List[Dict]) -> Dict:
        """
        Aggregate multiple fingerprints into a representative fingerprint.
        
        Args:
            fingerprints: List of fingerprint dictionaries
        
        Returns:
            Aggregated fingerprint dictionary
        """
        if not fingerprints:
            return {}
        
        # Collect all features
        all_features = {feature: [] for feature in self.features}
        
        for fp in fingerprints:
            features = fp.get('features', {})
            for feature in self.features:
                if feature in features:
                    all_features[feature].append(features[feature])
        
        # Compute median for each feature
        aggregated_features = {}
        for feature, values in all_features.items():
            if values:
                aggregated_features[feature] = float(np.median(values))
        
        # Generate hash
        fingerprint_hash = self._compute_hash(aggregated_features)
        
        return {
            'timestamp': fingerprints[-1].get('timestamp') if fingerprints else None,
            'hash': fingerprint_hash,
            'features': aggregated_features,
            'observation_count': len(fingerprints),
            'aggregated': True
        }
    
    def _interpret_comparison(self, similarity: float, is_match: bool) -> str:
        """
        Generate human-readable interpretation of fingerprint comparison.
        
        Args:
            similarity: Similarity score (0.0 - 1.0)
            is_match: Whether fingerprints match
        
        Returns:
            Interpretation string
        """
        if is_match:
            return f"Environments match (similarity: {similarity*100:.1f}%)"
        elif similarity > 0.70:
            return f"Environments similar but distinct (similarity: {similarity*100:.1f}%)"
        elif similarity > 0.50:
            return f"Environments moderately different (similarity: {similarity*100:.1f}%)"
        else:
            return f"Environments significantly different (similarity: {similarity*100:.1f}%)"

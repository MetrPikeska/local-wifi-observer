"""
Ambient Wi-Fi Monitor - Baseline Analysis Module
Builds and maintains statistical models of "normal" Wi-Fi environmental conditions.
"""

import logging
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
from scipy import stats


class BaselineMetrics:
    """
    Computes baseline statistical metrics from observations.
    """
    
    def __init__(self):
        self.logger = logging.getLogger('ambient_wifi_monitor.analysis.baseline.metrics')
    
    def compute_bssid_metrics(self, observations: List[Dict]) -> Dict:
        """
        Compute baseline metrics for BSSID counts.
        
        Args:
            observations: List of normalized observation dictionaries
        
        Returns:
            Dictionary of baseline BSSID metrics
        """
        counts = []
        
        for obs in observations:
            networks = obs.get('wlan_networks', {})
            summary = networks.get('summary', {})
            count = summary.get('bssid_count', 0)
            counts.append(count)
        
        if not counts:
            return {}
        
        return {
            'mean': float(np.mean(counts)),
            'median': float(np.median(counts)),
            'std': float(np.std(counts)),
            'min': int(np.min(counts)),
            'max': int(np.max(counts)),
            'percentile_25': float(np.percentile(counts, 25)),
            'percentile_75': float(np.percentile(counts, 75)),
            'samples': len(counts)
        }
    
    def compute_signal_metrics(self, observations: List[Dict]) -> Dict:
        """
        Compute baseline metrics for signal strength (as percentage).
        
        Args:
            observations: List of normalized observation dictionaries
        
        Returns:
            Dictionary of baseline signal metrics
        """
        signals = []
        
        for obs in observations:
            networks = obs.get('wlan_networks', {})
            bssids = networks.get('bssids', [])
            
            for bssid in bssids:
                signal = bssid.get('signal')
                if signal is not None:
                    signals.append(signal)
        
        if not signals:
            return {}
        
        return {
            'mean': float(np.mean(signals)),
            'median': float(np.median(signals)),
            'std': float(np.std(signals)),
            'min': int(np.min(signals)),
            'max': int(np.max(signals)),
            'percentile_25': float(np.percentile(signals, 25)),
            'percentile_75': float(np.percentile(signals, 75)),
            'samples': len(signals)
        }
    
    def compute_channel_metrics(self, observations: List[Dict]) -> Dict:
        """
        Compute baseline metrics for channel usage.
        
        Args:
            observations: List of normalized observation dictionaries
        
        Returns:
            Dictionary of baseline channel metrics
        """
        channel_counts = {}
        
        for obs in observations:
            networks = obs.get('wlan_networks', {})
            bssids = networks.get('bssids', [])
            
            for bssid in bssids:
                channel = bssid.get('channel')
                if channel is not None:
                    channel_counts[channel] = channel_counts.get(channel, 0) + 1
        
        if not channel_counts:
            return {}
        
        total_observations = sum(channel_counts.values())
        channel_distribution = {
            ch: count / total_observations
            for ch, count in channel_counts.items()
        }
        
        return {
            'channel_distribution': channel_distribution,
            'unique_channels': len(channel_counts),
            'most_common_channel': max(channel_counts, key=channel_counts.get),
            'channel_diversity': self._compute_diversity(list(channel_distribution.values()))
        }
    
    def compute_ssid_metrics(self, observations: List[Dict]) -> Dict:
        """
        Compute baseline metrics for SSID diversity.
        
        Args:
            observations: List of normalized observation dictionaries
        
        Returns:
            Dictionary of baseline SSID metrics
        """
        ssid_counts = {}
        
        for obs in observations:
            networks = obs.get('wlan_networks', {})
            summary = networks.get('summary', {})
            ssids = summary.get('ssids', [])
            
            for ssid in ssids:
                if ssid:  # Exclude empty SSIDs
                    ssid_counts[ssid] = ssid_counts.get(ssid, 0) + 1
        
        if not ssid_counts:
            return {}
        
        return {
            'unique_ssids': len(ssid_counts),
            'total_ssid_observations': sum(ssid_counts.values()),
            'ssid_diversity': self._compute_diversity(list(ssid_counts.values()))
        }
    
    def _compute_diversity(self, counts: List[float]) -> float:
        """
        Compute Shannon diversity index.
        
        Args:
            counts: List of occurrence counts
        
        Returns:
            Shannon diversity index
        """
        if not counts:
            return 0.0
        
        total = sum(counts)
        if total == 0:
            return 0.0
        
        proportions = [c / total for c in counts if c > 0]
        return float(-sum(p * np.log(p) for p in proportions))


class BaselineModel:
    """
    Maintains a statistical baseline model of the Wi-Fi environment.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize baseline model.
        
        Args:
            config: Application configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger('ambient_wifi_monitor.analysis.baseline')
        self.metrics_calculator = BaselineMetrics()
        
        # Configuration
        baseline_config = config.get('baseline', {})
        self.min_observations = baseline_config.get('min_observations', 100)
        self.rolling_window = baseline_config.get('rolling_window', 50)
        self.stability_threshold = baseline_config.get('stability_threshold', 0.85)
        self.update_interval = baseline_config.get('update_interval', 10)
    
    def build(self, observations: List[Dict]) -> Dict:
        """
        Build baseline model from observations.
        
        Args:
            observations: List of normalized observation dictionaries
        
        Returns:
            Baseline model dictionary
        """
        if len(observations) < self.min_observations:
            self.logger.warning(
                f"Insufficient observations for baseline: {len(observations)} < {self.min_observations}"
            )
            return self._create_provisional_baseline(observations)
        
        self.logger.info(f"Building baseline from {len(observations)} observations")
        
        baseline = {
            'created': datetime.now().isoformat(),
            'observation_count': len(observations),
            'status': 'stable',
            'confidence': self._compute_confidence(observations),
            'metrics': {
                'bssid': self.metrics_calculator.compute_bssid_metrics(observations),
                'signal': self.metrics_calculator.compute_signal_metrics(observations),
                'channel': self.metrics_calculator.compute_channel_metrics(observations),
                'ssid': self.metrics_calculator.compute_ssid_metrics(observations)
            },
            'temporal_patterns': self._analyze_temporal_patterns(observations)
        }
        
        self.logger.info(
            f"Baseline created with confidence {baseline['confidence']:.2f}"
        )
        
        return baseline
    
    def _create_provisional_baseline(self, observations: List[Dict]) -> Dict:
        """
        Create a provisional baseline with limited data.
        
        Args:
            observations: List of normalized observation dictionaries
        
        Returns:
            Provisional baseline dictionary
        """
        self.logger.info(f"Creating provisional baseline from {len(observations)} observations")
        
        return {
            'created': datetime.now().isoformat(),
            'observation_count': len(observations),
            'status': 'provisional',
            'confidence': 0.5,  # Lower confidence for provisional baseline
            'metrics': {
                'bssid': self.metrics_calculator.compute_bssid_metrics(observations),
                'signal': self.metrics_calculator.compute_signal_metrics(observations),
                'channel': self.metrics_calculator.compute_channel_metrics(observations),
                'ssid': self.metrics_calculator.compute_ssid_metrics(observations)
            },
            'temporal_patterns': {},
            'note': f'Provisional baseline - requires {self.min_observations} observations for stability'
        }
    
    def _compute_confidence(self, observations: List[Dict]) -> float:
        """
        Compute confidence score for baseline stability.
        
        Args:
            observations: List of normalized observation dictionaries
        
        Returns:
            Confidence score (0.0 - 1.0)
        """
        if len(observations) < self.min_observations:
            return 0.5
        
        # Check coefficient of variation for BSSID counts
        counts = []
        for obs in observations:
            networks = obs.get('wlan_networks', {})
            summary = networks.get('summary', {})
            count = summary.get('bssid_count', 0)
            counts.append(count)
        
        if not counts or np.mean(counts) == 0:
            return 0.6
        
        cv = np.std(counts) / np.mean(counts)
        
        # Lower CV means more stable, higher confidence
        # CV < 0.2 -> very stable (confidence ~0.95)
        # CV > 0.5 -> less stable (confidence ~0.70)
        confidence = max(0.70, min(0.95, 0.95 - cv))
        
        return float(confidence)
    
    def _analyze_temporal_patterns(self, observations: List[Dict]) -> Dict:
        """
        Analyze temporal patterns in observations.
        
        Args:
            observations: List of normalized observation dictionaries
        
        Returns:
            Dictionary of temporal patterns
        """
        # Extract timestamps and BSSID counts
        time_series = []
        
        for obs in observations:
            timestamp_str = obs.get('timestamp')
            networks = obs.get('wlan_networks', {})
            summary = networks.get('summary', {})
            count = summary.get('bssid_count', 0)
            
            if timestamp_str:
                try:
                    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    time_series.append((dt, count))
                except:
                    pass
        
        if len(time_series) < 10:
            return {}
        
        # Sort by time
        time_series.sort(key=lambda x: x[0])
        
        # Analyze hourly patterns (if we have enough data)
        hourly_counts = {}
        for dt, count in time_series:
            hour = dt.hour
            if hour not in hourly_counts:
                hourly_counts[hour] = []
            hourly_counts[hour].append(count)
        
        hourly_means = {
            hour: np.mean(counts)
            for hour, counts in hourly_counts.items()
        }
        
        return {
            'hourly_means': hourly_means,
            'has_temporal_data': True
        }
    
    def compare_to_baseline(self, current_observation: Dict, baseline: Dict) -> Dict:
        """
        Compare current observation to baseline.
        
        Args:
            current_observation: Current normalized observation
            baseline: Baseline model dictionary
        
        Returns:
            Comparison results dictionary
        """
        networks = current_observation.get('wlan_networks', {})
        summary = networks.get('summary', {})
        current_bssid_count = summary.get('bssid_count', 0)
        
        baseline_metrics = baseline.get('metrics', {})
        bssid_baseline = baseline_metrics.get('bssid', {})
        
        baseline_mean = bssid_baseline.get('mean', 0)
        baseline_std = bssid_baseline.get('std', 0)
        
        # Compute z-score
        if baseline_std > 0:
            z_score = (current_bssid_count - baseline_mean) / baseline_std
        else:
            z_score = 0.0
        
        # Determine status
        if abs(z_score) < 1.0:
            status = 'NORMAL'
            confidence = 0.90
        elif abs(z_score) < 2.0:
            status = 'SLIGHTLY_ELEVATED' if z_score > 0 else 'SLIGHTLY_REDUCED'
            confidence = 0.75
        else:
            status = 'ANOMALOUS_HIGH' if z_score > 0 else 'ANOMALOUS_LOW'
            confidence = 0.85
        
        return {
            'status': status,
            'confidence': confidence,
            'current_bssid_count': current_bssid_count,
            'baseline_mean': baseline_mean,
            'baseline_std': baseline_std,
            'z_score': float(z_score),
            'deviation_percent': float((current_bssid_count - baseline_mean) / baseline_mean * 100) if baseline_mean > 0 else 0.0
        }

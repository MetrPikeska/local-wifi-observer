"""
Ambient Wi-Fi Monitor - Anomaly Detection Module
Detects unusual patterns and deviations from expected behavior.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
from scipy import stats


class AnomalyDetector:
    """
    Detects anomalies in Wi-Fi environmental data.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize anomaly detector.
        
        Args:
            config: Application configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger('ambient_wifi_monitor.analysis.anomaly')
        
        # Configuration
        anomaly_config = config.get('anomaly', {})
        self.method = anomaly_config.get('method', 'zscore')
        self.zscore_threshold = anomaly_config.get('zscore_threshold', 3.0)
        self.iqr_multiplier = anomaly_config.get('iqr_multiplier', 1.5)
        self.confidence_high = anomaly_config.get('confidence_high', 0.90)
        self.confidence_medium = anomaly_config.get('confidence_medium', 0.70)
        self.confidence_low = anomaly_config.get('confidence_low', 0.50)
    
    def detect(self, current_observation: Dict, baseline: Optional[Dict], 
               historical_observations: List[Dict]) -> Dict:
        """
        Perform comprehensive anomaly detection.
        
        Args:
            current_observation: Current normalized observation
            baseline: Baseline model (if available)
            historical_observations: List of historical observations
        
        Returns:
            Anomaly detection results dictionary
        """
        self.logger.info("Performing anomaly detection")
        
        anomalies = []
        
        # BSSID count anomalies
        bssid_anomaly = self._detect_bssid_count_anomaly(
            current_observation, baseline, historical_observations
        )
        if bssid_anomaly:
            anomalies.append(bssid_anomaly)
        
        # Signal strength anomalies
        signal_anomaly = self._detect_signal_anomaly(
            current_observation, baseline, historical_observations
        )
        if signal_anomaly:
            anomalies.append(signal_anomaly)
        
        # Channel distribution anomalies
        channel_anomaly = self._detect_channel_anomaly(
            current_observation, baseline
        )
        if channel_anomaly:
            anomalies.append(channel_anomaly)
        
        # Sudden appearance/disappearance
        disappearance_anomaly = self._detect_sudden_changes(
            current_observation, historical_observations
        )
        if disappearance_anomaly:
            anomalies.extend(disappearance_anomaly)
        
        # Overall assessment
        if not anomalies:
            overall_status = 'NORMAL'
            overall_confidence = 0.90
        elif len(anomalies) == 1:
            overall_status = 'ANOMALY_DETECTED'
            overall_confidence = anomalies[0].get('confidence', 0.70)
        else:
            overall_status = 'MULTIPLE_ANOMALIES'
            overall_confidence = 0.85
        
        return {
            'timestamp': current_observation.get('timestamp'),
            'status': overall_status,
            'confidence': overall_confidence,
            'anomaly_count': len(anomalies),
            'anomalies': anomalies,
            'interpretation': self._interpret_anomalies(anomalies)
        }
    
    def _detect_bssid_count_anomaly(self, current_observation: Dict, 
                                     baseline: Optional[Dict],
                                     historical_observations: List[Dict]) -> Optional[Dict]:
        """
        Detect anomalies in BSSID count.
        
        Args:
            current_observation: Current observation
            baseline: Baseline model
            historical_observations: Historical observations
        
        Returns:
            Anomaly dictionary if detected, None otherwise
        """
        networks = current_observation.get('wlan_networks', {})
        summary = networks.get('summary', {})
        current_count = summary.get('bssid_count', 0)
        
        # Use baseline if available
        if baseline:
            metrics = baseline.get('metrics', {})
            bssid_metrics = metrics.get('bssid', {})
            mean = bssid_metrics.get('mean', 0)
            std = bssid_metrics.get('std', 0)
        # Otherwise use historical data
        elif len(historical_observations) >= 10:
            counts = []
            for obs in historical_observations:
                obs_networks = obs.get('wlan_networks', {})
                obs_summary = obs_networks.get('summary', {})
                counts.append(obs_summary.get('bssid_count', 0))
            mean = np.mean(counts)
            std = np.std(counts)
        else:
            return None
        
        # Compute z-score
        if std == 0:
            return None
        
        z_score = (current_count - mean) / std
        
        # Check if anomalous
        if abs(z_score) >= self.zscore_threshold:
            direction = 'high' if z_score > 0 else 'low'
            confidence = min(0.95, self.confidence_high + abs(z_score) * 0.01)
            
            return {
                'type': 'bssid_count',
                'severity': 'high' if abs(z_score) > 4 else 'medium',
                'direction': direction,
                'confidence': confidence,
                'current_value': current_count,
                'expected_value': mean,
                'z_score': float(z_score),
                'description': f"BSSID count ({current_count}) is significantly {direction} (z-score: {z_score:.2f})"
            }
        
        return None
    
    def _detect_signal_anomaly(self, current_observation: Dict,
                                baseline: Optional[Dict],
                                historical_observations: List[Dict]) -> Optional[Dict]:
        """
        Detect anomalies in signal strength distribution.
        
        Args:
            current_observation: Current observation
            baseline: Baseline model
            historical_observations: Historical observations
        
        Returns:
            Anomaly dictionary if detected, None otherwise
        """
        networks = current_observation.get('wlan_networks', {})
        bssids = networks.get('bssids', [])
        
        current_signals = [b.get('signal') for b in bssids if b.get('signal') is not None]
        
        if not current_signals:
            return None
        
        current_mean = np.mean(current_signals)
        current_std = np.std(current_signals)
        
        # Compare to baseline
        if baseline:
            metrics = baseline.get('metrics', {})
            signal_metrics = metrics.get('signal', {})
            baseline_mean = signal_metrics.get('mean', 0)
            baseline_std = signal_metrics.get('std', 0)
        else:
            return None
        
        # Check if standard deviation is unusually high (unstable signals)
        if baseline_std > 0:
            std_ratio = current_std / baseline_std
            
            if std_ratio > 2.0:
                return {
                    'type': 'signal_instability',
                    'severity': 'medium',
                    'confidence': 0.75,
                    'current_std': float(current_std),
                    'baseline_std': float(baseline_std),
                    'ratio': float(std_ratio),
                    'description': f"Signal strength highly unstable (std: {current_std:.1f}, baseline: {baseline_std:.1f})"
                }
        
        return None
    
    def _detect_channel_anomaly(self, current_observation: Dict,
                                 baseline: Optional[Dict]) -> Optional[Dict]:
        """
        Detect anomalies in channel distribution.
        
        Args:
            current_observation: Current observation
            baseline: Baseline model
        
        Returns:
            Anomaly dictionary if detected, None otherwise
        """
        if not baseline:
            return None
        
        networks = current_observation.get('wlan_networks', {})
        bssids = networks.get('bssids', [])
        
        # Current channel distribution
        current_channels = {}
        for bssid in bssids:
            channel = bssid.get('channel')
            if channel:
                current_channels[channel] = current_channels.get(channel, 0) + 1
        
        if not current_channels:
            return None
        
        # Baseline channel distribution
        metrics = baseline.get('metrics', {})
        channel_metrics = metrics.get('channel', {})
        baseline_distribution = channel_metrics.get('channel_distribution', {})
        
        if not baseline_distribution:
            return None
        
        # Check for new heavily-used channels
        for channel, count in current_channels.items():
            baseline_prop = baseline_distribution.get(str(channel), 0.0)
            current_prop = count / len(bssids)
            
            # New channel with significant usage
            if baseline_prop < 0.05 and current_prop > 0.20:
                return {
                    'type': 'channel_shift',
                    'severity': 'medium',
                    'confidence': 0.80,
                    'channel': channel,
                    'current_proportion': float(current_prop),
                    'baseline_proportion': float(baseline_prop),
                    'description': f"Unusual activity on channel {channel} ({current_prop*100:.1f}% vs baseline {baseline_prop*100:.1f}%)"
                }
        
        return None
    
    def _detect_sudden_changes(self, current_observation: Dict,
                                historical_observations: List[Dict]) -> List[Dict]:
        """
        Detect sudden appearance or disappearance of many signals.
        
        Args:
            current_observation: Current observation
            historical_observations: Historical observations
        
        Returns:
            List of anomaly dictionaries
        """
        if len(historical_observations) < 3:
            return []
        
        networks = current_observation.get('wlan_networks', {})
        summary = networks.get('summary', {})
        current_count = summary.get('bssid_count', 0)
        
        # Get recent counts
        recent_counts = []
        for obs in historical_observations[:5]:
            obs_networks = obs.get('wlan_networks', {})
            obs_summary = obs_networks.get('summary', {})
            recent_counts.append(obs_summary.get('bssid_count', 0))
        
        recent_mean = np.mean(recent_counts)
        
        anomalies = []
        
        # Sudden spike
        if current_count > recent_mean * 1.5 and current_count - recent_mean > 5:
            anomalies.append({
                'type': 'sudden_spike',
                'severity': 'high',
                'confidence': 0.85,
                'current_count': current_count,
                'recent_mean': float(recent_mean),
                'increase': current_count - recent_mean,
                'description': f"Sudden spike in BSSID count: {current_count} vs recent average {recent_mean:.1f}"
            })
        
        # Sudden drop
        elif current_count < recent_mean * 0.5 and recent_mean - current_count > 5:
            anomalies.append({
                'type': 'sudden_drop',
                'severity': 'high',
                'confidence': 0.85,
                'current_count': current_count,
                'recent_mean': float(recent_mean),
                'decrease': recent_mean - current_count,
                'description': f"Sudden drop in BSSID count: {current_count} vs recent average {recent_mean:.1f}"
            })
        
        return anomalies
    
    def _interpret_anomalies(self, anomalies: List[Dict]) -> str:
        """
        Generate human-readable interpretation of detected anomalies.
        
        Args:
            anomalies: List of anomaly dictionaries
        
        Returns:
            Interpretation string
        """
        if not anomalies:
            return "No anomalies detected. Environment operating within normal parameters."
        
        high_severity = [a for a in anomalies if a.get('severity') == 'high']
        medium_severity = [a for a in anomalies if a.get('severity') == 'medium']
        
        parts = []
        
        if high_severity:
            parts.append(f"{len(high_severity)} high-severity anomaly/anomalies")
        if medium_severity:
            parts.append(f"{len(medium_severity)} medium-severity anomaly/anomalies")
        
        summary = " and ".join(parts) + " detected."
        
        # Add descriptions
        descriptions = [a.get('description', '') for a in anomalies[:3]]
        
        return summary + " " + " ".join(descriptions)

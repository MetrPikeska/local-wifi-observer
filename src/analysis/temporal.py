"""
Ambient Wi-Fi Monitor - Temporal Analysis Module
Analyzes changes and trends over time windows.
"""

import logging
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime


class TemporalAnalyzer:
    """
    Performs temporal analysis on Wi-Fi environmental observations.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize temporal analyzer.
        
        Args:
            config: Application configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger('ambient_wifi_monitor.analysis.temporal')
        
        # Configuration
        temporal_config = config.get('temporal', {})
        self.short_term_window = temporal_config.get('short_term_window', 10)
        self.medium_term_window = temporal_config.get('medium_term_window', 50)
        self.long_term_window = temporal_config.get('long_term_window', 200)
        self.smoothing_factor = temporal_config.get('smoothing_factor', 0.3)
        self.min_change_threshold = temporal_config.get('min_change_threshold', 15.0)
    
    def analyze(self, current_observation: Dict, historical_observations: List[Dict]) -> Dict:
        """
        Perform comprehensive temporal analysis.
        
        Args:
            current_observation: Current normalized observation
            historical_observations: List of historical observations (newest first)
        
        Returns:
            Temporal analysis results dictionary
        """
        self.logger.info(f"Performing temporal analysis with {len(historical_observations)} historical observations")
        
        # Extract BSSID count from current observation
        current_count = self._get_bssid_count(current_observation)
        
        # Analyze different time windows
        short_term = self._analyze_window(
            current_count,
            historical_observations[:self.short_term_window],
            'short_term'
        )
        
        medium_term = self._analyze_window(
            current_count,
            historical_observations[:self.medium_term_window],
            'medium_term'
        )
        
        long_term = self._analyze_window(
            current_count,
            historical_observations[:self.long_term_window],
            'long_term'
        )
        
        # Detect trends
        trend = self._detect_trend(historical_observations)
        
        # Compute smoothed values
        smoothed = self._compute_smoothed_value(current_count, historical_observations)
        
        return {
            'timestamp': current_observation.get('timestamp'),
            'current_bssid_count': current_count,
            'smoothed_value': smoothed,
            'windows': {
                'short_term': short_term,
                'medium_term': medium_term,
                'long_term': long_term
            },
            'trend': trend,
            'interpretation': self._interpret_results(short_term, medium_term, long_term, trend)
        }
    
    def _get_bssid_count(self, observation: Dict) -> int:
        """
        Extract BSSID count from observation.
        
        Args:
            observation: Normalized observation dictionary
        
        Returns:
            BSSID count
        """
        networks = observation.get('wlan_networks', {})
        summary = networks.get('summary', {})
        return summary.get('bssid_count', 0)
    
    def _analyze_window(self, current_count: int, window_observations: List[Dict], window_name: str) -> Dict:
        """
        Analyze a specific time window.
        
        Args:
            current_count: Current BSSID count
            window_observations: Observations in this window
            window_name: Name of the window
        
        Returns:
            Window analysis results
        """
        if not window_observations:
            return {
                'available': False,
                'window_size': 0
            }
        
        counts = [self._get_bssid_count(obs) for obs in window_observations]
        
        window_mean = np.mean(counts)
        window_std = np.std(counts)
        
        # Compute change percentage
        if window_mean > 0:
            change_percent = ((current_count - window_mean) / window_mean) * 100
        else:
            change_percent = 0.0
        
        # Determine status
        if abs(change_percent) < self.min_change_threshold:
            status = 'stable'
        elif change_percent > 0:
            status = 'increasing'
        else:
            status = 'decreasing'
        
        return {
            'available': True,
            'window_size': len(counts),
            'mean': float(window_mean),
            'std': float(window_std),
            'min': int(np.min(counts)),
            'max': int(np.max(counts)),
            'change_percent': float(change_percent),
            'status': status
        }
    
    def _detect_trend(self, observations: List[Dict]) -> Dict:
        """
        Detect overall trend using linear regression.
        
        Args:
            observations: List of historical observations
        
        Returns:
            Trend analysis results
        """
        if len(observations) < 10:
            return {
                'available': False,
                'reason': 'insufficient_data'
            }
        
        # Extract counts
        counts = [self._get_bssid_count(obs) for obs in observations[:self.medium_term_window]]
        
        # Simple linear regression
        x = np.arange(len(counts))
        y = np.array(counts)
        
        # Compute slope
        if len(x) > 1:
            slope, intercept = np.polyfit(x, y, 1)
        else:
            slope = 0.0
            intercept = 0.0
        
        # Classify trend
        if abs(slope) < 0.1:
            direction = 'stable'
            strength = 'weak'
        elif slope > 0:
            direction = 'upward'
            strength = 'strong' if slope > 0.5 else 'moderate'
        else:
            direction = 'downward'
            strength = 'strong' if slope < -0.5 else 'moderate'
        
        return {
            'available': True,
            'direction': direction,
            'strength': strength,
            'slope': float(slope),
            'confidence': 0.75
        }
    
    def _compute_smoothed_value(self, current_count: int, historical_observations: List[Dict]) -> float:
        """
        Compute exponentially weighted moving average.
        
        Args:
            current_count: Current BSSID count
            historical_observations: List of historical observations
        
        Returns:
            Smoothed value
        """
        if not historical_observations:
            return float(current_count)
        
        recent_counts = [
            self._get_bssid_count(obs)
            for obs in historical_observations[:self.short_term_window]
        ]
        
        # EWMA
        smoothed = current_count
        for count in recent_counts:
            smoothed = self.smoothing_factor * count + (1 - self.smoothing_factor) * smoothed
        
        return float(smoothed)
    
    def _interpret_results(self, short_term: Dict, medium_term: Dict, long_term: Dict, trend: Dict) -> str:
        """
        Generate human-readable interpretation of temporal analysis.
        
        Args:
            short_term: Short-term analysis results
            medium_term: Medium-term analysis results
            long_term: Long-term analysis results
            trend: Trend analysis results
        
        Returns:
            Interpretation string
        """
        parts = []
        
        # Short-term status
        if short_term.get('available'):
            st_status = short_term.get('status')
            st_change = short_term.get('change_percent', 0)
            
            if st_status == 'stable':
                parts.append("Short-term: Stable")
            elif st_status == 'increasing':
                parts.append(f"Short-term: Increasing ({st_change:+.1f}%)")
            else:
                parts.append(f"Short-term: Decreasing ({st_change:+.1f}%)")
        
        # Medium-term status
        if medium_term.get('available'):
            mt_status = medium_term.get('status')
            if mt_status != 'stable':
                parts.append(f"Medium-term: {mt_status.capitalize()}")
        
        # Trend
        if trend.get('available'):
            trend_dir = trend.get('direction')
            trend_str = trend.get('strength')
            if trend_dir != 'stable':
                parts.append(f"Trend: {trend_str.capitalize()} {trend_dir}")
        
        if not parts:
            return "Temporal analysis: Insufficient historical data"
        
        return " | ".join(parts)

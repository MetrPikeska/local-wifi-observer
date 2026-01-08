"""
Ambient Wi-Fi Monitor - Distance Estimation Module
Estimates pseudo-distance from RSSI using path loss models.

IMPORTANT DISCLAIMER:
This module provides ROUGH ESTIMATES only. Accuracy is typically ±10-20 meters
in real-world conditions. Results are influenced by:
- Building materials (walls, floors, furniture)
- Environmental interference
- Unknown transmit power of access points
- Multipath propagation
- Calibration accuracy

This is for ENVIRONMENTAL ANALYSIS, not precise positioning or tracking.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
from enum import Enum


class DistanceZone(Enum):
    """Distance zones for rough proximity classification."""
    VERY_CLOSE = "VERY_CLOSE"    # < 2m
    CLOSE = "CLOSE"                # 2-10m
    MEDIUM = "MEDIUM"              # 10-30m
    FAR = "FAR"                    # 30-70m
    VERY_FAR = "VERY_FAR"          # > 70m
    UNKNOWN = "UNKNOWN"            # Cannot estimate


class DistanceEstimator:
    """
    Estimates distance from Wi-Fi access points using RSSI.
    
    Uses Log-Distance Path Loss Model:
    RSSI = TxPower - 10 * n * log10(d) - C
    
    Where:
    - RSSI: Received Signal Strength Indicator
    - TxPower: Transmit power (typically ~20 dBm for Wi-Fi)
    - n: Path loss exponent (2-4, environment dependent)
    - d: Distance in meters
    - C: Environmental constant
    """
    
    def __init__(self, config: Dict):
        """
        Initialize distance estimator.
        
        Args:
            config: Application configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger('ambient_wifi_monitor.analysis.distance')
        
        # Configuration
        distance_config = config.get('distance_estimation', {})
        self.enabled = distance_config.get('enabled', True)
        self.reference_tx_power = distance_config.get('reference_tx_power', 20)
        self.path_loss_exponent = distance_config.get('path_loss_exponent', 3.0)
        self.environmental_constant = distance_config.get('environmental_constant', 0)
        self.show_exact_distances = distance_config.get('show_exact_distances', False)
        self.show_distance_zones = distance_config.get('show_distance_zones', True)
        self.uncertainty_margin = distance_config.get('uncertainty_margin', 10)
        
        self.logger.info(f"Distance estimation initialized (n={self.path_loss_exponent})")
        
        # Log important disclaimer
        self.logger.warning(
            "Distance estimation provides ROUGH ESTIMATES with ±%dm uncertainty. "
            "Not suitable for precise positioning or tracking.",
            self.uncertainty_margin
        )
    
    def rssi_percent_to_dbm(self, rssi_percent: int) -> float:
        """
        Convert RSSI percentage (0-100) to approximate dBm.
        
        Windows netsh reports signal as percentage, but we need dBm for calculations.
        Typical mapping: 100% ≈ -30 dBm, 0% ≈ -100 dBm
        
        Args:
            rssi_percent: Signal strength as percentage (0-100)
        
        Returns:
            Approximate RSSI in dBm
        """
        # Linear approximation: 0% = -100 dBm, 100% = -30 dBm
        rssi_dbm = -100 + (rssi_percent * 0.7)
        return rssi_dbm
    
    def estimate_distance(self, rssi_percent: int) -> Tuple[float, float, float]:
        """
        Estimate distance from RSSI percentage.
        
        Args:
            rssi_percent: Signal strength as percentage (0-100)
        
        Returns:
            Tuple of (distance_meters, lower_bound, upper_bound)
        """
        if not self.enabled or rssi_percent is None:
            return (None, None, None)
        
        # Convert to dBm
        rssi_dbm = self.rssi_percent_to_dbm(rssi_percent)
        
        # Path Loss Model: RSSI = TxPower - 10*n*log10(d) - C
        # Solving for d: d = 10^((TxPower - RSSI - C) / (10*n))
        
        numerator = self.reference_tx_power - rssi_dbm - self.environmental_constant
        denominator = 10 * self.path_loss_exponent
        
        if denominator == 0:
            return (None, None, None)
        
        distance = 10 ** (numerator / denominator)
        
        # Calculate uncertainty bounds
        lower_bound = max(0, distance - self.uncertainty_margin)
        upper_bound = distance + self.uncertainty_margin
        
        return (float(distance), float(lower_bound), float(upper_bound))
    
    def classify_distance_zone(self, distance: Optional[float]) -> DistanceZone:
        """
        Classify distance into zone.
        
        Args:
            distance: Distance in meters (can be None)
        
        Returns:
            DistanceZone classification
        """
        if distance is None:
            return DistanceZone.UNKNOWN
        
        if distance < 2:
            return DistanceZone.VERY_CLOSE
        elif distance < 10:
            return DistanceZone.CLOSE
        elif distance < 30:
            return DistanceZone.MEDIUM
        elif distance < 70:
            return DistanceZone.FAR
        else:
            return DistanceZone.VERY_FAR
    
    def analyze_observation(self, observation: Dict) -> Dict:
        """
        Analyze distances for all BSSIDs in observation.
        
        Args:
            observation: Normalized observation dictionary
        
        Returns:
            Distance analysis results
        """
        if not self.enabled:
            return {'enabled': False}
        
        networks = observation.get('wlan_networks', {})
        bssids = networks.get('bssids', [])
        
        if not bssids:
            return {
                'enabled': True,
                'bssid_count': 0,
                'distances': []
            }
        
        distances = []
        zone_counts = {zone: 0 for zone in DistanceZone}
        
        for bssid_info in bssids:
            signal = bssid_info.get('signal')
            
            if signal is not None:
                dist, lower, upper = self.estimate_distance(signal)
                zone = self.classify_distance_zone(dist)
                
                zone_counts[zone] += 1
                
                distances.append({
                    'ssid': bssid_info.get('ssid', ''),
                    'bssid': bssid_info.get('bssid', ''),
                    'signal_percent': signal,
                    'estimated_distance_m': dist,
                    'lower_bound_m': lower,
                    'upper_bound_m': upper,
                    'zone': zone.value,
                    'channel': bssid_info.get('channel')
                })
        
        # Calculate statistics
        valid_distances = [d['estimated_distance_m'] for d in distances if d['estimated_distance_m'] is not None]
        
        if valid_distances:
            stats = {
                'mean_distance': float(np.mean(valid_distances)),
                'median_distance': float(np.median(valid_distances)),
                'min_distance': float(np.min(valid_distances)),
                'max_distance': float(np.max(valid_distances)),
                'std_distance': float(np.std(valid_distances))
            }
        else:
            stats = {}
        
        # Zone distribution
        zone_distribution = {
            zone.value: count
            for zone, count in zone_counts.items()
            if count > 0
        }
        
        return {
            'enabled': True,
            'timestamp': observation.get('timestamp'),
            'bssid_count': len(bssids),
            'distances': distances,
            'statistics': stats,
            'zone_distribution': zone_distribution,
            'parameters': {
                'tx_power_dbm': self.reference_tx_power,
                'path_loss_exponent': self.path_loss_exponent,
                'uncertainty_margin_m': self.uncertainty_margin
            },
            'disclaimer': (
                f"Estimates have ±{self.uncertainty_margin}m uncertainty. "
                "Actual distances may vary significantly based on environment."
            )
        }
    
    def get_zone_description(self, zone: DistanceZone) -> str:
        """
        Get human-readable description of distance zone.
        
        Args:
            zone: DistanceZone enum value
        
        Returns:
            Description string
        """
        descriptions = {
            DistanceZone.VERY_CLOSE: "Very close (< 2m) - Same room, immediate vicinity",
            DistanceZone.CLOSE: "Close (2-10m) - Same room or adjacent space",
            DistanceZone.MEDIUM: "Medium (10-30m) - Nearby rooms or floor",
            DistanceZone.FAR: "Far (30-70m) - Different floor or distant area",
            DistanceZone.VERY_FAR: "Very far (> 70m) - Remote location or weak signal",
            DistanceZone.UNKNOWN: "Unknown - Cannot estimate distance"
        }
        return descriptions.get(zone, "Unknown zone")
    
    def format_distance_summary(self, analysis: Dict) -> str:
        """
        Format distance analysis as human-readable summary.
        
        Args:
            analysis: Distance analysis results
        
        Returns:
            Formatted summary string
        """
        if not analysis.get('enabled'):
            return "Distance estimation disabled"
        
        if analysis.get('bssid_count', 0) == 0:
            return "No BSSIDs to analyze"
        
        lines = []
        
        # Statistics
        stats = analysis.get('statistics', {})
        if stats:
            mean = stats.get('mean_distance', 0)
            std = stats.get('std_distance', 0)
            min_d = stats.get('min_distance', 0)
            max_d = stats.get('max_distance', 0)
            
            lines.append(f"Average distance: {mean:.1f}m (±{std:.1f}m)")
            lines.append(f"Range: {min_d:.1f}m - {max_d:.1f}m")
        
        # Zone distribution
        zone_dist = analysis.get('zone_distribution', {})
        if zone_dist:
            lines.append("\nDistance zones:")
            for zone_name, count in zone_dist.items():
                percentage = (count / analysis['bssid_count']) * 100
                lines.append(f"  {zone_name}: {count} ({percentage:.1f}%)")
        
        # Disclaimer
        disclaimer = analysis.get('disclaimer', '')
        if disclaimer:
            lines.append(f"\n⚠ {disclaimer}")
        
        return "\n".join(lines)

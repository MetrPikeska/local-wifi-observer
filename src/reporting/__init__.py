"""
Ambient Wi-Fi Monitor - Reporting Module
Generates human and machine-readable reports of analytical findings.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any


class TextReportGenerator:
    """
    Generates human-readable text reports.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize text report generator.
        
        Args:
            config: Application configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger('ambient_wifi_monitor.reporting.text')
        
        reporting_config = config.get('reporting', {})
        self.verbosity = reporting_config.get('verbosity', 'standard')
        self.timestamp_format = reporting_config.get('timestamp_format', '%Y-%m-%d %H:%M:%S')
    
    def generate(self, analysis_results: Dict) -> str:
        """
        Generate comprehensive text report.
        
        Args:
            analysis_results: Complete analysis results dictionary
        
        Returns:
            Formatted text report
        """
        lines = []
        
        # Header
        lines.append("=" * 70)
        lines.append("Wi-Fi Environmental Analysis Report")
        lines.append("=" * 70)
        lines.append("")
        
        # Metadata
        metadata = analysis_results.get('metadata', {})
        timestamp = metadata.get('timestamp', datetime.now().isoformat())
        obs_num = metadata.get('observation_number', 'N/A')
        
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            timestamp_str = dt.strftime(self.timestamp_format)
        except:
            timestamp_str = timestamp
        
        lines.append(f"Timestamp: {timestamp_str}")
        lines.append(f"Observation: #{obs_num}")
        lines.append("")
        
        # Environmental Status
        lines.append("ENVIRONMENTAL STATUS")
        lines.append("-" * 70)
        
        baseline_comparison = analysis_results.get('baseline_comparison', {})
        status = baseline_comparison.get('status', 'UNKNOWN')
        confidence = baseline_comparison.get('confidence', 0.0)
        
        lines.append(f"Status: {status} (confidence: {confidence:.2f})")
        
        current_count = baseline_comparison.get('current_bssid_count', 0)
        baseline_mean = baseline_comparison.get('baseline_mean', 0)
        
        lines.append(f"  - Activity level: {current_count} BSSIDs detected")
        if baseline_mean > 0:
            lines.append(f"  - Baseline average: {baseline_mean:.1f} BSSIDs")
            deviation = baseline_comparison.get('deviation_percent', 0)
            lines.append(f"  - Deviation: {deviation:+.1f}%")
        
        lines.append("")
        
        # Current Environment Summary
        lines.append("CURRENT ENVIRONMENT")
        lines.append("-" * 70)
        
        current_obs = analysis_results.get('current_observation', {})
        networks = current_obs.get('wlan_networks', {})
        summary = networks.get('summary', {})
        
        lines.append(f"Networks (SSIDs): {summary.get('network_count', 0)}")
        lines.append(f"Access Points (BSSIDs): {summary.get('bssid_count', 0)}")
        
        channels = summary.get('channels', [])
        if channels:
            lines.append(f"Channels in use: {', '.join(map(str, sorted(channels)))}")
        
        radio_types = summary.get('radio_types', [])
        if radio_types:
            lines.append(f"Radio types: {', '.join(radio_types)}")
        
        lines.append("")
        
        # Temporal Analysis
        temporal = analysis_results.get('temporal_analysis', {})
        if temporal:
            lines.append("TEMPORAL TRENDS")
            lines.append("-" * 70)
            
            interpretation = temporal.get('interpretation', '')
            if interpretation:
                lines.append(interpretation)
            
            if self.verbosity in ['detailed']:
                windows = temporal.get('windows', {})
                for window_name, window_data in windows.items():
                    if window_data.get('available'):
                        lines.append(f"\n{window_name.replace('_', ' ').title()}:")
                        lines.append(f"  Mean: {window_data.get('mean', 0):.1f}")
                        lines.append(f"  Range: {window_data.get('min', 0)} - {window_data.get('max', 0)}")
                        lines.append(f"  Change: {window_data.get('change_percent', 0):+.1f}%")
            
            lines.append("")
        
        # Anomaly Detection
        anomaly_results = analysis_results.get('anomaly_detection', {})
        if anomaly_results:
            lines.append("ANOMALY DETECTION")
            lines.append("-" * 70)
            
            anomaly_count = anomaly_results.get('anomaly_count', 0)
            
            if anomaly_count == 0:
                lines.append("No anomalies detected")
            else:
                lines.append(f"Detected: {anomaly_count} anomaly/anomalies")
                lines.append("")
                
                anomalies = anomaly_results.get('anomalies', [])
                for i, anomaly in enumerate(anomalies, 1):
                    severity = anomaly.get('severity', 'unknown').upper()
                    confidence = anomaly.get('confidence', 0.0)
                    description = anomaly.get('description', '')
                    
                    lines.append(f"{i}. [{severity}] {description}")
                    lines.append(f"   Confidence: {confidence:.2f}")
            
            lines.append("")
        
        # Environmental Fingerprint
        fingerprint = analysis_results.get('fingerprint', {})
        if fingerprint:
            lines.append("ENVIRONMENTAL FINGERPRINT")
            lines.append("-" * 70)
            
            fp_hash = fingerprint.get('hash', 'N/A')
            lines.append(f"Fingerprint: {fp_hash}")
            
            baseline_fp = analysis_results.get('baseline_fingerprint', {})
            if baseline_fp:
                comparison = analysis_results.get('fingerprint_comparison', {})
                if comparison:
                    similarity = comparison.get('overall_similarity', 0.0)
                    interpretation = comparison.get('interpretation', '')
                    lines.append(f"Match to baseline: {similarity*100:.1f}%")
                    lines.append(f"{interpretation}")
            
            if self.verbosity == 'detailed':
                features = fingerprint.get('features', {})
                if features:
                    lines.append("\nFeatures:")
                    for key, value in features.items():
                        if isinstance(value, float):
                            lines.append(f"  {key}: {value:.2f}")
                        else:
                            lines.append(f"  {key}: {value}")
            
            lines.append("")
        
        # Distance Analysis
        distance_analysis = analysis_results.get('distance_analysis', {})
        if distance_analysis and distance_analysis.get('enabled'):
            lines.append("DISTANCE ESTIMATION")
            lines.append("-" * 70)
            
            stats = distance_analysis.get('statistics', {})
            if stats:
                mean = stats.get('mean_distance', 0)
                std = stats.get('std_distance', 0)
                min_d = stats.get('min_distance', 0)
                max_d = stats.get('max_distance', 0)
                
                lines.append(f"Average distance: {mean:.1f}m (σ={std:.1f}m)")
                lines.append(f"Range: {min_d:.1f}m - {max_d:.1f}m")
            
            # Zone distribution
            zone_dist = distance_analysis.get('zone_distribution', {})
            if zone_dist:
                bssid_count = distance_analysis.get('bssid_count', 0)
                lines.append("\nDistance zones:")
                for zone_name, count in zone_dist.items():
                    if bssid_count > 0:
                        percentage = (count / bssid_count) * 100
                        lines.append(f"  {zone_name}: {count} ({percentage:.1f}%)")
            
            # Show closest/farthest if detailed
            if self.verbosity == 'detailed':
                distances = distance_analysis.get('distances', [])
                if distances:
                    valid = [d for d in distances if d.get('estimated_distance_m') is not None]
                    if valid:
                        closest = min(valid, key=lambda x: x['estimated_distance_m'])
                        farthest = max(valid, key=lambda x: x['estimated_distance_m'])
                        
                        lines.append(f"\nClosest AP: {closest['ssid'] or 'Hidden'} ({closest['estimated_distance_m']:.1f}m)")
                        lines.append(f"Farthest AP: {farthest['ssid'] or 'Hidden'} ({farthest['estimated_distance_m']:.1f}m)")
            
            # Disclaimer
            disclaimer = distance_analysis.get('disclaimer', '')
            params = distance_analysis.get('parameters', {})
            if disclaimer:
                lines.append(f"\n⚠ {disclaimer}")
                if self.verbosity == 'detailed':
                    lines.append(f"Parameters: n={params.get('path_loss_exponent', 0)}, "
                               f"TxPower={params.get('tx_power_dbm', 0)}dBm")
            
            lines.append("")
        
        # Baseline Information
        if self.verbosity in ['standard', 'detailed']:
            baseline_info = analysis_results.get('baseline_info', {})
            if baseline_info:
                lines.append("BASELINE INFORMATION")
                lines.append("-" * 70)
                
                status = baseline_info.get('status', 'unknown')
                obs_count = baseline_info.get('observation_count', 0)
                confidence = baseline_info.get('confidence', 0.0)
                
                lines.append(f"Status: {status}")
                lines.append(f"Observations: {obs_count}")
                lines.append(f"Confidence: {confidence:.2f}")
                
                lines.append("")
        
        # Footer
        lines.append("=" * 70)
        lines.append("Report generated by Ambient Wi-Fi Monitor")
        lines.append("Environmental sensing and analysis system")
        lines.append("=" * 70)
        
        return "\n".join(lines)


class JSONReportGenerator:
    """
    Generates machine-readable JSON reports.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize JSON report generator.
        
        Args:
            config: Application configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger('ambient_wifi_monitor.reporting.json')
        
        reporting_config = config.get('reporting', {})
        self.include_raw = reporting_config.get('include_raw', False)
    
    def generate(self, analysis_results: Dict) -> str:
        """
        Generate JSON report.
        
        Args:
            analysis_results: Complete analysis results dictionary
        
        Returns:
            JSON-formatted report string
        """
        # Create simplified report structure
        report = {
            'metadata': analysis_results.get('metadata', {}),
            'status': {
                'environmental_status': analysis_results.get('baseline_comparison', {}).get('status'),
                'confidence': analysis_results.get('baseline_comparison', {}).get('confidence'),
                'anomaly_count': analysis_results.get('anomaly_detection', {}).get('anomaly_count', 0)
            },
            'metrics': {
                'bssid_count': analysis_results.get('baseline_comparison', {}).get('current_bssid_count'),
                'baseline_mean': analysis_results.get('baseline_comparison', {}).get('baseline_mean'),
                'deviation_percent': analysis_results.get('baseline_comparison', {}).get('deviation_percent')
            },
            'temporal_analysis': analysis_results.get('temporal_analysis', {}),
            'anomalies': analysis_results.get('anomaly_detection', {}).get('anomalies', []),
            'fingerprint': {
                'hash': analysis_results.get('fingerprint', {}).get('hash'),
                'features': analysis_results.get('fingerprint', {}).get('features', {}),
                'baseline_similarity': analysis_results.get('fingerprint_comparison', {}).get('overall_similarity') if analysis_results.get('fingerprint_comparison') else None
            },
            'distance_analysis': analysis_results.get('distance_analysis', {})
        }
        
        # Optionally include raw observation data
        if self.include_raw:
            report['raw_observation'] = analysis_results.get('current_observation', {})
        
        return json.dumps(report, indent=2, ensure_ascii=False)


class ReportOrchestrator:
    """
    Orchestrates report generation in multiple formats.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize report orchestrator.
        
        Args:
            config: Application configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger('ambient_wifi_monitor.reporting')
        
        # Initialize generators
        self.text_generator = TextReportGenerator(config)
        self.json_generator = JSONReportGenerator(config)
        
        # Configuration
        reporting_config = config.get('reporting', {})
        self.formats = reporting_config.get('formats', ['text', 'json'])
    
    def generate_reports(self, analysis_results: Dict) -> Dict[str, str]:
        """
        Generate reports in all configured formats.
        
        Args:
            analysis_results: Complete analysis results dictionary
        
        Returns:
            Dictionary mapping format name to report content
        """
        self.logger.info(f"Generating reports in formats: {', '.join(self.formats)}")
        
        reports = {}
        
        if 'text' in self.formats:
            reports['text'] = self.text_generator.generate(analysis_results)
        
        if 'json' in self.formats:
            reports['json'] = self.json_generator.generate(analysis_results)
        
        return reports
    
    def save_reports(self, reports: Dict[str, str], storage_orchestrator) -> Dict[str, str]:
        """
        Save generated reports to disk.
        
        Args:
            reports: Dictionary of reports by format
            storage_orchestrator: StorageOrchestrator instance
        
        Returns:
            Dictionary mapping format to file path
        """
        import os
        
        storage = self.config.get('storage', {})
        base_dir = storage.get('data_dir', 'data')
        reports_dir = storage.get('reports_dir', 'reports')
        reports_path = os.path.join(base_dir, reports_dir)
        
        os.makedirs(reports_path, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        saved_files = {}
        
        for fmt, content in reports.items():
            if fmt == 'text':
                filename = f"report_{timestamp}.txt"
            elif fmt == 'json':
                filename = f"report_{timestamp}.json"
            else:
                filename = f"report_{timestamp}.{fmt}"
            
            filepath = os.path.join(reports_path, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            saved_files[fmt] = filepath
            self.logger.info(f"Saved {fmt} report to {filepath}")
        
        return saved_files

"""
Ambient Wi-Fi Monitor - Main Application
Professional Wi-Fi environmental intelligence system.
"""

import sys
import argparse
import logging
from typing import Dict, Optional, List

# Import core modules
from src.utils import load_config, setup_logging, ensure_directories, ComplianceValidator
from src.collectors import DataCollectionOrchestrator
from src.normalizers import DataNormalizationOrchestrator
from src.storage import StorageOrchestrator
from src.analysis import BaselineModel, TemporalAnalyzer, AnomalyDetector, EnvironmentalFingerprint, DistanceEstimator
from src.reporting import ReportOrchestrator


class AmbientWifiMonitor:
    """
    Main application class for Ambient Wi-Fi Monitor.
    """
    
    def __init__(self, config_path: str = 'config.yaml'):
        """
        Initialize the application.
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = load_config(config_path)
        
        # Setup logging
        self.logger = setup_logging(self.config)
        self.logger.info("=" * 70)
        self.logger.info("Ambient Wi-Fi Monitor - Starting")
        self.logger.info("=" * 70)
        
        # Ensure directories exist
        ensure_directories(self.config)
        
        # Initialize compliance validator
        self.compliance = ComplianceValidator(self.config)
        
        # Initialize components
        self.collector = DataCollectionOrchestrator(self.config, self.compliance)
        self.normalizer = DataNormalizationOrchestrator()
        self.storage = StorageOrchestrator(self.config)
        self.baseline_model = BaselineModel(self.config)
        self.temporal_analyzer = TemporalAnalyzer(self.config)
        self.anomaly_detector = AnomalyDetector(self.config)
        self.fingerprinter = EnvironmentalFingerprint(self.config)
        self.distance_estimator = DistanceEstimator(self.config)
        self.reporter = ReportOrchestrator(self.config)
        
        self.logger.info("Application initialized successfully")
    
    def scan(self, save: bool = True, report: bool = True) -> Dict:
        """
        Perform a single scan and analysis.
        
        Args:
            save: Whether to save results to disk
            report: Whether to generate reports
        
        Returns:
            Analysis results dictionary
        """
        self.logger.info("Starting environmental scan")
        
        # Collect data
        raw_data = self.collector.collect_all()
        
        if not raw_data.get('success'):
            self.logger.error("Data collection failed")
            return {'success': False, 'error': 'Data collection failed'}
        
        # Normalize data
        normalized_data = self.normalizer.normalize_all(raw_data)
        
        # Save observation
        if save:
            obs_num = self.storage.save_observation(raw_data, normalized_data)
        else:
            metadata = self.storage.metadata_store.load()
            obs_num = metadata.get('observation_count', 0) + 1
        
        # Perform analysis
        analysis_results = self._analyze_observation(normalized_data, obs_num)
        
        # Generate reports
        if report:
            reports = self.reporter.generate_reports(analysis_results)
            
            # Print text report to console
            if 'text' in reports:
                print("\n" + reports['text'])
            
            # Save reports
            if save:
                self.reporter.save_reports(reports, self.storage)
        
        self.logger.info("Scan completed successfully")
        
        return analysis_results
    
    def _analyze_observation(self, observation: Dict, obs_num: int) -> Dict:
        """
        Perform comprehensive analysis on an observation.
        
        Args:
            observation: Normalized observation dictionary
            obs_num: Observation number
        
        Returns:
            Complete analysis results dictionary
        """
        self.logger.info(f"Analyzing observation #{obs_num}")
        
        # Load baseline
        baseline = self.storage.baseline_store.load('current')
        
        # Load historical observations
        historical = self.storage.normalized_store.load_recent(
            self.config.get('temporal', {}).get('long_term_window', 200)
        )
        
        # Baseline comparison
        if baseline:
            baseline_comparison = self.baseline_model.compare_to_baseline(observation, baseline)
            baseline_info = {
                'status': baseline.get('status'),
                'observation_count': baseline.get('observation_count'),
                'confidence': baseline.get('confidence')
            }
        else:
            baseline_comparison = {
                'status': 'NO_BASELINE',
                'confidence': 0.0,
                'current_bssid_count': observation.get('wlan_networks', {}).get('summary', {}).get('bssid_count', 0)
            }
            baseline_info = None
        
        # Temporal analysis
        if len(historical) > 0:
            temporal_analysis = self.temporal_analyzer.analyze(observation, historical)
        else:
            temporal_analysis = None
        
        # Anomaly detection
        anomaly_detection = self.anomaly_detector.detect(observation, baseline, historical)
        
        # Environmental fingerprint
        fingerprint = self.fingerprinter.generate(observation)
        
        # Compare fingerprint to baseline
        if baseline:
            baseline_fingerprint = self._get_or_create_baseline_fingerprint(baseline, historical)
            fingerprint_comparison = self.fingerprinter.compare(fingerprint, baseline_fingerprint)
        else:
            baseline_fingerprint = None
            fingerprint_comparison = None
        
        # Distance estimation
        distance_analysis = self.distance_estimator.analyze_observation(observation)
        
        # Update baseline if needed
        self._update_baseline_if_needed(historical, obs_num)
        
        return {
            'metadata': {
                'timestamp': observation.get('timestamp'),
                'observation_number': obs_num
            },
            'current_observation': observation,
            'baseline_info': baseline_info,
            'baseline_comparison': baseline_comparison,
            'temporal_analysis': temporal_analysis,
            'anomaly_detection': anomaly_detection,
            'fingerprint': fingerprint,
            'baseline_fingerprint': baseline_fingerprint,
            'fingerprint_comparison': fingerprint_comparison,
            'distance_analysis': distance_analysis
        }
    
    def _get_or_create_baseline_fingerprint(self, baseline: Dict, historical: List[Dict]) -> Dict:
        """
        Get or create fingerprint for baseline.
        
        Args:
            baseline: Baseline model
            historical: Historical observations
        
        Returns:
            Baseline fingerprint dictionary
        """
        # Check if baseline already has fingerprint
        if 'fingerprint' in baseline:
            return baseline['fingerprint']
        
        # Generate from historical observations used in baseline
        baseline_obs_count = baseline.get('observation_count', 0)
        
        if len(historical) >= baseline_obs_count:
            # Use the observations that were in the baseline
            baseline_obs = historical[:baseline_obs_count]
            fingerprints = [self.fingerprinter.generate(obs) for obs in baseline_obs]
            return self.fingerprinter.aggregate_fingerprints(fingerprints)
        
        # Fallback: use all available historical data
        fingerprints = [self.fingerprinter.generate(obs) for obs in historical]
        return self.fingerprinter.aggregate_fingerprints(fingerprints)
    
    def _update_baseline_if_needed(self, historical: List[Dict], current_obs_num: int) -> None:
        """
        Update baseline model if conditions are met.
        
        Args:
            historical: Historical observations
            current_obs_num: Current observation number
        """
        baseline_config = self.config.get('baseline', {})
        min_obs = baseline_config.get('min_observations', 100)
        update_interval = baseline_config.get('update_interval', 10)
        
        # Check if we should create/update baseline
        baseline = self.storage.baseline_store.load('current')
        
        if baseline is None and len(historical) >= min_obs:
            # Create initial baseline
            self.logger.info(f"Creating initial baseline from {len(historical)} observations")
            new_baseline = self.baseline_model.build(historical)
            self.storage.baseline_store.save(new_baseline, 'current')
            
            # Update metadata
            metadata = self.storage.metadata_store.load()
            metadata['baseline_initialized'] = True
            metadata['baseline_observation_count'] = len(historical)
            self.storage.metadata_store.save(metadata)
        
        elif baseline and current_obs_num % update_interval == 0:
            # Update existing baseline
            self.logger.info(f"Updating baseline with {len(historical)} observations")
            updated_baseline = self.baseline_model.build(historical)
            self.storage.baseline_store.save(updated_baseline, 'current')
            
            # Save previous baseline as backup
            self.storage.baseline_store.save(baseline, f'backup_{current_obs_num}')
    
    def status(self) -> Dict:
        """
        Get current system status.
        
        Returns:
            Status dictionary
        """
        metadata = self.storage.metadata_store.load()
        baseline = self.storage.baseline_store.load('current')
        
        status = {
            'observation_count': metadata.get('observation_count', 0),
            'last_observation': metadata.get('last_observation'),
            'baseline_initialized': metadata.get('baseline_initialized', False),
            'baseline_status': baseline.get('status') if baseline else 'not_initialized',
            'baseline_confidence': baseline.get('confidence') if baseline else 0.0,
            'baseline_observation_count': baseline.get('observation_count') if baseline else 0
        }
        
        return status
    
    def show_baseline(self) -> None:
        """
        Display baseline information.
        """
        baseline = self.storage.baseline_store.load('current')
        
        if not baseline:
            print("No baseline has been established yet.")
            print(f"Minimum observations required: {self.config.get('baseline', {}).get('min_observations', 100)}")
            return
        
        print("=" * 70)
        print("BASELINE MODEL")
        print("=" * 70)
        print()
        print(f"Status: {baseline.get('status')}")
        print(f"Confidence: {baseline.get('confidence', 0):.2f}")
        print(f"Observations: {baseline.get('observation_count', 0)}")
        print(f"Created: {baseline.get('created', 'Unknown')}")
        print()
        
        metrics = baseline.get('metrics', {})
        
        # BSSID metrics
        bssid = metrics.get('bssid', {})
        if bssid:
            print("BSSID Count Statistics:")
            print(f"  Mean: {bssid.get('mean', 0):.1f}")
            print(f"  Median: {bssid.get('median', 0):.1f}")
            print(f"  Std Dev: {bssid.get('std', 0):.1f}")
            print(f"  Range: {bssid.get('min', 0)} - {bssid.get('max', 0)}")
            print()
        
        # Signal metrics
        signal = metrics.get('signal', {})
        if signal:
            print("Signal Strength Statistics (%):")
            print(f"  Mean: {signal.get('mean', 0):.1f}%")
            print(f"  Std Dev: {signal.get('std', 0):.1f}%")
            print()
        
        # Channel metrics
        channel = metrics.get('channel', {})
        if channel:
            print("Channel Usage:")
            print(f"  Unique channels: {channel.get('unique_channels', 0)}")
            print(f"  Most common: {channel.get('most_common_channel', 'N/A')}")
            print()
        
        print("=" * 70)


def main():
    """
    Main entry point for CLI.
    """
    parser = argparse.ArgumentParser(
        description='Ambient Wi-Fi Monitor - Professional Wi-Fi Environmental Intelligence',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py scan                    # Single scan with analysis
  python main.py monitor --interval 60   # Continuous monitoring (60s interval)
  python main.py status                  # Show system status
  python main.py baseline --show         # Display baseline information
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Perform single scan and analysis')
    scan_parser.add_argument('--no-save', action='store_true', help='Do not save results')
    scan_parser.add_argument('--no-report', action='store_true', help='Do not generate report')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Continuous monitoring')
    monitor_parser.add_argument('--interval', type=int, default=60, 
                               help='Scan interval in seconds (default: 60)')
    monitor_parser.add_argument('--count', type=int, help='Number of scans (default: unlimited)')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    
    # Baseline command
    baseline_parser = subparsers.add_parser('baseline', help='Baseline operations')
    baseline_parser.add_argument('--show', action='store_true', help='Display baseline information')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate report from last observation')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        # Initialize application
        app = AmbientWifiMonitor()
        
        if args.command == 'scan':
            app.scan(save=not args.no_save, report=not args.no_report)
        
        elif args.command == 'monitor':
            import time
            
            count = 0
            max_count = args.count if args.count else float('inf')
            
            print(f"Starting continuous monitoring (interval: {args.interval}s)")
            print("Press Ctrl+C to stop")
            print()
            
            try:
                while count < max_count:
                    count += 1
                    print(f"\n[Scan #{count}]")
                    app.scan(save=True, report=True)
                    
                    if count < max_count:
                        print(f"\nWaiting {args.interval} seconds...")
                        time.sleep(args.interval)
            
            except KeyboardInterrupt:
                print("\n\nMonitoring stopped by user")
        
        elif args.command == 'status':
            status = app.status()
            
            print("=" * 70)
            print("SYSTEM STATUS")
            print("=" * 70)
            print()
            print(f"Total observations: {status['observation_count']}")
            print(f"Last observation: {status['last_observation']}")
            print()
            print(f"Baseline initialized: {status['baseline_initialized']}")
            if status['baseline_initialized']:
                print(f"Baseline status: {status['baseline_status']}")
                print(f"Baseline confidence: {status['baseline_confidence']:.2f}")
                print(f"Baseline observations: {status['baseline_observation_count']}")
            print()
            print("=" * 70)
        
        elif args.command == 'baseline':
            if args.show:
                app.show_baseline()
        
        elif args.command == 'report':
            # Load last observation and generate report
            recent = app.storage.normalized_store.load_recent(1)
            if recent:
                obs_num = app.storage.metadata_store.load().get('observation_count', 0)
                analysis = app._analyze_observation(recent[0], obs_num)
                reports = app.reporter.generate_reports(analysis)
                
                if 'text' in reports:
                    print("\n" + reports['text'])
            else:
                print("No observations found")
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(0)
    
    except Exception as e:
        logging.error(f"Application error: {e}", exc_info=True)
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

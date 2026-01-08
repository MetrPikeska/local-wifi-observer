"""
Ambient Wi-Fi Monitor - Data Collectors Module
Responsible for executing OS-level commands to gather Wi-Fi environmental data.
"""

import subprocess
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple


class CommandExecutor:
    """
    Executes Windows system commands with timeout and error handling.
    """
    
    def __init__(self, timeout: int = 30):
        """
        Initialize command executor.
        
        Args:
            timeout: Command timeout in seconds
        """
        self.timeout = timeout
        self.logger = logging.getLogger('ambient_wifi_monitor.collectors')
    
    def execute(self, command: str) -> Tuple[bool, str, str]:
        """
        Execute a system command and capture output.
        
        Args:
            command: Command string to execute
        
        Returns:
            Tuple of (success: bool, stdout: str, stderr: str)
        """
        self.logger.debug(f"Executing command: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                encoding='utf-8',
                errors='replace'
            )
            
            success = result.returncode == 0
            
            if not success:
                self.logger.warning(
                    f"Command failed with return code {result.returncode}: {command}"
                )
            
            return success, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timeout after {self.timeout}s: {command}")
            return False, "", f"Command timeout after {self.timeout} seconds"
        
        except Exception as e:
            self.logger.error(f"Command execution error: {e}")
            return False, "", str(e)


class WlanInterfaceCollector:
    """
    Collects data from 'netsh wlan show interfaces' command.
    """
    
    def __init__(self, executor: CommandExecutor):
        """
        Initialize WLAN interface collector.
        
        Args:
            executor: CommandExecutor instance
        """
        self.executor = executor
        self.logger = logging.getLogger('ambient_wifi_monitor.collectors.interface')
    
    def collect(self) -> Dict:
        """
        Collect current WLAN interface information.
        
        Returns:
            Dictionary containing collection results
        """
        self.logger.info("Collecting WLAN interface data")
        
        success, stdout, stderr = self.executor.execute("netsh wlan show interfaces")
        
        return {
            'timestamp': datetime.now().isoformat(),
            'command': 'netsh wlan show interfaces',
            'success': success,
            'stdout': stdout,
            'stderr': stderr,
            'data_type': 'wlan_interface'
        }


class WlanNetworksCollector:
    """
    Collects data from 'netsh wlan show networks mode=bssid' command.
    """
    
    def __init__(self, executor: CommandExecutor):
        """
        Initialize WLAN networks collector.
        
        Args:
            executor: CommandExecutor instance
        """
        self.executor = executor
        self.logger = logging.getLogger('ambient_wifi_monitor.collectors.networks')
    
    def collect(self) -> Dict:
        """
        Collect visible WLAN networks with BSSID information.
        
        Returns:
            Dictionary containing collection results
        """
        self.logger.info("Collecting WLAN networks data")
        
        success, stdout, stderr = self.executor.execute("netsh wlan show networks mode=bssid")
        
        return {
            'timestamp': datetime.now().isoformat(),
            'command': 'netsh wlan show networks mode=bssid',
            'success': success,
            'stdout': stdout,
            'stderr': stderr,
            'data_type': 'wlan_networks'
        }


class IpConfigCollector:
    """
    Collects data from 'ipconfig /all' command.
    """
    
    def __init__(self, executor: CommandExecutor):
        """
        Initialize ipconfig collector.
        
        Args:
            executor: CommandExecutor instance
        """
        self.executor = executor
        self.logger = logging.getLogger('ambient_wifi_monitor.collectors.ipconfig')
    
    def collect(self) -> Dict:
        """
        Collect network configuration information.
        
        Returns:
            Dictionary containing collection results
        """
        self.logger.info("Collecting ipconfig data")
        
        success, stdout, stderr = self.executor.execute("ipconfig /all")
        
        return {
            'timestamp': datetime.now().isoformat(),
            'command': 'ipconfig /all',
            'success': success,
            'stdout': stdout,
            'stderr': stderr,
            'data_type': 'ipconfig'
        }


class ArpCollector:
    """
    Collects data from 'arp -a' command.
    """
    
    def __init__(self, executor: CommandExecutor):
        """
        Initialize ARP collector.
        
        Args:
            executor: CommandExecutor instance
        """
        self.executor = executor
        self.logger = logging.getLogger('ambient_wifi_monitor.collectors.arp')
    
    def collect(self) -> Dict:
        """
        Collect ARP table information.
        
        Returns:
            Dictionary containing collection results
        """
        self.logger.info("Collecting ARP table data")
        
        success, stdout, stderr = self.executor.execute("arp -a")
        
        return {
            'timestamp': datetime.now().isoformat(),
            'command': 'arp -a',
            'success': success,
            'stdout': stdout,
            'stderr': stderr,
            'data_type': 'arp'
        }


class DataCollectionOrchestrator:
    """
    Orchestrates all data collection operations.
    """
    
    def __init__(self, config: Dict, compliance_validator):
        """
        Initialize data collection orchestrator.
        
        Args:
            config: Application configuration dictionary
            compliance_validator: ComplianceValidator instance
        """
        self.config = config
        self.compliance_validator = compliance_validator
        self.logger = logging.getLogger('ambient_wifi_monitor.collectors')
        
        # Initialize command executor
        timeout = config.get('collection', {}).get('command_timeout', 30)
        self.executor = CommandExecutor(timeout=timeout)
        
        # Initialize individual collectors
        self.interface_collector = WlanInterfaceCollector(self.executor)
        self.networks_collector = WlanNetworksCollector(self.executor)
        self.ipconfig_collector = IpConfigCollector(self.executor)
        self.arp_collector = ArpCollector(self.executor)
    
    def collect_all(self) -> Dict:
        """
        Execute all data collectors and aggregate results.
        
        Returns:
            Dictionary containing all collection results
        """
        self.logger.info("Starting comprehensive data collection")
        
        # Validate compliance
        self.compliance_validator.validate_operation('read_only_collection')
        
        # Collect from all sources
        results = {
            'collection_timestamp': datetime.now().isoformat(),
            'wlan_interface': self.interface_collector.collect(),
            'wlan_networks': self.networks_collector.collect(),
            'ipconfig': self.ipconfig_collector.collect(),
            'arp': self.arp_collector.collect()
        }
        
        # Check for failures
        failures = [
            name for name, data in results.items()
            if isinstance(data, dict) and not data.get('success', False)
        ]
        
        if failures:
            self.logger.warning(f"Collection failures: {', '.join(failures)}")
        
        results['success'] = len(failures) == 0
        results['failures'] = failures
        
        self.logger.info(f"Data collection completed. Failures: {len(failures)}")
        
        return results

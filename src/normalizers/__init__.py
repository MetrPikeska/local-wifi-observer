"""
Ambient Wi-Fi Monitor - Data Normalizers Module
Parses raw OS command outputs into structured, analyzable data.
"""

import re
import logging
from typing import Dict, List, Optional
from datetime import datetime


class WlanInterfaceNormalizer:
    """
    Normalizes output from 'netsh wlan show interfaces'.
    """
    
    def __init__(self):
        self.logger = logging.getLogger('ambient_wifi_monitor.normalizers.interface')
    
    def normalize(self, raw_data: Dict) -> Dict:
        """
        Parse and normalize WLAN interface data.
        
        Args:
            raw_data: Raw collection data dictionary
        
        Returns:
            Normalized data dictionary
        """
        if not raw_data.get('success', False):
            self.logger.warning("Cannot normalize failed collection")
            return {
                'timestamp': raw_data.get('timestamp'),
                'success': False,
                'data': None
            }
        
        stdout = raw_data.get('stdout', '')
        
        # Parse key-value pairs
        interface_data = {}
        for line in stdout.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                if value:
                    interface_data[key] = value
        
        return {
            'timestamp': raw_data.get('timestamp'),
            'success': True,
            'data': interface_data
        }


class WlanNetworksNormalizer:
    """
    Normalizes output from 'netsh wlan show networks mode=bssid'.
    """
    
    def __init__(self):
        self.logger = logging.getLogger('ambient_wifi_monitor.normalizers.networks')
    
    def normalize(self, raw_data: Dict) -> Dict:
        """
        Parse and normalize WLAN networks data.
        
        Args:
            raw_data: Raw collection data dictionary
        
        Returns:
            Normalized data dictionary with list of networks and BSSIDs
        """
        if not raw_data.get('success', False):
            self.logger.warning("Cannot normalize failed collection")
            return {
                'timestamp': raw_data.get('timestamp'),
                'success': False,
                'networks': [],
                'bssids': [],
                'summary': {
                    'network_count': 0,
                    'bssid_count': 0
                }
            }
        
        stdout = raw_data.get('stdout', '')
        networks = []
        current_network = None
        
        for line in stdout.split('\n'):
            line = line.strip()
            
            # New network
            if line.startswith('SSID'):
                # Save previous network
                if current_network:
                    networks.append(current_network)
                
                # Start new network
                parts = line.split(':', 1)
                ssid = parts[1].strip() if len(parts) > 1 else ''
                current_network = {
                    'ssid': ssid,
                    'bssids': []
                }
            
            # Network type
            elif 'Network type' in line:
                if current_network:
                    parts = line.split(':', 1)
                    current_network['network_type'] = parts[1].strip() if len(parts) > 1 else ''
            
            # Authentication
            elif 'Authentication' in line:
                if current_network:
                    parts = line.split(':', 1)
                    current_network['authentication'] = parts[1].strip() if len(parts) > 1 else ''
            
            # Encryption
            elif 'Encryption' in line:
                if current_network:
                    parts = line.split(':', 1)
                    current_network['encryption'] = parts[1].strip() if len(parts) > 1 else ''
            
            # BSSID
            elif 'BSSID' in line:
                if current_network:
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        bssid = parts[1].strip()
                        # Extract MAC address pattern
                        mac_match = re.search(r'([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}', bssid)
                        if mac_match:
                            current_network['bssids'].append({
                                'bssid': mac_match.group(0),
                                'signal': None,
                                'channel': None,
                                'radio_type': None
                            })
            
            # Signal
            elif 'Signal' in line and current_network and current_network['bssids']:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    signal_str = parts[1].strip().rstrip('%')
                    try:
                        current_network['bssids'][-1]['signal'] = int(signal_str)
                    except ValueError:
                        pass
            
            # Channel
            elif 'Channel' in line and current_network and current_network['bssids']:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    try:
                        current_network['bssids'][-1]['channel'] = int(parts[1].strip())
                    except ValueError:
                        pass
            
            # Radio type
            elif 'Radio type' in line and current_network and current_network['bssids']:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    current_network['bssids'][-1]['radio_type'] = parts[1].strip()
        
        # Save last network
        if current_network:
            networks.append(current_network)
        
        # Flatten BSSID list
        all_bssids = []
        for network in networks:
            for bssid_info in network.get('bssids', []):
                all_bssids.append({
                    'ssid': network.get('ssid', ''),
                    'bssid': bssid_info.get('bssid'),
                    'signal': bssid_info.get('signal'),
                    'channel': bssid_info.get('channel'),
                    'radio_type': bssid_info.get('radio_type'),
                    'network_type': network.get('network_type', ''),
                    'authentication': network.get('authentication', ''),
                    'encryption': network.get('encryption', '')
                })
        
        return {
            'timestamp': raw_data.get('timestamp'),
            'success': True,
            'networks': networks,
            'bssids': all_bssids,
            'summary': {
                'network_count': len(networks),
                'bssid_count': len(all_bssids),
                'ssids': list(set(n['ssid'] for n in networks if n.get('ssid'))),
                'channels': list(set(b['channel'] for b in all_bssids if b.get('channel'))),
                'radio_types': list(set(b['radio_type'] for b in all_bssids if b.get('radio_type')))
            }
        }


class IpConfigNormalizer:
    """
    Normalizes output from 'ipconfig /all'.
    """
    
    def __init__(self):
        self.logger = logging.getLogger('ambient_wifi_monitor.normalizers.ipconfig')
    
    def normalize(self, raw_data: Dict) -> Dict:
        """
        Parse and normalize ipconfig data.
        
        Args:
            raw_data: Raw collection data dictionary
        
        Returns:
            Normalized data dictionary
        """
        if not raw_data.get('success', False):
            self.logger.warning("Cannot normalize failed collection")
            return {
                'timestamp': raw_data.get('timestamp'),
                'success': False,
                'adapters': []
            }
        
        stdout = raw_data.get('stdout', '')
        adapters = []
        current_adapter = None
        
        for line in stdout.split('\n'):
            # New adapter
            if line and not line.startswith(' ') and ':' in line:
                if current_adapter:
                    adapters.append(current_adapter)
                current_adapter = {
                    'name': line.split(':')[0].strip(),
                    'properties': {}
                }
            
            # Adapter property
            elif line.startswith(' ') and ':' in line and current_adapter:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_').replace('.', '')
                value = value.strip()
                if value:
                    current_adapter['properties'][key] = value
        
        if current_adapter:
            adapters.append(current_adapter)
        
        return {
            'timestamp': raw_data.get('timestamp'),
            'success': True,
            'adapters': adapters,
            'summary': {
                'adapter_count': len(adapters)
            }
        }


class ArpNormalizer:
    """
    Normalizes output from 'arp -a'.
    """
    
    def __init__(self):
        self.logger = logging.getLogger('ambient_wifi_monitor.normalizers.arp')
    
    def normalize(self, raw_data: Dict) -> Dict:
        """
        Parse and normalize ARP table data.
        
        Args:
            raw_data: Raw collection data dictionary
        
        Returns:
            Normalized data dictionary
        """
        if not raw_data.get('success', False):
            self.logger.warning("Cannot normalize failed collection")
            return {
                'timestamp': raw_data.get('timestamp'),
                'success': False,
                'entries': []
            }
        
        stdout = raw_data.get('stdout', '')
        entries = []
        current_interface = None
        
        for line in stdout.split('\n'):
            line = line.strip()
            
            # Interface line
            if line.startswith('Interface:'):
                current_interface = line.split('Interface:')[1].strip()
            
            # ARP entry
            elif re.match(r'\d+\.\d+\.\d+\.\d+', line):
                parts = line.split()
                if len(parts) >= 3:
                    entries.append({
                        'interface': current_interface,
                        'ip': parts[0],
                        'mac': parts[1],
                        'type': parts[2] if len(parts) > 2 else ''
                    })
        
        return {
            'timestamp': raw_data.get('timestamp'),
            'success': True,
            'entries': entries,
            'summary': {
                'entry_count': len(entries)
            }
        }


class DataNormalizationOrchestrator:
    """
    Orchestrates all data normalization operations.
    """
    
    def __init__(self):
        self.logger = logging.getLogger('ambient_wifi_monitor.normalizers')
        
        # Initialize normalizers
        self.interface_normalizer = WlanInterfaceNormalizer()
        self.networks_normalizer = WlanNetworksNormalizer()
        self.ipconfig_normalizer = IpConfigNormalizer()
        self.arp_normalizer = ArpNormalizer()
    
    def normalize_all(self, raw_collection: Dict) -> Dict:
        """
        Normalize all collected raw data.
        
        Args:
            raw_collection: Raw collection dictionary from collectors
        
        Returns:
            Dictionary containing all normalized data
        """
        self.logger.info("Starting data normalization")
        
        normalized = {
            'timestamp': raw_collection.get('collection_timestamp'),
            'wlan_interface': self.interface_normalizer.normalize(
                raw_collection.get('wlan_interface', {})
            ),
            'wlan_networks': self.networks_normalizer.normalize(
                raw_collection.get('wlan_networks', {})
            ),
            'ipconfig': self.ipconfig_normalizer.normalize(
                raw_collection.get('ipconfig', {})
            ),
            'arp': self.arp_normalizer.normalize(
                raw_collection.get('arp', {})
            )
        }
        
        self.logger.info("Data normalization completed")
        
        return normalized

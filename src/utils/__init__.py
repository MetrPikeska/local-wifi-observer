"""
Ambient Wi-Fi Monitor - Utilities Module
Common utilities and helper functions.
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict
import yaml


def setup_logging(config: Dict[str, Any]) -> logging.Logger:
    """
    Configure application logging based on configuration.
    
    Args:
        config: Application configuration dictionary
    
    Returns:
        Configured logger instance
    """
    log_config = config.get('logging', {})
    level_name = log_config.get('level', 'INFO')
    level = getattr(logging, level_name, logging.INFO)
    
    logger = logging.getLogger('ambient_wifi_monitor')
    logger.setLevel(level)
    logger.handlers.clear()
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if log_config.get('console_enabled', True):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_config.get('file_enabled', True):
        log_file = log_config.get('log_file', 'logs/ambient-wifi-monitor.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def load_config(config_path: str = 'config.yaml') -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
    
    Returns:
        Configuration dictionary
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def ensure_directories(config: Dict[str, Any]) -> None:
    """
    Ensure all required data directories exist.
    
    Args:
        config: Application configuration dictionary
    """
    storage = config.get('storage', {})
    base_dir = storage.get('data_dir', 'data')
    
    directories = [
        base_dir,
        os.path.join(base_dir, storage.get('raw_dir', 'raw')),
        os.path.join(base_dir, storage.get('normalized_dir', 'normalized')),
        os.path.join(base_dir, storage.get('baselines_dir', 'baselines')),
        os.path.join(base_dir, storage.get('reports_dir', 'reports')),
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def get_timestamp(fmt: str = None) -> str:
    """
    Get current timestamp in specified format.
    
    Args:
        fmt: Timestamp format string (defaults to ISO format)
    
    Returns:
        Formatted timestamp string
    """
    if fmt is None:
        return datetime.now().isoformat()
    return datetime.now().strftime(fmt)


def get_data_path(config: Dict[str, Any], subdir: str, filename: str = None) -> str:
    """
    Construct path to data file or directory.
    
    Args:
        config: Application configuration dictionary
        subdir: Subdirectory name (raw, normalized, baselines, reports)
        filename: Optional filename to append
    
    Returns:
        Full path to data location
    """
    storage = config.get('storage', {})
    base_dir = storage.get('data_dir', 'data')
    subdir_name = storage.get(f'{subdir}_dir', subdir)
    
    path = os.path.join(base_dir, subdir_name)
    
    if filename:
        path = os.path.join(path, filename)
    
    return path


class ComplianceValidator:
    """
    Validates that operations comply with ethical and legal constraints.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize compliance validator.
        
        Args:
            config: Application configuration dictionary
        """
        self.compliance = config.get('compliance', {})
        self.logger = logging.getLogger('ambient_wifi_monitor.compliance')
    
    def validate_operation(self, operation: str) -> bool:
        """
        Check if an operation is permitted.
        
        Args:
            operation: Operation name to validate
        
        Returns:
            True if operation is permitted, False otherwise
        
        Raises:
            PermissionError: If operation violates compliance rules
        """
        prohibited = {
            'packet_sniffing': self.compliance.get('packet_sniffing_disabled', True),
            'monitor_mode': self.compliance.get('monitor_mode_disabled', True),
            'tracking': self.compliance.get('tracking_disabled', True),
            'mac_tracking': self.compliance.get('mac_tracking_disabled', True),
            'person_identification': self.compliance.get('person_identification_disabled', True),
            'location_computation': self.compliance.get('location_computation_disabled', True),
        }
        
        if operation in prohibited and prohibited[operation]:
            self.logger.error(f"Prohibited operation attempted: {operation}")
            raise PermissionError(
                f"Operation '{operation}' is disabled by compliance configuration. "
                "This tool is designed for ethical, read-only environmental analysis only."
            )
        
        return True
    
    def log_access(self, resource: str, purpose: str) -> None:
        """
        Log data access for audit trail.
        
        Args:
            resource: Resource being accessed
            purpose: Purpose of access
        """
        self.logger.info(f"Data access - Resource: {resource}, Purpose: {purpose}")

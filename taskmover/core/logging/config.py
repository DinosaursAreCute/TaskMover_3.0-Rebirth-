"""
Logging Configuration Management

Handles loading, validation, and management of logging configuration
from YAML files with support for environment variable overrides.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum


class LogLevel(Enum):
    """Standard logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO" 
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class FileRotationConfig:
    """Configuration for log file rotation and cleanup"""
    max_size: str = "10MB"  # Size before rotation (e.g., "10MB", "1GB")
    backup_count: int = 5   # Number of backup files to keep
    retention_days: int = 30  # Days to keep log files
    compression_enabled: bool = True  # Compress rotated files
    cleanup_schedule: str = "daily"  # When to run cleanup (immediate, daily, weekly)
    

@dataclass
class FileConfig:
    """File logging configuration"""
    enabled: bool = True
    path: str = "logs/taskmover.log"
    rotation: FileRotationConfig = field(default_factory=FileRotationConfig)
    format: str = "detailed"  # detailed, compact, json
    

@dataclass 
class ConsoleConfig:
    """Console logging configuration"""
    enabled: bool = True
    colors: bool = True
    format: str = "compact"  # compact, detailed, minimal
    

@dataclass
class LoggingConfig:
    """Main logging configuration"""
    level: LogLevel = LogLevel.INFO
    console: ConsoleConfig = field(default_factory=ConsoleConfig)
    file: FileConfig = field(default_factory=FileConfig)
    components: Dict[str, LogLevel] = field(default_factory=dict)
    session_tracking: bool = True
    performance_monitoring: bool = False
    

class ConfigurationLoader:
    """Loads and manages logging configuration"""
    
    DEFAULT_CONFIG_PATH = "taskmover/core/logging_config.yml"
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        self.config_path = Path(config_path) if config_path else None
        self._config: Optional[LoggingConfig] = None
        
    def load_config(self) -> LoggingConfig:
        """Load configuration from file with environment variable overrides"""
        if self._config is None:
            self._config = self._load_from_file()
            self._apply_environment_overrides()
            self._validate_config()
        return self._config
    
    def _load_from_file(self) -> LoggingConfig:
        """Load configuration from YAML file"""
        config_data = {}
        
        # Try to load from specified path or default locations
        config_paths = []
        if self.config_path:
            config_paths.append(self.config_path)
        
        # Add default paths
        config_paths.extend([
            Path("logging_config.yml"),
            Path("taskmover/core/logging_config.yml"),
            Path("config/logging.yml"),
        ])
        
        for path in config_paths:
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        config_data = yaml.safe_load(f) or {}
                    break
                except Exception as e:
                    print(f"Warning: Failed to load config from {path}: {e}")
                    continue
        
        # Create config from loaded data
        return self._create_config_from_dict(config_data.get('logging', {}))
    
    def _create_config_from_dict(self, data: Dict[str, Any]) -> LoggingConfig:
        """Create LoggingConfig from dictionary data"""
        
        # Parse file rotation config
        rotation_data = data.get('file', {}).get('rotation', {})
        rotation_config = FileRotationConfig(
            max_size=rotation_data.get('max_size', '10MB'),
            backup_count=rotation_data.get('backup_count', 5),
            retention_days=rotation_data.get('retention_days', 30),
            compression_enabled=rotation_data.get('compression_enabled', True),
            cleanup_schedule=rotation_data.get('cleanup_schedule', 'daily'),
        )
        
        # Parse file config
        file_data = data.get('file', {})
        file_config = FileConfig(
            enabled=file_data.get('enabled', True),
            path=file_data.get('path', 'logs/taskmover.log'),
            rotation=rotation_config,
            format=file_data.get('format', 'detailed'),
        )
        
        # Parse console config
        console_data = data.get('console', {})
        console_config = ConsoleConfig(
            enabled=console_data.get('enabled', True),
            colors=console_data.get('colors', True),
            format=console_data.get('format', 'compact'),
        )
        
        # Parse component levels
        components = {}
        for component, level_str in data.get('components', {}).items():
            try:
                components[component] = LogLevel(level_str.upper())
            except ValueError:
                print(f"Warning: Invalid log level '{level_str}' for component '{component}'")
        
        # Create main config
        return LoggingConfig(
            level=LogLevel(data.get('level', 'INFO').upper()),
            console=console_config,
            file=file_config,
            components=components,
            session_tracking=data.get('session_tracking', True),
            performance_monitoring=data.get('performance_monitoring', False),
        )
    
    def _apply_environment_overrides(self):
        """Apply environment variable overrides"""
        if not self._config:
            return
            
        # Override global log level
        if env_level := os.getenv('TASKMOVER_LOG_LEVEL'):
            try:
                self._config.level = LogLevel(env_level.upper())
            except ValueError:
                print(f"Warning: Invalid log level in TASKMOVER_LOG_LEVEL: {env_level}")
        
        # Override file path
        if env_path := os.getenv('TASKMOVER_LOG_FILE'):
            self._config.file.path = env_path
            
        # Override console colors
        if env_colors := os.getenv('TASKMOVER_LOG_COLORS'):
            self._config.console.colors = env_colors.lower() in ('true', '1', 'yes', 'on')
            
        # Override file size limit
        if env_size := os.getenv('TASKMOVER_LOG_MAX_SIZE'):
            self._config.file.rotation.max_size = env_size
    
    def _validate_config(self):
        """Validate configuration settings"""
        if not self._config:
            return
            
        # Validate file path directory exists or can be created
        log_dir = Path(self._config.file.path).parent
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Warning: Cannot create log directory {log_dir}: {e}")
        
        # Validate max_size format
        if not self._validate_size_format(self._config.file.rotation.max_size):
            print(f"Warning: Invalid max_size format: {self._config.file.rotation.max_size}")
            self._config.file.rotation.max_size = "10MB"
    
    def _validate_size_format(self, size_str: str) -> bool:
        """Validate size format (e.g., '10MB', '1GB')"""
        import re
        pattern = r'^\d+(?:\.\d+)?\s*(?:B|KB|MB|GB|TB)$'
        return bool(re.match(pattern, size_str.upper().replace(' ', '')))
    
    def create_default_config_file(self, path: Optional[Path] = None) -> Path:
        """Create a default configuration file"""
        config_path = path or Path("logging_config.yml")
        
        default_config = {
            'logging': {
                'level': 'INFO',
                'console': {
                    'enabled': True,
                    'colors': True,
                    'format': 'compact'
                },
                'file': {
                    'enabled': True,
                    'path': 'logs/taskmover.log',
                    'format': 'detailed',
                    'rotation': {
                        'max_size': '10MB',
                        'backup_count': 5,
                        'retention_days': 30,
                        'compression_enabled': True,
                        'cleanup_schedule': 'daily'
                    }
                },
                'components': {
                    'ui': 'INFO',
                    'core': 'INFO', 
                    'build': 'WARNING',
                    'tests': 'DEBUG'
                },
                'session_tracking': True,
                'performance_monitoring': False
            }
        }
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False, indent=2)
        
        return config_path
    
    def reload_config(self) -> LoggingConfig:
        """Reload configuration from file"""
        self._config = None
        return self.load_config()


def parse_size_to_bytes(size_str: str) -> int:
    """Convert size string to bytes (e.g., '10MB' -> 10485760)"""
    import re
    
    match = re.match(r'^(\d+(?:\.\d+)?)\s*([KMGT]?B)$', size_str.upper().replace(' ', ''))
    if not match:
        raise ValueError(f"Invalid size format: {size_str}")
    
    value, unit = match.groups()
    value = float(value)
    
    multipliers = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 ** 2, 
        'GB': 1024 ** 3,
        'TB': 1024 ** 4,
    }
    
    return int(value * multipliers[unit])


# Global configuration instance
_config_loader: Optional[ConfigurationLoader] = None


def get_config() -> LoggingConfig:
    """Get the global logging configuration"""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigurationLoader()
    return _config_loader.load_config()


def reload_config() -> LoggingConfig:
    """Reload the global logging configuration"""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigurationLoader()
    return _config_loader.reload_config()

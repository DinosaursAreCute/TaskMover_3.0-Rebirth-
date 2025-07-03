"""
Predefined Setting Definitions

Provides comprehensive predefined setting definitions for all major
TaskMover components including user preferences, application settings,
UI configuration, and rule system settings.
"""

import logging
from pathlib import Path
from typing import List

from . import (
    SettingDefinition,
    SettingScope,
    SettingType,
)


def get_user_setting_definitions() -> List[SettingDefinition]:
    """Get predefined user setting definitions."""
    return [
        # User Interface Preferences
        SettingDefinition(
            key="ui.theme",
            name="UI Theme",
            description="Application theme (light, dark, auto)",
            type=SettingType.ENUM,
            default_value="auto",
            scope=SettingScope.USER,
            allowed_values=["light", "dark", "auto"],
            category="Appearance",
            help_text="Choose the application theme. Auto will follow system theme."
        ),
        
        SettingDefinition(
            key="ui.language",
            name="Language",
            description="Application language",
            type=SettingType.STRING,
            default_value="en",
            scope=SettingScope.USER,
            category="Localization",
            help_text="Set the application language (ISO 639-1 code)"
        ),
        
        SettingDefinition(
            key="ui.font_size",
            name="Font Size",
            description="UI font size in points",
            type=SettingType.INTEGER,
            default_value=10,
            scope=SettingScope.USER,
            min_value=8,
            max_value=24,
            category="Appearance",
            help_text="Adjust the font size for better readability"
        ),
        
        SettingDefinition(
            key="ui.font_family",
            name="Font Family",
            description="UI font family",
            type=SettingType.STRING,
            default_value="Segoe UI",
            scope=SettingScope.USER,
            category="Appearance",
            help_text="Choose the font family for the user interface"
        ),
        
        SettingDefinition(
            key="ui.show_tooltips",
            name="Show Tooltips",
            description="Show helpful tooltips in the interface",
            type=SettingType.BOOLEAN,
            default_value=True,
            scope=SettingScope.USER,
            category="Interface",
            help_text="Enable or disable tooltips for UI elements"
        ),
        
        SettingDefinition(
            key="ui.confirm_deletions",
            name="Confirm Deletions",
            description="Show confirmation dialog for file deletions",
            type=SettingType.BOOLEAN,
            default_value=True,
            scope=SettingScope.USER,
            category="Safety",
            help_text="Require confirmation before deleting files"
        ),
        
        # Directory and File Preferences
        SettingDefinition(
            key="directories.default_source",
            name="Default Source Directory",
            description="Default directory to monitor for files",
            type=SettingType.PATH,
            default_value=str(Path.home() / "Downloads"),
            scope=SettingScope.USER,
            category="Directories",
            help_text="Set the default directory to watch for new files"
        ),
        
        SettingDefinition(
            key="directories.default_destination",
            name="Default Destination Directory",
            description="Default directory for organized files",
            type=SettingType.PATH,
            default_value=str(Path.home() / "Documents" / "Organized"),
            scope=SettingScope.USER,
            category="Directories",
            help_text="Set the default destination for organized files"
        ),
        
        SettingDefinition(
            key="directories.favorites",
            name="Favorite Directories",
            description="List of frequently used directories",
            type=SettingType.LIST,
            default_value=[],
            scope=SettingScope.USER,
            category="Directories",
            help_text="Bookmark frequently used directories for quick access"
        ),
        
        SettingDefinition(
            key="directories.recent_limit",
            name="Recent Directories Limit",
            description="Maximum number of recent directories to remember",
            type=SettingType.INTEGER,
            default_value=10,
            scope=SettingScope.USER,
            min_value=5,
            max_value=50,
            category="Directories",
            help_text="Control how many recent directories are remembered"
        ),
        
        # File Operation Preferences
        SettingDefinition(
            key="files.default_action",
            name="Default File Action",
            description="Default action for file operations (move, copy, link)",
            type=SettingType.ENUM,
            default_value="move",
            scope=SettingScope.USER,
            allowed_values=["move", "copy", "link"],
            category="File Operations",
            help_text="Choose the default action when organizing files"
        ),
        
        SettingDefinition(
            key="files.preserve_timestamps",
            name="Preserve Timestamps",
            description="Keep original file timestamps during operations",
            type=SettingType.BOOLEAN,
            default_value=True,
            scope=SettingScope.USER,
            category="File Operations",
            help_text="Maintain original creation and modification dates"
        ),
        
        SettingDefinition(
            key="files.handle_duplicates",
            name="Duplicate Handling",
            description="How to handle duplicate files (skip, rename, overwrite, ask)",
            type=SettingType.ENUM,
            default_value="ask",
            scope=SettingScope.USER,
            allowed_values=["skip", "rename", "overwrite", "ask"],
            category="File Operations",
            help_text="Choose how to handle files with the same name"
        ),
        
        SettingDefinition(
            key="files.create_directories",
            name="Create Directories",
            description="Automatically create destination directories if they don't exist",
            type=SettingType.BOOLEAN,
            default_value=True,
            scope=SettingScope.USER,
            category="File Operations",
            help_text="Create target directories automatically during operations"
        ),
        
        # Notification Preferences
        SettingDefinition(
            key="notifications.enabled",
            name="Enable Notifications",
            description="Show desktop notifications for completed operations",
            type=SettingType.BOOLEAN,
            default_value=True,
            scope=SettingScope.USER,
            category="Notifications",
            help_text="Display notifications when file operations complete"
        ),
        
        SettingDefinition(
            key="notifications.sound",
            name="Notification Sound",
            description="Play sound with notifications",
            type=SettingType.BOOLEAN,
            default_value=False,
            scope=SettingScope.USER,
            category="Notifications",
            help_text="Play an audio notification for completed operations"
        ),
        
        SettingDefinition(
            key="notifications.timeout",
            name="Notification Timeout",
            description="How long notifications stay visible (seconds)",
            type=SettingType.INTEGER,
            default_value=5,
            scope=SettingScope.USER,
            min_value=1,
            max_value=30,
            category="Notifications",
            help_text="Set how long notifications remain visible"
        ),
    ]


def get_application_setting_definitions() -> List[SettingDefinition]:
    """Get predefined application setting definitions."""
    return [
        # Application Behavior
        SettingDefinition(
            key="app.auto_start",
            name="Auto Start",
            description="Start TaskMover when Windows starts",
            type=SettingType.BOOLEAN,
            default_value=False,
            scope=SettingScope.APPLICATION,
            category="Startup",
            help_text="Automatically start TaskMover with Windows",
            restart_required=True
        ),
        
        SettingDefinition(
            key="app.minimize_to_tray",
            name="Minimize to Tray",
            description="Minimize to system tray instead of taskbar",
            type=SettingType.BOOLEAN,
            default_value=True,
            scope=SettingScope.APPLICATION,
            category="Window",
            help_text="Hide in system tray when minimized"
        ),
        
        SettingDefinition(
            key="app.close_to_tray",
            name="Close to Tray",
            description="Close to system tray instead of exiting",
            type=SettingType.BOOLEAN,
            default_value=False,
            scope=SettingScope.APPLICATION,
            category="Window",
            help_text="Keep running in tray when window is closed"
        ),
        
        SettingDefinition(
            key="app.check_updates",
            name="Check for Updates",
            description="Automatically check for application updates",
            type=SettingType.BOOLEAN,
            default_value=True,
            scope=SettingScope.APPLICATION,
            category="Updates",
            help_text="Check for new versions automatically"
        ),
        
        SettingDefinition(
            key="app.update_frequency",
            name="Update Check Frequency",
            description="How often to check for updates (hours)",
            type=SettingType.INTEGER,
            default_value=24,
            scope=SettingScope.APPLICATION,
            min_value=1,
            max_value=168,  # 1 week
            category="Updates",
            dependencies=["app.check_updates"],
            help_text="Frequency of automatic update checks in hours"
        ),
        
        # Performance Settings
        SettingDefinition(
            key="performance.max_concurrent_operations",
            name="Max Concurrent Operations",
            description="Maximum number of file operations to run simultaneously",
            type=SettingType.INTEGER,
            default_value=4,
            scope=SettingScope.APPLICATION,
            min_value=1,
            max_value=16,
            category="Performance",
            help_text="Control how many file operations run at once"
        ),
        
        SettingDefinition(
            key="performance.operation_timeout",
            name="Operation Timeout",
            description="Timeout for file operations (seconds)",
            type=SettingType.INTEGER,
            default_value=300,  # 5 minutes
            scope=SettingScope.APPLICATION,
            min_value=30,
            max_value=3600,  # 1 hour
            category="Performance",
            help_text="Maximum time to wait for file operations to complete"
        ),
        
        SettingDefinition(
            key="performance.cache_size",
            name="Cache Size",
            description="Size of internal cache (MB)",
            type=SettingType.INTEGER,
            default_value=100,
            scope=SettingScope.APPLICATION,
            min_value=10,
            max_value=1000,
            category="Performance",
            help_text="Amount of memory to use for caching"
        ),
        
        # Security Settings
        SettingDefinition(
            key="security.require_admin",
            name="Require Administrator",
            description="Require administrator privileges for system operations",
            type=SettingType.BOOLEAN,
            default_value=False,
            scope=SettingScope.APPLICATION,
            category="Security",
            help_text="Enable for enhanced security when modifying system files",
            restart_required=True
        ),
        
        SettingDefinition(
            key="security.backup_before_operations",
            name="Backup Before Operations",
            description="Create backups before potentially destructive operations",
            type=SettingType.BOOLEAN,
            default_value=True,
            scope=SettingScope.APPLICATION,
            category="Security",
            help_text="Automatically backup files before risky operations"
        ),
    ]


def get_logging_setting_definitions() -> List[SettingDefinition]:
    """Get predefined logging setting definitions."""
    return [
        SettingDefinition(
            key="logging.level",
            name="Logging Level",
            description="Minimum level for log messages",
            type=SettingType.ENUM,
            default_value="INFO",
            scope=SettingScope.LOGGING,
            allowed_values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            category="General",
            help_text="Control the verbosity of log messages"
        ),
        
        SettingDefinition(
            key="logging.file_enabled",
            name="File Logging",
            description="Enable logging to file",
            type=SettingType.BOOLEAN,
            default_value=True,
            scope=SettingScope.LOGGING,
            category="Output",
            help_text="Save log messages to a file"
        ),
        
        SettingDefinition(
            key="logging.file_path",
            name="Log File Path",
            description="Path for log files",
            type=SettingType.PATH,
            default_value="logs/taskmover.log",
            scope=SettingScope.LOGGING,
            category="Output",
            dependencies=["logging.file_enabled"],
            help_text="Location where log files are saved"
        ),
        
        SettingDefinition(
            key="logging.file_max_size",
            name="Max Log File Size",
            description="Maximum size for log files (MB)",
            type=SettingType.INTEGER,
            default_value=10,
            scope=SettingScope.LOGGING,
            min_value=1,
            max_value=100,
            category="Rotation",
            dependencies=["logging.file_enabled"],
            help_text="Maximum size before log files are rotated"
        ),
        
        SettingDefinition(
            key="logging.file_backup_count",
            name="Log File Backup Count",
            description="Number of backup log files to keep",
            type=SettingType.INTEGER,
            default_value=5,
            scope=SettingScope.LOGGING,
            min_value=1,
            max_value=20,
            category="Rotation",
            dependencies=["logging.file_enabled"],
            help_text="How many old log files to keep"
        ),
        
        SettingDefinition(
            key="logging.console_enabled",
            name="Console Logging",
            description="Enable logging to console",
            type=SettingType.BOOLEAN,
            default_value=True,
            scope=SettingScope.LOGGING,
            category="Output",
            help_text="Display log messages in the console"
        ),
        
        SettingDefinition(
            key="logging.console_colors",
            name="Console Colors",
            description="Use colors in console output",
            type=SettingType.BOOLEAN,
            default_value=True,
            scope=SettingScope.LOGGING,
            category="Formatting",
            dependencies=["logging.console_enabled"],
            help_text="Enable colored output in console logs"
        ),
        
        SettingDefinition(
            key="logging.format",
            name="Log Format",
            description="Format string for log messages",
            type=SettingType.STRING,
            default_value="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            scope=SettingScope.LOGGING,
            category="Formatting",
            help_text="Python logging format string for log messages"
        ),
        
        SettingDefinition(
            key="logging.date_format",
            name="Date Format",
            description="Format string for timestamps",
            type=SettingType.STRING,
            default_value="%Y-%m-%d %H:%M:%S",
            scope=SettingScope.LOGGING,
            category="Formatting",
            help_text="Format string for timestamps in log messages"
        ),
    ]


def get_rule_setting_definitions() -> List[SettingDefinition]:
    """Get predefined rule system setting definitions."""
    return [
        SettingDefinition(
            key="rules.auto_execute",
            name="Auto Execute Rules",
            description="Automatically execute rules when files are detected",
            type=SettingType.BOOLEAN,
            default_value=True,
            scope=SettingScope.RULE,
            category="Execution",
            help_text="Run rules automatically when matching files are found"
        ),
        
        SettingDefinition(
            key="rules.execution_delay",
            name="Execution Delay",
            description="Delay before executing rules (seconds)",
            type=SettingType.INTEGER,
            default_value=2,
            scope=SettingScope.RULE,
            min_value=0,
            max_value=60,
            category="Execution",
            help_text="Wait time before executing rules to avoid conflicts"
        ),
        
        SettingDefinition(
            key="rules.max_retries",
            name="Max Retries",
            description="Maximum number of retries for failed rule executions",
            type=SettingType.INTEGER,
            default_value=3,
            scope=SettingScope.RULE,
            min_value=0,
            max_value=10,
            category="Error Handling",
            help_text="How many times to retry failed rule executions"
        ),
        
        SettingDefinition(
            key="rules.retry_delay",
            name="Retry Delay",
            description="Delay between retry attempts (seconds)",
            type=SettingType.INTEGER,
            default_value=5,
            scope=SettingScope.RULE,
            min_value=1,
            max_value=300,
            category="Error Handling",
            dependencies=["rules.max_retries"],
            help_text="Time to wait between retry attempts"
        ),
        
        SettingDefinition(
            key="rules.backup_enabled",
            name="Rule Backup",
            description="Create backups of rule configurations",
            type=SettingType.BOOLEAN,
            default_value=True,
            scope=SettingScope.RULE,
            category="Backup",
            help_text="Automatically backup rule configurations"
        ),
        
        SettingDefinition(
            key="rules.backup_frequency",
            name="Backup Frequency",
            description="How often to backup rules (hours)",
            type=SettingType.INTEGER,
            default_value=24,
            scope=SettingScope.RULE,
            min_value=1,
            max_value=168,
            category="Backup",
            dependencies=["rules.backup_enabled"],
            help_text="Frequency of automatic rule backups"
        ),
    ]


def get_ui_setting_definitions() -> List[SettingDefinition]:
    """Get predefined UI setting definitions."""
    return [
        # Window Settings
        SettingDefinition(
            key="window.width",
            name="Window Width",
            description="Main window width in pixels",
            type=SettingType.INTEGER,
            default_value=1200,
            scope=SettingScope.UI,
            min_value=800,
            max_value=3840,
            category="Window",
            help_text="Width of the main application window"
        ),
        
        SettingDefinition(
            key="window.height",
            name="Window Height",
            description="Main window height in pixels",
            type=SettingType.INTEGER,
            default_value=800,
            scope=SettingScope.UI,
            min_value=600,
            max_value=2160,
            category="Window",
            help_text="Height of the main application window"
        ),
        
        SettingDefinition(
            key="window.maximized",
            name="Start Maximized",
            description="Start with maximized window",
            type=SettingType.BOOLEAN,
            default_value=False,
            scope=SettingScope.UI,
            category="Window",
            help_text="Open the application window maximized"
        ),
        
        SettingDefinition(
            key="window.remember_position",
            name="Remember Position",
            description="Remember window position between sessions",
            type=SettingType.BOOLEAN,
            default_value=True,
            scope=SettingScope.UI,
            category="Window",
            help_text="Restore window position from previous session"
        ),
        
        # Panel Settings
        SettingDefinition(
            key="panels.sidebar_visible",
            name="Show Sidebar",
            description="Show the sidebar panel",
            type=SettingType.BOOLEAN,
            default_value=True,
            scope=SettingScope.UI,
            category="Panels",
            help_text="Display the sidebar with navigation and tools"
        ),
        
        SettingDefinition(
            key="panels.sidebar_width",
            name="Sidebar Width",
            description="Width of the sidebar panel in pixels",
            type=SettingType.INTEGER,
            default_value=250,
            scope=SettingScope.UI,
            min_value=150,
            max_value=500,
            category="Panels",
            dependencies=["panels.sidebar_visible"],
            help_text="Width of the sidebar panel"
        ),
        
        SettingDefinition(
            key="panels.log_visible",
            name="Show Log Panel",
            description="Show the log panel",
            type=SettingType.BOOLEAN,
            default_value=False,
            scope=SettingScope.UI,
            category="Panels",
            help_text="Display the log panel for debugging"
        ),
        
        SettingDefinition(
            key="panels.log_height",
            name="Log Panel Height",
            description="Height of the log panel in pixels",
            type=SettingType.INTEGER,
            default_value=200,
            scope=SettingScope.UI,
            min_value=100,
            max_value=400,
            category="Panels",
            dependencies=["panels.log_visible"],
            help_text="Height of the log panel"
        ),
        
        # View Settings
        SettingDefinition(
            key="views.default_view",
            name="Default View",
            description="Default view mode for file lists",
            type=SettingType.ENUM,
            default_value="details",
            scope=SettingScope.UI,
            allowed_values=["list", "details", "icons", "tiles"],
            category="Views",
            help_text="Default display mode for file and folder lists"
        ),
        
        SettingDefinition(
            key="views.show_hidden_files",
            name="Show Hidden Files",
            description="Display hidden files and folders",
            type=SettingType.BOOLEAN,
            default_value=False,
            scope=SettingScope.UI,
            category="Views",
            help_text="Include hidden files and folders in lists"
        ),
        
        SettingDefinition(
            key="views.icon_size",
            name="Icon Size",
            description="Size of icons in pixels",
            type=SettingType.INTEGER,
            default_value=16,
            scope=SettingScope.UI,
            min_value=12,
            max_value=48,
            category="Views",
            help_text="Size of icons in file and folder lists"
        ),
    ]


def get_all_setting_definitions() -> List[SettingDefinition]:
    """Get all predefined setting definitions."""
    definitions = []
    definitions.extend(get_user_setting_definitions())
    definitions.extend(get_application_setting_definitions())
    definitions.extend(get_logging_setting_definitions())
    definitions.extend(get_rule_setting_definitions())
    definitions.extend(get_ui_setting_definitions())
    return definitions


def register_all_definitions(manager) -> None:
    """Register all predefined setting definitions with a setting manager."""
    logger = logging.getLogger(f"{__name__}.register_all_definitions")
    
    definitions = get_all_setting_definitions()
    
    for definition in definitions:
        manager.register_definition(definition)
    
    logger.info(f"Registered {len(definitions)} setting definitions")


__all__ = [
    "get_user_setting_definitions",
    "get_application_setting_definitions", 
    "get_logging_setting_definitions",
    "get_rule_setting_definitions",
    "get_ui_setting_definitions",
    "get_all_setting_definitions",
    "register_all_definitions",
]

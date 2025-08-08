"""
Main Application
===============

TaskMover main application window integrating all UI components
with modern design, theme support, and comprehensive functionality.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional, Any
import logging
import sys
from pathlib import Path

from .base_component import BaseComponent, StatusBar
from .theme_manager import get_theme_manager, ThemeMode
from .navigation_components import ModernSidebar, ModernToolbar
from .pattern_management_components import PatternLibrary
from .input_components import SmartPatternInput
from .rule_management_components import RuleManagementView
from .execution_components import ExecutionView
from .history_components import HistoryAndStatsView
from .programming_courses_component import ProgrammingCoursesComponent

# Import backend services
from ..core.patterns import PatternSystem
from ..core.rules.service import RuleService
from ..core.conflict_resolution import ConflictManager

logger = logging.getLogger(__name__)


class MainContentArea(BaseComponent):
    """Main content area with tab-based navigation."""
    
    def __init__(self, parent: tk.Widget, rule_service=None, pattern_service=None, **kwargs):
        self.current_view = "dashboard"
        self.views: Dict[str, tk.Widget] = {}
        self.rule_service = rule_service
        self.pattern_service = pattern_service
        
        super().__init__(parent, **kwargs)
    
    def _create_component(self):
        """Create main content area."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Configure main area
        self.configure(bg=tokens.colors["background"])
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self, style="Modern.TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=tokens.spacing["md"], pady=tokens.spacing["md"])
        
        # Create default views
        self._create_dashboard_view()
        self._create_patterns_view()
        self._create_rules_view()
        self._create_rulesets_view()
        self._create_execute_view()
        self._create_history_view()
        self._create_courses_view()
        self._create_settings_view()
    
    def _create_dashboard_view(self):
        """Create dashboard view."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Dashboard frame
        dashboard_frame = tk.Frame(self.notebook, bg=tokens.colors["background"])
        self.notebook.add(dashboard_frame, text="Dashboard")
        self.views["dashboard"] = dashboard_frame
        
        # Welcome section
        welcome_label = tk.Label(
            dashboard_frame,
            text="Welcome to TaskMover",
            font=(tokens.fonts["family"], int(tokens.fonts["size_display"]), tokens.fonts["weight_bold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        )
        welcome_label.pack(pady=(tokens.spacing["xl"], tokens.spacing["md"]))
        
        subtitle_label = tk.Label(
            dashboard_frame,
            text="Intelligent file organization system with pattern-based rules",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body_large"]), tokens.fonts["weight_normal"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text_secondary"]
        )
        subtitle_label.pack(pady=(0, tokens.spacing["xl"]))
        
        # Quick stats cards
        stats_frame = tk.Frame(dashboard_frame, bg=tokens.colors["background"])
        stats_frame.pack(fill="x", padx=tokens.spacing["xl"], pady=tokens.spacing["lg"])
        
        # Stats data (placeholder)
        stats = [
            ("📋", "Patterns", "6", "3 system, 3 custom"),
            ("📏", "Rules", "8", "5 active, 3 inactive"),
            ("📦", "Rulesets", "3", "2 active templates"),
            ("📊", "Files Organized", "1,247", "This month")
        ]
        
        for icon, title, value, subtitle in stats:
            self._create_stat_card(stats_frame, icon, title, value, subtitle)
        
        # Recent activity
        activity_frame = tk.LabelFrame(
            dashboard_frame,
            text="Recent Activity",
            font=(tokens.fonts["family"], int(tokens.fonts["size_heading_2"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"],
            relief="solid",
            bd=1
        )
        activity_frame.pack(fill="both", expand=True, padx=tokens.spacing["xl"], pady=tokens.spacing["lg"])
        
        # Activity items (placeholder)
        activities = [
            ("🕐", "2 minutes ago", "25 files moved to Documents"),
            ("🕐", "5 minutes ago", "12 images organized to Pictures"), 
            ("🕐", "10 minutes ago", "3 conflicts resolved manually"),
            ("🕐", "1 hour ago", "Ruleset 'Media Files' executed"),
        ]
        
        for icon, time, description in activities:
            activity_item = tk.Frame(activity_frame, bg=tokens.colors["background"])
            activity_item.pack(fill="x", padx=tokens.spacing["md"], pady=tokens.spacing["xs"])
            
            time_label = tk.Label(
                activity_item,
                text=f"{icon} {time}:",
                font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), tokens.fonts["weight_normal"]),
                bg=tokens.colors["background"],
                fg=tokens.colors["text_secondary"],
                width=20,
                anchor="w"
            )
            time_label.pack(side="left")
            
            desc_label = tk.Label(
                activity_item,
                text=description,
                font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), tokens.fonts["weight_normal"]),
                bg=tokens.colors["background"],
                fg=tokens.colors["text"],
                anchor="w"
            )
            desc_label.pack(side="left", fill="x", expand=True, padx=(tokens.spacing["sm"], 0))
    
    def _create_stat_card(self, parent: tk.Widget, icon: str, title: str, value: str, subtitle: str):
        """Create statistics card."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        card = tk.Frame(
            parent,
            bg="white",
            relief="solid",
            bd=1,
            width=200,
            height=100
        )
        card.pack(side="left", fill="both", expand=True, padx=tokens.spacing["sm"], pady=tokens.spacing["sm"])
        card.pack_propagate(False)
        
        # Icon
        icon_label = tk.Label(
            card,
            text=icon,
            font=(tokens.fonts["family"], int(tokens.fonts["size_heading_1"]), tokens.fonts["weight_normal"]),
            bg="white",
            fg=tokens.colors["primary"]
        )
        icon_label.pack(pady=(tokens.spacing["sm"], 0))
        
        # Title and value
        title_label = tk.Label(
            card,
            text=title,
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), tokens.fonts["weight_normal"]),
            bg="white",
            fg=tokens.colors["text_secondary"]
        )
        title_label.pack()
        
        value_label = tk.Label(
            card,
            text=value,
            font=(tokens.fonts["family"], int(tokens.fonts["size_heading_2"]), tokens.fonts["weight_bold"]),
            bg="white",
            fg=tokens.colors["text"]
        )
        value_label.pack()
        
        subtitle_label = tk.Label(
            card,
            text=subtitle,
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), tokens.fonts["weight_normal"]),
            bg="white",
            fg=tokens.colors["text_secondary"]
        )
        subtitle_label.pack(pady=(0, tokens.spacing["sm"]))
    
    def _create_patterns_view(self):
        """Create patterns management view."""
        patterns_frame = tk.Frame(self.notebook, bg=get_theme_manager().get_current_tokens().colors["background"])
        self.notebook.add(patterns_frame, text="Patterns")
        self.views["patterns"] = patterns_frame
        
        # Pattern library
        pattern_library = PatternLibrary(patterns_frame)
        pattern_library.pack(fill="both", expand=True)
    
    def _create_rules_view(self):
        """Create rules management view."""
        rules_frame = tk.Frame(self.notebook, bg=get_theme_manager().get_current_tokens().colors["background"])
        self.notebook.add(rules_frame, text="Rules")
        self.views["rules"] = rules_frame
        
        # Rule management component
        if self.rule_service and self.pattern_service:
            rule_management = RuleManagementView(
                rules_frame, 
                rule_service=self.rule_service,
                pattern_service=self.pattern_service
            )
            rule_management.pack(fill="both", expand=True)
        else:
            # Fallback if services not available
            placeholder_label = tk.Label(
                rules_frame,
                text="Rule Management\n(Services not available)",
                font=(get_theme_manager().get_current_tokens().fonts["family"], 16),
                bg=get_theme_manager().get_current_tokens().colors["background"],
                fg=get_theme_manager().get_current_tokens().colors["text_secondary"]
            )
            placeholder_label.pack(expand=True)
    
    def _create_rulesets_view(self):
        """Create rulesets management view."""
        rulesets_frame = tk.Frame(self.notebook, bg=get_theme_manager().get_current_tokens().colors["background"])
        self.notebook.add(rulesets_frame, text="Rulesets")
        self.views["rulesets"] = rulesets_frame
        
        # Placeholder for rulesets management
        placeholder_label = tk.Label(
            rulesets_frame,
            text="Rulesets Management\n(Implementation in progress)",
            font=("Arial", 16),
            bg=get_theme_manager().get_current_tokens().colors["background"],
            fg=get_theme_manager().get_current_tokens().colors["text_secondary"]
        )
        placeholder_label.pack(expand=True)
    
    def _create_execute_view(self):
        """Create execution view."""
        execute_frame = tk.Frame(self.notebook, bg=get_theme_manager().get_current_tokens().colors["background"])
        self.notebook.add(execute_frame, text="Execute")
        self.views["execute"] = execute_frame
        
        # Execution component
        execution_view = ExecutionView(execute_frame)
        execution_view.pack(fill="both", expand=True)
    
    def _create_history_view(self):
        """Create history view."""
        history_frame = tk.Frame(self.notebook, bg=get_theme_manager().get_current_tokens().colors["background"])
        self.notebook.add(history_frame, text="History")
        self.views["history"] = history_frame
        
        # History and statistics component
        history_stats = HistoryAndStatsView(history_frame)
        history_stats.pack(fill="both", expand=True)
    
    def _create_courses_view(self):
        """Create programming courses view."""
        courses_frame = tk.Frame(self.notebook, bg=get_theme_manager().get_current_tokens().colors["background"])
        self.notebook.add(courses_frame, text="📚 Courses")
        self.views["courses"] = courses_frame
        
        # Programming courses component
        courses_component = ProgrammingCoursesComponent(courses_frame)
        courses_component.pack(fill="both", expand=True)
    
    def _create_settings_view(self):
        """Create settings view."""
        settings_frame = tk.Frame(self.notebook, bg=get_theme_manager().get_current_tokens().colors["background"])
        self.notebook.add(settings_frame, text="Settings")
        self.views["settings"] = settings_frame
        
        # Theme toggle
        theme_frame = tk.LabelFrame(
            settings_frame,
            text="Appearance",
            font=("Arial", 12, "bold"),
            bg=get_theme_manager().get_current_tokens().colors["background"],
            fg=get_theme_manager().get_current_tokens().colors["text"]
        )
        theme_frame.pack(fill="x", padx=20, pady=20)
        
        theme_button = tk.Button(
            theme_frame,
            text="Toggle Dark/Light Theme",
            font=("Arial", 11),
            command=self._toggle_theme,
            cursor="hand2"
        )
        theme_button.pack(padx=20, pady=10)
        
        # Placeholder for other settings
        placeholder_label = tk.Label(
            settings_frame,
            text="Additional Settings\n(Implementation in progress)",
            font=("Arial", 16),
            bg=get_theme_manager().get_current_tokens().colors["background"],
            fg=get_theme_manager().get_current_tokens().colors["text_secondary"]
        )
        placeholder_label.pack(expand=True, pady=50)
    
    def _toggle_theme(self):
        """Toggle between light and dark themes."""
        theme_manager = get_theme_manager()
        theme_manager.toggle_theme()
        logger.info(f"Theme toggled to {theme_manager.current_mode.value}")
    
    def show_view(self, view_name: str):
        """Show specific view."""
        if view_name in self.views:
            # Find the tab index
            for i in range(self.notebook.index("end")):
                tab_text = self.notebook.tab(i, "text")
                if tab_text.lower() == view_name.lower():
                    self.notebook.select(i)
                    self.current_view = view_name
                    break
            
            logger.debug(f"Switched to view: {view_name}")


class TaskMoverApplication:
    """
    Main TaskMover application integrating all components with
    modern design, theme support, and comprehensive functionality.
    """
    
    def __init__(self):
        self.root: Optional[tk.Tk] = None
        self.sidebar: Optional[ModernSidebar] = None
        self.toolbar: Optional[ModernToolbar] = None
        self.content_area: Optional[MainContentArea] = None
        self.status_bar: Optional[StatusBar] = None
        
        # Services
        self.rule_service = None
        self.pattern_service = None
        
        # Setup logging
        self._setup_logging()
        
        logger.info("TaskMover application initialized")
    
    def _setup_logging(self):
        """Setup application logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('logs/taskmover.log', mode='a') if Path('logs').exists() else logging.StreamHandler()
            ]
        )
    
    def run(self):
        """Run the application."""
        try:
            self._create_main_window()
            self._setup_theme()
            self._initialize_services()
            self._create_components()
            self._setup_event_handlers()
            self._finalize_setup()
            
            logger.info("Starting TaskMover application")
            self.root.mainloop()
            
        except Exception as e:
            logger.error(f"Error running application: {e}")
            raise
    
    def _initialize_services(self):
        """Initialize backend services."""
        try:
            # Setup paths
            storage_path = Path.cwd() / "data"
            storage_path.mkdir(exist_ok=True)
            
            # Initialize PatternSystem
            self.pattern_service = PatternSystem(storage_path / "patterns")
            
            # Initialize ConflictManager 
            conflict_manager = ConflictManager()
            
            # Initialize RuleService
            self.rule_service = RuleService(
                pattern_system=self.pattern_service,
                conflict_manager=conflict_manager,
                storage_path=storage_path / "rules"
            )
            
            logger.info("Backend services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            # Create mock services for UI testing
            self.pattern_service = None
            self.rule_service = None
    
    def _create_main_window(self):
        """Create main application window."""
        self.root = tk.Tk()
        self.root.title("TaskMover - Intelligent File Organization")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Set window icon (if available)
        try:
            # self.root.iconbitmap("assets/icon.ico")  # Uncomment when icon is available
            pass
        except:
            pass
        
        # Configure root styling
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        self.root.configure(bg=tokens.colors["background"])
    
    def _setup_theme(self):
        """Setup application theme."""
        theme_manager = get_theme_manager()
        if self.root:
            theme_manager.initialize_ttk_styles(self.root)
        
        # Add theme change observer
        theme_manager.add_theme_observer(self._on_theme_changed)
        
        logger.info(f"Theme initialized: {theme_manager.current_mode.value}")
    
    def _create_components(self):
        """Create all UI components."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Create main container
        main_container = tk.Frame(self.root, bg=tokens.colors["background"])
        main_container.pack(fill="both", expand=True)
        
        # Toolbar
        self.toolbar = ModernToolbar(main_container)
        self.toolbar.pack(fill="x", side="top")
        
        # Content container (sidebar + main area)
        content_container = tk.Frame(main_container, bg=tokens.colors["background"])
        content_container.pack(fill="both", expand=True)
        
        # Sidebar
        self.sidebar = ModernSidebar(content_container, width=250, min_width=50)
        self.sidebar.pack(side="left", fill="y")
        
        # Main content area
        self.content_area = MainContentArea(
            content_container,
            rule_service=self.rule_service,
            pattern_service=self.pattern_service
        )
        self.content_area.pack(side="right", fill="both", expand=True)
        
        # Status bar
        self.status_bar = StatusBar(main_container)
        self.status_bar.pack(fill="x", side="bottom")
        
        # Initialize status
        self._update_status()
        
        logger.info("UI components created successfully")
    
    def _setup_event_handlers(self):
        """Setup event handlers for components."""
        # Sidebar navigation
        if self.sidebar:
            self.sidebar.add_callback('item_selected', self._on_navigation_item_selected)
            self.sidebar.add_callback('collapsed', self._on_sidebar_collapsed)
            self.sidebar.add_callback('expanded', self._on_sidebar_expanded)
        
        # Toolbar actions
        if self.toolbar:
            self.toolbar.add_callback('button_clicked', self._on_toolbar_button_clicked)
        
        # Window events
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_closing)
        self.root.bind("<Control-q>", lambda e: self._on_window_closing())
        self.root.bind("<F11>", self._toggle_fullscreen)
        
        # Theme toggle shortcut
        self.root.bind("<Control-t>", lambda e: self._toggle_theme())
    
    def _finalize_setup(self):
        """Finalize application setup."""
        # Set initial focus
        if self.content_area:
            self.content_area.focus_set()
        
        # Center window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        logger.info("Application setup completed")
    
    def _on_navigation_item_selected(self, data: Dict[str, Any]):
        """Handle sidebar navigation selection."""
        item_id = data['item_id']
        
        # Map navigation items to views
        view_mapping = {
            'dashboard': 'dashboard',
            'patterns': 'patterns',
            'patterns_library': 'patterns',
            'patterns_groups': 'patterns',
            'patterns_new': 'patterns',
            'rules': 'rules',
            'rules_active': 'rules',
            'rules_disabled': 'rules',
            'rules_new': 'rules',
            'rulesets': 'rulesets',
            'rulesets_recent': 'rulesets',
            'rulesets_templates': 'rulesets',
            'rulesets_new': 'rulesets',
            'execute': 'execute',
            'history': 'history',
            'statistics': 'history',
            'logs': 'history',
            'settings': 'settings',
            'help': 'settings'
        }
        
        view_name = view_mapping.get(item_id, 'dashboard')
        if self.content_area:
            self.content_area.show_view(view_name)
        
        # Update status
        self._update_status(f"Viewing: {item_id.replace('_', ' ').title()}")
        
        logger.debug(f"Navigation item selected: {item_id} -> {view_name}")
    
    def _on_toolbar_button_clicked(self, data: Dict[str, Any]):
        """Handle toolbar button clicks."""
        button_id = data['button_id']
        
        # Handle common toolbar actions
        if button_id == 'home':
            if self.sidebar:
                self.sidebar.select_item('dashboard')
        elif button_id == 'settings':
            if self.sidebar:
                self.sidebar.select_item('settings')
        elif button_id == 'help':
            self._show_help()
        elif button_id == 'new':
            self._create_new_item()
        
        logger.debug(f"Toolbar button clicked: {button_id}")
    
    def _on_sidebar_collapsed(self, data: Any):
        """Handle sidebar collapse."""
        self._update_status("Sidebar collapsed")
    
    def _on_sidebar_expanded(self, data: Any):
        """Handle sidebar expansion."""
        self._update_status("Sidebar expanded")
    
    def _on_theme_changed(self, old_mode: ThemeMode, new_mode: ThemeMode):
        """Handle theme changes."""
        # Update root window background
        tokens = get_theme_manager().get_current_tokens()
        self.root.configure(bg=tokens.colors["background"])
        
        self._update_status(f"Theme changed to {new_mode.value}")
        logger.info(f"Theme changed from {old_mode.value} to {new_mode.value}")
    
    def _update_status(self, message: str = ""):
        """Update status bar."""
        if self.status_bar:
            if message:
                self.status_bar.set_status("message", message)
            
            # Update standard status items
            self.status_bar.set_status("ready", "Ready")
            self.status_bar.set_status("patterns", "6 patterns")
            self.status_bar.set_status("rules", "8 rules") 
            self.status_bar.set_status("rulesets", "3 rulesets")
            self.status_bar.set_status("last_run", "Last run: Never", "right")
    
    def _toggle_theme(self):
        """Toggle application theme."""
        get_theme_manager().toggle_theme()
    
    def _toggle_fullscreen(self, event):
        """Toggle fullscreen mode."""
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)
    
    def _show_help(self):
        """Show help dialog."""
        help_window = tk.Toplevel(self.root)
        help_window.title("TaskMover Help")
        help_window.geometry("600x400")
        help_window.transient(self.root)
        help_window.grab_set()
        
        help_text = """TaskMover - Intelligent File Organization System

OVERVIEW:
TaskMover helps you organize files automatically using pattern-based rules.

KEY FEATURES:
• Pattern Library: Create and manage file patterns
• Rules Management: Define organization rules
• Rulesets: Group rules for different scenarios
• Live Preview: See what files match your patterns
• Conflict Resolution: Handle file conflicts intelligently

KEYBOARD SHORTCUTS:
• Ctrl+T: Toggle theme
• Ctrl+Q: Quit application
• F11: Toggle fullscreen

GETTING STARTED:
1. Create patterns in the Pattern Library
2. Define rules using those patterns
3. Group rules into rulesets
4. Execute organization operations

For more information, visit the TaskMover documentation."""
        
        text_widget = tk.Text(
            help_window,
            wrap="word",
            padx=20,
            pady=20,
            font=("Arial", 11),
            bg="white",
            fg="black"
        )
        text_widget.insert("1.0", help_text)
        text_widget.configure(state="disabled")
        text_widget.pack(fill="both", expand=True)
        
        # Close button
        close_btn = tk.Button(
            help_window,
            text="Close",
            command=help_window.destroy,
            font=("Arial", 11),
            cursor="hand2"
        )
        close_btn.pack(pady=10)
    
    def _create_new_item(self):
        """Create new item based on current view."""
        if self.content_area and self.content_area.current_view == "patterns":
            # Create new pattern
            logger.debug("Creating new pattern")
        else:
            # Default to new pattern
            if self.sidebar:
                self.sidebar.select_item('patterns_new')
    
    def _on_window_closing(self):
        """Handle window closing."""
        logger.info("Application shutting down")
        
        # Save any pending state
        try:
            # Add state saving logic here
            pass
        except Exception as e:
            logger.error(f"Error saving state: {e}")
        
        # Destroy window
        self.root.quit()
        self.root.destroy()


def main():
    """Main entry point."""
    try:
        app = TaskMoverApplication()
        app.run()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        raise


if __name__ == "__main__":
    main()


# Export main class
__all__ = ["TaskMoverApplication", "main"]

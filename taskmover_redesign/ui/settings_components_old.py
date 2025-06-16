"""
Settings UI components for TaskMover Redesigned.
Clean, organized settings interface with better UX.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as ttkb
from typing import Dict, Any, Optional, Callable
import logging

from .components import Tooltip, create_labeled_frame
from ..core.config import ConfigManager

logger = logging.getLogger("TaskMover.UI.Settings")


class SettingsDialog:
    """Modern settings dialog with tabbed interface."""
    
    def __init__(self, parent: tk.Widget, config_manager: ConfigManager):
        self.parent = parent
        self.config_manager = config_manager
        self.settings = config_manager.load_settings()
        self.result = False
        
        # Create dialog
        self.dialog = ttkb.Toplevel(parent)
        self.dialog.title("Settings")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        from ..core.utils import center_window
        center_window(self.dialog, 600, 500)
        
        self._create_widgets()
        self._load_settings()
    
    def _create_widgets(self):
        """Create the dialog widgets."""
        main_frame = ttkb.Frame(self.dialog, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Create notebook for tabs
        self.notebook = ttkb.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True, pady=(0, 15))
        
        # Create tabs
        self._create_general_tab()
        self._create_ui_tab()
        self._create_organization_tab()
        self._create_logging_tab()
        
        # Buttons
        button_frame = ttkb.Frame(main_frame)
        button_frame.pack(fill="x")
        
        # Reset to defaults button
        reset_btn = ttkb.Button(button_frame, text="Reset to Defaults", 
                               command=self._reset_to_defaults,
                               style="warning.TButton")
        reset_btn.pack(side="left")
        
        # Cancel and Save buttons
        cancel_btn = ttkb.Button(button_frame, text="Cancel", command=self._on_cancel)
        cancel_btn.pack(side="right", padx=(10, 0))
        
        save_btn = ttkb.Button(button_frame, text="Save", command=self._on_save,
                              style="success.TButton")
        save_btn.pack(side="right")
        
        # Bind keys
        self.dialog.bind('<Return>', lambda e: self._on_save())
        self.dialog.bind('<Escape>', lambda e: self._on_cancel())
    
    def _create_general_tab(self):
        """Create the general settings tab."""
        general_frame = ttkb.Frame(self.notebook, padding=15)
        self.notebook.add(general_frame, text="General")
        
        # Organization folder
        folder_frame, folder_content = create_labeled_frame(general_frame, "File Organization")
        folder_frame.pack(fill="x", pady=(0, 15))
        
        ttkb.Label(folder_content, text="Organization Folder:", font=("Arial", 10, "bold")).pack(anchor="w")
        ttkb.Label(folder_content, text="Folder where TaskMover will look for files to organize",
                  font=("Arial", 9), foreground="gray").pack(anchor="w", pady=(0, 5))
        
        folder_entry_frame = ttkb.Frame(folder_content)
        folder_entry_frame.pack(fill="x")
        
        self.org_folder_var = tk.StringVar()
        folder_entry = ttkb.Entry(folder_entry_frame, textvariable=self.org_folder_var, font=("Arial", 10))
        folder_entry.pack(side="left", fill="x", expand=True)
        
        browse_btn = ttkb.Button(folder_entry_frame, text="Browse...", 
                                command=self._browse_org_folder)
        browse_btn.pack(side="right", padx=(10, 0))
        
        Tooltip(folder_entry, "The folder that TaskMover will organize")
        Tooltip(browse_btn, "Browse for organization folder")
        
        # Auto-save
        auto_save_frame, auto_save_content = create_labeled_frame(general_frame, "Auto-Save")
        auto_save_frame.pack(fill="x", pady=(0, 15))
        
        self.auto_save_var = tk.BooleanVar()
        auto_save_cb = ttkb.Checkbutton(auto_save_content, text="Automatically save changes", 
                                       variable=self.auto_save_var)
        auto_save_cb.pack(anchor="w")
        Tooltip(auto_save_cb, "Save changes automatically without prompting")
        
        # Confirmations
        confirm_frame, confirm_content = create_labeled_frame(general_frame, "Confirmations")
        confirm_frame.pack(fill="x")
        
        self.confirm_deletions_var = tk.BooleanVar()
        confirm_del_cb = ttkb.Checkbutton(confirm_content, text="Confirm rule deletions", 
                                         variable=self.confirm_deletions_var)
        confirm_del_cb.pack(anchor="w")
        Tooltip(confirm_del_cb, "Ask for confirmation before deleting rules")
    
    def _create_ui_tab(self):
        """Create the UI settings tab."""
        ui_frame = ttkb.Frame(self.notebook, padding=15)
        self.notebook.add(ui_frame, text="Interface")
        
        # Theme
        theme_frame, theme_content = create_labeled_frame(ui_frame, "Appearance")
        theme_frame.pack(fill="x", pady=(0, 15))
        
        ttkb.Label(theme_content, text="Theme:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        self.theme_var = tk.StringVar()
        theme_combo = ttkb.Combobox(theme_content, textvariable=self.theme_var, 
                                   values=self._get_available_themes(), state="readonly")
        theme_combo.pack(fill="x", pady=(5, 0))
        Tooltip(theme_combo, "Select the visual theme for the application")
        
        # Rule display
        rules_frame, rules_content = create_labeled_frame(ui_frame, "Rule Display")
        rules_frame.pack(fill="x")
        
        self.collapse_on_start_var = tk.BooleanVar()
        collapse_cb = ttkb.Checkbutton(rules_content, text="Collapse rules on startup", 
                                      variable=self.collapse_on_start_var)
        collapse_cb.pack(anchor="w", pady=2)
        Tooltip(collapse_cb, "Start with all rules collapsed in the list")
    
    def _create_organization_tab(self):
        """Create the organization settings tab."""
        org_frame = ttkb.Frame(self.notebook, padding=15)
        self.notebook.add(org_frame, text="Organization")
        
        # File handling
        file_frame, file_content = create_labeled_frame(org_frame, "File Handling")
        file_frame.pack(fill="x", pady=(0, 15))
        
        self.skip_hidden_var = tk.BooleanVar()
        hidden_cb = ttkb.Checkbutton(file_content, text="Skip hidden files", 
                                    variable=self.skip_hidden_var)
        hidden_cb.pack(anchor="w", pady=2)
        Tooltip(hidden_cb, "Ignore files that start with a dot (hidden files)")
        
        self.create_folders_var = tk.BooleanVar()
        folders_cb = ttkb.Checkbutton(file_content, text="Create destination folders if needed", 
                                     variable=self.create_folders_var)
        folders_cb.pack(anchor="w", pady=2)
        Tooltip(folders_cb, "Automatically create destination folders if they don't exist")
        
        # Conflict resolution
        conflict_frame, conflict_content = create_labeled_frame(org_frame, "File Conflicts")
        conflict_frame.pack(fill="x")
        
        ttkb.Label(conflict_content, text="When a file already exists at the destination:",
                  font=("Arial", 10, "bold")).pack(anchor="w")
        
        self.conflict_action_var = tk.StringVar(value="rename")
        
        rename_rb = ttkb.Radiobutton(conflict_content, text="Rename the new file", 
                                    variable=self.conflict_action_var, value="rename")
        rename_rb.pack(anchor="w", pady=2)
        
        skip_rb = ttkb.Radiobutton(conflict_content, text="Skip the file", 
                                  variable=self.conflict_action_var, value="skip")
        skip_rb.pack(anchor="w", pady=2)
        
        overwrite_rb = ttkb.Radiobutton(conflict_content, text="Overwrite the existing file", 
                                       variable=self.conflict_action_var, value="overwrite")
        overwrite_rb.pack(anchor="w", pady=2)
    
    def _create_logging_tab(self):
        """Create the logging settings tab."""
        log_frame = ttkb.Frame(self.notebook, padding=15)
        self.notebook.add(log_frame, text="Logging")
        
        # Log level
        level_frame, level_content = create_labeled_frame(log_frame, "Log Level")
        level_frame.pack(fill="x", pady=(0, 15))
        
        ttkb.Label(level_content, text="Logging Level:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        self.log_level_var = tk.StringVar()
        level_combo = ttkb.Combobox(level_content, textvariable=self.log_level_var,
                                   values=["DEBUG", "INFO", "WARNING", "ERROR"], state="readonly")
        level_combo.pack(fill="x", pady=(5, 0))
        Tooltip(level_combo, "Set the minimum level of messages to log")
        
        # Component logging
        components_frame, components_content = create_labeled_frame(log_frame, "Component Logging")
        components_frame.pack(fill="x")
        
        ttkb.Label(components_content, text="Enable logging for:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        self.logging_vars = {}
        components = ["UI", "File Operations", "Rules", "Settings"]
        
        for component in components:
            var = tk.BooleanVar()
            cb = ttkb.Checkbutton(components_content, text=component, variable=var)
            cb.pack(anchor="w", pady=2)
            self.logging_vars[component] = var
    
    def _get_available_themes(self) -> list[str]:
        """Get list of available ttkbootstrap themes."""
        return [
            "cosmo", "flatly", "journal", "litera", "lumen", "minty", "pulse", 
            "sandstone", "united", "yeti", "morph", "simplex", "cerculean",
            "cyborg", "darkly", "slate", "solar", "superhero", "vapor"
        ]
    
    def _browse_org_folder(self):
        """Browse for organization folder."""
        folder = filedialog.askdirectory(
            title="Select Organization Folder",
            initialdir=self.org_folder_var.get() or "/"
        )
        if folder:
            self.org_folder_var.set(folder)
    
    def _load_settings(self):
        """Load current settings into the UI."""
        self.org_folder_var.set(self.settings.get("organisation_folder", ""))
        self.theme_var.set(self.settings.get("theme", "flatly"))
        self.auto_save_var.set(self.settings.get("auto_save", True))
        self.confirm_deletions_var.set(self.settings.get("confirm_deletions", True))
        self.collapse_on_start_var.set(self.settings.get("collapse_on_start", True))
        self.skip_hidden_var.set(self.settings.get("skip_hidden_files", True))
        self.create_folders_var.set(self.settings.get("create_folders", True))
        self.conflict_action_var.set(self.settings.get("conflict_action", "rename"))
        self.log_level_var.set(self.settings.get("logging_level", "INFO"))
        
        # Load logging components
        logging_components = self.settings.get("logging_components", {})
        for component, var in self.logging_vars.items():
            var.set(logging_components.get(component, True))
    
    def _save_settings(self):
        """Save settings from the UI."""
        self.settings["organisation_folder"] = self.org_folder_var.get()
        self.settings["theme"] = self.theme_var.get()
        self.settings["auto_save"] = self.auto_save_var.get()
        self.settings["confirm_deletions"] = self.confirm_deletions_var.get()
        self.settings["collapse_on_start"] = self.collapse_on_start_var.get()
        self.settings["skip_hidden_files"] = self.skip_hidden_var.get()
        self.settings["create_folders"] = self.create_folders_var.get()
        self.settings["conflict_action"] = self.conflict_action_var.get()
        self.settings["logging_level"] = self.log_level_var.get()
        
        # Save logging components
        logging_components = {}
        for component, var in self.logging_vars.items():
            logging_components[component] = var.get()
        self.settings["logging_components"] = logging_components
        
        return self.config_manager.save_settings(self.settings)
    
    def _reset_to_defaults(self):
        """Reset all settings to defaults."""
        from .components import ConfirmDialog
        
        dialog = ConfirmDialog(
            self.dialog,
            "Reset Settings",
            "Are you sure you want to reset all settings to their default values?",
            "Reset", "Cancel"
        )
        
        if dialog.show():
            # Create fresh default settings
            default_config = ConfigManager()
            self.settings = default_config.load_settings()
            self._load_settings()
    
    def _on_save(self):
        """Handle save button."""
        try:
            success = self._save_settings()
            if success:
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to save settings", parent=self.dialog)
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}", parent=self.dialog)
    
    def _on_cancel(self):
        """Handle cancel button."""
        self.result = False
        self.dialog.destroy()
    
    def show(self) -> bool:
        """Show dialog and return result."""
        self.dialog.wait_window()
        return self.result


# Backward compatibility function
def open_settings_window(root: tk.Tk, settings: Dict[str, Any], 
                        save_settings: Callable, logger) -> None:
    """Legacy function for backward compatibility."""
    # Create a temporary config manager using the existing settings
    config_manager = ConfigManager()
    config_manager.settings_file = config_manager.config_dir / "settings.yml"
    
    # Save current settings to ensure the config manager has them
    config_manager.save_settings(settings)
    
    dialog = SettingsDialog(root, config_manager)
    result = dialog.show()
    
    if result:
        # Update the passed settings dict with new values
        new_settings = config_manager.load_settings()
        settings.clear()
        settings.update(new_settings)
        
        # Call the legacy save function
        import os
        settings_path = os.path.expanduser("~/default_dir/config/settings.yml")
        save_settings(settings_path, settings, logger)

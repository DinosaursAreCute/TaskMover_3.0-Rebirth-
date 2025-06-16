"""
Modern settings components for TaskMover Redesigned.
Clean, independent settings dialog without legacy dependencies.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import ttkbootstrap as ttkb
from typing import Dict, Any, Optional, Callable
import os

from .components import SimpleDialog, Tooltip


class SettingsDialog(SimpleDialog):
    """Modern settings dialog."""
    
    def __init__(self, parent: tk.Widget, settings: Dict[str, Any], 
                 save_callback: Callable, logger):
        self.settings = settings.copy()  # Work with a copy
        self.save_callback = save_callback
        self.logger = logger
        
        # Theme options
        self.themes = [
            "flatly", "darkly", "cosmo", "journal", "litera", "lumen", 
            "pulse", "sandstone", "simplex", "sketchy", "solar", "united", "yeti"
        ]
        
        # Form variables
        self.theme_var = tk.StringVar(value=settings.get("theme", "flatly"))
        self.org_folder_var = tk.StringVar(value=settings.get("organisation_folder", ""))
        self.developer_mode_var = tk.BooleanVar(value=settings.get("developer_mode", False))
        self.auto_backup_var = tk.BooleanVar(value=settings.get("auto_backup", True))
        self.show_tooltips_var = tk.BooleanVar(value=settings.get("show_tooltips", True))
        
        super().__init__(parent, "Settings", 500, 400)
    
    def create_content(self):
        """Create the settings form."""
        # Create notebook for different setting categories
        notebook = ttkb.Notebook(self.main_frame)
        notebook.pack(fill="both", expand=True, pady=(0, 10))
        
        # General tab
        self.create_general_tab(notebook)
        
        # Appearance tab
        self.create_appearance_tab(notebook)
        
        # Advanced tab
        self.create_advanced_tab(notebook)
    
    def create_general_tab(self, notebook):
        """Create general settings tab."""
        frame = ttkb.Frame(notebook)
        notebook.add(frame, text="General")
        
        # Organization folder
        folder_frame = ttkb.LabelFrame(frame, text="Default Organization Folder", padding=15)
        folder_frame.pack(fill="x", padx=15, pady=10)
        
        folder_entry_frame = ttkb.Frame(folder_frame)
        folder_entry_frame.pack(fill="x")
        
        folder_entry = ttkb.Entry(folder_entry_frame, textvariable=self.org_folder_var)
        folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_btn = ttkb.Button(folder_entry_frame, text="Browse...", 
                                command=self.browse_organization_folder)
        browse_btn.pack(side="right")
        Tooltip(browse_btn, "Browse for default organization folder")
        
        # Backup options
        backup_frame = ttkb.LabelFrame(frame, text="Backup Options", padding=15)
        backup_frame.pack(fill="x", padx=15, pady=10)
        
        auto_backup_cb = ttkb.Checkbutton(backup_frame, text="Automatically backup rules before organization", 
                                         variable=self.auto_backup_var)
        auto_backup_cb.pack(anchor="w")
        Tooltip(auto_backup_cb, "Create backup of rules before each organization run")
    
    def create_appearance_tab(self, notebook):
        """Create appearance settings tab."""
        frame = ttkb.Frame(notebook)
        notebook.add(frame, text="Appearance")
        
        # Theme selection
        theme_frame = ttkb.LabelFrame(frame, text="Theme", padding=15)
        theme_frame.pack(fill="x", padx=15, pady=10)
        
        ttkb.Label(theme_frame, text="Select theme:").pack(anchor="w", pady=(0, 5))
        
        theme_combo = ttkb.Combobox(theme_frame, textvariable=self.theme_var, 
                                   values=self.themes, state="readonly")
        theme_combo.pack(fill="x", pady=(0, 10))
        theme_combo.bind("<<ComboboxSelected>>", self.preview_theme)
        Tooltip(theme_combo, "Choose application theme")
        
        preview_btn = ttkb.Button(theme_frame, text="Preview Theme", 
                                 command=lambda: self.preview_theme(None))
        preview_btn.pack()
        
        # UI options
        ui_frame = ttkb.LabelFrame(frame, text="Interface Options", padding=15)
        ui_frame.pack(fill="x", padx=15, pady=10)
        
        tooltips_cb = ttkb.Checkbutton(ui_frame, text="Show tooltips", 
                                      variable=self.show_tooltips_var)
        tooltips_cb.pack(anchor="w")
        Tooltip(tooltips_cb, "Enable/disable helpful tooltips")
    
    def create_advanced_tab(self, notebook):
        """Create advanced settings tab."""
        frame = ttkb.Frame(notebook)
        notebook.add(frame, text="Advanced")
        
        # Developer options
        dev_frame = ttkb.LabelFrame(frame, text="Developer Options", padding=15)
        dev_frame.pack(fill="x", padx=15, pady=10)
        
        dev_mode_cb = ttkb.Checkbutton(dev_frame, text="Enable developer mode", 
                                      variable=self.developer_mode_var)
        dev_mode_cb.pack(anchor="w")
        Tooltip(dev_mode_cb, "Enable debug logging and developer tools")
        
        # Additional options could go here
        info_frame = ttkb.LabelFrame(frame, text="Information", padding=15)
        info_frame.pack(fill="x", padx=15, pady=10)
        
        info_text = ("Developer mode enables detailed logging and additional debugging tools. "
                    "This may impact performance and should only be used for troubleshooting.")
        
        info_label = ttkb.Label(info_frame, text=info_text, wraplength=450, justify="left")
        info_label.pack()
    
    def browse_organization_folder(self):
        """Browse for organization folder."""
        current_folder = self.org_folder_var.get()
        folder = filedialog.askdirectory(
            title="Select Default Organization Folder",
            initialdir=current_folder if os.path.exists(current_folder) else None
        )
        if folder:
            self.org_folder_var.set(folder)
    
    def preview_theme(self, event):
        """Preview the selected theme."""
        try:
            theme = self.theme_var.get()
            if theme:
                # Apply theme to current window
                style = ttkb.Style()
                style.theme_use(theme)
                messagebox.showinfo("Theme Preview", f"Theme '{theme}' applied. "
                                   "Click OK in the settings dialog to save this theme.")
        except Exception as e:
            messagebox.showerror("Theme Error", f"Could not apply theme: {str(e)}")
    
    def validate(self) -> bool:
        """Validate settings."""
        org_folder = self.org_folder_var.get().strip()
        if org_folder and not os.path.exists(org_folder):
            result = messagebox.askyesno("Folder Not Found", 
                                        f"Organization folder does not exist:\n{org_folder}\n\n"
                                        "Do you want to continue anyway?")
            if not result:
                return False
        
        return True
    
    def get_result(self) -> Dict[str, Any]:
        """Return updated settings."""
        self.settings.update({
            "theme": self.theme_var.get(),
            "organisation_folder": self.org_folder_var.get().strip(),
            "developer_mode": self.developer_mode_var.get(),
            "auto_backup": self.auto_backup_var.get(),
            "show_tooltips": self.show_tooltips_var.get()
        })
        return self.settings
    
    def ok(self):
        """Handle OK button - save settings."""
        if self.validate():
            settings = self.get_result()
            
            # Save settings using callback
            try:
                self.save_callback("", settings, self.logger)  # Path handled by callback
                self.result = settings
                self.dialog.destroy()
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not save settings: {str(e)}")


def open_settings_window(parent: tk.Widget, settings: Dict[str, Any], 
                        save_callback: Callable, logger):
    """Open the settings dialog."""
    dialog = SettingsDialog(parent, settings, save_callback, logger)
    result = dialog.show()
    return result

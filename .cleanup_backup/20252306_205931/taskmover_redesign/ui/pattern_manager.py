"""
Advanced Pattern Management System for TaskMover
Integrates the POC pattern engine into the main application.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import ttkbootstrap as ttkb
from typing import List, Dict, Any, Optional, Callable
import json
import logging

# Import the POC pattern engine (placeholder for now)
# from poc_pattern_engine import (
#     PatternManager, PatternRule, PatternType, PatternBuilder,
#     PatternValidator, PatternTester, PatternSuggestionEngine
# )

# Temporary stub classes until POC pattern engine is implemented
class PatternType:
    def __init__(self, value):
        self.value = value
    
    # Common pattern types
    REGEX = "regex"
    GLOB = "glob"
    EXACT = "exact"

class PatternRule:
    def __init__(self, pattern, pattern_type, description="", is_valid=True, 
                 validation_message="", examples=None, priority=0):
        self.pattern = pattern
        self.pattern_type = pattern_type
        self.description = description
        self.is_valid = is_valid
        self.validation_message = validation_message
        self.examples = examples or []
        self.priority = priority

class PatternBuilder:
    def __init__(self):
        self.pattern_type = PatternType.GLOB
        
    def set_pattern_type(self, pattern_type):
        self.pattern_type = pattern_type

class PatternTester:
    def test_pattern(self, pattern_rule, filenames):
        return []

class PatternManager:
    def __init__(self):
        self.builder = PatternBuilder()
        self.tester = PatternTester()

from .components import SimpleDialog, Tooltip
from ..core import center_window_on_parent


class PatternLibraryManager:
    """Manages a library of reusable patterns shared across all rulesets."""
    
    def __init__(self, config_directory: str):
        self.config_directory = config_directory
        self.patterns_file = os.path.join(config_directory, "pattern_library.json")
        self.pattern_manager = PatternManager()
        self.patterns: List[PatternRule] = []
        
        self.load_patterns()
    
    def load_patterns(self):
        """Load patterns from disk."""
        try:
            if os.path.exists(self.patterns_file):
                with open(self.patterns_file, 'r') as f:
                    data = json.load(f)
                
                # Load patterns from the shared library
                self.patterns = []
                for p_data in data.get('patterns', []):
                    pattern_rule = PatternRule(
                        pattern=p_data['pattern'],
                        pattern_type=PatternType(p_data['pattern_type']),
                        description=p_data.get('description', ''),
                        is_valid=p_data.get('is_valid', True),
                        validation_message=p_data.get('validation_message', ''),
                        examples=p_data.get('examples', []),
                        priority=p_data.get('priority', 0)
                    )
                    self.patterns.append(pattern_rule)
                    
        except Exception as e:
            logging.error(f"Error loading patterns: {e}")
            self.patterns = []
    
    def save_patterns(self):
        """Save patterns to disk."""
        try:
            os.makedirs(self.config_directory, exist_ok=True)
            
            # Convert patterns to serializable format
            patterns_data = []
            for pattern in self.patterns:
                pattern_data = {
                    'pattern': pattern.pattern,
                    'pattern_type': pattern.pattern_type.value,
                    'description': pattern.description,
                    'is_valid': pattern.is_valid,
                    'validation_message': pattern.validation_message,
                    'examples': pattern.examples,
                    'priority': pattern.priority
                }
                patterns_data.append(pattern_data)
            
            data = {
                'patterns': patterns_data
            }
            
            with open(self.patterns_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logging.error(f"Error saving patterns: {e}")
    
    def add_pattern(self, pattern_rule: PatternRule):
        """Add a pattern to the shared library."""
        if self.current_set not in self.pattern_sets:
            self.pattern_sets[self.current_set] = []
        
        self.pattern_sets[self.current_set].append(pattern_rule)
        self.patterns = self.pattern_sets[self.current_set]
        self.save_patterns()
    
    def remove_pattern(self, index: int):
        """Remove a pattern from the current set."""
        if 0 <= index < len(self.patterns):
            del self.patterns[index]
            self.pattern_sets[self.current_set] = self.patterns
            self.save_patterns()
    
    def get_pattern_sets(self) -> List[str]:
        """Get list of available pattern sets."""
        return list(self.pattern_sets.keys())
    
    def switch_set(self, set_name: str):
        """Switch to a different pattern set."""
        if set_name not in self.pattern_sets:
            self.pattern_sets[set_name] = []
        
        self.current_set = set_name
        self.patterns = self.pattern_sets[set_name]
        self.save_patterns()
    
    def create_set(self, set_name: str) -> bool:
        """Create a new pattern set."""
        if set_name in self.pattern_sets:
            return False
        
        self.pattern_sets[set_name] = []
        self.save_patterns()
        return True
    
    def delete_set(self, set_name: str) -> bool:
        """Delete a pattern set."""
        if set_name == 'Default' or set_name not in self.pattern_sets:
            return False
        
        del self.pattern_sets[set_name]
        if self.current_set == set_name:
            self.current_set = 'Default'
            self.patterns = self.pattern_sets['Default']
        
        self.save_patterns()
        return True


class PatternBuilderDialog(SimpleDialog):
    """Enhanced pattern builder dialog with multi-criteria support."""
    
    def __init__(self, parent, pattern_library: PatternLibraryManager, 
                 existing_pattern: Optional[PatternRule] = None):
        self.pattern_library = pattern_library
        self.pattern_manager = pattern_library.pattern_manager
        self.builder = self.pattern_manager.builder
        self.existing_pattern = existing_pattern
        self.result_pattern = None
        
        # Track all criteria
        self.criteria_vars = {}
        
        title = "Edit Pattern" if existing_pattern else "Build New Pattern"
        super().__init__(parent, title, 700, 600)
    
    def create_content(self):
        """Create the pattern builder UI."""
        # Main container with scrolling
        main_frame = ttkb.Frame(self.content_frame)
        main_frame.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(main_frame)
        scrollbar = ttkb.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttkb.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Header
        header_label = ttkb.Label(scrollable_frame, text="Multi-Criteria Pattern Builder", 
                                 font=("", 14, "bold"))
        header_label.pack(anchor="w", pady=(0, 15))
        
        # Help section
        help_frame = ttkb.LabelFrame(scrollable_frame, text="Quick Help", padding=10)
        help_frame.pack(fill="x", pady=(0, 15))
        
        help_text = """💡 Pattern Builder Tips:
• Combine multiple criteria to create precise file matching rules
• Extension: Match files by file type (pdf, jpg, txt)
• Starts With: Match files beginning with specific text
• Contains: Match files containing specific text (can add multiple)
• Ends With: Match text before the file extension
• Suffix: Match text at the very end of the filename

Example: PDF files starting with "report" and containing "2024" → report*2024*.pdf"""
        
        help_label = ttkb.Label(help_frame, text=help_text, justify="left", 
                               font=("", 9), foreground="darkblue")
        help_label.pack(anchor="w")
        
        # Pattern Type
        type_frame = ttkb.LabelFrame(scrollable_frame, text="1. Pattern Type", padding=10)
        type_frame.pack(fill="x", pady=(0, 10))
        
        self.pattern_type_var = tk.StringVar(value="glob")
        
        type_options = [
            ("glob", "Glob Pattern (recommended - uses * and ? wildcards)"),
            ("regex", "Regular Expression (advanced users only)")
        ]
        
        for value, text in type_options:
            radio = ttkb.Radiobutton(type_frame, text=text, variable=self.pattern_type_var, 
                                   value=value, command=self.update_preview)
            radio.pack(anchor="w", pady=2)
        
        # Criteria sections
        criteria_frame = ttkb.LabelFrame(scrollable_frame, text="2. Pattern Criteria (select and combine)", padding=10)
        criteria_frame.pack(fill="x", pady=(0, 10))
        
        self.setup_extension_criteria(criteria_frame)
        self.setup_starts_with_criteria(criteria_frame)
        self.setup_contains_criteria(criteria_frame)
        self.setup_ends_with_criteria(criteria_frame)
        self.setup_suffix_criteria(criteria_frame)
        
        # Live Preview
        preview_frame = ttkb.LabelFrame(scrollable_frame, text="3. Live Preview", padding=10)
        preview_frame.pack(fill="x", pady=(0, 10))
        
        self.preview_var = tk.StringVar()
        preview_label = ttkb.Label(preview_frame, textvariable=self.preview_var, 
                                  font=("Consolas", 10, "bold"), foreground="blue", wraplength=600)
        preview_label.pack(anchor="w", pady=(0, 5))
        
        self.description_var = tk.StringVar()
        desc_label = ttkb.Label(preview_frame, textvariable=self.description_var, 
                               font=("", 9), foreground="gray", wraplength=600)
        desc_label.pack(anchor="w")
        
        # Test section
        test_frame = ttkb.LabelFrame(scrollable_frame, text="4. Test Your Pattern", padding=10)
        test_frame.pack(fill="x", pady=(0, 10))
        
        test_input_frame = ttkb.Frame(test_frame)
        test_input_frame.pack(fill="x", pady=(0, 5))
        
        ttkb.Label(test_input_frame, text="Test filename:").pack(side="left")
        self.test_filename_var = tk.StringVar()
        test_entry = ttkb.Entry(test_input_frame, textvariable=self.test_filename_var, width=40)
        test_entry.pack(side="left", padx=(5, 5))
        
        test_btn = ttkb.Button(test_input_frame, text="Test", command=self.test_filename)
        test_btn.pack(side="left")
        
        self.test_result_var = tk.StringVar()
        test_result_label = ttkb.Label(test_frame, textvariable=self.test_result_var, 
                                      font=("", 9), wraplength=600)
        test_result_label.pack(anchor="w")
        
        # Pattern description
        desc_frame = ttkb.LabelFrame(scrollable_frame, text="5. Pattern Description (optional)", padding=10)
        desc_frame.pack(fill="x", pady=(0, 10))
        
        self.custom_description_var = tk.StringVar()
        desc_entry = ttkb.Entry(desc_frame, textvariable=self.custom_description_var, width=70)
        desc_entry.pack(fill="x")
        
        ttkb.Label(desc_frame, text="Leave empty to use auto-generated description", 
                  font=("", 8), foreground="gray").pack(anchor="w", pady=(2, 0))
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load existing pattern if editing
        if self.existing_pattern:
            self.load_existing_pattern()
        
        # Initial preview update
        self.update_preview()
    
    def setup_extension_criteria(self, parent):
        """Set up file extension criteria."""
        ext_frame = ttkb.LabelFrame(parent, text="File Extension", padding=5)
        ext_frame.pack(fill="x", pady=(0, 5))
        
        self.ext_enabled_var = tk.BooleanVar()
        ext_cb = ttkb.Checkbutton(ext_frame, text="Match file extension:", 
                                 variable=self.ext_enabled_var, command=self.update_preview)
        ext_cb.pack(anchor="w")
        
        ext_input_frame = ttkb.Frame(ext_frame)
        ext_input_frame.pack(fill="x", padx=(20, 0))
        
        self.ext_var = tk.StringVar()
        ext_entry = ttkb.Entry(ext_input_frame, textvariable=self.ext_var, width=20)
        ext_entry.pack(side="left", padx=(0, 5))
        
        ttkb.Label(ext_input_frame, text="(e.g., pdf, jpg, txt - no dot needed)").pack(side="left", anchor="w")
        
        self.ext_var.trace('w', self.update_preview)
        self.criteria_vars['extension'] = (self.ext_enabled_var, self.ext_var)
    
    def setup_starts_with_criteria(self, parent):
        """Set up name starts with criteria."""
        starts_frame = ttkb.LabelFrame(parent, text="Name Starts With", padding=5)
        starts_frame.pack(fill="x", pady=(0, 5))
        
        self.starts_enabled_var = tk.BooleanVar()
        starts_cb = ttkb.Checkbutton(starts_frame, text="Filename starts with:", 
                                    variable=self.starts_enabled_var, command=self.update_preview)
        starts_cb.pack(anchor="w")
        
        starts_input_frame = ttkb.Frame(starts_frame)
        starts_input_frame.pack(fill="x", padx=(20, 0))
        
        self.starts_var = tk.StringVar()
        starts_entry = ttkb.Entry(starts_input_frame, textvariable=self.starts_var, width=30)
        starts_entry.pack(side="left", padx=(0, 5))
        
        ttkb.Label(starts_input_frame, text="(e.g., report, IMG, backup)").pack(side="left", anchor="w")
        
        self.starts_var.trace('w', self.update_preview)
        self.criteria_vars['starts_with'] = (self.starts_enabled_var, self.starts_var)
    
    def setup_contains_criteria(self, parent):
        """Set up name contains criteria (supports multiple)."""
        contains_frame = ttkb.LabelFrame(parent, text="Name Contains", padding=5)
        contains_frame.pack(fill="x", pady=(0, 5))
        
        self.contains_enabled_var = tk.BooleanVar()
        contains_cb = ttkb.Checkbutton(contains_frame, text="Filename contains text:", 
                                      variable=self.contains_enabled_var, command=self.update_preview)
        contains_cb.pack(anchor="w")
        
        # Container for multiple contains entries
        self.contains_container = ttkb.Frame(contains_frame)
        self.contains_container.pack(fill="x", padx=(20, 0))
        
        # List to track contains entries
        self.contains_vars = []
        
        # Add first contains entry
        self.add_contains_entry()
        
        # Add button for more contains entries
        add_contains_btn = ttkb.Button(contains_frame, text="+ Add Another 'Contains'", 
                                      command=self.add_contains_entry)
        add_contains_btn.pack(anchor="w", padx=(20, 0), pady=(5, 0))
        
        self.criteria_vars['contains'] = (self.contains_enabled_var, self.contains_vars)
    
    def add_contains_entry(self):
        """Add a new contains text entry."""
        entry_frame = ttkb.Frame(self.contains_container)
        entry_frame.pack(fill="x", pady=2)
        
        contains_var = tk.StringVar()
        contains_entry = ttkb.Entry(entry_frame, textvariable=contains_var, width=25)
        contains_entry.pack(side="left", padx=(0, 5))
        
        if len(self.contains_vars) == 0:
            ttkb.Label(entry_frame, text="(e.g., report, 2024, temp)").pack(side="left")
        else:
            remove_btn = ttkb.Button(entry_frame, text="Remove", 
                                   command=lambda: self.remove_contains_entry(entry_frame, contains_var))
            remove_btn.pack(side="left")
        
        contains_var.trace('w', self.update_preview)
        self.contains_vars.append(contains_var)
    
    def remove_contains_entry(self, entry_frame, contains_var):
        """Remove a contains entry."""
        if contains_var in self.contains_vars:
            self.contains_vars.remove(contains_var)
        entry_frame.destroy()
        self.update_preview()
    
    def setup_ends_with_criteria(self, parent):
        """Set up name ends with criteria."""
        ends_frame = ttkb.LabelFrame(parent, text="Name Ends With (before extension)", padding=5)
        ends_frame.pack(fill="x", pady=(0, 5))
        
        self.ends_enabled_var = tk.BooleanVar()
        ends_cb = ttkb.Checkbutton(ends_frame, text="Filename ends with (before extension):", 
                                  variable=self.ends_enabled_var, command=self.update_preview)
        ends_cb.pack(anchor="w")
        
        ends_input_frame = ttkb.Frame(ends_frame)
        ends_input_frame.pack(fill="x", padx=(20, 0))
        
        self.ends_var = tk.StringVar()
        ends_entry = ttkb.Entry(ends_input_frame, textvariable=self.ends_var, width=30)
        ends_entry.pack(side="left", padx=(0, 5))
        
        ttkb.Label(ends_input_frame, text="(e.g., _backup, _copy, _final)").pack(side="left", anchor="w")
        
        self.ends_var.trace('w', self.update_preview)
        self.criteria_vars['ends_with'] = (self.ends_enabled_var, self.ends_var)
    
    def setup_suffix_criteria(self, parent):
        """Set up name suffix criteria."""
        suffix_frame = ttkb.LabelFrame(parent, text="Name Suffix (at very end)", padding=5)
        suffix_frame.pack(fill="x", pady=(0, 5))
        
        self.suffix_enabled_var = tk.BooleanVar()
        suffix_cb = ttkb.Checkbutton(suffix_frame, text="Filename has suffix at end:", 
                                    variable=self.suffix_enabled_var, command=self.update_preview)
        suffix_cb.pack(anchor="w")
        
        suffix_input_frame = ttkb.Frame(suffix_frame)
        suffix_input_frame.pack(fill="x", padx=(20, 0))
        
        self.suffix_var = tk.StringVar()
        suffix_entry = ttkb.Entry(suffix_input_frame, textvariable=self.suffix_var, width=30)
        suffix_entry.pack(side="left", padx=(0, 5))
        
        ttkb.Label(suffix_input_frame, text="(e.g., (1), _old, .bak)").pack(side="left", anchor="w")
        
        self.suffix_var.trace('w', self.update_preview)
        self.criteria_vars['suffix'] = (self.suffix_enabled_var, self.suffix_var)
    
    def load_existing_pattern(self):
        """Load an existing pattern for editing."""
        if not self.existing_pattern:
            return
        
        pattern = self.existing_pattern
        
        # Set pattern type
        if pattern.pattern_type == PatternType.REGEX:
            self.pattern_type_var.set("regex")
        else:
            self.pattern_type_var.set("glob")
        
        # Set custom description
        self.custom_description_var.set(pattern.description)
        
        # For now, we'll parse simple patterns
        # This is a simplified approach - in a full implementation,
        # you'd want to store the original criteria when saving patterns
        if pattern.pattern_type == PatternType.GLOB:
            self.parse_glob_pattern(pattern.pattern)
    
    def parse_glob_pattern(self, pattern: str):
        """Parse a glob pattern to extract criteria (simplified)."""
        # This is a basic parser - could be enhanced
        if pattern.endswith('.*'):
            pattern = pattern[:-2]
        
        # Check for extension
        if '.' in pattern and not pattern.startswith('.'):
            parts = pattern.rsplit('.', 1)
            if len(parts) == 2 and parts[1] and not '*' in parts[1]:
                self.ext_enabled_var.set(True)
                self.ext_var.set(parts[1])
                pattern = parts[0]
        
        # Check for starts with
        if not pattern.startswith('*'):
            # Find first asterisk
            star_pos = pattern.find('*')
            if star_pos > 0:
                self.starts_enabled_var.set(True)
                self.starts_var.set(pattern[:star_pos])
    
    def update_preview(self, *args):
        """Update pattern preview based on current criteria."""
        try:
            # Reset builder
            self.builder.reset()
            
            # Set pattern type
            if self.pattern_type_var.get() == "regex":
                self.builder.set_pattern_type(PatternType.REGEX)
            else:
                self.builder.set_pattern_type(PatternType.GLOB)
            
            # Apply criteria based on what's enabled
            if hasattr(self, 'ext_enabled_var') and self.ext_enabled_var.get() and self.ext_var.get().strip():
                self.builder.set_extension(self.ext_var.get().strip())
            
            if hasattr(self, 'starts_enabled_var') and self.starts_enabled_var.get() and self.starts_var.get().strip():
                self.builder.add_name_starts_with(self.starts_var.get().strip())
            
            if hasattr(self, 'contains_enabled_var') and self.contains_enabled_var.get():
                for contains_var in self.contains_vars:
                    text = contains_var.get().strip()
                    if text:
                        self.builder.add_name_contains(text)
            
            if hasattr(self, 'ends_enabled_var') and self.ends_enabled_var.get() and self.ends_var.get().strip():
                self.builder.add_name_ends_with(self.ends_var.get().strip())
            
            if hasattr(self, 'suffix_enabled_var') and self.suffix_enabled_var.get() and self.suffix_var.get().strip():
                self.builder.add_name_suffix(self.suffix_var.get().strip())
            
            # Build preview pattern
            pattern_rule = self.builder.build()
            
            self.preview_var.set(f"Pattern: {pattern_rule.pattern}")
            
            # Use custom description if provided, otherwise auto-generated
            if self.custom_description_var.get().strip():
                self.description_var.set(f"Description: {self.custom_description_var.get().strip()}")
            else:
                self.description_var.set(f"Auto Description: {pattern_rule.description}")
            
        except Exception as e:
            self.preview_var.set(f"Error: {str(e)}")
            self.description_var.set("")
    
    def test_filename(self):
        """Test the current pattern against a filename."""
        filename = self.test_filename_var.get().strip()
        if not filename:
            self.test_result_var.set("Please enter a filename to test")
            return
        
        try:
            pattern_rule = self.builder.build()
            result = self.pattern_manager.tester.test_pattern(pattern_rule, [filename])
            
            if filename in result.matching_files:
                self.test_result_var.set(f"✓ '{filename}' MATCHES the pattern")
            else:
                self.test_result_var.set(f"✗ '{filename}' does NOT match the pattern")
                
        except Exception as e:
            self.test_result_var.set(f"Test error: {str(e)}")
    
    def create_buttons(self):
        """Create dialog buttons."""
        button_frame = ttkb.Frame(self.content_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        # Cancel button
        cancel_btn = ttkb.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side="right", padx=(5, 0))
        
        # Save button
        save_btn = ttkb.Button(button_frame, text="Save Pattern", style="success.TButton", 
                              command=self.save_pattern)
        save_btn.pack(side="right")
        
        # Reset button
        reset_btn = ttkb.Button(button_frame, text="Reset All", command=self.reset_all)
        reset_btn.pack(side="left")
    
    def reset_all(self):
        """Reset all criteria."""
        # Reset all checkboxes and fields
        for criteria_name, (enabled_var, value_var) in self.criteria_vars.items():
            enabled_var.set(False)
            if criteria_name == 'contains':
                # Reset contains entries
                for contains_var in value_var:
                    contains_var.set("")
            else:
                value_var.set("")
        
        self.pattern_type_var.set("glob")
        self.custom_description_var.set("")
        self.test_filename_var.set("")
        self.test_result_var.set("")
        self.update_preview()
    
    def save_pattern(self):
        """Save the built pattern."""
        try:
            pattern_rule = self.builder.build()
            
            # Use custom description if provided
            if self.custom_description_var.get().strip():
                pattern_rule.description = self.custom_description_var.get().strip()
            
            if not pattern_rule.is_valid:
                if not messagebox.askyesno("Warning", 
                    f"Pattern validation failed: {pattern_rule.validation_message}\n\nSave anyway?"):
                    return
            
            self.result_pattern = pattern_rule
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save pattern: {str(e)}")


class PatternManagerTab:
    """Tab for managing patterns within the main application."""
    
    def __init__(self, parent_notebook, pattern_library: PatternLibraryManager):
        self.parent_notebook = parent_notebook
        self.pattern_library = pattern_library
        self.selected_pattern_index = None
        
        # Create the tab
        self.frame = ttkb.Frame(parent_notebook)
        parent_notebook.add(self.frame, text="📋 Pattern Manager")
        
        self.setup_ui()
        self.refresh_patterns()
    
    def setup_ui(self):
        """Set up the pattern manager UI."""
        # Header with help
        header_frame = ttkb.Frame(self.frame)
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        title_label = ttkb.Label(header_frame, text="Pattern Library", font=("", 16, "bold"))
        title_label.pack(side="left")
        
        help_btn = ttkb.Button(header_frame, text="? Help", style="info.TButton", 
                              command=self.show_help)
        help_btn.pack(side="right")
        Tooltip(help_btn, "Show pattern management help")
        
        # Pattern set management
        set_frame = ttkb.LabelFrame(self.frame, text="Pattern Sets", padding=10)
        set_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        set_controls = ttkb.Frame(set_frame)
        set_controls.pack(fill="x")
        
        ttkb.Label(set_controls, text="Current Set:").pack(side="left", padx=(0, 5))
        
        self.set_var = tk.StringVar()
        self.set_combo = ttkb.Combobox(set_controls, textvariable=self.set_var, 
                                      values=self.pattern_library.get_pattern_sets(),
                                      state="readonly", width=20)
        self.set_combo.set(self.pattern_library.current_set)
        self.set_combo.pack(side="left", padx=(0, 10))
        self.set_combo.bind("<<ComboboxSelected>>", self.on_set_changed)
        
        new_set_btn = ttkb.Button(set_controls, text="+ New Set", command=self.create_new_set)
        new_set_btn.pack(side="left", padx=(0, 5))
        
        delete_set_btn = ttkb.Button(set_controls, text="Delete Set", style="danger.TButton",
                                    command=self.delete_current_set)
        delete_set_btn.pack(side="left")
        
        # Quick info
        info_text = "Pattern sets allow you to organize patterns into groups (e.g., 'Work', 'Personal', 'Archives')"
        info_label = ttkb.Label(set_frame, text=info_text, font=("", 8), foreground="gray")
        info_label.pack(anchor="w", pady=(5, 0))
        
        # Pattern list
        list_frame = ttkb.LabelFrame(self.frame, text="Patterns in Current Set", padding=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        
        # Pattern treeview
        columns = ("Pattern", "Type", "Description")
        self.pattern_tree = ttkb.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        self.pattern_tree.heading("Pattern", text="Pattern")
        self.pattern_tree.heading("Type", text="Type")
        self.pattern_tree.heading("Description", text="Description")
        
        self.pattern_tree.column("Pattern", width=200)
        self.pattern_tree.column("Type", width=80)
        self.pattern_tree.column("Description", width=300)
        
        # Scrollbar for pattern list
        pattern_scrollbar = ttkb.Scrollbar(list_frame, orient="vertical", command=self.pattern_tree.yview)
        self.pattern_tree.configure(yscrollcommand=pattern_scrollbar.set)
        
        self.pattern_tree.pack(side="left", fill="both", expand=True)
        pattern_scrollbar.pack(side="right", fill="y")
        
        # Bind events
        self.pattern_tree.bind("<<TreeviewSelect>>", self.on_pattern_select)
        self.pattern_tree.bind("<Double-1>", self.edit_selected_pattern)
        
        # Pattern actions
        actions_frame = ttkb.Frame(self.frame)
        actions_frame.pack(fill="x", padx=10, pady=10)
        
        # Left side - pattern management
        left_actions = ttkb.Frame(actions_frame)
        left_actions.pack(side="left")
        
        new_pattern_btn = ttkb.Button(left_actions, text="+ New Pattern", style="success.TButton",
                                     command=self.create_new_pattern)
        new_pattern_btn.pack(side="left", padx=(0, 5))
        Tooltip(new_pattern_btn, "Create a new pattern using the pattern builder")
        
        edit_pattern_btn = ttkb.Button(left_actions, text="Edit Pattern", command=self.edit_selected_pattern)
        edit_pattern_btn.pack(side="left", padx=(0, 5))
        Tooltip(edit_pattern_btn, "Edit the selected pattern")
        
        delete_pattern_btn = ttkb.Button(left_actions, text="Delete Pattern", style="danger.TButton",
                                        command=self.delete_selected_pattern)
        delete_pattern_btn.pack(side="left", padx=(0, 15))
        Tooltip(delete_pattern_btn, "Delete the selected pattern")
        
        # Right side - rule integration
        right_actions = ttkb.Frame(actions_frame)
        right_actions.pack(side="right")
        
        add_to_rule_btn = ttkb.Button(right_actions, text="Add to Rule →", style="info.TButton",
                                     command=self.add_pattern_to_rule)
        add_to_rule_btn.pack(side="right")
        Tooltip(add_to_rule_btn, "Add the selected pattern to a rule")
        
        # Pattern details/preview section
        details_frame = ttkb.LabelFrame(self.frame, text="Pattern Details", padding=10)
        details_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.details_text = ttkb.Text(details_frame, height=4, wrap="word", state="disabled")
        self.details_text.pack(fill="x")
    
    def refresh_patterns(self):
        """Refresh the pattern list."""
        # Clear tree
        for item in self.pattern_tree.get_children():
            self.pattern_tree.delete(item)
        
        # Add patterns
        for i, pattern in enumerate(self.pattern_library.patterns):
            self.pattern_tree.insert("", "end", values=(
                pattern.pattern,
                pattern.pattern_type.value.title(),
                pattern.description[:50] + "..." if len(pattern.description) > 50 else pattern.description
            ))
        
        # Update set combo
        self.set_combo.configure(values=self.pattern_library.get_pattern_sets())
        self.set_var.set(self.pattern_library.current_set)
        
        # Clear selection and details
        self.selected_pattern_index = None
        self.update_pattern_details()
    
    def on_set_changed(self, event=None):
        """Handle pattern set change."""
        new_set = self.set_var.get()
        if new_set != self.pattern_library.current_set:
            self.pattern_library.switch_set(new_set)
            self.refresh_patterns()
    
    def on_pattern_select(self, event=None):
        """Handle pattern selection."""
        selection = self.pattern_tree.selection()
        if selection:
            item = selection[0]
            self.selected_pattern_index = self.pattern_tree.index(item)
            self.update_pattern_details()
        else:
            self.selected_pattern_index = None
            self.update_pattern_details()
    
    def update_pattern_details(self):
        """Update the pattern details section."""
        self.details_text.config(state="normal")
        self.details_text.delete(1.0, "end")
        
        if self.selected_pattern_index is not None and self.selected_pattern_index < len(self.pattern_library.patterns):
            pattern = self.pattern_library.patterns[self.selected_pattern_index]
            
            details = f"Pattern: {pattern.pattern}\n"
            details += f"Type: {pattern.pattern_type.value}\n"
            details += f"Description: {pattern.description}\n"
            details += f"Valid: {'Yes' if pattern.is_valid else 'No'}"
            if not pattern.is_valid and pattern.validation_message:
                details += f" - {pattern.validation_message}"
            
            if pattern.examples:
                details += f"\nExample matches: {', '.join(pattern.examples[:3])}"
            
            self.details_text.insert(1.0, details)
        else:
            self.details_text.insert(1.0, "Select a pattern to view details")
        
        self.details_text.config(state="disabled")
    
    def create_new_pattern(self):
        """Create a new pattern."""
        dialog = PatternBuilderDialog(self.frame, self.pattern_library)
        dialog.wait_window()
        
        if dialog.result_pattern:
            self.pattern_library.add_pattern(dialog.result_pattern)
            self.refresh_patterns()
            messagebox.showinfo("Success", "Pattern added to library!")
    
    def edit_selected_pattern(self, event=None):
        """Edit the selected pattern."""
        if self.selected_pattern_index is None:
            messagebox.showwarning("No Selection", "Please select a pattern to edit")
            return
        
        pattern = self.pattern_library.patterns[self.selected_pattern_index]
        dialog = PatternBuilderDialog(self.frame, self.pattern_library, pattern)
        dialog.wait_window()
        
        if dialog.result_pattern:
            self.pattern_library.patterns[self.selected_pattern_index] = dialog.result_pattern
            self.pattern_library.pattern_sets[self.pattern_library.current_set] = self.pattern_library.patterns
            self.pattern_library.save_patterns()
            self.refresh_patterns()
            messagebox.showinfo("Success", "Pattern updated!")
    
    def delete_selected_pattern(self):
        """Delete the selected pattern."""
        if self.selected_pattern_index is None:
            messagebox.showwarning("No Selection", "Please select a pattern to delete")
            return
        
        pattern = self.pattern_library.patterns[self.selected_pattern_index]
        if messagebox.askyesno("Confirm Delete", 
                              f"Delete pattern '{pattern.pattern}'?\n\nThis action cannot be undone."):
            self.pattern_library.remove_pattern(self.selected_pattern_index)
            self.refresh_patterns()
            messagebox.showinfo("Success", "Pattern deleted!")
    
    def create_new_set(self):
        """Create a new pattern set."""
        name = simpledialog.askstring("New Pattern Set", 
                                     "Enter name for the new pattern set:",
                                     parent=self.frame)
        if name and name.strip():
            name = name.strip()
            if self.pattern_library.create_set(name):
                self.refresh_patterns()
                messagebox.showinfo("Success", f"Created pattern set '{name}'")
            else:
                messagebox.showerror("Error", f"Pattern set '{name}' already exists")
    
    def delete_current_set(self):
        """Delete the current pattern set."""
        current_set = self.pattern_library.current_set
        if current_set == "Default":
            messagebox.showwarning("Cannot Delete", "Cannot delete the Default pattern set")
            return
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Delete pattern set '{current_set}' and all its patterns?\n\nThis action cannot be undone."):
            if self.pattern_library.delete_set(current_set):
                self.refresh_patterns()
                messagebox.showinfo("Success", f"Deleted pattern set '{current_set}'")
    
    def add_pattern_to_rule(self):
        """Add the selected pattern to a rule."""
        if self.selected_pattern_index is None:
            messagebox.showwarning("No Selection", "Please select a pattern to add to a rule")
            return
        
        # This would integrate with the rule system
        # For now, show a placeholder message
        pattern = self.pattern_library.patterns[self.selected_pattern_index]
        messagebox.showinfo("Add to Rule", 
                           f"Pattern '{pattern.pattern}' will be added to the selected rule.\n\n"
                           "This feature will integrate with the rule editor.")
    
    def show_help(self):
        """Show pattern management help."""
        help_window = PatternHelpWindow(self.frame)


class PatternHelpWindow:
    """Comprehensive help window for pattern management."""
    
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Pattern Management Help")
        self.window.geometry("800x600")
        center_window_on_parent(self.window, parent, proportional=True, width_ratio=0.8, height_ratio=0.8)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the help window UI."""
        # Create notebook for different help sections
        notebook = ttkb.Notebook(self.window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Overview tab
        overview_frame = ttkb.Frame(notebook)
        notebook.add(overview_frame, text="Overview")
        self.create_overview_tab(overview_frame)
        
        # Pattern Types tab
        types_frame = ttkb.Frame(notebook)
        notebook.add(types_frame, text="Pattern Types")
        self.create_types_tab(types_frame)
        
        # Examples tab
        examples_frame = ttkb.Frame(notebook)
        notebook.add(examples_frame, text="Examples")
        self.create_examples_tab(examples_frame)
        
        # Tips tab
        tips_frame = ttkb.Frame(notebook)
        notebook.add(tips_frame, text="Tips & Tricks")
        self.create_tips_tab(tips_frame)
        
        # Close button
        close_btn = ttkb.Button(self.window, text="Close", command=self.window.destroy)
        close_btn.pack(pady=(0, 10))
    
    def create_overview_tab(self, parent):
        """Create the overview help tab."""
        text_widget = ttkb.Text(parent, wrap="word", padx=10, pady=10)
        scrollbar = ttkb.Scrollbar(parent, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        content = """PATTERN MANAGEMENT OVERVIEW

What are Patterns?
Patterns are rules that define which files should be matched based on their names, extensions, or other criteria. TaskMover uses patterns to automatically organize your files.

Pattern Sets
Pattern sets allow you to organize your patterns into logical groups:
• Work: Patterns for work-related files
• Personal: Patterns for personal files  
• Archives: Patterns for old files
• Project-specific: Patterns for specific projects

Why Use the Pattern Library?
1. REUSABILITY: Create patterns once, use them in multiple rules
2. ORGANIZATION: Keep your patterns organized in sets
3. CONSISTENCY: Ensure the same pattern works the same way everywhere
4. EFFICIENCY: No need to recreate complex patterns

Basic Workflow:
1. Create pattern sets for different categories
2. Build patterns using the Pattern Builder
3. Add patterns to your library
4. Use patterns in rules to organize files
5. Test and refine patterns as needed

Multi-Criteria Patterns:
The Pattern Builder lets you combine multiple criteria:
• File extension (pdf, jpg, txt)
• Name starts with (report, IMG, backup)
• Name contains (multiple terms)
• Name ends with (before extension)
• Name suffix (at very end)

This makes it easy to create precise matching rules without learning complex pattern syntax."""
        
        text_widget.insert(1.0, content)
        text_widget.config(state="disabled")
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_types_tab(self, parent):
        """Create the pattern types help tab."""
        text_widget = ttkb.Text(parent, wrap="word", padx=10, pady=10)
        scrollbar = ttkb.Scrollbar(parent, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        content = """PATTERN TYPES EXPLAINED

GLOB PATTERNS (Recommended)
Glob patterns use simple wildcards and are easy to understand:

* (asterisk) - Matches any number of characters
  Example: report*.pdf matches report.pdf, report_2024.pdf, report_monthly.pdf

? (question mark) - Matches exactly one character
  Example: IMG_?.jpg matches IMG_1.jpg, IMG_A.jpg (but not IMG_10.jpg)

[] (brackets) - Matches any one character inside
  Example: file[123].txt matches file1.txt, file2.txt, file3.txt

Common Glob Examples:
• *.pdf - All PDF files
• report* - Files starting with "report"
• *backup* - Files containing "backup"
• *.{jpg,jpeg,png} - Image files (multiple extensions)

REGULAR EXPRESSIONS (Advanced)
Regex patterns are powerful but complex. Use only if you're familiar with regex:

. (dot) - Matches any single character
+ (plus) - One or more of the preceding character
* (asterisk) - Zero or more of the preceding character  
^ (caret) - Start of string
$ (dollar) - End of string

Regular Expression Examples:
• ^report.*\\.pdf$ - PDF files starting with "report"
• .*\\.(jpe?g|png|gif)$ - Image files
• \\d{4}-\\d{2}-\\d{2} - Date pattern (YYYY-MM-DD)

WHEN TO USE WHICH:
• Use GLOB for 95% of cases - they're simpler and more readable
• Use REGEX only when you need complex pattern matching
• Always test your patterns with example filenames
• Document complex patterns so you remember what they do"""
        
        text_widget.insert(1.0, content)
        text_widget.config(state="disabled")
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_examples_tab(self, parent):
        """Create the examples help tab."""
        text_widget = ttkb.Text(parent, wrap="word", padx=10, pady=10)
        scrollbar = ttkb.Scrollbar(parent, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        content = """PATTERN EXAMPLES

SIMPLE PATTERNS:
• *.pdf → All PDF files
• *.{jpg,jpeg,png} → All image files
• report* → Files starting with "report"
• *backup* → Files containing "backup"
• *_temp.* → Files ending with "_temp" (any extension)

WORK DOCUMENTS:
• meeting_notes_*.docx → Meeting notes documents
• project_*_spec.pdf → Project specification PDFs
• invoice_2024_*.pdf → 2024 invoices
• *_presentation.pptx → Presentation files

PHOTOS & MEDIA:
• IMG_*.jpg → Camera photos
• Screenshot_*.png → Screenshots  
• *_edited.* → Edited files (any type)
• vacation_2024_*.* → 2024 vacation files

DOWNLOADS & ARCHIVES:
• *.zip → ZIP archives
• *setup*.exe → Software installers
• *manual*.pdf → PDF manuals
• temp_*.* → Temporary files

MULTI-CRITERIA EXAMPLES:
Using the Pattern Builder to combine criteria:

Example 1: Work Reports
• Extension: pdf
• Starts with: report
• Contains: 2024
• Result: report*2024*.pdf
• Matches: report_quarterly_2024.pdf, report_2024_summary.pdf

Example 2: Edited Photos
• Extension: jpg
• Contains: IMG
• Ends with: _edited
• Result: *IMG*_edited.jpg  
• Matches: vacation_IMG_001_edited.jpg, family_IMG_portrait_edited.jpg

Example 3: Project Documents
• Extension: docx
• Starts with: project
• Contains: spec, v2
• Result: project*spec*v2*.docx
• Matches: project_alpha_spec_v2_final.docx

TESTING YOUR PATTERNS:
Always test patterns with real filenames:
1. Use the "Test Your Pattern" feature in Pattern Builder
2. Try edge cases (short names, special characters)
3. Test with files you don't want to match
4. Start with broad patterns, then make them more specific"""
        
        text_widget.insert(1.0, content)
        text_widget.config(state="disabled")
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_tips_tab(self, parent):
        """Create the tips and tricks help tab."""
        text_widget = ttkb.Text(parent, wrap="word", padx=10, pady=10)
        scrollbar = ttkb.Scrollbar(parent, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        content = """TIPS & TRICKS

PATTERN ORGANIZATION:
✓ Use descriptive pattern set names (Work, Personal, Archives)
✓ Group related patterns together
✓ Include the purpose in pattern descriptions
✓ Test patterns before adding them to rules

PATTERN DESIGN:
✓ Start simple, add complexity gradually
✓ Use the most specific criteria first
✓ Avoid overly broad patterns that catch everything
✓ Test with both matching and non-matching files

COMMON MISTAKES:
✗ Making patterns too specific (they won't match anything)
✗ Making patterns too broad (they match too much)
✗ Forgetting to test with real filenames
✗ Using complex regex when simple glob would work
✗ Not documenting complex patterns

EFFICIENCY TIPS:
• Use "Contains" for multiple keywords
• Combine criteria instead of creating multiple simple patterns
• Use pattern sets to organize by project or category
• Reuse patterns across multiple rules
• Keep a "Testing" pattern set for experiments

TROUBLESHOOTING:
Problem: Pattern doesn't match expected files
Solution: Test with actual filenames, check for typos

Problem: Pattern matches too many files  
Solution: Add more specific criteria or use "ends with"

Problem: Can't remember what a pattern does
Solution: Always add clear descriptions

Problem: Complex pattern doesn't work
Solution: Break it down into simpler parts and test each

ADVANCED TECHNIQUES:
• Use negative patterns in rules (patterns that exclude files)
• Combine multiple patterns in a single rule
• Create pattern hierarchies (broad to specific)
• Use pattern priorities to control matching order

REAL-WORLD WORKFLOWS:
1. PHOTO ORGANIZATION:
   - Camera photos: IMG_*.jpg
   - Screenshots: Screenshot*.png
   - Edited photos: *_edited.*

2. DOCUMENT MANAGEMENT:
   - Invoices by year: invoice_2024_*.*
   - Meeting notes: meeting_*_notes.*
   - Contracts: contract_*_signed.*

3. SOFTWARE DEVELOPMENT:
   - Source code: *.{py,js,html,css}
   - Documentation: *{readme,doc,manual}*.*
   - Archives: *.{zip,tar,gz}

Remember: The best pattern is one that's simple, effective, and easy to understand later!"""
        
        text_widget.insert(1.0, content)
        text_widget.config(state="disabled")
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


class PatternLibrarySelectDialog(SimpleDialog):
    """Dialog for selecting patterns from the library."""
    
    def __init__(self, parent, pattern_library: PatternLibraryManager):
        self.pattern_library = pattern_library
        self.selected_patterns = []
        
        super().__init__(parent, "Select Patterns from Library", 600, 400)
    
    def create_content(self):
        """Create the pattern selection UI."""
        # Pattern set selection
        set_frame = ttkb.Frame(self.main_frame)
        set_frame.pack(fill="x", pady=(0, 10))
        
        ttkb.Label(set_frame, text="Pattern Set:").pack(side="left", padx=(0, 5))
        
        self.set_var = tk.StringVar(value=self.pattern_library.current_set)
        set_combo = ttkb.Combobox(set_frame, textvariable=self.set_var,
                                 values=self.pattern_library.get_pattern_sets(),
                                 state="readonly", width=20)
        set_combo.pack(side="left")
        set_combo.bind("<<ComboboxSelected>>", self.on_set_changed)
        
        # Pattern list with checkboxes
        list_frame = ttkb.LabelFrame(self.main_frame, text="Available Patterns", padding=10)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Create scrollable frame for checkboxes
        canvas = tk.Canvas(list_frame)
        scrollbar = ttkb.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttkb.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.pattern_vars = {}
        self.refresh_patterns()
    
    def refresh_patterns(self):
        """Refresh the pattern list."""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.pattern_vars = {}
        
        # Get patterns from current set
        current_set = self.set_var.get()
        if current_set in self.pattern_library.pattern_sets:
            patterns = self.pattern_library.pattern_sets[current_set]
        else:
            patterns = []
        
        if not patterns:
            no_patterns_label = ttkb.Label(self.scrollable_frame, 
                                          text="No patterns in this set. Create some in the Pattern Manager!", 
                                          foreground="gray")
            no_patterns_label.pack(pady=20)
            return
        
        # Create checkboxes for each pattern
        for i, pattern in enumerate(patterns):
            pattern_frame = ttkb.Frame(self.scrollable_frame)
            pattern_frame.pack(fill="x", pady=2)
            
            var = tk.BooleanVar()
            self.pattern_vars[i] = var
            
            cb = ttkb.Checkbutton(pattern_frame, variable=var)
            cb.pack(side="left", padx=(0, 10))
            
            # Pattern info
            info_text = f"{pattern.pattern} ({pattern.pattern_type.value})"
            if pattern.description:
                info_text += f" - {pattern.description}"
            
            info_label = ttkb.Label(pattern_frame, text=info_text, font=("", 9))
            info_label.pack(side="left", anchor="w")
    
    def on_set_changed(self, event=None):
        """Handle pattern set change."""
        self.refresh_patterns()
    
    def create_buttons(self):
        """Create dialog buttons."""
        button_frame = ttkb.Frame(self.main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        # Cancel button
        cancel_btn = ttkb.Button(button_frame, text="Cancel", command=self.dialog.destroy)
        cancel_btn.pack(side="right", padx=(5, 0))
        
        # Select button
        select_btn = ttkb.Button(button_frame, text="Add Selected", style="success.TButton",
                                command=self.select_patterns)
        select_btn.pack(side="right")
        
        # Select all/none buttons
        select_all_btn = ttkb.Button(button_frame, text="Select All", command=self.select_all)
        select_all_btn.pack(side="left")
        
        select_none_btn = ttkb.Button(button_frame, text="Select None", command=self.select_none)
        select_none_btn.pack(side="left", padx=(5, 0))
    
    def select_all(self):
        """Select all patterns."""
        for var in self.pattern_vars.values():
            var.set(True)
    
    def select_none(self):
        """Deselect all patterns."""
        for var in self.pattern_vars.values():
            var.set(False)
    
    def select_patterns(self):
        """Select the checked patterns."""
        current_set = self.set_var.get()
        if current_set in self.pattern_library.pattern_sets:
            patterns = self.pattern_library.pattern_sets[current_set]
            
            self.selected_patterns = []
            for i, var in self.pattern_vars.items():
                if var.get() and i < len(patterns):
                    self.selected_patterns.append(patterns[i])
        
        self.dialog.destroy()

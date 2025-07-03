"""
Rule Management Components
=========================

Advanced components for managing file organization rules with full integration
to the Pattern System and Rule System backends. Provides intuitive interfaces
for rule creation, editing, execution, and monitoring with real-time validation.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Optional, Any, List, Callable, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import UUID
import asyncio
import threading
import time

from .base_component import BaseComponent, ModernButton, ModernCard, ComponentState
from .theme_manager import get_theme_manager
from .input_components import ModernEntry, ModernCombobox, SmartPatternInput
from .dialog_components import ModernDialog, ConfirmationDialog, ProgressDialog

# Import backend services
from ..core.rules.models import Rule, RuleExecutionResult, ErrorHandlingBehavior
from ..core.rules.service import RuleService
from ..core.rules.exceptions import RuleSystemError, RuleValidationError
from ..core.patterns.models import Pattern


@dataclass
class RuleDisplayInfo:
    """Display information for rules in UI components."""
    rule: Rule
    pattern_name: str = ""
    validation_status: str = "unknown"
    last_execution: Optional[datetime] = None
    execution_count: int = 0


class RuleCreationWizard(ModernDialog):
    """
    Step-by-step wizard for creating new rules with pattern integration.
    Guides users through pattern selection, destination setup, and validation.
    """
    
    def __init__(self, parent: tk.Widget, rule_service: RuleService, pattern_service, **kwargs):
        self.rule_service = rule_service
        self.pattern_service = pattern_service
        self.created_rule = None
        self.current_step = 0
        self.steps = ["Pattern", "Destination", "Settings", "Review"]
        
        # Wizard data
        self.selected_pattern_id = None
        self.destination_path = None
        self.rule_name = ""
        self.rule_description = ""
        self.priority = 5
        self.error_handling = ErrorHandlingBehavior.CONTINUE_ON_RECOVERABLE
        
        super().__init__(
            parent,
            title="Create New Rule",
            size=(600, 500),
            resizable=True,
            **kwargs
        )
    
    def _create_dialog_content(self):
        """Create wizard content with step navigation."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Header with step indicator
        header_frame = tk.Frame(self.dialog_window, bg=tokens.colors["background"])
        header_frame.pack(fill="x", padx=tokens.spacing["lg"], pady=(tokens.spacing["lg"], 0))
        
        self.step_indicator = self._create_step_indicator(header_frame)
        self.step_indicator.pack(fill="x", pady=(0, tokens.spacing["lg"]))
        
        # Content area for steps
        self.step_content = tk.Frame(self.dialog_window, bg=tokens.colors["background"])
        self.step_content.pack(fill="both", expand=True, padx=tokens.spacing["lg"])
        
        # Navigation buttons
        nav_frame = tk.Frame(self.dialog_window, bg=tokens.colors["background"])
        nav_frame.pack(fill="x", padx=tokens.spacing["lg"], pady=tokens.spacing["lg"])
        
        self.prev_button = ModernButton(
            nav_frame,
            text="← Previous",
            command=self._previous_step,
            state="disabled"
        )
        self.prev_button.pack(side="left")
        
        self.next_button = ModernButton(
            nav_frame,
            text="Next →",
            command=self._next_step
        )
        self.next_button.pack(side="right", padx=(tokens.spacing["sm"], 0))
        
        self.cancel_button = ModernButton(
            nav_frame,
            text="Cancel",
            variant="secondary",
            command=self._on_cancel
        )
        self.cancel_button.pack(side="right")
        
        # Show first step
        self._show_step(0)
    
    def _create_step_indicator(self, parent: tk.Widget) -> tk.Widget:
        """Create visual step indicator."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        indicator_frame = tk.Frame(parent, bg=tokens.colors["background"])
        
        self.step_labels = []
        for i, step in enumerate(self.steps):
            # Step circle
            circle_frame = tk.Frame(indicator_frame, bg=tokens.colors["background"])
            circle_frame.pack(side="left", padx=(0, tokens.spacing["lg"]))
            
            circle = tk.Label(
                circle_frame,
                text=str(i + 1),
                font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), "bold"),
                bg=tokens.colors["surface_variant"],
                fg=tokens.colors["on_surface_variant"],
                width=3,
                height=1,
                relief="solid",
                bd=2
            )
            circle.pack()
            
            # Step label
            label = tk.Label(
                circle_frame,
                text=step,
                font=(tokens.fonts["family"], int(tokens.fonts["size_caption"])),
                bg=tokens.colors["background"],
                fg=tokens.colors["text_secondary"]
            )
            label.pack(pady=(tokens.spacing["xs"], 0))
            
            self.step_labels.append((circle, label))
            
            # Connection line (except for last step)
            if i < len(self.steps) - 1:
                line = tk.Frame(
                    indicator_frame,
                    bg=tokens.colors["outline"],
                    height=2
                )
                line.pack(side="left", fill="x", expand=True, pady=(15, 0))
        
        return indicator_frame
    
    def _update_step_indicator(self):
        """Update step indicator visual state."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        for i, (circle, label) in enumerate(self.step_labels):
            if i == self.current_step:
                # Current step
                circle.configure(
                    bg=tokens.colors["primary"],
                    fg=tokens.colors["on_primary"]
                )
                label.configure(fg=tokens.colors["text"])
            elif i < self.current_step:
                # Completed step
                circle.configure(
                    bg=tokens.colors["success"],
                    fg=tokens.colors["on_success"]
                )
                label.configure(fg=tokens.colors["text"])
            else:
                # Future step
                circle.configure(
                    bg=tokens.colors["surface_variant"],
                    fg=tokens.colors["on_surface_variant"]
                )
                label.configure(fg=tokens.colors["text_secondary"])
    
    def _show_step(self, step: int):
        """Show specific wizard step."""
        # Clear current content
        for widget in self.step_content.winfo_children():
            widget.destroy()
        
        # Update current step
        self.current_step = step
        self._update_step_indicator()
        
        # Show step content
        if step == 0:
            self._show_pattern_step()
        elif step == 1:
            self._show_destination_step()
        elif step == 2:
            self._show_settings_step()
        elif step == 3:
            self._show_review_step()
        
        # Update navigation buttons
        if step > 0:
            self.prev_button.set_state(ComponentState.DEFAULT)
        else:
            self.prev_button.set_state(ComponentState.DISABLED)
        
        # Update next button text
        self.next_button.button.configure(
            text="Create Rule" if step == len(self.steps) - 1 else "Next →"
        )
    
    def _show_pattern_step(self):
        """Show pattern selection step."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Step title
        title = tk.Label(
            self.step_content,
            text="Select Pattern",
            font=(tokens.fonts["family"], int(tokens.fonts["size_h3"]), tokens.fonts["weight_bold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        )
        title.pack(pady=(0, tokens.spacing["lg"]))
        
        # Description
        desc = tk.Label(
            self.step_content,
            text="Choose a pattern that matches the files you want to organize.",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"])),
            bg=tokens.colors["background"],
            fg=tokens.colors["text_secondary"],
            wraplength=500
        )
        desc.pack(pady=(0, tokens.spacing["lg"]))
        
        # Pattern selector (placeholder)
        pattern_frame = tk.Frame(self.step_content, bg=tokens.colors["background"])
        pattern_frame.pack(fill="x", pady=tokens.spacing["md"])
        
        tk.Label(
            pattern_frame,
            text="Pattern ID:",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(anchor="w", pady=(0, tokens.spacing["xs"]))
        
        self.pattern_id_var = tk.StringVar()
        self.pattern_id_entry = ModernEntry(
            pattern_frame,
            textvariable=self.pattern_id_var,
            placeholder="Enter pattern ID..."
        )
        self.pattern_id_entry.pack(fill="x")
    
    def _show_destination_step(self):
        """Show destination configuration step."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Step title
        title = tk.Label(
            self.step_content,
            text="Set Destination",
            font=(tokens.fonts["family"], int(tokens.fonts["size_h3"]), tokens.fonts["weight_bold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        )
        title.pack(pady=(0, tokens.spacing["lg"]))
        
        # Description
        desc = tk.Label(
            self.step_content,
            text="Specify where matching files should be moved.",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"])),
            bg=tokens.colors["background"],
            fg=tokens.colors["text_secondary"]
        )
        desc.pack(pady=(0, tokens.spacing["lg"]))
        
        # Directory selection
        dir_frame = tk.Frame(self.step_content, bg=tokens.colors["background"])
        dir_frame.pack(fill="x", pady=(0, tokens.spacing["lg"]))
        
        tk.Label(
            dir_frame,
            text="Destination Directory:",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(anchor="w", pady=(0, tokens.spacing["xs"]))
        
        path_frame = tk.Frame(dir_frame, bg=tokens.colors["background"])
        path_frame.pack(fill="x")
        
        self.dest_path_var = tk.StringVar(value=str(self.destination_path) if self.destination_path else "")
        self.dest_entry = ModernEntry(
            path_frame,
            textvariable=self.dest_path_var,
            placeholder="Select destination directory..."
        )
        self.dest_entry.pack(side="left", fill="x", expand=True, padx=(0, tokens.spacing["sm"]))
        
        browse_button = ModernButton(
            path_frame,
            text="Browse...",
            command=self._browse_destination
        )
        browse_button.pack(side="right")
        
        # Rule name and description
        name_frame = tk.Frame(self.step_content, bg=tokens.colors["background"])
        name_frame.pack(fill="x", pady=(0, tokens.spacing["md"]))
        
        tk.Label(
            name_frame,
            text="Rule Name:",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(anchor="w", pady=(0, tokens.spacing["xs"]))
        
        self.name_var = tk.StringVar(value=self.rule_name)
        name_entry = ModernEntry(
            name_frame,
            textvariable=self.name_var,
            placeholder="Enter rule name..."
        )
        name_entry.pack(fill="x")
        
        desc_frame = tk.Frame(self.step_content, bg=tokens.colors["background"])
        desc_frame.pack(fill="x")
        
        tk.Label(
            desc_frame,
            text="Description (optional):",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(anchor="w", pady=(0, tokens.spacing["xs"]))
        
        self.desc_var = tk.StringVar(value=self.rule_description)
        desc_entry = ModernEntry(
            desc_frame,
            textvariable=self.desc_var,
            placeholder="Enter description..."
        )
        desc_entry.pack(fill="x")
    
    def _show_settings_step(self):
        """Show rule settings step."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Step title
        title = tk.Label(
            self.step_content,
            text="Rule Settings",
            font=(tokens.fonts["family"], int(tokens.fonts["size_h3"]), tokens.fonts["weight_bold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        )
        title.pack(pady=(0, tokens.spacing["lg"]))
        
        # Priority setting
        priority_frame = tk.Frame(self.step_content, bg=tokens.colors["background"])
        priority_frame.pack(fill="x", pady=(0, tokens.spacing["lg"]))
        
        tk.Label(
            priority_frame,
            text="Priority (1-10):",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(anchor="w", pady=(0, tokens.spacing["xs"]))
        
        priority_control = tk.Frame(priority_frame, bg=tokens.colors["background"])
        priority_control.pack(fill="x")
        
        self.priority_var = tk.IntVar(value=self.priority)
        priority_scale = tk.Scale(
            priority_control,
            from_=1,
            to=10,
            orient="horizontal",
            variable=self.priority_var,
            bg=tokens.colors["background"],
            fg=tokens.colors["text"],
            highlightthickness=0,
            troughcolor=tokens.colors["surface_variant"]
        )
        priority_scale.pack(side="left", fill="x", expand=True, padx=(0, tokens.spacing["md"]))
        
        priority_label = tk.Label(
            priority_control,
            textvariable=self.priority_var,
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_bold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"],
            width=3
        )
        priority_label.pack(side="right")
        
        # Error handling
        error_frame = tk.Frame(self.step_content, bg=tokens.colors["background"])
        error_frame.pack(fill="x")
        
        tk.Label(
            error_frame,
            text="Error Handling:",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(anchor="w", pady=(0, tokens.spacing["xs"]))
        
        self.error_handling_var = tk.StringVar(value=self.error_handling.value)
        error_combo = ModernCombobox(
            error_frame,
            textvariable=self.error_handling_var,
            values=[e.value for e in ErrorHandlingBehavior],
            state="readonly"
        )
        error_combo.pack(fill="x")
        
        # Help text
        help_text = tk.Label(
            self.step_content,
            text="• Priority determines execution order (higher = first)\n"
                 "• Error handling controls behavior when files can't be moved",
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"])),
            bg=tokens.colors["background"],
            fg=tokens.colors["text_secondary"],
            justify="left"
        )
        help_text.pack(anchor="w", pady=(tokens.spacing["lg"], 0))
    
    def _show_review_step(self):
        """Show rule review and confirmation step."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Step title
        title = tk.Label(
            self.step_content,
            text="Review Rule",
            font=(tokens.fonts["family"], int(tokens.fonts["size_h3"]), tokens.fonts["weight_bold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        )
        title.pack(pady=(0, tokens.spacing["lg"]))
        
        # Review card
        review_card = ModernCard(self.step_content)
        review_card.pack(fill="both", expand=True)
        
        # Get pattern info
        try:
            pattern = self.pattern_service.get_pattern(self.selected_pattern_id)
            pattern_name = pattern.name if pattern else "Unknown Pattern"
            pattern_expr = pattern.expression if pattern else "Unknown"
        except Exception:
            pattern_name = "Unknown Pattern"
            pattern_expr = "Unknown"
        
        # Review content
        review_content = [
            ("Rule Name", self.name_var.get() if hasattr(self, 'name_var') else self.rule_name),
            ("Description", self.desc_var.get() if hasattr(self, 'desc_var') else self.rule_description),
            ("Pattern", f"{pattern_name} ({pattern_expr})"),
            ("Destination", self.dest_path_var.get() if hasattr(self, 'dest_path_var') else str(self.destination_path)),
            ("Priority", str(self.priority_var.get() if hasattr(self, 'priority_var') else self.priority)),
            ("Error Handling", self.error_handling_var.get() if hasattr(self, 'error_handling_var') else self.error_handling.value)
        ]
        
        for label, value in review_content:
            item_frame = tk.Frame(review_card, bg=tokens.colors["surface"])
            item_frame.pack(fill="x", padx=tokens.spacing["md"], pady=tokens.spacing["xs"])
            
            tk.Label(
                item_frame,
                text=f"{label}:",
                font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_semibold"]),
                bg=tokens.colors["surface"],
                fg=tokens.colors["text"],
                width=15,
                anchor="w"
            ).pack(side="left")
            
            tk.Label(
                item_frame,
                text=value or "Not specified",
                font=(tokens.fonts["family"], int(tokens.fonts["size_body"])),
                bg=tokens.colors["surface"],
                fg=tokens.colors["text"],
                anchor="w"
            ).pack(side="left", fill="x", expand=True, padx=(tokens.spacing["sm"], 0))
    
    def _on_pattern_selected(self, pattern_id: UUID):
        """Handle pattern selection."""
        self.selected_pattern_id = pattern_id
    
    def _browse_destination(self):
        """Browse for destination directory."""
        directory = filedialog.askdirectory(
            title="Select Destination Directory",
            initialdir=str(self.destination_path) if self.destination_path else ""
        )
        if directory:
            self.dest_path_var.set(directory)
            self.destination_path = Path(directory)
    
    def _previous_step(self):
        """Go to previous step."""
        if self.current_step > 0:
            self._show_step(self.current_step - 1)
    
    def _next_step(self):
        """Go to next step or create rule."""
        if self.current_step < len(self.steps) - 1:
            # Validate current step
            if self._validate_current_step():
                self._show_step(self.current_step + 1)
        else:
            # Create rule
            self._create_rule()
    
    def _validate_current_step(self) -> bool:
        """Validate current step input."""
        if self.current_step == 0:
            # Pattern step
            if not self.selected_pattern_id:
                messagebox.showerror("Validation Error", "Please select a pattern.")
                return False
        elif self.current_step == 1:
            # Destination step
            if not self.dest_path_var.get().strip():
                messagebox.showerror("Validation Error", "Please select a destination directory.")
                return False
            if not self.name_var.get().strip():
                messagebox.showerror("Validation Error", "Please enter a rule name.")
                return False
            
            # Update internal state
            self.destination_path = Path(self.dest_path_var.get())
            self.rule_name = self.name_var.get()
            self.rule_description = self.desc_var.get()
        elif self.current_step == 2:
            # Settings step
            self.priority = self.priority_var.get()
            self.error_handling = ErrorHandlingBehavior(self.error_handling_var.get())
        
        return True
    
    def _create_rule(self):
        """Create the rule using the backend service."""
        try:
            # Validate required fields
            if not self.selected_pattern_id:
                raise RuleValidationError("Pattern must be selected")
            if not self.destination_path:
                raise RuleValidationError("Destination path must be specified")
                
            # Create rule using backend service
            rule = self.rule_service.create_rule(
                name=self.rule_name,
                description=self.rule_description,
                pattern_id=self.selected_pattern_id,
                destination_path=self.destination_path,
                priority=self.priority,
                error_handling=self.error_handling
            )
            
            self.created_rule = rule
            messagebox.showinfo("Success", f"Rule '{rule.name}' created successfully!")
            self._on_ok()
            
        except RuleValidationError as e:
            messagebox.showerror("Validation Error", f"Rule validation failed:\n{e}")
        except RuleSystemError as e:
            messagebox.showerror("Error", f"Failed to create rule:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error:\n{e}")
    
    def _on_cancel(self):
        """Handle cancel action."""
        if messagebox.askyesno("Confirm", "Are you sure you want to cancel rule creation?"):
            self.result = None
            self.destroy()
    
    def _on_ok(self):
        """Handle OK action."""
        self.result = self.created_rule
        self.destroy()


class RuleManagementView(BaseComponent):
    """
    Main rule management interface with list view, filtering, and actions.
    Integrates with Pattern System to show pattern-rule relationships.
    """
    
    def __init__(self, parent: tk.Widget, rule_service: RuleService, pattern_service, **kwargs):
        # Store custom parameters before calling super()
        self.rule_service = rule_service
        self.pattern_service = pattern_service
        self.rules_data: List[RuleDisplayInfo] = []
        self.selected_rule_id: Optional[UUID] = None
        self.filter_text = ""
        self.show_inactive = False
        
        # Filter out custom parameters that shouldn't go to tkinter
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in ['rule_service', 'pattern_service']}
        super().__init__(parent, **filtered_kwargs)
        self._refresh_rules()
    
    def _create_component(self):
        """Create main rule management interface."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Configure main frame
        self.configure(bg=tokens.colors["background"])
        
        # Header section
        header_frame = self._create_header()
        header_frame.pack(fill="x", padx=tokens.spacing["lg"], pady=(tokens.spacing["lg"], 0))
        
        # Toolbar section  
        toolbar_frame = self._create_toolbar()
        toolbar_frame.pack(fill="x", padx=tokens.spacing["lg"], pady=tokens.spacing["md"])
        
        # Main content area
        content_frame = tk.Frame(self, bg=tokens.colors["background"])
        content_frame.pack(fill="both", expand=True, padx=tokens.spacing["lg"], pady=(0, tokens.spacing["lg"]))
        
        # Rules list
        self.rules_list = self._create_rules_list(content_frame)
        self.rules_list.pack(fill="both", expand=True)
    
    def _create_header(self) -> tk.Frame:
        """Create header section with title and stats."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        header_frame = tk.Frame(self, bg=tokens.colors["background"])
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="Rule Management",
            font=(tokens.fonts["family"], int(tokens.fonts["size_heading_1"]), tokens.fonts["weight_bold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        )
        title_label.pack(side="left")
        
        # Stats
        self.stats_label = tk.Label(
            header_frame,
            text="",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_normal"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text_secondary"]
        )
        self.stats_label.pack(side="right")
        
        return header_frame
    
    def _create_toolbar(self) -> tk.Frame:
        """Create toolbar with filtering and action buttons."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        toolbar_frame = tk.Frame(self, bg=tokens.colors["background"])
        
        # Filter section
        filter_frame = tk.Frame(toolbar_frame, bg=tokens.colors["background"])
        filter_frame.pack(side="left", fill="x", expand=True)
        
        # Search entry
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_changed)
        
        search_entry = ModernEntry(
            filter_frame,
            textvariable=self.search_var,
            placeholder="Search rules...",
            width=30
        )
        search_entry.pack(side="left", padx=(0, tokens.spacing["md"]))
        
        # Show inactive checkbox
        self.show_inactive_var = tk.BooleanVar(value=self.show_inactive)
        self.show_inactive_var.trace_add("write", self._on_filter_changed)
        
        inactive_cb = tk.Checkbutton(
            filter_frame,
            text="Show inactive rules",
            variable=self.show_inactive_var,
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_normal"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"],
            selectcolor=tokens.colors["background"],
            activebackground=tokens.colors["background"],
            activeforeground=tokens.colors["text"]
        )
        inactive_cb.pack(side="left")
        
        # Action buttons
        action_frame = tk.Frame(toolbar_frame, bg=tokens.colors["background"])
        action_frame.pack(side="right")
        
        self.create_button = ModernButton(
            action_frame,
            text="+ Create Rule",
            command=self._create_rule,
            variant="primary",
            width=120
        )
        self.create_button.pack(side="left", padx=(0, tokens.spacing["sm"]))
        
        self.edit_button = ModernButton(
            action_frame,
            text="Edit",
            command=self._edit_rule,
            variant="secondary",
            width=80
        )
        self.edit_button.pack(side="left", padx=(0, tokens.spacing["sm"]))
        self.edit_button.set_state(ComponentState.DISABLED)
        
        self.delete_button = ModernButton(
            action_frame,
            text="Delete",
            command=self._delete_rule,
            variant="danger",
            width=80
        )
        self.delete_button.pack(side="left", padx=(0, tokens.spacing["sm"]))
        self.delete_button.set_state(ComponentState.DISABLED)
        
        self.validate_button = ModernButton(
            action_frame,
            text="Validate",
            command=self._validate_rule,
            variant="secondary",
            width=80
        )
        self.validate_button.pack(side="left", padx=(0, tokens.spacing["sm"]))
        self.validate_button.set_state(ComponentState.DISABLED)
        
        self.execute_button = ModernButton(
            action_frame,
            text="Execute",
            command=self._execute_rule,
            variant="primary",
            width=80
        )
        self.execute_button.pack(side="left")
        self.execute_button.set_state(ComponentState.DISABLED)
        
        return toolbar_frame
    
    def _create_rules_list(self, parent: tk.Widget) -> tk.Frame:
        """Create rules list with tree view."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Tree frame
        tree_frame = tk.Frame(parent, bg=tokens.colors["background"])
        
        # Tree columns
        columns = ("name", "status", "priority", "pattern", "validation", "last_execution")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            style="Modern.Treeview"
        )
        
        # Configure columns
        self.tree.heading("name", text="Rule Name")
        self.tree.heading("status", text="Status")
        self.tree.heading("priority", text="Priority")
        self.tree.heading("pattern", text="Pattern")
        self.tree.heading("validation", text="Validation")
        self.tree.heading("last_execution", text="Last Execution")
        
        self.tree.column("name", width=200, minwidth=150)
        self.tree.column("status", width=80, minwidth=60)
        self.tree.column("priority", width=80, minwidth=60)
        self.tree.column("pattern", width=120, minwidth=100)
        self.tree.column("validation", width=100, minwidth=80)
        self.tree.column("last_execution", width=150, minwidth=120)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack tree and scrollbars
        self.tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Bind events
        self.tree.bind("<<TreeviewSelect>>", self._on_rule_selected)
        self.tree.bind("<Double-1>", self._on_rule_double_click)
        
        return tree_frame
    
    def _refresh_rules(self):
        """Refresh rules list from backend."""
        try:
            # Get rules from backend
            rules = self.rule_service.list_rules(active_only=False)
            
            # Create display info for each rule
            self.rules_data = []
            for rule in rules:
                # Get validation status
                try:
                    # Get rule to pass to validation
                    rule_for_validation = self.rule_service.get_rule(rule.id)
                    if rule_for_validation:
                        validation = self.rule_service.validate_rule(rule_for_validation)
                        status = "Valid" if validation.is_valid else "Invalid"
                    else:
                        status = "Not Found"
                except Exception:
                    status = "Unknown"
                
                self.rules_data.append(RuleDisplayInfo(
                    rule=rule,
                    pattern_name="",  # Will be populated when pattern integration is complete
                    validation_status=status,
                    last_execution=rule.last_executed,
                    execution_count=rule.execution_count
                ))
            
            self._update_tree()
            self._update_stats()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load rules:\n{e}")
    
    def _update_tree(self):
        """Update tree view with current rules data."""
        if not hasattr(self, 'tree'):
            return
            
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filter rules based on current filters
        filtered_rules = self._filter_rules()
        
        # Add filtered rules to tree
        for rule_info in filtered_rules:
            rule = rule_info.rule
            
            # Format last execution
            last_exec = ""
            if rule_info.last_execution:
                last_exec = rule_info.last_execution.strftime("%Y-%m-%d %H:%M")
            
            self.tree.insert("", "end", values=(
                rule.name,
                "Enabled" if rule.is_enabled else "Disabled",
                rule.priority,
                f"Pattern {str(rule.pattern_id)[:8]}...",
                rule_info.validation_status,
                last_exec
            ), tags=(str(rule.id),))
    
    def _filter_rules(self) -> List[RuleDisplayInfo]:
        """Filter rules based on current filter settings."""
        filtered = []
        
        for rule_info in self.rules_data:
            rule = rule_info.rule
            
            # Filter by active/inactive status
            if not self.show_inactive and not rule.is_enabled:
                continue
            
            # Filter by search text
            if self.filter_text:
                search_text = self.filter_text.lower()
                if (search_text not in rule.name.lower() and 
                    search_text not in rule.description.lower()):
                    continue
            
            filtered.append(rule_info)
        
        return filtered
    
    def _update_stats(self):
        """Update statistics display."""
        if not hasattr(self, 'stats_label'):
            return
            
        total_rules = len(self.rules_data)
        active_rules = sum(1 for r in self.rules_data if r.rule.is_enabled)
        
        stats_text = f"{total_rules} rules total, {active_rules} active"
        self.stats_label.configure(text=stats_text)
    
    def _on_search_changed(self, *args):
        """Handle search text change."""
        self.filter_text = self.search_var.get()
        self._update_tree()
    
    def _on_filter_changed(self, *args):
        """Handle filter settings change."""
        self.show_inactive = self.show_inactive_var.get()
        self._update_tree()
    
    def _on_rule_selected(self, event):
        """Handle rule selection."""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            tags = self.tree.item(item, "tags")
            if tags:
                rule_id = UUID(tags[0])
                self.selected_rule_id = rule_id
                
                # Enable action buttons
                self.edit_button.set_state(ComponentState.DEFAULT)
                self.delete_button.set_state(ComponentState.DEFAULT)
                self.validate_button.set_state(ComponentState.DEFAULT)
                self.execute_button.set_state(ComponentState.DEFAULT)
        else:
            self.selected_rule_id = None
            
            # Disable action buttons
            self.edit_button.set_state(ComponentState.DISABLED)
            self.delete_button.set_state(ComponentState.DISABLED)
            self.validate_button.set_state(ComponentState.DISABLED)
            self.execute_button.set_state(ComponentState.DISABLED)
    
    def _on_rule_double_click(self, event):
        """Handle double-click on rule."""
        self._edit_rule()
    
    def _create_rule(self):
        """Open rule creation wizard."""
        wizard = RuleCreationWizard(
            self,
            self.rule_service,
            self.pattern_service
        )
        wizard.wait_window()
        
        if wizard.result:
            self._refresh_rules()
    
    def _edit_rule(self):
        """Edit selected rule."""
        if not self.selected_rule_id:
            return
        
        try:
            rule = self.rule_service.get_rule(self.selected_rule_id)
            if not rule:
                messagebox.showerror("Error", "Rule not found.")
                return
            
            editor = RuleEditor(self, rule)
            editor.wait_window()
            
            if editor.result:
                # Update rule in backend
                self.rule_service.update_rule(editor.result)
                self._refresh_rules()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit rule:\n{e}")
    
    def _delete_rule(self):
        """Delete selected rule."""
        if not self.selected_rule_id:
            return
        
        try:
            rule = self.rule_service.get_rule(self.selected_rule_id)
            if not rule:
                messagebox.showerror("Error", "Rule not found.")
                return
            
            # Confirm deletion
            dialog = ConfirmationDialog(
                self,
                title="Confirm Deletion",
                message=f"Are you sure you want to delete the rule '{rule.name}'?\n\nThis action cannot be undone.",
                icon="🗑️"
            )
            
            if dialog.show():
                self.rule_service.delete_rule(self.selected_rule_id)
                self._refresh_rules()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete rule:\n{e}")
    
    def _validate_rule(self, rule_id: UUID):
        """Validate selected rule."""
        try:
            rule = self.rule_service.get_rule(rule_id)
            if not rule:
                messagebox.showerror("Error", "Rule not found.")
                return
                
            validation = self.rule_service.validate_rule(rule)
            
            if validation.is_valid:
                messagebox.showinfo("Validation", "Rule is valid and ready to execute.")
            else:
                errors = "\n".join(validation.errors)
                messagebox.showwarning("Validation", f"Rule has validation errors:\n\n{errors}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Validation failed:\n{e}")
    
    def _execute_rule(self):
        """Execute selected rule."""
        if not self.selected_rule_id:
            return
        
        # Open execution dialog
        dialog = RuleExecutionDialog(
            self,
            self.rule_service,
            self.selected_rule_id
        )
        dialog.wait_window()
        
        # Refresh to show updated execution statistics
        self._refresh_rules()


class RuleEditor(ModernDialog):
    """Dialog for editing rules."""
    
    def __init__(self, parent: tk.Widget, rule: Rule, **kwargs):
        self.rule = rule
        super().__init__(parent, title=f"Edit Rule: {rule.name}", size=(600, 400), **kwargs)
    
    def _create_dialog_content(self):
        """Create rule editor dialog content."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Main frame
        main_frame = tk.Frame(self.dialog_window, bg=tokens.colors["background"])
        main_frame.pack(fill="both", expand=True, padx=tokens.spacing["lg"], pady=tokens.spacing["lg"])
        
        # Rule name
        name_frame = tk.Frame(main_frame, bg=tokens.colors["background"])
        name_frame.pack(fill="x", pady=(0, tokens.spacing["md"]))
        
        tk.Label(
            name_frame,
            text="Rule Name:",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(anchor="w", pady=(0, tokens.spacing["xs"]))
        
        self.name_var = tk.StringVar(value=self.rule.name)
        name_entry = ModernEntry(
            name_frame,
            textvariable=self.name_var,
            placeholder="Enter rule name..."
        )
        name_entry.pack(fill="x")
        
        # Description
        desc_frame = tk.Frame(main_frame, bg=tokens.colors["background"])
        desc_frame.pack(fill="x", pady=(0, tokens.spacing["md"]))
        
        tk.Label(
            desc_frame,
            text="Description:",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(anchor="w", pady=(0, tokens.spacing["xs"]))
        
        self.description_text = tk.Text(
            desc_frame,
            height=4,
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_normal"]),
            bg="white",
            fg=tokens.colors["text"],
            relief="solid",
            bd=1,
            wrap="word"
        )
        self.description_text.pack(fill="x")
        self.description_text.insert("1.0", self.rule.description)
        
        # Destination
        dest_frame = tk.Frame(main_frame, bg=tokens.colors["background"])
        dest_frame.pack(fill="x", pady=(0, tokens.spacing["md"]))
        
        tk.Label(
            dest_frame,
            text="Destination:",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(anchor="w", pady=(0, tokens.spacing["xs"]))
        
        self.dest_var = tk.StringVar(value=str(self.rule.destination_path))
        dest_entry = ModernEntry(
            dest_frame,
            textvariable=self.dest_var,
            placeholder="Enter destination path..."
        )
        dest_entry.pack(fill="x")
        
        # Priority and enabled
        settings_frame = tk.Frame(main_frame, bg=tokens.colors["background"])
        settings_frame.pack(fill="x", pady=(0, tokens.spacing["lg"]))
        
        # Priority
        tk.Label(
            settings_frame,
            text="Priority:",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(side="left", padx=(0, tokens.spacing["sm"]))
        
        self.priority_var = tk.IntVar(value=self.rule.priority)
        priority_spin = tk.Spinbox(
            settings_frame,
            from_=0,
            to=100,
            textvariable=self.priority_var,
            width=5
        )
        priority_spin.pack(side="left", padx=(0, tokens.spacing["lg"]))
        
        # Enabled checkbox
        self.enabled_var = tk.BooleanVar(value=self.rule.is_enabled)
        enabled_cb = tk.Checkbutton(
            settings_frame,
            text="Rule is enabled",
            variable=self.enabled_var,
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_normal"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"],
            selectcolor=tokens.colors["background"],
            activebackground=tokens.colors["background"],
            activeforeground=tokens.colors["text"]
        )
        enabled_cb.pack(side="left")
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg=tokens.colors["background"])
        button_frame.pack(fill="x")
        
        cancel_btn = ModernButton(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            variant="secondary",
            width=100
        )
        cancel_btn.pack(side="right", padx=(tokens.spacing["sm"], 0))
        
        save_btn = ModernButton(
            button_frame,
            text="Save",
            command=self._on_save,
            variant="primary",
            width=100
        )
        save_btn.pack(side="right")
    
    def _on_save(self):
        """Handle save action."""
        # Update rule with new values
        self.rule.name = self.name_var.get()
        self.rule.description = self.description_text.get("1.0", "end-1c").strip()
        self.rule.destination_path = Path(self.dest_var.get())
        self.rule.priority = self.priority_var.get()
        self.rule.is_enabled = self.enabled_var.get()
        
        self.result = self.rule
        self.dialog_window.destroy()
    
    def _on_cancel(self):
        """Handle cancel action."""
        self.result = None
        self.dialog_window.destroy()


class RuleExecutionDialog(ModernDialog):
    """Dialog for executing rules with progress tracking."""
    
    def __init__(self, parent: tk.Widget, rule_service: RuleService, rule_id: UUID, **kwargs):
        self.rule_service = rule_service
        self.rule_id = rule_id
        self.execution_result = None
        
        # Get rule info
        rule = rule_service.get_rule(rule_id)
        title = f"Execute Rule: {rule.name}" if rule else "Execute Rule"
        
        super().__init__(parent, title=title, size=(600, 500), **kwargs)
    
    def _create_dialog_content(self):
        """Create rule execution dialog content."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Main frame
        main_frame = tk.Frame(self.dialog_window, bg=tokens.colors["background"])
        main_frame.pack(fill="both", expand=True, padx=tokens.spacing["lg"], pady=tokens.spacing["lg"])
        
        # Rule info
        rule = self.rule_service.get_rule(self.rule_id)
        if rule:
            info_frame = tk.Frame(main_frame, bg=tokens.colors["background"])
            info_frame.pack(fill="x", pady=(0, tokens.spacing["lg"]))
            
            tk.Label(
                info_frame,
                text=f"Rule: {rule.name}",
                font=(tokens.fonts["family"], int(tokens.fonts["size_heading_2"]), tokens.fonts["weight_semibold"]),
                bg=tokens.colors["background"],
                fg=tokens.colors["text"]
            ).pack(anchor="w")
            
            tk.Label(
                info_frame,
                text=f"Destination: {rule.destination_path}",
                font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_normal"]),
                bg=tokens.colors["background"],
                fg=tokens.colors["text_secondary"]
            ).pack(anchor="w")
        
        # Source directory selection
        source_frame = tk.Frame(main_frame, bg=tokens.colors["background"])
        source_frame.pack(fill="x", pady=(0, tokens.spacing["lg"]))
        
        tk.Label(
            source_frame,
            text="Source Directory:",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(anchor="w", pady=(0, tokens.spacing["xs"]))
        
        path_frame = tk.Frame(source_frame, bg=tokens.colors["background"])
        path_frame.pack(fill="x")
        
        self.source_var = tk.StringVar()
        source_entry = ModernEntry(
            path_frame,
            textvariable=self.source_var,
            placeholder="Select source directory..."
        )
        source_entry.pack(side="left", fill="x", expand=True, padx=(0, tokens.spacing["sm"]))
        
        browse_btn = ModernButton(
            path_frame,
            text="Browse...",
            command=self._browse_source,
            variant="secondary",
            width=80
        )
        browse_btn.pack(side="right")
        
        # Options
        options_frame = tk.Frame(main_frame, bg=tokens.colors["background"])
        options_frame.pack(fill="x", pady=(0, tokens.spacing["lg"]))
        
        self.dry_run_var = tk.BooleanVar(value=True)
        dry_run_cb = tk.Checkbutton(
            options_frame,
            text="Dry run (preview only, don't move files)",
            variable=self.dry_run_var,
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_normal"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"],
            selectcolor=tokens.colors["background"],
            activebackground=tokens.colors["background"],
            activeforeground=tokens.colors["text"]
        )
        dry_run_cb.pack(anchor="w")
        
        # Progress area
        self.progress_frame = tk.Frame(main_frame, bg=tokens.colors["background"])
        self.progress_frame.pack(fill="both", expand=True, pady=(0, tokens.spacing["lg"]))
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg=tokens.colors["background"])
        button_frame.pack(fill="x")
        
        cancel_btn = ModernButton(
            button_frame,
            text="Close",
            command=self._on_cancel,
            variant="secondary",
            width=100
        )
        cancel_btn.pack(side="right", padx=(tokens.spacing["sm"], 0))
        
        self.execute_button = ModernButton(
            button_frame,
            text="Execute",
            command=self._execute_rule,
            variant="primary",
            width=100
        )
        self.execute_button.pack(side="right")
    
    def _browse_source(self):
        """Browse for source directory."""
        directory = filedialog.askdirectory(title="Select Source Directory")
        if directory:
            self.source_var.set(directory)
    
    def _execute_rule(self):
        """Execute the rule."""
        source_path = self.source_var.get().strip()
        if not source_path:
            messagebox.showerror("Error", "Please select a source directory.")
            return
        
        if not Path(source_path).exists():
            messagebox.showerror("Error", "Source directory does not exist.")
            return
        
        # Disable execute button
        self.execute_button.set_state(ComponentState.DISABLED)
        
        # Clear progress area
        for widget in self.progress_frame.winfo_children():
            widget.destroy()
        
        try:
            # Show progress
            progress_label = tk.Label(
                self.progress_frame,
                text="Executing rule...",
                font=(get_theme_manager().get_current_tokens().fonts["family"], 
                      int(get_theme_manager().get_current_tokens().fonts["size_body"]), 
                      get_theme_manager().get_current_tokens().fonts["weight_normal"]),
                bg=get_theme_manager().get_current_tokens().colors["background"],
                fg=get_theme_manager().get_current_tokens().colors["text"]
            )
            progress_label.pack(pady=get_theme_manager().get_current_tokens().spacing["md"])
            
            # Execute rule
            result = self.rule_service.execute_rule(
                rule_id=self.rule_id,
                source_directory=Path(source_path),
                dry_run=self.dry_run_var.get()
            )
            
            self._show_execution_results(result)
            
        except Exception as e:
            self._show_execution_error(e)
    
    def _show_execution_results(self, result: RuleExecutionResult):
        """Show execution results."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Clear progress area
        for widget in self.progress_frame.winfo_children():
            widget.destroy()
        
        # Show results
        results_text = (
            f"Execution completed!\n\n"
            f"Files matched: {result.files_matched}\n"
            f"Files {'would be moved' if result.dry_run else 'moved'}: {result.files_moved}\n"
            f"Files failed: {result.files_failed}\n"
            f"Execution time: {result.execution_time_ms:.2f}ms\n"
            f"Status: {result.status.value}"
        )
        
        if result.errors:
            results_text += f"\n\nErrors:\n" + "\n".join(
                f"• {error}" for error in result.errors
            )
        
        result_label = tk.Label(
            self.progress_frame,
            text=results_text,
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"])),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"],
            justify="left"
        )
        result_label.pack(fill="both", expand=True, pady=tokens.spacing["lg"])
        
        # Store result and re-enable execute
        self.execution_result = result
        self.execute_button.set_state(ComponentState.DEFAULT)
        self.execute_button.button.configure(text="Execute Again")
    
    def _show_execution_error(self, error: Exception):
        """Show execution error."""
        # Stop progress - no actual progress bar to stop in this implementation
        
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Clear progress area
        for widget in self.progress_frame.winfo_children():
            widget.destroy()
        
        # Show error
        error_label = tk.Label(
            self.progress_frame,
            text=f"Execution failed:\n\n{str(error)}",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"])),
            bg=tokens.colors["background"],
            fg=tokens.colors["error"],
            justify="left"
        )
        error_label.pack(pady=tokens.spacing["lg"])
        
        # Re-enable execute button
        self.execute_button.set_state(ComponentState.DEFAULT)
    
    def _on_cancel(self):
        """Handle cancel action."""
        self.result = self.execution_result
        self.dialog_window.destroy()




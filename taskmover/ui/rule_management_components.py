"""
Rule Management Components
=========================

Components for creating, editing, and managing file organization rules
with pattern matching, condition setting, and action configuration.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional, Any, List, Callable
from dataclasses import dataclass, field
import time
from .base_component import BaseComponent, ModernButton, ModernCard
from .theme_manager import get_theme_manager
from .input_components import ModernEntry, ModernCombobox, SmartPatternInput
from .dialog_components import ModernDialog, ConfirmationDialog


@dataclass
class Rule:
    """Data class representing a file organization rule."""
    id: str
    name: str
    description: str
    pattern: str
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    is_active: bool = True
    priority: int = 0
    tags: List[str] = field(default_factory=list)


class RuleConditionEditor(BaseComponent):
    """Editor for rule conditions."""
    
    def __init__(self, parent: tk.Widget, condition: Optional[Dict[str, Any]] = None, **kwargs):
        self.condition = condition or {"type": "file_size", "operator": "greater_than", "value": ""}
        self.condition_types = [
            "file_size", "file_age", "file_extension", "file_name", 
            "directory_depth", "file_count", "custom_pattern"
        ]
        self.operators = {
            "file_size": ["greater_than", "less_than", "equals", "between"],
            "file_age": ["older_than", "newer_than", "equals", "between"],
            "file_extension": ["is", "is_not", "contains", "matches"],
            "file_name": ["contains", "starts_with", "ends_with", "matches", "regex"],
            "directory_depth": ["greater_than", "less_than", "equals"],
            "file_count": ["greater_than", "less_than", "equals"],
            "custom_pattern": ["matches", "not_matches"]
        }
        
        super().__init__(parent, **kwargs)
    
    def _create_component(self):
        """Create condition editor component."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Configure main frame
        self.configure(bg=tokens.colors["background"], relief="solid", bd=1)
        
        # Main content frame
        content_frame = tk.Frame(self, bg=tokens.colors["background"])
        content_frame.pack(fill="both", expand=True, padx=tokens.spacing["md"], pady=tokens.spacing["md"])
        
        # Condition type selection
        type_frame = tk.Frame(content_frame, bg=tokens.colors["background"])
        type_frame.pack(fill="x", pady=(0, tokens.spacing["sm"]))
        
        tk.Label(
            type_frame,
            text="Condition Type:",
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(side="left", padx=(0, tokens.spacing["sm"]))
        
        self.type_var = tk.StringVar(value=self.condition.get("type", "file_size"))
        self.type_combo = ModernCombobox(
            type_frame,
            textvariable=self.type_var,
            values=self.condition_types,
            state="readonly",
            width=15
        )
        self.type_combo.pack(side="left")
        
        # Operator selection
        operator_frame = tk.Frame(content_frame, bg=tokens.colors["background"])
        operator_frame.pack(fill="x", pady=(0, tokens.spacing["sm"]))
        
        tk.Label(
            operator_frame,
            text="Operator:",
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(side="left", padx=(0, tokens.spacing["sm"]))
        
        self.operator_var = tk.StringVar(value=self.condition.get("operator", "greater_than"))
        self.operator_combo = ModernCombobox(
            operator_frame,
            textvariable=self.operator_var,
            values=self.operators.get(self.type_var.get(), []),
            state="readonly",
            width=15
        )
        self.operator_combo.pack(side="left")
        
        # Value input
        value_frame = tk.Frame(content_frame, bg=tokens.colors["background"])
        value_frame.pack(fill="x", pady=(0, tokens.spacing["sm"]))
        
        tk.Label(
            value_frame,
            text="Value:",
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(side="left", padx=(0, tokens.spacing["sm"]))
        
        self.value_var = tk.StringVar(value=str(self.condition.get("value", "")))
        self.value_entry = ModernEntry(
            value_frame,
            textvariable=self.value_var,
            width=20
        )
        self.value_entry.pack(side="left", fill="x", expand=True)
        
        # Bind events
        self.type_var.trace_add("write", self._on_type_changed)
    
    def _on_type_changed(self, *args):
        """Handle condition type change."""
        condition_type = self.type_var.get()
        operators = self.operators.get(condition_type, [])
        
        # Update operator combo
        self.operator_combo['values'] = operators
        if operators:
            self.operator_var.set(operators[0])
        
        # Clear value
        self.value_var.set("")
    
    def get_condition(self) -> Dict[str, Any]:
        """Get current condition configuration."""
        return {
            "type": self.type_var.get(),
            "operator": self.operator_var.get(),
            "value": self.value_var.get()
        }
    
    def set_condition(self, condition: Dict[str, Any]):
        """Set condition configuration."""
        self.condition = condition
        self.type_var.set(condition.get("type", "file_size"))
        self.operator_var.set(condition.get("operator", "greater_than"))
        self.value_var.set(str(condition.get("value", "")))


class RuleActionEditor(BaseComponent):
    """Editor for rule actions."""
    
    def __init__(self, parent: tk.Widget, action: Optional[Dict[str, Any]] = None, **kwargs):
        self.action = action or {"type": "move", "target": "", "create_folder": True}
        self.action_types = [
            "move", "copy", "delete", "rename", "organize_by_date", 
            "organize_by_type", "create_folder", "run_command"
        ]
        
        super().__init__(parent, **kwargs)
    
    def _create_component(self):
        """Create action editor component."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Configure main frame
        self.configure(bg=tokens.colors["background"], relief="solid", bd=1)
        
        # Main content frame
        content_frame = tk.Frame(self, bg=tokens.colors["background"])
        content_frame.pack(fill="both", expand=True, padx=tokens.spacing["md"], pady=tokens.spacing["md"])
        
        # Action type selection
        type_frame = tk.Frame(content_frame, bg=tokens.colors["background"])
        type_frame.pack(fill="x", pady=(0, tokens.spacing["sm"]))
        
        tk.Label(
            type_frame,
            text="Action Type:",
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(side="left", padx=(0, tokens.spacing["sm"]))
        
        self.type_var = tk.StringVar(value=self.action.get("type", "move"))
        self.type_combo = ModernCombobox(
            type_frame,
            textvariable=self.type_var,
            values=self.action_types,
            state="readonly",
            width=15
        )
        self.type_combo.pack(side="left")
        
        # Target/parameter input
        target_frame = tk.Frame(content_frame, bg=tokens.colors["background"])
        target_frame.pack(fill="x", pady=(0, tokens.spacing["sm"]))
        
        tk.Label(
            target_frame,
            text="Target/Parameter:",
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(side="left", padx=(0, tokens.spacing["sm"]))
        
        self.target_var = tk.StringVar(value=self.action.get("target", ""))
        self.target_entry = ModernEntry(
            target_frame,
            textvariable=self.target_var,
            placeholder="Enter target path or parameter..."
        )
        self.target_entry.pack(side="left", fill="x", expand=True)
        
        # Options
        options_frame = tk.Frame(content_frame, bg=tokens.colors["background"])
        options_frame.pack(fill="x")
        
        self.create_folder_var = tk.BooleanVar(value=self.action.get("create_folder", True))
        create_folder_cb = tk.Checkbutton(
            options_frame,
            text="Create target folder if it doesn't exist",
            variable=self.create_folder_var,
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), tokens.fonts["weight_normal"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"],
            selectcolor=tokens.colors["background"],
            activebackground=tokens.colors["background"],
            activeforeground=tokens.colors["text"]
        )
        create_folder_cb.pack(anchor="w")
        
        self.preserve_structure_var = tk.BooleanVar(value=self.action.get("preserve_structure", False))
        preserve_structure_cb = tk.Checkbutton(
            options_frame,
            text="Preserve directory structure",
            variable=self.preserve_structure_var,
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), tokens.fonts["weight_normal"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"],
            selectcolor=tokens.colors["background"],
            activebackground=tokens.colors["background"],
            activeforeground=tokens.colors["text"]
        )
        preserve_structure_cb.pack(anchor="w")
    
    def get_action(self) -> Dict[str, Any]:
        """Get current action configuration."""
        return {
            "type": self.type_var.get(),
            "target": self.target_var.get(),
            "create_folder": self.create_folder_var.get(),
            "preserve_structure": self.preserve_structure_var.get()
        }
    
    def set_action(self, action: Dict[str, Any]):
        """Set action configuration."""
        self.action = action
        self.type_var.set(action.get("type", "move"))
        self.target_var.set(action.get("target", ""))
        self.create_folder_var.set(action.get("create_folder", True))
        self.preserve_structure_var.set(action.get("preserve_structure", False))


class RuleEditor(ModernDialog):
    """Dialog for creating and editing rules."""
    
    def __init__(self, parent: tk.Widget, rule: Optional[Rule] = None, **kwargs):
        self.rule = rule
        self.is_editing = rule is not None
        self.condition_editors: List[RuleConditionEditor] = []
        self.action_editors: List[RuleActionEditor] = []
        
        title = "Edit Rule" if self.is_editing else "Create New Rule"
        super().__init__(parent, title, **kwargs)
    
    def _create_dialog_content(self):
        """Create rule editor dialog content."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Configure dialog size
        self.dialog_window.geometry("800x600")
        
        # Main frame with scrollbar
        main_frame = tk.Frame(self.dialog_window, bg=tokens.colors["background"])
        main_frame.pack(fill="both", expand=True, padx=tokens.spacing["lg"], pady=tokens.spacing["lg"])
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(main_frame, style="Modern.TNotebook")
        self.notebook.pack(fill="both", expand=True, pady=(0, tokens.spacing["lg"]))
        
        # Basic info tab
        self._create_basic_info_tab()
        
        # Pattern tab
        self._create_pattern_tab()
        
        # Conditions tab
        self._create_conditions_tab()
        
        # Actions tab
        self._create_actions_tab()
        
        # Advanced tab
        self._create_advanced_tab()
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg=tokens.colors["background"])
        button_frame.pack(fill="x")
        
        # Buttons
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
            text="Save Rule",
            command=self._on_save,
            variant="primary",
            width=100
        )
        save_btn.pack(side="right")
        
        # Load existing rule data if editing
        if self.is_editing and self.rule:
            self._load_rule_data()
    
    def _create_basic_info_tab(self):
        """Create basic information tab."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        basic_frame = tk.Frame(self.notebook, bg=tokens.colors["background"])
        self.notebook.add(basic_frame, text="Basic Info")
        
        # Rule name
        name_frame = tk.Frame(basic_frame, bg=tokens.colors["background"])
        name_frame.pack(fill="x", padx=tokens.spacing["lg"], pady=(tokens.spacing["lg"], tokens.spacing["md"]))
        
        tk.Label(
            name_frame,
            text="Rule Name:",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(anchor="w", pady=(0, tokens.spacing["xs"]))
        
        self.name_var = tk.StringVar()
        self.name_entry = ModernEntry(
            name_frame,
            textvariable=self.name_var,
            placeholder="Enter rule name..."
        )
        self.name_entry.pack(fill="x")
        
        # Rule description
        desc_frame = tk.Frame(basic_frame, bg=tokens.colors["background"])
        desc_frame.pack(fill="x", padx=tokens.spacing["lg"], pady=(0, tokens.spacing["md"]))
        
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
        
        # Rule status and priority
        status_frame = tk.Frame(basic_frame, bg=tokens.colors["background"])
        status_frame.pack(fill="x", padx=tokens.spacing["lg"], pady=(0, tokens.spacing["md"]))
        
        # Active checkbox
        self.active_var = tk.BooleanVar(value=True)
        active_cb = tk.Checkbutton(
            status_frame,
            text="Rule is active",
            variable=self.active_var,
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_normal"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"],
            selectcolor=tokens.colors["background"],
            activebackground=tokens.colors["background"],
            activeforeground=tokens.colors["text"]
        )
        active_cb.pack(side="left")
        
        # Priority
        tk.Label(
            status_frame,
            text="Priority:",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(side="right", padx=(tokens.spacing["xl"], tokens.spacing["sm"]))
        
        self.priority_var = tk.StringVar(value="0")
        priority_spin = tk.Spinbox(
            status_frame,
            from_=0,
            to=100,
            textvariable=self.priority_var,
            width=5,
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_normal"])
        )
        priority_spin.pack(side="right")
        
        # Tags
        tags_frame = tk.Frame(basic_frame, bg=tokens.colors["background"])
        tags_frame.pack(fill="x", padx=tokens.spacing["lg"], pady=(0, tokens.spacing["md"]))
        
        tk.Label(
            tags_frame,
            text="Tags (comma-separated):",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(anchor="w", pady=(0, tokens.spacing["xs"]))
        
        self.tags_var = tk.StringVar()
        self.tags_entry = ModernEntry(
            tags_frame,
            textvariable=self.tags_var,
            placeholder="e.g., media, documents, cleanup..."
        )
        self.tags_entry.pack(fill="x")
    
    def _create_pattern_tab(self):
        """Create pattern matching tab."""
        pattern_frame = tk.Frame(self.notebook, bg=get_theme_manager().get_current_tokens().colors["background"])
        self.notebook.add(pattern_frame, text="Pattern")
        
        # Pattern input
        self.pattern_input = SmartPatternInput(
            pattern_frame,
            show_checkboxes=True,
            allow_multiple=False
        )
        self.pattern_input.pack(fill="x", padx=20, pady=20)
    
    def _create_conditions_tab(self):
        """Create conditions tab."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        conditions_frame = tk.Frame(self.notebook, bg=tokens.colors["background"])
        self.notebook.add(conditions_frame, text="Conditions")
        
        # Header
        header_frame = tk.Frame(conditions_frame, bg=tokens.colors["background"])
        header_frame.pack(fill="x", padx=tokens.spacing["lg"], pady=(tokens.spacing["lg"], tokens.spacing["md"]))
        
        tk.Label(
            header_frame,
            text="Rule Conditions",
            font=(tokens.fonts["family"], int(tokens.fonts["size_heading_2"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(side="left")
        
        add_condition_btn = ModernButton(
            header_frame,
            text="+ Add Condition",
            command=self._add_condition,
            variant="secondary",
            width=120
        )
        add_condition_btn.pack(side="right")
        
        # Conditions container
        self.conditions_container = tk.Frame(conditions_frame, bg=tokens.colors["background"])
        self.conditions_container.pack(fill="both", expand=True, padx=tokens.spacing["lg"], pady=(0, tokens.spacing["lg"]))
    
    def _create_actions_tab(self):
        """Create actions tab."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        actions_frame = tk.Frame(self.notebook, bg=tokens.colors["background"])
        self.notebook.add(actions_frame, text="Actions")
        
        # Header
        header_frame = tk.Frame(actions_frame, bg=tokens.colors["background"])
        header_frame.pack(fill="x", padx=tokens.spacing["lg"], pady=(tokens.spacing["lg"], tokens.spacing["md"]))
        
        tk.Label(
            header_frame,
            text="Rule Actions",
            font=(tokens.fonts["family"], int(tokens.fonts["size_heading_2"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(side="left")
        
        add_action_btn = ModernButton(
            header_frame,
            text="+ Add Action",
            command=self._add_action,
            variant="secondary",
            width=120
        )
        add_action_btn.pack(side="right")
        
        # Actions container
        self.actions_container = tk.Frame(actions_frame, bg=tokens.colors["background"])
        self.actions_container.pack(fill="both", expand=True, padx=tokens.spacing["lg"], pady=(0, tokens.spacing["lg"]))
    
    def _create_advanced_tab(self):
        """Create advanced options tab."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        advanced_frame = tk.Frame(self.notebook, bg=tokens.colors["background"])
        self.notebook.add(advanced_frame, text="Advanced")
        
        # Advanced options would go here
        placeholder_label = tk.Label(
            advanced_frame,
            text="Advanced Options\\n(Coming soon)",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_normal"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text_secondary"]
        )
        placeholder_label.pack(expand=True)
    
    def _add_condition(self):
        """Add new condition editor."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Create condition editor frame
        condition_frame = tk.Frame(self.conditions_container, bg=tokens.colors["background"])
        condition_frame.pack(fill="x", pady=(0, tokens.spacing["md"]))
        
        # Create condition editor
        condition_editor = RuleConditionEditor(condition_frame)
        condition_editor.pack(side="left", fill="x", expand=True)
        
        # Remove button
        remove_btn = ModernButton(
            condition_frame,
            text="Remove",
            command=lambda: self._remove_condition(condition_frame, condition_editor),
            variant="danger",
            width=80
        )
        remove_btn.pack(side="right", padx=(tokens.spacing["sm"], 0))
        
        self.condition_editors.append(condition_editor)
    
    def _add_action(self):
        """Add new action editor."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Create action editor frame
        action_frame = tk.Frame(self.actions_container, bg=tokens.colors["background"])
        action_frame.pack(fill="x", pady=(0, tokens.spacing["md"]))
        
        # Create action editor
        action_editor = RuleActionEditor(action_frame)
        action_editor.pack(side="left", fill="x", expand=True)
        
        # Remove button
        remove_btn = ModernButton(
            action_frame,
            text="Remove",
            command=lambda: self._remove_action(action_frame, action_editor),
            variant="danger",
            width=80
        )
        remove_btn.pack(side="right", padx=(tokens.spacing["sm"], 0))
        
        self.action_editors.append(action_editor)
    
    def _remove_condition(self, frame: tk.Widget, editor: RuleConditionEditor):
        """Remove condition editor."""
        if editor in self.condition_editors:
            self.condition_editors.remove(editor)
        frame.destroy()
    
    def _remove_action(self, frame: tk.Widget, editor: RuleActionEditor):
        """Remove action editor."""
        if editor in self.action_editors:
            self.action_editors.remove(editor)
        frame.destroy()
    
    def _load_rule_data(self):
        """Load existing rule data into editor."""
        if not self.rule:
            return
        
        # Basic info
        self.name_var.set(self.rule.name)
        self.description_text.insert("1.0", self.rule.description)
        self.active_var.set(self.rule.is_active)
        self.priority_var.set(str(self.rule.priority))
        self.tags_var.set(", ".join(self.rule.tags))
        
        # Pattern
        if hasattr(self, 'pattern_input'):
            self.pattern_input.set_pattern(self.rule.pattern)
        
        # Conditions
        for condition in self.rule.conditions:
            self._add_condition()
            if self.condition_editors:
                self.condition_editors[-1].set_condition(condition)
        
        # Actions
        for action in self.rule.actions:
            self._add_action()
            if self.action_editors:
                self.action_editors[-1].set_action(action)
    
    def _on_save(self):
        """Handle save button click."""
        # Validate inputs
        if not self.name_var.get().strip():
            messagebox.showerror("Validation Error", "Rule name is required")
            return
        
        # Create rule object
        rule = Rule(
            id=self.rule.id if self.rule else f"rule_{int(time.time())}",
            name=self.name_var.get().strip(),
            description=self.description_text.get("1.0", "end-1c").strip(),
            pattern=self.pattern_input.get_pattern() if hasattr(self, 'pattern_input') else "",
            conditions=[editor.get_condition() for editor in self.condition_editors],
            actions=[editor.get_action() for editor in self.action_editors],
            is_active=self.active_var.get(),
            priority=int(self.priority_var.get()),
            tags=[tag.strip() for tag in self.tags_var.get().split(",") if tag.strip()]
        )
        
        self.result = rule
        self.dialog_window.destroy()
    
    def _on_cancel(self):
        """Handle cancel button click."""
        self.result = None
        self.dialog_window.destroy()


class RuleList(BaseComponent):
    """Component for displaying and managing rules list."""
    
    def __init__(self, parent: tk.Widget, **kwargs):
        self.rules: List[Rule] = []
        self.selected_rule: Optional[Rule] = None
        self.tree: Optional[ttk.Treeview] = None
        self.callbacks: Dict[str, List[Callable]] = {
            "rule_selected": [],
            "rule_edited": [],
            "rule_deleted": []
        }
        
        super().__init__(parent, **kwargs)
    
    def _create_component(self):
        """Create rules list component."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Configure main frame
        self.configure(bg=tokens.colors["background"])
        
        # Header
        header_frame = tk.Frame(self, bg=tokens.colors["background"])
        header_frame.pack(fill="x", pady=(0, tokens.spacing["md"]))
        
        tk.Label(
            header_frame,
            text="Rules",
            font=(tokens.fonts["family"], int(tokens.fonts["size_heading_2"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(side="left")
        
        # Action buttons
        button_frame = tk.Frame(header_frame, bg=tokens.colors["background"])
        button_frame.pack(side="right")
        
        new_btn = ModernButton(
            button_frame,
            text="+ New Rule",
            command=self._create_new_rule,
            variant="primary",
            width=100
        )
        new_btn.pack(side="left", padx=(0, tokens.spacing["sm"]))
        
        edit_btn = ModernButton(
            button_frame,
            text="Edit",
            command=self._edit_selected_rule,
            variant="secondary",
            width=80
        )
        edit_btn.pack(side="left", padx=(0, tokens.spacing["sm"]))
        
        delete_btn = ModernButton(
            button_frame,
            text="Delete",
            command=self._delete_selected_rule,
            variant="danger",
            width=80
        )
        delete_btn.pack(side="left")
        
        # Rules tree
        tree_frame = tk.Frame(self, bg=tokens.colors["background"])
        tree_frame.pack(fill="both", expand=True)
        
        columns = ("name", "status", "priority", "pattern", "actions")
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
        self.tree.heading("actions", text="Actions")
        
        self.tree.column("name", width=200, minwidth=150)
        self.tree.column("status", width=80, minwidth=60)
        self.tree.column("priority", width=80, minwidth=60)
        self.tree.column("pattern", width=150, minwidth=100)
        self.tree.column("actions", width=100, minwidth=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack tree and scrollbars
        self.tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self._on_selection_changed)
        self.tree.bind("<Double-1>", self._on_double_click)
        
        # Load sample rules
        self._load_sample_rules()
    
    def _load_sample_rules(self):
        """Load sample rules for demonstration."""
        sample_rules = [
            Rule(
                id="rule_1",
                name="Organize Images",
                description="Move image files to organized folders by date",
                pattern="*.{jpg,jpeg,png,gif,bmp}",
                conditions=[{"type": "file_extension", "operator": "is", "value": "jpg,jpeg,png,gif,bmp"}],
                actions=[{"type": "organize_by_date", "target": "Pictures", "create_folder": True}],
                is_active=True,
                priority=10,
                tags=["media", "images"]
            ),
            Rule(
                id="rule_2",
                name="Clean Downloads",
                description="Organize downloaded files by type",
                pattern="*",
                conditions=[{"type": "directory_depth", "operator": "equals", "value": "0"}],
                actions=[{"type": "organize_by_type", "target": "Organized", "create_folder": True}],
                is_active=True,
                priority=5,
                tags=["cleanup", "downloads"]
            ),
            Rule(
                id="rule_3",
                name="Archive Old Documents",
                description="Move old documents to archive",
                pattern="*.{pdf,doc,docx,txt}",
                conditions=[{"type": "file_age", "operator": "older_than", "value": "365"}],
                actions=[{"type": "move", "target": "Archive/Documents", "create_folder": True}],
                is_active=False,
                priority=1,
                tags=["documents", "archive"]
            )
        ]
        
        self.rules = sample_rules
        self._refresh_tree()
    
    def _refresh_tree(self):
        """Refresh tree view with current rules."""
        if not self.tree:
            return
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add rules
        for rule in self.rules:
            status = "Active" if rule.is_active else "Inactive"
            actions_text = f"{len(rule.actions)} action(s)"
            
            self.tree.insert("", "end", values=(
                rule.name,
                status,
                rule.priority,
                rule.pattern[:30] + "..." if len(rule.pattern) > 30 else rule.pattern,
                actions_text
            ), tags=(rule.id,))
    
    def _on_selection_changed(self, event):
        """Handle tree selection change."""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            tags = self.tree.item(item, "tags")
            if tags:
                rule_id = tags[0]
                self.selected_rule = next((r for r in self.rules if r.id == rule_id), None)
                
                # Notify callbacks
                for callback in self.callbacks["rule_selected"]:
                    callback(self.selected_rule)
    
    def _on_double_click(self, event):
        """Handle double-click on rule."""
        self._edit_selected_rule()
    
    def _create_new_rule(self):
        """Create new rule."""
        editor = RuleEditor(self)
        rule = editor.show()
        
        if rule:
            self.rules.append(rule)
            self._refresh_tree()
            
            # Notify callbacks
            for callback in self.callbacks["rule_edited"]:
                callback(rule)
    
    def _edit_selected_rule(self):
        """Edit selected rule."""
        if not self.selected_rule:
            messagebox.showwarning("No Selection", "Please select a rule to edit")
            return
        
        editor = RuleEditor(self, self.selected_rule)
        updated_rule = editor.show()
        
        if updated_rule:
            # Update rule in list
            for i, rule in enumerate(self.rules):
                if rule.id == updated_rule.id:
                    self.rules[i] = updated_rule
                    break
            
            self._refresh_tree()
            
            # Notify callbacks
            for callback in self.callbacks["rule_edited"]:
                callback(updated_rule)
    
    def _delete_selected_rule(self):
        """Delete selected rule."""
        if not self.selected_rule:
            messagebox.showwarning("No Selection", "Please select a rule to delete")
            return
        
        # Confirm deletion
        dialog = ConfirmationDialog(
            self,
            title="Confirm Deletion",
            message=f"Are you sure you want to delete the rule '{self.selected_rule.name}'?\\n\\nThis action cannot be undone.",
            icon="🗑️"
        )
        
        if dialog.show():
            # Remove rule
            self.rules = [r for r in self.rules if r.id != self.selected_rule.id]
            self.selected_rule = None
            self._refresh_tree()
            
            # Notify callbacks
            for callback in self.callbacks["rule_deleted"]:
                callback()
    
    def add_callback(self, event: str, callback: Callable):
        """Add callback for events."""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    def get_rules(self) -> List[Rule]:
        """Get all rules."""
        return self.rules
    
    def get_selected_rule(self) -> Optional[Rule]:
        """Get selected rule."""
        return self.selected_rule


class RuleManagementView(BaseComponent):
    """Complete rule management view."""
    
    def __init__(self, parent: tk.Widget, **kwargs):
        self.rule_list: Optional[RuleList] = None
        self.rule_details: Optional[tk.Frame] = None
        
        super().__init__(parent, **kwargs)
    
    def _create_component(self):
        """Create rule management view."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Configure main frame
        self.configure(bg=tokens.colors["background"])
        
        # Create paned window for list and details
        paned_window = ttk.PanedWindow(self, orient="horizontal", style="Modern.TPanedwindow")
        paned_window.pack(fill="both", expand=True, padx=tokens.spacing["lg"], pady=tokens.spacing["lg"])
        
        # Rules list
        list_frame = tk.Frame(paned_window, bg=tokens.colors["background"])
        paned_window.add(list_frame, weight=2)
        
        self.rule_list = RuleList(list_frame)
        self.rule_list.pack(fill="both", expand=True)
        
        # Rule details
        details_frame = tk.Frame(paned_window, bg=tokens.colors["background"])
        paned_window.add(details_frame, weight=1)
        
        self.rule_details = self._create_rule_details(details_frame)
        
        # Bind callbacks
        if self.rule_list:
            self.rule_list.add_callback("rule_selected", self._on_rule_selected)
    
    def _create_rule_details(self, parent: tk.Widget) -> tk.Frame:
        """Create rule details panel."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Details frame
        details_frame = tk.Frame(parent, bg=tokens.colors["background"])
        details_frame.pack(fill="both", expand=True, padx=(tokens.spacing["lg"], 0))
        
        # Title
        title_label = tk.Label(
            details_frame,
            text="Rule Details",
            font=(tokens.fonts["family"], int(tokens.fonts["size_heading_2"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        )
        title_label.pack(fill="x", pady=(0, tokens.spacing["lg"]))
        
        # Details content
        self.details_content = tk.Text(
            details_frame,
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_normal"]),
            bg="white",
            fg=tokens.colors["text"],
            relief="solid",
            bd=1,
            wrap="word",
            state="disabled"
        )
        self.details_content.pack(fill="both", expand=True)
        
        # Initially show placeholder
        self._show_placeholder()
        
        return details_frame
    
    def _show_placeholder(self):
        """Show placeholder text in details panel."""
        self.details_content.config(state="normal")
        self.details_content.delete("1.0", "end")
        self.details_content.insert("1.0", "Select a rule to view details")
        self.details_content.config(state="disabled")
    
    def _on_rule_selected(self, rule: Optional[Rule]):
        """Handle rule selection."""
        if not rule:
            self._show_placeholder()
            return
        
        # Format rule details
        details = f"Name: {rule.name}\\n\\n"
        details += f"Description: {rule.description}\\n\\n"
        details += f"Status: {'Active' if rule.is_active else 'Inactive'}\\n"
        details += f"Priority: {rule.priority}\\n\\n"
        details += f"Pattern: {rule.pattern}\\n\\n"
        
        if rule.conditions:
            details += "Conditions:\\n"
            for i, condition in enumerate(rule.conditions, 1):
                details += f"  {i}. {condition.get('type', '')} {condition.get('operator', '')} {condition.get('value', '')}\\n"
            details += "\\n"
        
        if rule.actions:
            details += "Actions:\\n"
            for i, action in enumerate(rule.actions, 1):
                details += f"  {i}. {action.get('type', '')} to {action.get('target', '')}\\n"
            details += "\\n"
        
        if rule.tags:
            details += f"Tags: {', '.join(rule.tags)}\\n"
        
        # Update details content
        self.details_content.config(state="normal")
        self.details_content.delete("1.0", "end")
        self.details_content.insert("1.0", details)
        self.details_content.config(state="disabled")

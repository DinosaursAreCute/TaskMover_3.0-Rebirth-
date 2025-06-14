"""
Pattern grid and editing UI logic for TaskMover rule management.
"""

import tkinter as tk
import ttkbootstrap as ttkb
from taskmover.config import save_rules

def pattern_grid_label(patterns_grid, rules, rule_key, show_pattern_edit):
    """
    Display patterns as labels in a responsive grid. Clicking a label switches to edit mode.
    """
    def layout_patterns(event=None):
        for w in patterns_grid.winfo_children():
            w.destroy()
        pattern_strs = rules[rule_key]['patterns']
        width = patterns_grid.winfo_width()
        if width <= 1:
            patterns_grid.after(10, layout_patterns)
            return
        pattern_pixel_width = 120
        max_per_row = max(1, width // pattern_pixel_width)
        for idx, pattern in enumerate(pattern_strs):
            row = idx // max_per_row
            col = idx % max_per_row
            label = ttkb.Label(patterns_grid, text=pattern, font=("Helvetica", 10), style="light.TLabel", cursor="hand2")
            label.grid(row=row, column=col, padx=2, pady=2, sticky="w")
            # Fix: capture current rule_key and pattern index in lambda
            label.bind("<Button-1>", lambda event, rk=rule_key: show_pattern_edit())
        if not pattern_strs:
            label = ttkb.Label(patterns_grid, text="<no patterns>", font=("Helvetica", 10), style="light.TLabel", cursor="hand2")
            label.grid(row=0, column=0, padx=2, pady=2, sticky="w")
            label.bind("<Button-1>", lambda event, rk=rule_key: show_pattern_edit())
    patterns_grid.bind("<Configure>", layout_patterns)
    layout_patterns()

def pattern_grid_edit(patterns_grid, rules, rule_key, config_path, logger, show_pattern_label):
    """
    Display patterns as editable entries in a responsive grid. Handles add, save, discard, and plus button.
    """
    patterns_grid.unbind("<Configure>")
    def layout_entries(event=None):
        for w in patterns_grid.winfo_children():
            w.destroy()
        width = patterns_grid.winfo_width()
        if width <= 1:
            patterns_grid.after(10, layout_entries)
            return
        entry_pixel_width = 120
        max_per_row = max(1, width // entry_pixel_width)
        pattern_vars = []
        entries = []
        new_vars = []
        plus_buttons = []
        def save_patterns(event=None):
            new_patterns = [v.get().strip() for v in pattern_vars if v.get().strip() and v.get().strip() != '<add pattern>']
            new_patterns += [v.get().strip() for v in new_vars if v.get().strip() and v.get().strip() != '<add pattern>']
            rules[rule_key]['patterns'] = new_patterns
            save_rules(config_path, rules)
            logger.info(f"Patterns for rule '{rule_key}' updated: {new_patterns}")
            patterns_grid.unbind("<Configure>")
            show_pattern_label()
        def discard_patterns(event=None):
            patterns_grid.unbind("<Configure>")
            show_pattern_label()
        # Existing patterns
        for idx, pattern in enumerate(rules[rule_key]['patterns']):
            row = idx // max_per_row
            col = idx % max_per_row
            var = tk.StringVar(value=pattern)
            entry = ttkb.Entry(patterns_grid, textvariable=var, width=15)
            entry.grid(row=row, column=col, padx=2, pady=2, sticky="w")
            entry.bind("<Return>", save_patterns)
            entry.bind("<Escape>", discard_patterns)
            pattern_vars.append(var)
            entries.append(entry)
        # Dynamic add pattern entry with plus button
        idx = len(rules[rule_key]['patterns'])
        row = idx // max_per_row
        col = idx % max_per_row
        new_var = tk.StringVar()
        new_vars.append(new_var)
        entry = ttkb.Entry(patterns_grid, textvariable=new_var, width=15)
        entry.grid(row=row, column=col, padx=2, pady=2, sticky="w")
        entry.insert(0, "<add pattern>")
        def clear_placeholder(event, v=new_var):
            if entry.get() == "<add pattern>":
                entry.delete(0, tk.END)
        entry.bind("<FocusIn>", clear_placeholder)
        entry.bind("<Return>", save_patterns)
        entry.bind("<Escape>", discard_patterns)
        entries.append(entry)
        def add_and_focus():
            # Add a new entry and re-layout
            rules[rule_key]['patterns'] += [v.get().strip() for v in new_vars if v.get().strip() and v.get().strip() != '<add pattern>']
            save_rules(config_path, rules)
            logger.info(f"Patterns for rule '{rule_key}' updated: {rules[rule_key]['patterns']}")
            layout_entries()
            # Focus the last Entry widget
            all_entries = patterns_grid.winfo_children()
            for widget in reversed(all_entries):
                if isinstance(widget, ttkb.Entry):
                    widget.focus_set()
                    widget.icursor(tk.END)
                    break
        plus_btn = ttkb.Button(patterns_grid, text="+", width=2, style="success.TButton", command=add_and_focus)
        plus_btn.grid(row=row, column=col+1, padx=(0, 6), pady=2, sticky="w")
        plus_buttons.append(plus_btn)
        if entries:
            entries[0].focus_set()
    patterns_grid.bind("<Configure>", layout_entries)
    layout_entries()

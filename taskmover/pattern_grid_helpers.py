"""
Pattern grid and editing UI logic for TaskMover rule management.
"""

import tkinter as tk
import ttkbootstrap as ttkb
from taskmover.config import save_rules
from typing import Any, Dict, Optional

def pattern_grid_label(patterns_grid, rules, rule_key, show_pattern_edit):
    """
    Display patterns as labels in a responsive grid. Clicking a label switches to edit mode.
    Debounced and only redraws if layout actually changes. Reuses widgets for performance.
    """
    redraw_after_id = [None]
    last_state: Dict[str, Any] = {'cols': None, 'patterns': None}
    widget_cache = []
    def do_layout_patterns():
        pattern_strs = rules[rule_key]['patterns']
        width = patterns_grid.winfo_width()
        if width <= 1:
            patterns_grid.after(10, do_layout_patterns)
            return
        pattern_pixel_width = 120
        max_per_row = max(1, width // pattern_pixel_width)
        # Only redraw if columns or patterns changed
        if last_state['cols'] == max_per_row and last_state['patterns'] == tuple(pattern_strs):
            redraw_after_id[0] = None
            return
        last_state['cols'] = max_per_row
        last_state['patterns'] = tuple(pattern_strs)
        # Reuse or create widgets as needed
        needed = len(pattern_strs) if pattern_strs else 1
        while len(widget_cache) < needed:
            label = ttkb.Label(patterns_grid, font=("Helvetica", 10), style="light.TLabel", cursor="hand2")
            widget_cache.append(label)
        for idx, label in enumerate(widget_cache):
            label.grid_remove()
        if pattern_strs:
            for idx, pattern in enumerate(pattern_strs):
                row = idx // max_per_row
                col = idx % max_per_row
                label = widget_cache[idx]
                label.config(text=pattern)
                label.grid(row=row, column=col, padx=2, pady=2, sticky="w")
                label.bind("<Button-1>", lambda event, rk=rule_key: show_pattern_edit())
        else:
            label = widget_cache[0]
            label.config(text="<no patterns>")
            label.grid(row=0, column=0, padx=2, pady=2, sticky="w")
            label.bind("<Button-1>", lambda event, rk=rule_key: show_pattern_edit())
        redraw_after_id[0] = None
    def layout_patterns(event=None):
        if redraw_after_id[0]:
            patterns_grid.after_cancel(redraw_after_id[0])
        redraw_after_id[0] = patterns_grid.after(80, do_layout_patterns)
    patterns_grid.bind("<Configure>", layout_patterns)
    # Ensure all previous widgets are removed before drawing labels
    for widget in patterns_grid.winfo_children():
        widget.grid_remove()
    do_layout_patterns()


def pattern_grid_edit(patterns_grid, rules, rule_key, config_path, logger, show_pattern_label):
    """
    Display patterns as editable entries in a responsive grid. Handles add, save, discard, and plus button.
    Debounced and only redraws if layout actually changes. Reuses widgets for performance.
    """
    patterns_grid.unbind("<Configure>")
    redraw_after_id = [None]
    last_state: Dict[str, Any] = {'cols': None, 'patterns': None}
    entry_cache = []
    plus_btn_cache: list[Optional[ttkb.Button]] = [None]
    def do_layout_entries():
        pattern_strs = rules[rule_key]['patterns']
        width = patterns_grid.winfo_width()
        if width <= 1:
            patterns_grid.after(10, do_layout_entries)
            return
        entry_pixel_width = 120
        max_per_row = max(1, width // entry_pixel_width)
        # Only redraw if columns or patterns changed
        if last_state['cols'] == max_per_row and last_state['patterns'] == tuple(pattern_strs):
            redraw_after_id[0] = None
            return
        last_state['cols'] = max_per_row
        last_state['patterns'] = tuple(pattern_strs)
        # Reuse or create entry widgets as needed
        needed = len(pattern_strs) + 1  # +1 for add field
        while len(entry_cache) < needed:
            var = tk.StringVar()
            entry = ttkb.Entry(patterns_grid, textvariable=var, width=15)
            entry_cache.append((entry, var))
        for entry, _ in entry_cache:
            entry.grid_remove()
        pattern_vars = []
        entries = []
        new_vars = []
        def save_patterns(event=None):
            new_patterns = [v.get().strip() for _, v in entry_cache[:len(pattern_strs)] if v.get().strip() and v.get().strip() != '<add pattern>']
            new_patterns += [v.get().strip() for _, v in entry_cache[len(pattern_strs):len(pattern_strs)+1] if v.get().strip() and v.get().strip() != '<add pattern>']
            rules[rule_key]['patterns'] = new_patterns
            save_rules(config_path, rules)
            logger.info(f"Patterns for rule '{rule_key}' updated: {new_patterns}")
            patterns_grid.unbind("<Configure>")
            show_pattern_label()
            # Rebind <Configure> for label mode
            patterns_grid.bind("<Configure>", lambda e: pattern_grid_label(patterns_grid, rules, rule_key, show_pattern_label))
        def discard_patterns(event=None):
            show_pattern_label()
            # Rebind <Configure> for label mode
            patterns_grid.bind("<Configure>", lambda e: pattern_grid_label(patterns_grid, rules, rule_key, show_pattern_label))
        # Existing patterns
        for idx, pattern in enumerate(pattern_strs):
            row = idx // max_per_row
            col = idx % max_per_row
            entry, var = entry_cache[idx]
            var.set(pattern)
            entry.grid(row=row, column=col, padx=2, pady=2, sticky="w")
            entry.bind("<Return>", save_patterns)
            entry.bind("<Escape>", discard_patterns)
            pattern_vars.append(var)
            entries.append(entry)
        # Add pattern entry
        idx = len(pattern_strs)
        row = idx // max_per_row
        col = idx % max_per_row
        entry, var = entry_cache[idx]
        var.set("")
        entry.delete(0, tk.END)
        entry.insert(0, "<add pattern>")
        def clear_placeholder(event, v=var):
            if entry.get() == "<add pattern>":
                entry.delete(0, tk.END)
        entry.grid(row=row, column=col, padx=2, pady=2, sticky="w")
        entry.bind("<FocusIn>", clear_placeholder)
        entry.bind("<Return>", save_patterns)
        entry.bind("<Escape>", discard_patterns)
        entries.append(entry)
        new_vars.append(var)
        # Plus button
        if plus_btn_cache[0] is None:
            def add_and_focus():
                # Prevent adding if the current add pattern field is empty or only whitespace
                if not new_vars or not new_vars[0].get().strip() or new_vars[0].get().strip() == '<add pattern>':
                    return  # Do nothing if the add field is empty
                # Add a new entry and re-layout
                rules[rule_key]['patterns'] += [v.get().strip() for v in new_vars if v.get().strip() and v.get().strip() != '<add pattern>']
                save_rules(config_path, rules)
                logger.info(f"Patterns for rule '{rule_key}' updated: {rules[rule_key]['patterns']}")
                do_layout_entries()
                # Focus the last Entry widget
                all_entries = patterns_grid.winfo_children()
                for widget in reversed(all_entries):
                    if isinstance(widget, ttkb.Entry):
                        widget.focus_set()
                        widget.icursor(tk.END)
                        break
            plus_btn_cache[0] = ttkb.Button(patterns_grid, text="+", width=2, style="success.TButton", command=add_and_focus)
        plus_btn = plus_btn_cache[0]
        plus_btn.grid(row=row, column=col+1, padx=(0, 6), pady=2, sticky="w")
        if entries:
            entries[0].focus_set()
        redraw_after_id[0] = None
    def layout_entries(event=None):
        if redraw_after_id[0]:
            patterns_grid.after_cancel(redraw_after_id[0])
        redraw_after_id[0] = patterns_grid.after(80, do_layout_entries)
    patterns_grid.bind("<Configure>", layout_entries)
    do_layout_entries()

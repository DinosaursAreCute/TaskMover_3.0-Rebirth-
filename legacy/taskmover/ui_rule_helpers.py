"""
Rule management UI helpers for TaskMover.
"""

import tkinter as tk
from .ui_helpers import Tooltip
import ttkbootstrap as ttkb
from tkinter import messagebox, filedialog, simpledialog
from taskmover.config import save_rules
from taskmover.pattern_grid_helpers import pattern_grid_label, pattern_grid_edit
from .rule_priority import get_sorted_rule_keys, move_rule_priority, set_rule_priority
from .rule_name_editor import editable_rule_name
import logging
import time

# Define loggers at the top of the file for consistency and configurability
ui_logger = logging.getLogger("UI")
frames_logger = logging.getLogger("frames")
geo_logger = logging.getLogger("geometry")
rules_logger = logging.getLogger("Rules")
rule_ids_logger = logging.getLogger("rule_ids")

def update_parent_canvas_scrollregion(widget):
    """
    Safely update the scrollregion of the parent canvas containing the widget.
    - Only update if widget and canvas are mapped and not destroyed.
    - Only update if bbox is valid (not [0, 0, 1, 1] unless truly empty).
    - Debounce rapid updates to avoid recursion.
    - Add robust error handling and debug logging.
    """
    try:
        parent = getattr(widget, 'master', None)
        canvas = None
        while parent is not None:
            if isinstance(parent, tk.Canvas):
                canvas = parent
                break
            parent = getattr(parent, 'master', None)
        frames_logger.debug(f"Attempting to update scrollregion for widget: {widget}")
        if canvas is None:
            frames_logger.debug("No parent canvas found for widget %r", widget)
            return
        frames_logger.debug(f"Found parent canvas: {canvas}")
        # Check if widget and canvas are mapped and not destroyed
        if not hasattr(widget, 'winfo_exists') or not widget.winfo_exists():
            ui_logger.debug("Widget %r does not exist", widget)
            return
        if not hasattr(canvas, 'winfo_exists') or not canvas.winfo_exists():
            ui_logger.debug("Canvas %r does not exist", canvas)
            return
        if hasattr(canvas, 'winfo_ismapped') and not canvas.winfo_ismapped():
            ui_logger.debug("Canvas %r is not mapped", canvas)
            return
        # Debounce: only allow update every 50ms per canvas
        now = time.time()
        last_update = getattr(canvas, '_last_scrollregion_update', 0)
        if now - last_update < 0.05:
            ui_logger.debug("Debounced scrollregion update for canvas %r", canvas)
            return
        setattr(canvas, '_last_scrollregion_update', now)
        bbox = canvas.bbox("all")
        ui_logger.debug(f"Canvas bbox for scrollregion: {bbox}")
        # Only update if bbox is valid
        if bbox is None:
            ui_logger.debug("Canvas bbox is None; skipping scrollregion update.")
            return
        if bbox == (0, 0, 1, 1):
            # Check if canvas is truly empty (no children)
            if len(canvas.find_all()) == 0:
                ui_logger.debug("Canvas is empty; setting scrollregion to (0,0,0,0)")
                canvas.configure(scrollregion=(0, 0, 0, 0))
            else:
                ui_logger.debug("Canvas bbox is (0,0,1,1) but canvas is not empty; will attempt to update with size of window item")
                # Find the first window item and use its width and height as fallback
                windows = [canvas.itemcget(item, 'window') for item in canvas.find_all() if canvas.type(item) == 'window']
                for win_id in windows:
                    if win_id:
                        try:
                            win = canvas.nametowidget(win_id)
                            # Use a timer to allow the window to be drawn before calculating scrollregion
                            def delayed_update():
                                try:
                                    win.update_idletasks()
                                    width = win.winfo_width() or 500  # Fallback width
                                    height = win.winfo_height() or 500  # Fallback height
                                    ui_logger.debug(f"Using window dimensions for scrollregion: {width}x{height}")
                                    canvas.configure(scrollregion=(0, 0, width, height))
                                except Exception as ex:
                                    ui_logger.error(f"Error in delayed scrollregion update: {ex}")
                            canvas.after(50, delayed_update)
                            return
                        except Exception as ex:
                            ui_logger.error(f"Error finding window for scrollregion: {ex}")
                # If we can't find any valid window, set a fallback scrollregion
                canvas.configure(scrollregion=(0, 0, 500, 500))  # Default fallback
            # Don't return here, allow the function to continue in case other logic is needed
        # Normal update
        canvas.configure(scrollregion=bbox)
        ui_logger.debug(f"Updated canvas scrollregion to {bbox}")
    except Exception as e:
        ui_logger.exception(f"Exception in update_parent_canvas_scrollregion: {e}")

def update_rule_list(rule_frame, rules, config_path, logger, update_rule_list_fn=None, scrollable_widget=None):
    """
    Update the rule list UI with all current rules, sorted by priority.
    This function handles:
    1. Maintaining the mapping of rule keys to UI frames
    2. Removing frames for deleted rules
    3. Creating or updating frames for current rules
    4. Ensuring proper visibility and scrolling
    
    Args:
        rule_frame: The parent frame that contains all rule UI elements
        rules: The dictionary of rules to display
        config_path: Path to the configuration file for saving changes
        logger: Logger for debug messages
        update_rule_list_fn: Optional callback for updating the rule list (e.g. for scroll preservation)
        scrollable_widget: Optional widget to update scrolling for
    """
    geo_logger.debug(f"update_rule_list called: rebuilding rule list")
    
    # Track the total height to ensure proper scrolling
    total_content_height = 0
    
    # Initialize frame mapping if needed
    if not hasattr(rule_frame, '_rule_frames'):
        rule_frame._rule_frames = {}
    rule_frames = rule_frame._rule_frames
    
    # --- Pre-measure content before changes ---
    orig_height = rule_frame.winfo_height() if hasattr(rule_frame, 'winfo_height') else 0
    geo_logger.debug(f"Original rule frame height before update: {orig_height}")
    
    # Log empty rule sets
    if not rules:
        ui_logger.info("No rules to display - rule list is empty")
    
    # --- Flicker-free update: hide frame during update ---
    was_visible = rule_frame.winfo_ismapped() if hasattr(rule_frame, 'winfo_ismapped') else True
    if was_visible:
        rule_frame.pack_forget()
        
    # Force update to ensure consistent state
    rule_frame.update_idletasks()
    
    # Track which frames were removed for logging
    removed_frames = []
    
    # Remove frames for deleted rules
    for key in list(rule_frames.keys()):
        if key in rules:
            continue
        if key.endswith('_active_var'):
            del rule_frames[key]
            continue
        frame_widget = rule_frames[key]
        if hasattr(frame_widget, 'destroy'):
            removed_frames.append(key)
            frame_widget.destroy()
        del rule_frames[key]
    
    if removed_frames:
        ui_logger.info(f"Removed frames for deleted rules: {', '.join(removed_frames)}")
    
    # Add or update frames for all rules, sorted by priority
    rule_keys = get_sorted_rule_keys(rules)
    ui_logger.debug(f"Updating {len(rule_keys)} rules in priority order")
    
    # Enable height tracking for scrollregion calculation
    rule_frame._calculate_total_height = True
    
    for rule_key in rule_keys:
        update_or_create_rule_frame(rule_key, rules, config_path, logger, rule_frame, rule_frames, update_rule_list_fn, scrollable_widget)
        
        # Track frame height for proper scrolling
        if rule_key in rule_frames:
            frame_widget = rule_frames[rule_key]
            if hasattr(frame_widget, 'winfo_reqheight'):
                try:
                    # Force immediate layout calculation for this frame
                    frame_widget.update_idletasks()
                    height = frame_widget.winfo_reqheight() or 0
                    
                    # Also try actual height if reqheight is too small
                    if height < 10:  
                        height = frame_widget.winfo_height() or 0
                        
                    # If still no height, estimate based on content
                    if height < 10:
                        # Estimate height from children
                        child_height = 0
                        for child in frame_widget.winfo_children():
                            if hasattr(child, 'winfo_ismapped') and child.winfo_ismapped():
                                child_y = child.winfo_y() + (child.winfo_height() or 20)
                                child_height = max(child_height, child_y)
                        height = child_height if child_height > 0 else 50  # 50px default per rule
                    
                    geo_logger.debug(f"Rule '{rule_key}' frame height: {height}")
                    total_content_height += height + 5  # Include padding
                except Exception as e:
                    ui_logger.warning(f"Error calculating height for rule '{rule_key}': {e}")
                    # Use a reasonable default
                    total_content_height += 75  # Default rule height with padding
    
    # Add extra padding at the bottom for better scroll experience
    total_content_height += 20
    
    geo_logger.debug(f"Total calculated content height: {total_content_height}")
    
    # --- Restore frame visibility ---
    if was_visible:
        # Before showing, force the frame to maintain at least original height
        min_height = max(orig_height, total_content_height)
        if min_height > 0:
            # This helps prevent the frame from collapsing during transitions
            rule_frame.config(height=min_height)
            geo_logger.debug(f"Setting minimum frame height to {min_height}")
        
        # Show the frame
        rule_frame.pack(fill="both", expand=True)
    
    # Force update to calculate proper dimensions
    rule_frame.update_idletasks()
    
    # Store the calculated height for other functions to use
    rule_frame._total_content_height = total_content_height
    
    # Update scrollregion with calculated content height
    update_scrollregion_with_fallback(rule_frame, total_content_height)
    
    # Schedule an additional verification to catch any late layout changes
    def verify_layout_complete():
        if hasattr(rule_frame, 'winfo_exists') and rule_frame.winfo_exists():
            # Check if scrollregion needs updating
            update_scrollregion_with_fallback(rule_frame, total_content_height)
    
    # Schedule verification after UI has settled
    if hasattr(rule_frame, 'after'):
        rule_frame.after(200, verify_layout_complete)

def update_scrollregion_with_fallback(rule_frame, min_height=500):
    """
    Enhanced scrollregion update that provides fallback mechanisms
    when bbox returns invalid values. This function implements multiple
    strategies to ensure the scrollregion is always valid:
    
    1. First try standard bbox-based update
    2. If bbox fails, calculate based on frame dimensions
    3. If frame dimensions inadequate, use child widgets
    4. Schedule verification to catch delayed UI updates
    5. Use a progressive fallback series with increasing aggressiveness
    """
    try:
        # First try standard update
        update_parent_canvas_scrollregion(rule_frame)
        
        # Find parent canvas if any
        parent = getattr(rule_frame, 'master', None)
        canvas = None
        while parent is not None:
            if isinstance(parent, tk.Canvas):
                canvas = parent
                break
            parent = getattr(parent, 'master', None)
            
        if canvas is None:
            ui_logger.debug("No parent canvas found")
            return
            
        # Double-check scrollregion is valid
        current_scrollregion = canvas.cget("scrollregion")
        is_valid = (current_scrollregion and 
                   current_scrollregion != "0 0 1 1" and 
                   current_scrollregion != "" and
                   not (current_scrollregion.endswith("0") and current_scrollregion.startswith("0 0")))
                   
        if not is_valid:
            # Log the issue
            geo_logger.warning(f"Invalid scrollregion detected: '{current_scrollregion}'")
            
            # Calculate proper dimensions using multiple methods
            canvas.update_idletasks()
            rule_frame.update_idletasks()
            
            # Method 1: Canvas dimensions
            canvas_width = canvas.winfo_width() or 800
            
            # Method 2: Rule frame dimensions - most reliable if available
            frame_height = 0
            try:
                frame_height = rule_frame.winfo_reqheight()
                geo_logger.debug(f"Frame reqheight: {frame_height}")
            except Exception:
                pass
                
            if not frame_height or frame_height < 50:
                geo_logger.debug("Frame height too small or zero, trying winfo_height")
                try:
                    frame_height = rule_frame.winfo_height() 
                    geo_logger.debug(f"Frame winfo_height: {frame_height}")
                except Exception:
                    pass
            
            # Method 3: Sum all visible children heights
            if not frame_height or frame_height < 50:
                geo_logger.debug("Frame height still too small, calculating from children")
                try:
                    total_height = 0
                    for child in rule_frame.winfo_children():
                        if hasattr(child, 'winfo_ismapped') and child.winfo_ismapped():
                            child_height = child.winfo_reqheight() or child.winfo_height() or 0
                            child_y = child.winfo_y() + child_height
                            total_height = max(total_height, child_y)
                    if total_height > 0:
                        frame_height = total_height + 20  # Add padding
                        geo_logger.debug(f"Calculated height from children: {frame_height}")
                except Exception as e:
                    geo_logger.error(f"Error calculating child heights: {e}")
            
            # Method 4: Check children recursively
            if not frame_height or frame_height < 50:
                geo_logger.debug("Still no valid height, trying recursive depth calculation")
                try:
                    def get_max_depth(widget, current_depth=0):
                        max_depth = current_depth
                        for child in widget.winfo_children():
                            if hasattr(child, 'winfo_ismapped') and child.winfo_ismapped():
                                child_depth = get_max_depth(child, current_depth + 1)
                                max_depth = max(max_depth, child_depth)
                        return max_depth
                    
                    depth = get_max_depth(rule_frame)
                    if depth > 0:
                        # Estimate ~50px per depth level as fallback
                        frame_height = depth * 50
                        geo_logger.debug(f"Calculated height from widget depth ({depth}): {frame_height}")
                except Exception as e:
                    geo_logger.error(f"Error in recursive depth calculation: {e}")
            
            # Final fallback: min_height or a reasonable default
            if not frame_height or frame_height < 50:
                frame_height = min_height
                geo_logger.debug(f"Using minimum fallback height: {frame_height}")
            
            # Ensure minimum height
            content_height = max(frame_height, min_height)
            
            # Set a proper scrollregion with calculated dimensions
            new_scrollregion = (0, 0, canvas_width, content_height)
            canvas.configure(scrollregion=new_scrollregion)
            geo_logger.info(f"Forced scrollregion to: {new_scrollregion}")
            
            # Schedule multiple verification attempts with increasing delays
            def verify_scrollregion(attempt=1, max_attempts=3):
                try:
                    if not canvas.winfo_exists():
                        return
                        
                    current = canvas.cget("scrollregion")
                    geo_logger.debug(f"Verification attempt {attempt}/{max_attempts}: scrollregion={current}")
                    
                    # Check if scrollregion is still invalid
                    is_valid = (current and 
                           current != "0 0 1 1" and 
                           current != "" and
                           not (current.endswith("0") and current.startswith("0 0")))
                           
                    if not is_valid:
                        # Get fresh dimensions
                        canvas.update_idletasks()
                        rule_frame.update_idletasks()
                        width = canvas.winfo_width() or canvas_width
                        
                        # On final attempt, be more aggressive with height calculation
                        if attempt == max_attempts:
                            # Force an explicit calculation of all contents
                            total_height = 0
                            try:
                                rule_frame._calculate_total_height = True  # Signal for debug
                                rule_frame.update_idletasks()
                                
                                # Log all child widgets and their heights
                                for i, child in enumerate(rule_frame.winfo_children()):
                                    if hasattr(child, 'winfo_ismapped') and child.winfo_ismapped():
                                        child_height = child.winfo_reqheight() or child.winfo_height() or 0
                                        child_y = child.winfo_y() + child_height
                                        total_height = max(total_height, child_y)
                                        geo_logger.debug(f"Child {i}: y={child.winfo_y()}, height={child_height}, bottom={child_y}")
                                
                                if total_height > 0:
                                    height = total_height + 50  # Extra padding on final attempt
                                else:
                                    height = content_height * 1.2  # 20% increase as safety
                            except Exception as e:
                                geo_logger.error(f"Error in final height calculation: {e}")
                                height = content_height
                        else:
                            # Use previous calculation plus a small increase
                            height = content_height * (1.0 + (attempt * 0.05))
                        
                        # Force the update with fresh dimensions
                        canvas.configure(scrollregion=(0, 0, width, height))
                        geo_logger.info(f"Verification force update {attempt}: (0, 0, {width}, {height})")
                        
                        # Schedule next verification if not last attempt
                        if attempt < max_attempts:
                            canvas.after(150 * attempt, lambda: verify_scrollregion(attempt + 1, max_attempts))
                except Exception as e:
                    geo_logger.exception(f"Error in verify_scrollregion attempt {attempt}: {e}")
                    if attempt < max_attempts:
                        canvas.after(100 * attempt, lambda: verify_scrollregion(attempt + 1, max_attempts))
            
            # Start the verification process
            canvas.after(80, verify_scrollregion)
                
    except Exception as e:
        ui_logger.exception(f"Exception in update_scrollregion_with_fallback: {e}")

def open_file_dialog(initial_dir):
    from pathlib import Path
    import os
    dir_path = filedialog.askdirectory(initialdir=initial_dir, title="Select Directory")
    if dir_path:
        dir_path = Path(dir_path)
        if os.name == 'nt':  # Windows
            dir_path = str(dir_path).replace("/", "\\")
        else:  # macOS and Linux
            dir_path = str(dir_path)
        return dir_path
    return initial_dir

def toggle_rule_active(rule_key, rules, config_path, active, logger):
    import logging
    rules[rule_key]['active'] = bool(active)
    save_rules(config_path, rules)
    ui_logger.info(f"User toggled rule '{rule_key}' to {'enabled' if active else 'disabled'}.")
    rules_logger.info(f"Rule '{rule_key}' active state set to {bool(active)}.")

def toggle_unzip(rule_key, rules, config_path, unzip, logger):
    import logging
    rules[rule_key]['unzip'] = bool(unzip)
    save_rules(config_path, rules)
    ui_logger.info(f"User toggled unzip for rule '{rule_key}' to {bool(unzip)}.")
    rules_logger.info(f"Rule '{rule_key}' unzip state set to {bool(unzip)}.")

def enable_all_rules(rules, config_path, rule_frame, logger, update_rule_list_fn=None):
    import logging
    rule_frames = getattr(rule_frame, '_rule_frames', {})
    for rule_key, rule in rules.items():
        rule['active'] = True
        var = rule_frames.get(rule_key+'_active_var')
        if var:
            var.set(1)
        ui_logger.info(f"User enabled rule '{rule_key}'.")
        rules_logger.info(f"Rule '{rule_key}' enabled.")
    save_rules(config_path, rules)
    # No UI rebuild needed

def disable_all_rules(rules, config_path, rule_frame, logger, update_rule_list_fn=None):
    import logging
    rule_frames = getattr(rule_frame, '_rule_frames', {})
    for rule_key, rule in rules.items():
        rule['active'] = False
        var = rule_frames.get(rule_key+'_active_var')
        if var:
            var.set(0)
        ui_logger.info(f"User disabled rule '{rule_key}'.")
        rules_logger.info(f"Rule '{rule_key}' disabled.")
    save_rules(config_path, rules)
    # No UI rebuild needed

def add_rule_button(rules, config_path, rule_frame, logger, root, update_rule_list_fn=None):
    import uuid
    rule_name = simpledialog.askstring("Add Rule", "Enter the name of the new rule:", parent=root)
    if rule_name:
        if rule_name in rules:
            messagebox.showerror("Error", f"Rule '{rule_name}' already exists.", parent=root)
            logger.warning(f"Attempted to add duplicate rule: {rule_name}")
        else:
            # Assign a unique id and priority
            max_priority = max((r.get('priority', 0) for r in rules.values()), default=-1)
            rules[rule_name] = {
                "patterns": [],
                "path": "",
                "unzip": False,
                "active": True,
                "id": str(uuid.uuid4()),
                "priority": max_priority + 1
            }
            save_rules(config_path, rules)
            if update_rule_list_fn:
                update_rule_list_fn(rules, config_path, logger)
            else:
                update_rule_list(rule_frame, rules, config_path, logger)
            logger.info(f"Added new rule: {rule_name}")
            edit_rule(rule_name, rules, config_path, logger, rule_frame)

def delete_rule(rule_key, rules, config_path, logger, rule_frame, update_rule_list_fn=None):
    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the rule '{rule_key}'?"):
        del rules[rule_key]
        save_rules(config_path, rules)
        logger.info(f"Rule '{rule_key}' deleted.")
        if update_rule_list_fn:
            update_rule_list_fn(rules, config_path, logger)
        else:
            update_rule_list(rule_frame, rules, config_path, logger)

def delete_multiple_rules(rules, config_path, logger, rule_frame, update_rule_list_fn=None):
    import taskmover.center_window as cw
    delete_window = tk.Toplevel()
    delete_window.title("Delete Rules")
    delete_window.geometry("600x600")
    cw.center_window(delete_window)
    ttkb.Label(delete_window, text="Select Rules to Delete", font=("Helvetica", 12, "bold")).pack(pady=10)
    listbox = tk.Listbox(delete_window, selectmode=tk.MULTIPLE, width=50, height=15)
    listbox.pack(pady=10, padx=10)
    for rule_key in rules.keys():
        listbox.insert(tk.END, rule_key)
    def confirm_delete():
        selected_indices = listbox.curselection()
        selected_rules = [listbox.get(i) for i in selected_indices]
        if selected_rules and messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the selected rules?"):
            for rule_key in selected_rules:
                del rules[rule_key]
                logger.info(f"Rule '{rule_key}' deleted.")
            save_rules(config_path, rules)
            if update_rule_list_fn:
                update_rule_list_fn(rules, config_path, logger)
            else:
                update_rule_list(rule_frame, rules, config_path, logger)
            delete_window.destroy()
    ttkb.Button(delete_window, text="Delete Selected", command=confirm_delete).pack(pady=10)
    ttkb.Button(delete_window, text="Cancel", command=delete_window.destroy).pack(pady=5)

def edit_rule(rule_key, rules, config_path, logger, rule_frame):
    import taskmover.center_window as cw
    edit_window = tk.Toplevel()
    edit_window.title(f"Edit Rule: {rule_key}")
    edit_window.geometry("400x300")
    root = rule_frame.winfo_toplevel()
    cw.center_window(edit_window)
    edit_window.attributes('-topmost', True)
    edit_window.update()
    edit_window.attributes('-topmost', False)
    edit_window.grab_set()
    # --- Editable rule name ---
    def on_rename(new_name):
        edit_window.title(f"Edit Rule: {new_name}")
        update_rule_list(rule_frame, rules, config_path, logger)

    name_frame, name_var = editable_rule_name(edit_window, rule_key, rules, config_path, logger, on_rename, font=("Helvetica", 12, "bold"))
    name_frame.pack(pady=10)
    ttkb.Label(edit_window, text="Directory:").pack(anchor="w", padx=10)
    dir_var = tk.StringVar(value=rules[name_var.get()]['path'])
    dir_entry = ttkb.Entry(edit_window, textvariable=dir_var, width=50)
    dir_entry.pack(pady=5, padx=10)
    dir_entry.bind("<Button-1>", lambda e: dir_var.set(filedialog.askdirectory(title="Select Directory")))
    ttkb.Label(edit_window, text="Patterns (comma-separated):").pack(anchor="w", padx=10)
    patterns_var = tk.StringVar(value=", ".join(rules[name_var.get()]['patterns']))
    patterns_entry = ttkb.Entry(edit_window, textvariable=patterns_var, width=50)
    patterns_entry.pack(pady=5, padx=10)
    def save_changes():
        current_key = name_var.get()
        rules[current_key]['path'] = dir_var.get()
        rules[current_key]['patterns'] = [pattern.strip() for pattern in patterns_var.get().split(",")]
        save_rules(config_path, rules)
        logger.info(f"Rule '{current_key}' updated.")
        update_rule_list(rule_frame, rules, config_path, logger)
        edit_window.destroy()
    ttkb.Button(edit_window, text="Save", command=save_changes).pack(pady=10)
    ttkb.Button(edit_window, text="Cancel", command=edit_window.destroy).pack(pady=5)

# The editable_rule_name function has been moved to rule_name_editor.py
# and is imported at the top of this file

def update_or_create_rule_frame(rule_key, rules, config_path, logger, rule_frame, rule_frames, update_rule_list_fn=None, scrollable_widget=None):
    # Remove old frame if it exists (for rename or delete)
    if rule_key in rule_frames:
        rule_frames[rule_key].destroy()
    frame = ttkb.Frame(rule_frame)
    frame.pack(fill="x", pady=5, padx=10)
    rule_frames[rule_key] = frame
    # --- Collapsible rule info ---
    user_priority = rules[rule_key].get('priority', 0) + 1
    # Use collapse_on_start setting if available
    collapse_default = getattr(rule_frame, '_collapse_default', True)
    if hasattr(rule_frame, 'winfo_toplevel'):
        app_settings = getattr(rule_frame.winfo_toplevel(), 'app_settings', None)
        if app_settings and 'collapse_on_start' in app_settings:
            collapse_default = app_settings['collapse_on_start']
    if not hasattr(rule_frame, '_collapse_state'):
        rule_frame._collapse_state = {}
    collapse_state = rule_frame._collapse_state
    collapsed = tk.BooleanVar(value=collapse_state.get(rule_key, collapse_default))
    header_frame = ttkb.Frame(frame)
    header_frame.pack(fill="x", pady=2)
    priority_label = ttkb.Label(header_frame, text=f"{user_priority}.", font=("Helvetica", 12, "bold"))
    priority_label.pack(side="left", padx=(0, 4))
    
    def on_rename(new_name):
        # Preserve collapse state on rename
        collapse_state[new_name] = collapse_state.pop(rule_key, collapsed.get())
        # Instead of just updating this single rule, do a complete rebuild
        # of the rule list to ensure rules are displayed in correct priority order
        if update_rule_list_fn:
            # Use the update_rule_list_preserve_scroll function if available
            logger.debug(f"Using update_rule_list_fn to rebuild rule list after renaming rule to {new_name}")
            update_rule_list_fn(rules, config_path, logger)
        else:
            # Fall back to standard update if no scroll-preserving function
            logger.debug(f"Doing standard rebuild after renaming rule to {new_name}")
            frame.destroy()
            rule_frames.pop(rule_key, None) 
            update_or_create_rule_frame(new_name, rules, config_path, logger, rule_frame, rule_frames, update_rule_list_fn, scrollable_widget)
    name_frame, _ = editable_rule_name(header_frame, rule_key, rules, config_path, logger, on_rename)
    name_frame.pack(side="left", pady=2)
    # Active toggle in header
    active_var = tk.IntVar(value=1 if rules[rule_key]['active'] else 0)
    rule_frames[rule_key+'_active_var'] = active_var
    active_switch = ttkb.Checkbutton(header_frame, text="Active", variable=active_var, command=lambda rk=rule_key, av=active_var: toggle_rule_active(rk, rules, config_path, av.get(), logger))
    active_switch.pack(side="left", padx=10)
    Tooltip(active_switch, "Enable or disable this rule.")
    # Collapse/expand button with arrow
    def update_collapse_btn():
        collapse_btn.config(text="▲" if not collapsed.get() else "▼")
    def toggle_collapse():
        logger.debug(f"toggle_collapse ENTER: rule '{rule_key}' | frame id: {id(frame)} | collapsed var id: {id(collapsed)} | info_frame id: {id(info_frame) if 'info_frame' in locals() else 'N/A'}")
        try:
            logger.debug(f"toggle_collapse called for rule '{rule_key}'")
            if not hasattr(info_frame, 'winfo_exists') or not info_frame.winfo_exists():
                logger.warning(f"toggle_collapse: info_frame for rule '{rule_key}' no longer exists. frame id: {id(info_frame) if 'info_frame' in locals() else 'N/A'}")
                return
            if not hasattr(collapsed, 'get'):
                logger.warning(f"toggle_collapse: collapsed variable for rule '{rule_key}' is invalid. collapsed id: {id(collapsed)}")
                return            collapsed.set(not collapsed.get())
            collapse_state[rule_key] = collapsed.get()
            if collapsed.get():
                info_frame.pack_forget()
                logger.info(f"Collapsed rule: {rule_key}")
            else:
                info_frame.pack(fill="x", pady=2)
                logger.info(f"Expanded rule: {rule_key}")
            update_collapse_btn()
            update_parent_canvas_scrollregion(frame)
            log_widget_tree(rule_frame.winfo_toplevel(), frames_logger)
        except Exception as e:
            import traceback
            logger.error(f"Exception in toggle_collapse for rule '{rule_key}' | frame id: {id(frame)} | collapsed id: {id(collapsed)}: {e}\n{traceback.format_exc()}")
            try:
                log_widget_tree(rule_frame.winfo_toplevel(), frames_logger)
            except Exception as tree_exc:
                logger.error(f"Exception logging widget tree in toggle_collapse: {tree_exc}")
    collapse_btn = ttkb.Button(header_frame, text="▼", width=2, command=toggle_collapse)
    collapse_btn.pack(side="left", padx=2)
    logger_frames = frames_logger
    logger_rule_ids = rule_ids_logger
    info_frame_id = 'N/A'
    if 'info_frame' in locals():
        try:
            info_frame_id = id(locals()['info_frame'])
        except Exception:
            info_frame_id = 'N/A'
    logger_frames.debug(f"Created collapse_btn for rule '{rule_key}' | frame id: {id(frame)} | collapsed var id: {id(collapsed)} | info_frame id: {info_frame_id}")
    logger_rule_ids.debug(f"Rule '{rule_key}' | frame id: {id(frame)} | collapsed var id: {id(collapsed)} | info_frame id: {info_frame_id}")
    update_collapse_btn()
    # Info frame (collapsible)
    info_frame = ttkb.Frame(frame)
    if not collapsed.get():
        info_frame.pack(fill="x", pady=2)
    # --- Patterns ---
    patterns_frame = ttkb.Frame(info_frame)
    patterns_frame.pack(anchor="w", padx=10, pady=2, fill="x")
    patterns_label = ttkb.Label(patterns_frame, text="Patterns:", font=("Helvetica", 10))
    patterns_label.pack(anchor="w")
    Tooltip(patterns_label, "File name patterns (e.g., *.pdf, report_*.docx) that this rule will match.")
    patterns_grid = ttkb.Frame(patterns_frame)
    patterns_grid.pack(anchor="w", fill="x")
    def make_show_pattern_label(rk, pg):
        def show_pattern_label():
            pattern_grid_label(pg, rules, rk, make_show_pattern_edit(rk, pg), scrollable_widget)
        return show_pattern_label
    def make_show_pattern_edit(rk, pg):
        def show_pattern_edit():
            pattern_grid_edit(pg, rules, rk, config_path, logger, make_show_pattern_label(rk, pg), scrollable_widget)
        return show_pattern_edit
    make_show_pattern_label(rule_key, patterns_grid)()
    # --- Path field ---
    path_var = tk.StringVar(value=rules[rule_key]['path'])
    def choose_path(event=None, rk=rule_key, pv=path_var):
        selected = filedialog.askdirectory(title="Select Directory", initialdir=pv.get())
        if selected:
            pv.set(selected)
            rules[rk]['path'] = selected
            save_rules(config_path, rules)
            logger.info(f"Path for rule '{rk}' updated: {selected}")
            update_or_create_rule_frame(rk, rules, config_path, logger, rule_frame, rule_frames, update_rule_list_fn, scrollable_widget)
    path_entry = ttkb.Entry(info_frame, textvariable=path_var, font=("Helvetica", 10), width=40)
    path_entry.pack(anchor="w", padx=10)
    path_entry.bind("<Button-1>", lambda event, rk=rule_key, pv=path_var: choose_path(event, rk, pv))
    path_entry.bind("<Return>", lambda event, rk=rule_key, pv=path_var: choose_path(event, rk, pv))
    path_entry.config(state="readonly", cursor="hand2")
    Tooltip(path_entry, "Click to select the folder where files matching this rule will be moved.")
    # --- Details switches ---
    details_frame = ttkb.Frame(info_frame)
    details_frame.pack(fill="x", pady=5)
    unzip_var = tk.IntVar(value=1 if rules[rule_key].get('unzip', False) else 0)
    unzip_switch = ttkb.Checkbutton(
        details_frame,
        text="Unzip",
        variable=unzip_var,
        command=lambda rk=rule_key, uv=unzip_var: toggle_unzip(rk, rules, config_path, uv.get(), logger)
    )
    unzip_switch.pack(side="left", padx=10)
    Tooltip(unzip_switch, "Automatically unzip .zip files matching this rule.")
    # --- Action buttons ---
    actions_frame = ttkb.Frame(info_frame)
    actions_frame.pack(fill="x", pady=5)
    edit_button = ttkb.Button(actions_frame, text="Edit", style="info.TButton", command=lambda rk=rule_key: edit_rule(rk, rules, config_path, logger, rule_frame))
    edit_button.pack(side="left", padx=10)
    Tooltip(edit_button, "Edit this rule.")
    delete_button = ttkb.Button(actions_frame, text="Delete", style="danger.TButton", command=lambda rk=rule_key: delete_rule(rk, rules, config_path, logger, rule_frame))
    delete_button.pack(side="left", padx=10)
    Tooltip(delete_button, "Delete this rule.")
    # --- Priority up/down buttons ---
    from .rule_priority import move_rule_priority
    up_btn = ttkb.Button(actions_frame, text="↑", width=2, command=lambda: move_and_refresh(-1))
    #up_btn.pack(side="left", padx=2)
    Tooltip(up_btn, "Move rule up in priority.")
    down_btn = ttkb.Button(actions_frame, text="↓", width=2, command=lambda: move_and_refresh(1))
    #down_btn.pack(side="left", padx=2)
    Tooltip(down_btn, "Move rule down in priority.")
    def move_and_refresh(direction):
        old_priority = rules[rule_key].get('priority')
        if move_rule_priority(rules, rule_key, direction):
            new_priority = rules[rule_key].get('priority')
            logger.info(f"Rule '{rule_key}' priority changed from {old_priority} to {new_priority}")
            save_rules(config_path, rules)
            # Full UI rebuild after priority change
            root = frame.winfo_toplevel()
            rebuild_fn = getattr(root, "rebuild_main_ui", None)
            if callable(rebuild_fn):
                rebuild_fn()
            else:
                update_rule_list(frame.master, rules, config_path, logger)

def log_widget_tree(widget, logger=None, prefix=""):  # Helper to log widget tree
    if logger is None:
        logger = frames_logger  # Assign the 'frames' logger by default
    try:
        children = widget.winfo_children()
        logger.debug(f"{prefix}{widget.winfo_class()} {widget.winfo_name()} ({str(widget)})")
        for child in children:
            log_widget_tree(child, logger, prefix + "  ")
    except Exception as e:
        logger.error(f"Error logging widget tree: {e}")

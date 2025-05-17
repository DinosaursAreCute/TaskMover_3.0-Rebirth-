"""
Settings and theme UI helpers for TaskMover.
"""

import tkinter as tk
import ttkbootstrap as ttkb
from tkinter import messagebox, colorchooser, simpledialog, WORD, END, BOTH, DISABLED, ttk
from taskmover.config import save_rules
from .ui_color_helpers import choose_color_and_update, browse_path_and_update
from .ui_developer_helpers import trigger_developer_function
from .theme_manager import save_theme, load_all_themes, apply_theme, delete_theme, get_theme

# Settings window and theme helpers

def open_settings_window(
    root: tk.Tk,
    settings: dict,
    save_settings,
    logger
) -> None:
    """
    Open the settings window for TaskMover, allowing the user to configure general settings and manage themes.

    Args:
        root (tk.Tk): The root Tkinter window.
        settings (dict): The current application settings.
        save_settings (callable): Function to save updated settings.
        logger: Logger instance for logging events.
    """
    settings_window = tk.Toplevel(root)
    settings_window.attributes('-topmost', True)
    settings_window.title("Settings")
    settings_window.geometry("600x700")  # Adjusted window size

    notebook = ttk.Notebook(settings_window)
    notebook.pack(fill="both", expand=True)

    # --- General Tab ---
    general_frame = ttkb.Frame(notebook)
    notebook.add(general_frame, text="General")
    ttkb.Label(general_frame, text="Settings", font=("Helvetica", 14, "bold")).pack(pady=10)
    ttkb.Label(general_frame, text="Organisation Folder:").pack(anchor="w", padx=10, pady=5)
    organisation_folder_var = tk.StringVar(value=settings.get("organisation_folder", ""))
    organisation_folder_frame = ttkb.Frame(general_frame)
    organisation_folder_frame.pack(fill="x", padx=10, pady=5)
    ttkb.Entry(organisation_folder_frame, textvariable=organisation_folder_var, width=40).pack(side="left", padx=5)
    ttkb.Button(organisation_folder_frame, text="Browse", command=lambda: browse_path_and_update(organisation_folder_var, logger)).pack(side="left", padx=5)
    ttkb.Label(general_frame, text="Theme:").pack(anchor="w", padx=10, pady=5)
    theme_var = tk.StringVar(value=settings.get("theme", "flatly"))
    valid_themes = ttkb.Style().theme_names()
    def preview_theme(event=None):
        selected_theme = theme_var.get()
        custom_themes = settings.get("custom_themes", {})
        if selected_theme in valid_themes:
            try:
                ttkb.Style().theme_use(selected_theme)
            except tk.TclError:
                messagebox.showerror("Invalid Theme", f"'{selected_theme}' is not a valid theme. Please select a valid theme.")
        elif selected_theme in custom_themes:
            theme = custom_themes[selected_theme]
            style = ttkb.Style()
            style.configure("TButton", foreground=theme.get("accent_color", "#007bff"))
            style.configure("TFrame", background=theme.get("background_color", "#FFFFFF"))
            style.configure("TLabel", foreground=theme.get("text_color", "#000000"))
            # Optionally update menubar and other UI elements
            for child in root.winfo_children():
                if isinstance(child, tk.Menu):
                    child.config(bg=theme.get("background_color", "#FFFFFF"), fg=theme.get("text_color", "#000000"))
        else:
            messagebox.showerror("Invalid Theme", f"'{selected_theme}' is not a valid theme. Please select a valid theme.")

    # --- Theme selection dropdown (General tab) ---
    theme_combobox = ttkb.Combobox(
        general_frame,
        textvariable=theme_var,
        values=list(valid_themes) + list(settings.get("custom_themes", {}).keys()),
        state="readonly"
    )
    theme_combobox.pack(fill="x", padx=10, pady=5)
    theme_combobox.bind("<<ComboboxSelected>>", preview_theme)
    ttkb.Label(general_frame, text="Developer Mode:").pack(anchor="w", padx=10, pady=5)
    developer_mode_var = tk.BooleanVar(value=settings.get("developer_mode", False))
    ttkb.Checkbutton(general_frame, text="Enable Developer Mode", variable=developer_mode_var).pack(anchor="w", padx=10, pady=5)
    ttkb.Label(general_frame, text="Logging Level:").pack(anchor="w", padx=10, pady=5)
    logging_level_var = tk.StringVar(value=settings.get("logging_level", "INFO"))
    ttkb.Combobox(general_frame, textvariable=logging_level_var, values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], state="readonly").pack(fill="x", padx=10, pady=5)
    ttkb.Label(general_frame, text="Logging Components:", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=10, pady=5)
    components_frame = ttkb.Frame(general_frame)
    components_frame.pack(fill="x", padx=10, pady=5)
    components = ["UI", "File Operations", "Rules", "Settings"]
    component_vars = {component: tk.IntVar(value=settings.get("logging_components", {}).get(component, 0)) for component in components}
    for component, var in component_vars.items():
        ttkb.Checkbutton(components_frame, text=component, variable=var).pack(anchor="w")
    ttkb.Button(general_frame, text="Create Dummy Files", command=lambda: trigger_developer_function(organisation_folder_var.get(), logger)).pack(anchor="w", padx=10, pady=10)

    # --- Theme Manager Tab ---
    theme_frame = ttkb.Frame(notebook)
    notebook.add(theme_frame, text="Theme Manager")

    # --- Theme selection dropdown ---
    ttkb.Label(theme_frame, text="Select Theme to Edit:", font=("Helvetica", 12, "bold")).pack(anchor="w", padx=10, pady=5)
    theme_names = list(settings.get("custom_themes", {}).keys())
    theme_select_var = tk.StringVar()
    theme_select_dropdown = ttkb.Combobox(theme_frame, textvariable=theme_select_var, values=theme_names, state="readonly")
    theme_select_dropdown.pack(fill="x", padx=10, pady=2)

    # --- Widget/Button type selection dropdown ---
    ttkb.Label(theme_frame, text="Select Widget/Button Type:", font=("Helvetica", 12, "bold")).pack(anchor="w", padx=10, pady=5)
    widget_types = [
        # Tkinter/ttk
        ("TButton", "Button"),
        ("TCheckbutton", "Checkbutton"),
        ("TRadiobutton", "Radiobutton"),
        ("TEntry", "Entry"),
        ("TLabel", "Label"),
        ("TFrame", "Frame"),
        ("TMenubutton", "Menubutton"),
        ("TCombobox", "Combobox"),
        ("TMenubar", "Menubar"),
        ("TNotebook", "Notebook"),
        ("TScrollbar", "Scrollbar"),
        ("TProgressbar", "Progressbar"),
        ("TScale", "Scale"),
        ("TSpinbox", "Spinbox"),
        ("TSeparator", "Separator"),
        ("TLabelframe", "Labelframe"),
        ("TPanedwindow", "Panedwindow"),
        ("TTreeview", "Treeview"),
        ("TText", "Text"),
        ("TListbox", "Listbox"),
        # ttkbootstrap special button styles
        ("primary.TButton", "Primary Button"),
        ("success.TButton", "Success Button"),
        ("info.TButton", "Info Button"),
        ("warning.TButton", "Warning Button"),
        ("danger.TButton", "Danger Button"),
        ("secondary.TButton", "Secondary Button"),
        ("outline.TButton", "Outline Button"),
        ("link.TButton", "Link Button"),
    ]
    widget_type_var = tk.StringVar(value=widget_types[0][0])
    widget_type_dropdown = ttkb.Combobox(theme_frame, textvariable=widget_type_var, values=[w[1] for w in widget_types], state="readonly")
    widget_type_dropdown.pack(fill="x", padx=10, pady=2)

    # --- Color field and picker for selected widget/button type ---
    color_var = tk.StringVar()
    color_entry = ttkb.Entry(theme_frame, textvariable=color_var)
    color_entry.pack(fill="x", padx=10, pady=2)
    color_picker_btn = ttkb.Button(theme_frame, text="Choose Color", command=lambda: color_var.set(colorchooser.askcolor()[1] or color_var.get()))
    color_picker_btn.pack(padx=10, pady=2)

    # --- Helper: update color field when widget type or theme changes ---
    def update_color_field(*args):
        theme_name = theme_select_var.get()
        widget_idx = widget_type_dropdown.current()
        widget_style = widget_types[widget_idx][0] if widget_idx >= 0 else widget_types[0][0]
        theme = get_theme(theme_name) if theme_name else None
        if theme and widget_style in theme:
            color_var.set(theme[widget_style])
        else:
            color_var.set("")
    theme_select_var.trace_add("write", update_color_field)
    widget_type_var.trace_add("write", update_color_field)
    widget_type_dropdown.bind("<<ComboboxSelected>>", update_color_field)
    theme_select_dropdown.bind("<<ComboboxSelected>>", update_color_field)

    # --- Save color for selected widget/button type in selected theme ---
    def save_widget_color():
        theme_name = theme_select_var.get()
        widget_idx = widget_type_dropdown.current()
        widget_style = widget_types[widget_idx][0] if widget_idx >= 0 else widget_types[0][0]
        if not theme_name:
            messagebox.showerror("No Theme Selected", "Please select a theme to edit.")
            return
        # Only update custom themes, not built-in themes
        if theme_name in settings.get("custom_themes", {}):
            theme = get_theme(theme_name) or {}
            theme[widget_style] = color_var.get()
            save_theme(theme_name, theme, logger)
            settings["custom_themes"][theme_name] = theme
        else:
            messagebox.showerror("Not a Custom Theme", "You can only edit and save custom themes.")

    # --- Apply selected theme to UI ---
    def apply_selected_theme():
        theme_name = theme_select_var.get()
        if not theme_name:
            messagebox.showerror("No Theme Selected", "Please select a theme to apply.")
            return
        theme = get_theme(theme_name)
        if not theme:
            messagebox.showerror("Theme Not Found", f"Theme '{theme_name}' not found.")
            return
        style = ttkb.Style()
        # List of built-in style keys to avoid reconfiguring
        builtin_styles = {"TScrollbar", "TProgressbar", "TScale", "TSpinbox"}
        background_supported = {"TFrame", "Labelframe", "Panedwindow", "TMenubutton", "TNotebook", "TSeparator", "TPanedwindow", "TTreeview"}
        for style_key, color in theme.items():
            # Only apply to custom style names or safe built-in ones
            if style_key in builtin_styles:
                continue
            if "Menubar" in style_key or "Menu" in style_key:
                continue  # Do not try to style Menubar/Menu via ttk style
            try:
                if ".TButton" in style_key or "Button" in style_key:
                    style.configure(style_key, foreground=color)
                elif any(x in style_key for x in background_supported):
                    style.configure(style_key, background=color)
                elif "Label" in style_key:
                    style.configure(style_key, foreground=color)
                elif ("Entry" in style_key):
                    style.configure(style_key, fieldbackground=color)
                # Do NOT try to style TListbox or TText with fieldbackground (not supported by ttkbootstrap)
                elif ("Text" in style_key or "Listbox" in style_key):
                    continue
                elif ("Scrollbar" in style_key or "Progressbar" in style_key or "Scale" in style_key or "Spinbox" in style_key):
                    if style_key not in builtin_styles:
                        style.configure(style_key, troughcolor=color)
                else:
                    # Only try background for known supported keys
                    pass
            except Exception:
                # Silently skip unsupported style keys
                continue
        if hasattr(root, 'config'):
            root.config(bg=theme.get("TFrame", "#FFFFFF"))
        for child in root.winfo_children():
            if isinstance(child, tk.Menu):
                child.config(bg=theme.get("TMenubar", "#FFFFFF"), fg=theme.get("TLabel", "#000000"))

    # --- Buttons for theme actions ---
    ttkb.Button(theme_frame, text="Save Color for Widget", style="success.TButton", command=save_widget_color).pack(pady=5)
    ttkb.Button(theme_frame, text="Apply Selected Theme", style="primary.TButton", command=apply_selected_theme).pack(pady=5)
    
    # --- Add Theme Button ---
    def refresh_theme_listbox():
        theme_names = list(settings.get("custom_themes", {}).keys())
        theme_select_dropdown["values"] = theme_names
        if theme_names:
            theme_select_var.set(theme_names[0])
        else:
            theme_select_var.set("")

    def add_custom_theme():
        name = simpledialog.askstring("Add Custom Theme", "Enter a name for the new theme:")
        if name:
            themes = load_all_themes()
            if name in themes:
                messagebox.showerror("Theme Exists", f"A custom theme named '{name}' already exists.")
                return
            blank_theme = {
                "accent_color": "#007bff",
                "background_color": "#FFFFFF",
                "text_color": "#000000",
                "warning_color": "#ffc107"
            }
            save_theme(name, blank_theme, logger)
            refresh_theme_listbox()
            theme_select_var.set(name)
    ttkb.Button(theme_frame, text="Add Theme", style="success.TButton", command=add_custom_theme).pack(anchor="w", padx=10, pady=5)

    def save_changes():
        settings["organisation_folder"] = organisation_folder_var.get()
        settings["theme"] = theme_var.get()
        settings["developer_mode"] = developer_mode_var.get()
        settings["logging_level"] = logging_level_var.get()
        settings["logging_components"] = {component: var.get() for component, var in component_vars.items()}
        try:
            ttkb.Style().theme_use(settings["theme"])
        except Exception:
            pass
        from taskmover.config import save_settings as save_settings_func
        import os
        settings_path = os.path.expanduser("~/default_dir/config/settings.yml")
        save_settings_func(settings_path, settings, logger)
        logger.info("Settings saved successfully.")
        settings_window.destroy()
    def close_window():
        settings_window.destroy()
    button_frame = ttkb.Frame(general_frame)
    button_frame.pack(fill="x", pady=10)
    ttkb.Button(button_frame, text="Save", command=save_changes).pack(side="right", padx=10)
    ttkb.Button(button_frame, text="Cancel", command=close_window).pack(side="right", padx=10)
    # Add a button to open the Theme Manager window in the settings UI
    ttkb.Button(general_frame, text="Open Theme Manager", style="info.TButton", command=lambda: open_theme_manager_window(root, ttkb.Style(), logger)).pack(anchor="w", padx=10, pady=10)

def open_theme_manager_window(
    root: tk.Tk,
    style: ttkb.Style,
    logger=None
) -> None:
    """
    Open a window for the user to create, edit, save, load, and delete custom themes.

    Args:
        root (tk.Tk): The root Tkinter window.
        style (ttkb.Style): The ttkbootstrap style object.
        logger: Logger instance for logging events (optional).
    """
    theme_win = ttkb.Toplevel(master=root)
    theme_win.title("Theme Manager")
    theme_win.geometry("500x500")

    # Theme list
    ttkb.Label(theme_win, text="Custom Themes", font=("Helvetica", 14, "bold")).pack(pady=10)
    theme_listbox = tk.Listbox(theme_win)
    theme_listbox.pack(fill="x", padx=10)
    def refresh_theme_listbox():
        theme_listbox.delete(0, tk.END)
        themes = load_all_themes()
        if isinstance(themes, dict):
            for name in themes.keys():
                theme_listbox.insert(tk.END, name)
    refresh_theme_listbox()
    # Add Theme button for standalone theme manager
    def add_custom_theme():
        name = simpledialog.askstring("Add Custom Theme", "Enter a name for the new theme:")
        if name:
            themes = load_all_themes()
            if name in themes:
                messagebox.showerror("Theme Exists", f"A custom theme named '{name}' already exists.")
                return
            blank_theme = {
                "accent_color": "#007bff",
                "background_color": "#FFFFFF",
                "text_color": "#000000",
                "warning_color": "#ffc107"
            }
            save_theme(name, blank_theme, logger)
            refresh_theme_listbox()
            theme_listbox.selection_clear(0, tk.END)
            theme_listbox.selection_set(tk.END)
    ttkb.Button(theme_win, text="Add Theme", style="success.TButton", command=add_custom_theme).pack(pady=5)

    # Theme config fields
    ttkb.Label(theme_win, text="Accent Color:").pack(anchor="w", padx=10, pady=2)
    accent_var = tk.StringVar()
    accent_entry = ttkb.Entry(theme_win, textvariable=accent_var)
    accent_entry.pack(fill="x", padx=10)
    ttkb.Button(theme_win, text="Choose", command=lambda: accent_var.set(colorchooser.askcolor()[1] or accent_var.get())).pack(padx=10, pady=2)

    ttkb.Label(theme_win, text="Background Color:").pack(anchor="w", padx=10, pady=2)
    bg_var = tk.StringVar()
    bg_entry = ttkb.Entry(theme_win, textvariable=bg_var)
    bg_entry.pack(fill="x", padx=10)
    ttkb.Button(theme_win, text="Choose", command=lambda: bg_var.set(colorchooser.askcolor()[1] or bg_var.get())).pack(padx=10, pady=2)

    ttkb.Label(theme_win, text="Text Color:").pack(anchor="w", padx=10, pady=2)
    text_var = tk.StringVar()
    text_entry = ttkb.Entry(theme_win, textvariable=text_var)
    text_entry.pack(fill="x", padx=10)
    ttkb.Button(theme_win, text="Choose", command=lambda: text_var.set(colorchooser.askcolor()[1] or text_var.get())).pack(padx=10, pady=2)

    ttkb.Label(theme_win, text="Warning Button Color:").pack(anchor="w", padx=10, pady=2)
    warning_var = tk.StringVar()
    warning_entry = ttkb.Entry(theme_win, textvariable=warning_var)
    warning_entry.pack(fill="x", padx=10)
    ttkb.Button(theme_win, text="Choose", command=lambda: warning_var.set(colorchooser.askcolor()[1] or warning_var.get())).pack(padx=10, pady=2)

    def load_selected_theme():
        sel = theme_listbox.curselection()
        if sel:
            name = theme_listbox.get(sel[0])
            theme = get_theme(name)
            if theme:
                accent_var.set(theme.get("accent_color", ""))
                bg_var.set(theme.get("background_color", ""))
                text_var.set(theme.get("text_color", ""))
                warning_var.set(theme.get("warning_color", "#ffc107"))

    def save_current_theme():
        name = simpledialog.askstring("Theme Name", "Enter a name for this theme:")
        if name:
            data = {
                "accent_color": accent_var.get(),
                "background_color": bg_var.get(),
                "text_color": text_var.get(),
                "warning_color": warning_var.get()
            }
            save_theme(name, data, logger)
            refresh_theme_listbox()

    def apply_current_theme():
        data = {
            "accent_color": accent_var.get(),
            "background_color": bg_var.get(),
            "text_color": text_var.get(),
            "warning_color": warning_var.get()
        }
        apply_theme(ttkb.Style(), data)
        # Also apply to menubar
        if hasattr(root, 'config'):
            root.config(bg=data.get("background_color", "#FFFFFF"))
        for child in root.winfo_children():
            if isinstance(child, tk.Menu):
                child.config(bg=data.get("background_color", "#FFFFFF"), fg=data.get("text_color", "#000000"))

    def delete_selected_theme():
        sel = theme_listbox.curselection()
        if sel:
            name = theme_listbox.get(sel[0])
            delete_theme(name, logger)
            theme_listbox.delete(sel[0])

    ttkb.Button(theme_win, text="Load Selected", style="info.TButton", command=load_selected_theme).pack(pady=5)
    ttkb.Button(theme_win, text="Save as New Theme", style="success.TButton", command=save_current_theme).pack(pady=5)
    ttkb.Button(theme_win, text="Apply Above Colors", style="primary.TButton", command=apply_current_theme).pack(pady=5)
    ttkb.Button(theme_win, text="Delete Selected", style="danger.TButton", command=delete_selected_theme).pack(pady=5)

def change_theme(
    style: ttkb.Style,
    settings: dict,
    save_settings,
    theme_name: str,
    logger
) -> None:
    """
    Change the current theme and update settings accordingly.

    Args:
        style (ttkb.Style): The ttkbootstrap style object.
        settings (dict): The current application settings.
        save_settings (callable): Function to save updated settings.
        theme_name (str): The name of the theme to apply.
        logger: Logger instance for logging events.
    """
    style.theme_use(theme_name)
    settings["theme"] = theme_name
    try:
        bg = style.lookup("TFrame", "background") or style.lookup("TLabel", "background")
        fg = style.lookup("TLabel", "foreground")
        accent = style.lookup("TButton", "foreground")
        if bg:
            settings["background_color"] = bg
        if fg:
            settings["text_color"] = fg
        if accent:
            settings["accent_color"] = accent
        logger.info(f"Theme colors saved as custom colors: bg={bg}, fg={fg}, accent={accent}")
    except Exception as e:
        logger.warning(f"Could not extract theme colors: {e}")
    save_settings(settings)
    logger.info(f"Theme changed to {theme_name}.")

def choose_color(
    setting: str,
    style: ttkb.Style,
    settings: dict,
    save_settings,
    logger
) -> None:
    """
    Open a color chooser dialog and apply the selected color to the specified setting.

    Args:
        setting (str): The setting to update (e.g., 'Accent', 'Background', 'Text').
        style (ttkb.Style): The ttkbootstrap style object.
        settings (dict): The current application settings.
        save_settings (callable): Function to save updated settings.
        logger: Logger instance for logging events.
    """
    color_code = colorchooser.askcolor(title=f"Choose {setting} Color")[1]
    if color_code:
        if setting == "Accent":
            style.configure('TButton', foreground=color_code)
            style.configure('TLabel', foreground=color_code)
            style.configure('TCheckbutton', foreground=color_code)
        elif setting == "Background":
            style.configure('TFrame', background=color_code)
        elif setting == "Text":
            style.configure('TLabel', foreground=color_code)
        settings[f"{setting.lower()}_color"] = color_code
        save_settings(settings)
        logger.info(f"{setting} color changed to {color_code}.")

def apply_custom_style(
    style: ttkb.Style,
    settings: dict,
    save_settings,
    custom_style: dict,
    logger
) -> None:
    """
    Apply a custom style to the application and update settings.

    Args:
        style (ttkb.Style): The ttkbootstrap style object.
        settings (dict): The current application settings.
        save_settings (callable): Function to save updated settings.
        custom_style (dict): The custom style to apply.
        logger: Logger instance for logging events.
    """
    style.configure('TFrame', background=custom_style["background"])
    style.configure('TLabel', foreground=custom_style["foreground"])
    settings["custom_style"] = custom_style
    save_settings(settings)
    logger.info(f"Applied custom style: {custom_style}")

import tkinter as tk

class Tooltip:
    """Create a tooltip for a given widget, shown after a hover delay."""
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.delay = delay  # milliseconds
        self._after_id = None
        self.widget.bind("<Enter>", self.schedule_show)
        self.widget.bind("<Leave>", self.hide_tip)

    def schedule_show(self, event=None):
        self._after_id = self.widget.after(self.delay, self.show_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, _, cy = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 20
        parent = self.widget.winfo_toplevel()
        self.tipwindow = tw = tk.Toplevel(parent)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        # Ensure tooltip is above its parent window
        tw.transient(parent)
        tw.lift()
        tw.attributes('-topmost', True)
        tw.after(10, lambda: tw.attributes('-topmost', False))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font="tahoma 8 normal")
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()
"""
History and Statistics Components
================================

Components for displaying organization history, statistics,
and analytics for the TaskMover application.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
import json
from .base_component import BaseComponent, ModernButton, ModernCard
from .theme_manager import get_theme_manager


class StatisticsCard(BaseComponent):
    """Card component for displaying statistics."""
    
    def __init__(self, parent: tk.Widget, title: str, value: str, 
                 subtitle: str = "", icon: str = "📊", **kwargs):
        self.title = title
        self.value = value
        self.subtitle = subtitle
        self.icon = icon
        
        super().__init__(parent, **kwargs)
    
    def _create_component(self):
        """Create statistics card."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Configure card
        self.configure(
            bg="white",
            relief="solid",
            bd=1,
            width=200,
            height=120
        )
        self.pack_propagate(False)
        
        # Main content frame
        content_frame = tk.Frame(self, bg="white")
        content_frame.pack(fill="both", expand=True, padx=tokens.spacing["md"], pady=tokens.spacing["md"])
        
        # Icon
        icon_label = tk.Label(
            content_frame,
            text=self.icon,
            font=(tokens.fonts["family"], 24, tokens.fonts["weight_normal"]),
            bg="white",
            fg=tokens.colors["primary"]
        )
        icon_label.pack(pady=(0, tokens.spacing["xs"]))
        
        # Value
        value_label = tk.Label(
            content_frame,
            text=self.value,
            font=(tokens.fonts["family"], int(tokens.fonts["size_heading_1"]), tokens.fonts["weight_bold"]),
            bg="white",
            fg=tokens.colors["text"]
        )
        value_label.pack()
        
        # Title
        title_label = tk.Label(
            content_frame,
            text=self.title,
            font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), tokens.fonts["weight_semibold"]),
            bg="white",
            fg=tokens.colors["text"]
        )
        title_label.pack()
        
        # Subtitle
        if self.subtitle:
            subtitle_label = tk.Label(
                content_frame,
                text=self.subtitle,
                font=(tokens.fonts["family"], int(tokens.fonts["size_caption"]), tokens.fonts["weight_normal"]),
                bg="white",
                fg=tokens.colors["text_secondary"]
            )
            subtitle_label.pack()
    
    def update_value(self, value: str, subtitle: str = None):
        """Update card value and subtitle."""
        self.value = value
        if subtitle is not None:
            self.subtitle = subtitle
        
        # Recreate component to reflect changes
        for widget in self.winfo_children():
            widget.destroy()
        self._create_component()


class HistoryEntry:
    """Data class for history entries."""
    
    def __init__(self, timestamp: datetime, operation: str, source: str, 
                 target: str, status: str, files_count: int = 1):
        self.timestamp = timestamp
        self.operation = operation
        self.source = source
        self.target = target
        self.status = status
        self.files_count = files_count


class HistoryTable(BaseComponent):
    """Table component for displaying organization history."""
    
    def __init__(self, parent: tk.Widget, **kwargs):
        self.history_entries: List[HistoryEntry] = []
        self.tree: Optional[ttk.Treeview] = None
        
        super().__init__(parent, **kwargs)
    
    def _create_component(self):
        """Create history table."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Configure main frame
        self.configure(bg=tokens.colors["background"])
        
        # Header
        header_frame = tk.Frame(self, bg=tokens.colors["background"])
        header_frame.pack(fill="x", pady=(0, tokens.spacing["md"]))
        
        tk.Label(
            header_frame,
            text="Organization History",
            font=(tokens.fonts["family"], int(tokens.fonts["size_heading_2"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(side="left")
        
        # Refresh button
        refresh_btn = ModernButton(
            header_frame,
            text="🔄 Refresh",
            command=self._refresh_history,
            variant="secondary",
            width=100
        )
        refresh_btn.pack(side="right")
        
        # Filter frame
        filter_frame = tk.Frame(self, bg=tokens.colors["background"])
        filter_frame.pack(fill="x", pady=(0, tokens.spacing["md"]))
        
        tk.Label(
            filter_frame,
            text="Filter:",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        ).pack(side="left", padx=(0, tokens.spacing["sm"]))
        
        # Time filter
        self.time_filter = tk.StringVar(value="All Time")
        time_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.time_filter,
            values=["All Time", "Today", "This Week", "This Month", "Last 30 Days"],
            state="readonly",
            width=15
        )
        time_combo.pack(side="left", padx=(0, tokens.spacing["md"]))
        time_combo.bind("<<ComboboxSelected>>", self._on_filter_changed)
        
        # Status filter
        self.status_filter = tk.StringVar(value="All")
        status_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.status_filter,
            values=["All", "Completed", "Failed", "Cancelled"],
            state="readonly",
            width=12
        )
        status_combo.pack(side="left")
        status_combo.bind("<<ComboboxSelected>>", self._on_filter_changed)
        
        # Tree frame
        tree_frame = tk.Frame(self, bg=tokens.colors["background"])
        tree_frame.pack(fill="both", expand=True)
        
        # Create treeview
        columns = ("timestamp", "operation", "source", "target", "files", "status")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            height=15,
            style="Modern.Treeview"
        )
        
        # Configure columns
        self.tree.heading("timestamp", text="Time")
        self.tree.heading("operation", text="Operation")
        self.tree.heading("source", text="Source")
        self.tree.heading("target", text="Target")
        self.tree.heading("files", text="Files")
        self.tree.heading("status", text="Status")
        
        self.tree.column("timestamp", width=120, minwidth=100)
        self.tree.column("operation", width=100, minwidth=80)
        self.tree.column("source", width=200, minwidth=150)
        self.tree.column("target", width=200, minwidth=150)
        self.tree.column("files", width=60, minwidth=50)
        self.tree.column("status", width=80, minwidth=60)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack tree and scrollbars
        self.tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Load sample history
        self._load_sample_history()
    
    def _load_sample_history(self):
        """Load sample history data."""
        now = datetime.now()
        
        sample_entries = [
            HistoryEntry(
                timestamp=now - timedelta(minutes=5),
                operation="Organize",
                source="Downloads",
                target="Documents/PDFs",
                status="Completed",
                files_count=15
            ),
            HistoryEntry(
                timestamp=now - timedelta(hours=2),
                operation="Move",
                source="Desktop",
                target="Pictures/Screenshots",
                status="Completed",
                files_count=8
            ),
            HistoryEntry(
                timestamp=now - timedelta(days=1),
                operation="Archive",
                source="Documents",
                target="Archive/2023",
                status="Completed",
                files_count=234
            ),
            HistoryEntry(
                timestamp=now - timedelta(days=2),
                operation="Cleanup",
                source="Temporary",
                target="Trash",
                status="Failed",
                files_count=5
            ),
            HistoryEntry(
                timestamp=now - timedelta(days=3),
                operation="Organize",
                source="Music",
                target="Music/By Artist",
                status="Completed",
                files_count=156
            )
        ]
        
        self.history_entries = sample_entries
        self._refresh_tree()
    
    def _refresh_tree(self):
        """Refresh tree with filtered history."""
        if not self.tree:
            return
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Apply filters
        filtered_entries = self._apply_filters()
        
        # Add entries to tree
        for entry in filtered_entries:
            timestamp_str = entry.timestamp.strftime("%Y-%m-%d %H:%M")
            status_icon = "✅" if entry.status == "Completed" else "❌" if entry.status == "Failed" else "⏸️"
            
            self.tree.insert("", "end", values=(
                timestamp_str,
                entry.operation,
                entry.source,
                entry.target,
                entry.files_count,
                f"{status_icon} {entry.status}"
            ))
    
    def _apply_filters(self) -> List[HistoryEntry]:
        """Apply current filters to history entries."""
        filtered = self.history_entries.copy()
        
        # Time filter
        time_filter = self.time_filter.get()
        now = datetime.now()
        
        if time_filter == "Today":
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            filtered = [e for e in filtered if e.timestamp >= start_of_day]
        elif time_filter == "This Week":
            start_of_week = now - timedelta(days=now.weekday())
            start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
            filtered = [e for e in filtered if e.timestamp >= start_of_week]
        elif time_filter == "This Month":
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            filtered = [e for e in filtered if e.timestamp >= start_of_month]
        elif time_filter == "Last 30 Days":
            thirty_days_ago = now - timedelta(days=30)
            filtered = [e for e in filtered if e.timestamp >= thirty_days_ago]
        
        # Status filter
        status_filter = self.status_filter.get()
        if status_filter != "All":
            filtered = [e for e in filtered if e.status == status_filter]
        
        # Sort by timestamp (newest first)
        filtered.sort(key=lambda e: e.timestamp, reverse=True)
        
        return filtered
    
    def _on_filter_changed(self, event):
        """Handle filter change."""
        self._refresh_tree()
    
    def _refresh_history(self):
        """Refresh history data."""
        # In a real implementation, this would reload from storage
        self._refresh_tree()
    
    def add_entry(self, entry: HistoryEntry):
        """Add new history entry."""
        self.history_entries.insert(0, entry)  # Add to beginning
        self._refresh_tree()


class StatisticsDashboard(BaseComponent):
    """Dashboard showing organization statistics."""
    
    def __init__(self, parent: tk.Widget, **kwargs):
        self.stats_cards: List[StatisticsCard] = []
        
        super().__init__(parent, **kwargs)
    
    def _create_component(self):
        """Create statistics dashboard."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Configure main frame
        self.configure(bg=tokens.colors["background"])
        
        # Header
        header_label = tk.Label(
            self,
            text="Statistics Overview",
            font=(tokens.fonts["family"], int(tokens.fonts["size_heading_2"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        )
        header_label.pack(fill="x", pady=(0, tokens.spacing["lg"]))
        
        # Stats cards grid
        cards_frame = tk.Frame(self, bg=tokens.colors["background"])
        cards_frame.pack(fill="x", pady=(0, tokens.spacing["xl"]))
        
        # Row 1
        row1_frame = tk.Frame(cards_frame, bg=tokens.colors["background"])
        row1_frame.pack(fill="x", pady=(0, tokens.spacing["md"]))
        
        # Total files organized
        total_files_card = StatisticsCard(
            row1_frame,
            title="Total Files Organized",
            value="2,459",
            subtitle="All time",
            icon="📁"
        )
        total_files_card.pack(side="left", padx=(0, tokens.spacing["md"]))
        self.stats_cards.append(total_files_card)
        
        # This month
        this_month_card = StatisticsCard(
            row1_frame,
            title="This Month",
            value="347",
            subtitle="12% increase",
            icon="📈"
        )
        this_month_card.pack(side="left", padx=(0, tokens.spacing["md"]))
        self.stats_cards.append(this_month_card)
        
        # Space saved
        space_saved_card = StatisticsCard(
            row1_frame,
            title="Space Organized",
            value="23.4 GB",
            subtitle="Duplicates removed",
            icon="💾"
        )
        space_saved_card.pack(side="left", padx=(0, tokens.spacing["md"]))
        self.stats_cards.append(space_saved_card)
        
        # Active rules
        active_rules_card = StatisticsCard(
            row1_frame,
            title="Active Rules",
            value="12",
            subtitle="3 auto-executing",
            icon="⚙️"
        )
        active_rules_card.pack(side="left")
        self.stats_cards.append(active_rules_card)
        
        # Row 2
        row2_frame = tk.Frame(cards_frame, bg=tokens.colors["background"])
        row2_frame.pack(fill="x")
        
        # Success rate
        success_rate_card = StatisticsCard(
            row2_frame,
            title="Success Rate",
            value="98.2%",
            subtitle="Last 30 days",
            icon="✅"
        )
        success_rate_card.pack(side="left", padx=(0, tokens.spacing["md"]))
        self.stats_cards.append(success_rate_card)
        
        # Average time
        avg_time_card = StatisticsCard(
            row2_frame,
            title="Avg. Processing Time",
            value="2.3s",
            subtitle="Per file",
            icon="⏱️"
        )
        avg_time_card.pack(side="left", padx=(0, tokens.spacing["md"]))
        self.stats_cards.append(avg_time_card)
        
        # Conflicts resolved
        conflicts_card = StatisticsCard(
            row2_frame,
            title="Conflicts Resolved",
            value="47",
            subtitle="This month",
            icon="🔧"
        )
        conflicts_card.pack(side="left", padx=(0, tokens.spacing["md"]))
        self.stats_cards.append(conflicts_card)
        
        # Patterns used
        patterns_card = StatisticsCard(
            row2_frame,
            title="Patterns Active",
            value="8",
            subtitle="Most: @documents",
            icon="🎯"
        )
        patterns_card.pack(side="left")
        self.stats_cards.append(patterns_card)
        
        # Charts section
        charts_frame = tk.LabelFrame(
            self,
            text="Trends",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_semibold"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text"]
        )
        charts_frame.pack(fill="both", expand=True, pady=(tokens.spacing["xl"], 0))
        
        # Placeholder for charts
        chart_placeholder = tk.Label(
            charts_frame,
            text="📊 Charts and trends visualization\\n(Coming soon)",
            font=(tokens.fonts["family"], int(tokens.fonts["size_body"]), tokens.fonts["weight_normal"]),
            bg=tokens.colors["background"],
            fg=tokens.colors["text_secondary"]
        )
        chart_placeholder.pack(expand=True, pady=tokens.spacing["xl"])
    
    def update_statistics(self, stats: Dict[str, Any]):
        """Update statistics values."""
        # This would update the cards with real data
        pass


class HistoryAndStatsView(BaseComponent):
    """Complete history and statistics view."""
    
    def __init__(self, parent: tk.Widget, **kwargs):
        self.stats_dashboard: Optional[StatisticsDashboard] = None
        self.history_table: Optional[HistoryTable] = None
        
        super().__init__(parent, **kwargs)
    
    def _create_component(self):
        """Create history and statistics view."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        # Configure main frame
        self.configure(bg=tokens.colors["background"])
        
        # Create notebook for stats and history
        self.notebook = ttk.Notebook(self, style="Modern.TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=tokens.spacing["lg"], pady=tokens.spacing["lg"])
        
        # Statistics tab
        stats_frame = tk.Frame(self.notebook, bg=tokens.colors["background"])
        self.notebook.add(stats_frame, text="Statistics")
        
        self.stats_dashboard = StatisticsDashboard(stats_frame)
        self.stats_dashboard.pack(fill="both", expand=True, padx=tokens.spacing["lg"], pady=tokens.spacing["lg"])
        
        # History tab
        history_frame = tk.Frame(self.notebook, bg=tokens.colors["background"])
        self.notebook.add(history_frame, text="History")
        
        self.history_table = HistoryTable(history_frame)
        self.history_table.pack(fill="both", expand=True, padx=tokens.spacing["lg"], pady=tokens.spacing["lg"])
    
    def add_history_entry(self, entry: HistoryEntry):
        """Add new history entry."""
        if self.history_table:
            self.history_table.add_entry(entry)
    
    def update_statistics(self, stats: Dict[str, Any]):
        """Update statistics."""
        if self.stats_dashboard:
            self.stats_dashboard.update_statistics(stats)

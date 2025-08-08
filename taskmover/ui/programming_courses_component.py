"""
Programming Courses Component
============================

Educational resource component providing information about free interactive
programming courses, integrated with TaskMover's UI system.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Any
import webbrowser
import logging

from .base_component import BaseComponent, ComponentState
from .theme_manager import get_theme_manager

logger = logging.getLogger(__name__)


class CourseData:
    """Data structure for programming course information."""
    
    def __init__(
        self,
        title: str,
        provider: str,
        url: str,
        description: str,
        language: str,
        level: str,
        features: List[str]
    ):
        self.title = title
        self.provider = provider
        self.url = url
        self.description = description
        self.language = language
        self.level = level
        self.features = features


class ProgrammingCoursesComponent(BaseComponent):
    """Component displaying curated list of free interactive programming courses."""
    
    # Curated list of high-quality free interactive programming courses
    COURSES_DATA = [
        CourseData(
            title="freeCodeCamp",
            provider="freeCodeCamp.org",
            url="https://www.freecodecamp.org/",
            description="Comprehensive full-stack curriculum with interactive coding challenges, projects, and certifications. Covers web development, data science, and more.",
            language="JavaScript, Python, HTML/CSS, React, Node.js",
            level="Beginner to Advanced",
            features=["Interactive challenges", "Real projects", "Free certificates", "Community forum"]
        ),
        CourseData(
            title="Codecademy Free Courses",
            provider="Codecademy",
            url="https://www.codecademy.com/catalog/subject/all",
            description="Interactive coding lessons with hands-on practice. Free tier includes basic courses in multiple programming languages.",
            language="Python, JavaScript, HTML/CSS, Java, C++",
            level="Beginner to Intermediate",
            features=["Interactive exercises", "Immediate feedback", "Progress tracking", "Code editor"]
        ),
        CourseData(
            title="Khan Academy Programming",
            provider="Khan Academy",
            url="https://www.khanacademy.org/computing/computer-programming",
            description="Interactive programming courses with visual feedback and creative projects. Great for beginners and visual learners.",
            language="JavaScript, HTML/CSS, SQL",
            level="Beginner",
            features=["Visual programming", "Creative projects", "Step-by-step tutorials", "Community showcase"]
        ),
        CourseData(
            title="The Odin Project",
            provider="The Odin Project",
            url="https://www.theodinproject.com/",
            description="Free comprehensive web development curriculum with hands-on projects and real-world applications.",
            language="JavaScript, Ruby, HTML/CSS, Git",
            level="Beginner to Intermediate",
            features=["Project-based learning", "Open source", "Community support", "Real applications"]
        ),
        CourseData(
            title="SoloLearn",
            provider="SoloLearn",
            url="https://www.sololearn.com/",
            description="Mobile-friendly interactive programming courses with code challenges and community features.",
            language="Python, Java, C++, JavaScript, PHP",
            level="Beginner to Intermediate",
            features=["Mobile app", "Code challenges", "Community", "Progress tracking"]
        ),
        CourseData(
            title="CS50x - Introduction to Computer Science",
            provider="Harvard University (edX)",
            url="https://cs50.harvard.edu/x/",
            description="Harvard's renowned computer science course with interactive problem sets and a supportive online community.",
            language="C, Python, SQL, JavaScript, HTML/CSS",
            level="Beginner to Intermediate",
            features=["University-level content", "Problem sets", "Video lectures", "Online IDE"]
        )
    ]
    
    def __init__(self, parent: tk.Widget, **kwargs):
        self.selected_course: Optional[CourseData] = None
        self.search_var = tk.StringVar()
        self.level_var = tk.StringVar(value="All Levels")
        self.filtered_courses = self.COURSES_DATA.copy()
        
        super().__init__(parent, **kwargs)
        
        # Set up search filtering
        self.search_var.trace_add('write', self._on_search_change)
        self.level_var.trace_add('write', self._on_filter_change)
    
    def _create_component(self):
        """Create the programming courses display component."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        self.configure(bg=tokens.colors["background"])
        
        # Main container with padding
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        self._create_header(main_frame)
        
        # Filters
        self._create_filters(main_frame)
        
        # Courses list
        self._create_courses_list(main_frame)
        
        # Course details
        self._create_course_details(main_frame)
        
        self._update_display()
    
    def _create_header(self, parent: tk.Widget):
        """Create component header."""
        theme = get_theme_manager()
        tokens = theme.get_current_tokens()
        
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text="🎓 Free Interactive Programming Courses",
            font=(tokens.fonts["family"], tokens.fonts["size_h2"], "bold")
        )
        title_label.pack(anchor=tk.W)
        
        # Subtitle
        subtitle_label = ttk.Label(
            header_frame,
            text="Curated collection of high-quality, free interactive programming resources",
            font=(tokens.fonts["family"], tokens.fonts["size_body"])
        )
        subtitle_label.pack(anchor=tk.W, pady=(5, 0))
    
    def _create_filters(self, parent: tk.Widget):
        """Create search and filter controls."""
        filters_frame = ttk.Frame(parent)
        filters_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Search box
        search_frame = ttk.Frame(filters_frame)
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(5, 20))
        
        # Level filter
        level_frame = ttk.Frame(filters_frame)
        level_frame.pack(side=tk.RIGHT)
        
        ttk.Label(level_frame, text="Level:").pack(side=tk.LEFT)
        level_combo = ttk.Combobox(
            level_frame,
            textvariable=self.level_var,
            values=["All Levels", "Beginner", "Beginner to Intermediate", "Beginner to Advanced", "Intermediate"],
            state="readonly",
            width=20
        )
        level_combo.pack(side=tk.LEFT, padx=(5, 0))
    
    def _create_courses_list(self, parent: tk.Widget):
        """Create scrollable list of courses."""
        list_frame = ttk.LabelFrame(parent, text="Available Courses", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create Treeview for course list
        columns = ("Provider", "Level", "Languages")
        self.course_tree = ttk.Treeview(list_frame, columns=columns, show="tree headings", height=8)
        
        # Configure columns
        self.course_tree.heading("#0", text="Course Title")
        self.course_tree.column("#0", width=250, minwidth=200)
        
        for col in columns:
            self.course_tree.heading(col, text=col)
            self.course_tree.column(col, width=150, minwidth=100)
        
        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.course_tree.yview)
        tree_scroll_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.course_tree.xview)
        self.course_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        # Pack components
        self.course_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind selection event
        self.course_tree.bind("<<TreeviewSelect>>", self._on_course_select)
        self.course_tree.bind("<Double-1>", self._on_course_double_click)
    
    def _create_course_details(self, parent: tk.Widget):
        """Create course details display."""
        details_frame = ttk.LabelFrame(parent, text="Course Details", padding=10)
        details_frame.pack(fill=tk.X)
        
        # Details text widget
        self.details_text = tk.Text(
            details_frame,
            height=6,
            wrap=tk.WORD,
            state=tk.DISABLED,
            relief=tk.FLAT,
            borderwidth=0
        )
        self.details_text.pack(fill=tk.X, pady=(0, 10))
        
        # Action buttons
        button_frame = ttk.Frame(details_frame)
        button_frame.pack(fill=tk.X)
        
        self.visit_button = ttk.Button(
            button_frame,
            text="🌐 Visit Course",
            command=self._visit_course,
            state=tk.DISABLED
        )
        self.visit_button.pack(side=tk.LEFT)
        
        # Info label
        info_label = ttk.Label(
            button_frame,
            text="💡 Tip: Double-click a course to open it directly",
            font=("Arial", 9, "italic")
        )
        info_label.pack(side=tk.RIGHT)
    
    def _update_display(self):
        """Update the course list display based on current filters."""
        # Clear current items
        for item in self.course_tree.get_children():
            self.course_tree.delete(item)
        
        # Add filtered courses
        for course in self.filtered_courses:
            self.course_tree.insert(
                "",
                tk.END,
                text=course.title,
                values=(course.provider, course.level, course.language)
            )
    
    def _filter_courses(self):
        """Filter courses based on search and level criteria."""
        search_term = self.search_var.get().lower()
        level_filter = self.level_var.get()
        
        self.filtered_courses = []
        
        for course in self.COURSES_DATA:
            # Apply search filter
            if search_term and search_term not in course.title.lower() and search_term not in course.description.lower() and search_term not in course.language.lower():
                continue
            
            # Apply level filter
            if level_filter != "All Levels" and level_filter not in course.level:
                continue
            
            self.filtered_courses.append(course)
        
        self._update_display()
    
    def _on_search_change(self, *args):
        """Handle search input changes."""
        self._filter_courses()
    
    def _on_filter_change(self, *args):
        """Handle filter changes."""
        self._filter_courses()
    
    def _on_course_select(self, event):
        """Handle course selection."""
        selection = self.course_tree.selection()
        if not selection:
            self.selected_course = None
            self.visit_button.configure(state=tk.DISABLED)
            self._update_course_details(None)
            return
        
        # Get selected course
        item = self.course_tree.item(selection[0])
        course_title = item["text"]
        
        # Find course data
        self.selected_course = next(
            (course for course in self.filtered_courses if course.title == course_title),
            None
        )
        
        if self.selected_course:
            self.visit_button.configure(state=tk.NORMAL)
            self._update_course_details(self.selected_course)
    
    def _on_course_double_click(self, event):
        """Handle double-click on course (opens directly)."""
        if self.selected_course:
            self._visit_course()
    
    def _update_course_details(self, course: Optional[CourseData]):
        """Update course details display."""
        self.details_text.configure(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        
        if course:
            details = f"""Description: {course.description}

Languages: {course.language}
Level: {course.level}
Provider: {course.provider}

Key Features:
{chr(10).join(f'• {feature}' for feature in course.features)}"""
            self.details_text.insert(tk.END, details)
        else:
            self.details_text.insert(tk.END, "Select a course to view details...")
        
        self.details_text.configure(state=tk.DISABLED)
    
    def _visit_course(self):
        """Open selected course in web browser."""
        if self.selected_course:
            try:
                webbrowser.open(self.selected_course.url)
                logger.info(f"Opened course: {self.selected_course.title}")
            except Exception as e:
                logger.error(f"Failed to open course URL: {e}")
    
    def get_course_count(self) -> int:
        """Get the number of available courses."""
        return len(self.filtered_courses)
    
    def search_courses(self, query: str) -> List[CourseData]:
        """Programmatically search courses."""
        self.search_var.set(query)
        return self.filtered_courses.copy()


# For testing and standalone usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Programming Courses")
    root.geometry("800x600")
    
    app = ProgrammingCoursesComponent(root)
    app.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()
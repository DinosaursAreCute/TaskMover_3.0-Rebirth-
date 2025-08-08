"""
Test for Programming Courses Component
=====================================

Tests the programming courses component functionality.
"""

import tkinter as tk
from unittest.mock import MagicMock, patch
import pytest

from taskmover.ui.programming_courses_component import ProgrammingCoursesComponent, CourseData


class TestProgrammingCoursesComponent:
    """Test cases for programming courses component."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during testing
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if self.root:
            self.root.destroy()
    
    def test_component_creation(self):
        """Test component can be created successfully."""
        component = ProgrammingCoursesComponent(self.root)
        assert component is not None
        assert hasattr(component, 'COURSES_DATA')
        assert len(component.COURSES_DATA) > 0
    
    def test_courses_data_structure(self):
        """Test that courses data has the expected structure."""
        component = ProgrammingCoursesComponent(self.root)
        
        for course in component.COURSES_DATA:
            assert isinstance(course, CourseData)
            assert course.title
            assert course.provider
            assert course.url
            assert course.description
            assert course.language
            assert course.level
            assert isinstance(course.features, list)
            assert len(course.features) > 0
    
    def test_course_filtering(self):
        """Test course search and filtering functionality."""
        component = ProgrammingCoursesComponent(self.root)
        
        # Test search functionality
        original_count = len(component.COURSES_DATA)
        component.search_var.set("JavaScript")
        component._filter_courses()
        
        # Should have fewer or equal courses after filtering
        assert len(component.filtered_courses) <= original_count
        
        # Test that filtered courses contain the search term
        for course in component.filtered_courses:
            assert ("javascript" in course.title.lower() or 
                   "javascript" in course.description.lower() or 
                   "javascript" in course.language.lower())
    
    def test_level_filtering(self):
        """Test level filtering functionality."""
        component = ProgrammingCoursesComponent(self.root)
        
        # Test beginner level filter
        component.level_var.set("Beginner")
        component._filter_courses()
        
        for course in component.filtered_courses:
            assert "beginner" in course.level.lower()
    
    def test_get_course_count(self):
        """Test getting course count."""
        component = ProgrammingCoursesComponent(self.root)
        count = component.get_course_count()
        assert count == len(component.COURSES_DATA)
        
        # Test after filtering
        component.search_var.set("freeCodeCamp")
        component._filter_courses()
        filtered_count = component.get_course_count()
        assert filtered_count <= count
    
    @patch('webbrowser.open')
    def test_visit_course(self, mock_browser):
        """Test visiting a course URL."""
        component = ProgrammingCoursesComponent(self.root)
        
        # Set a selected course
        component.selected_course = component.COURSES_DATA[0]
        
        # Call visit course
        component._visit_course()
        
        # Verify browser was called with correct URL
        mock_browser.assert_called_once_with(component.COURSES_DATA[0].url)
    
    def test_search_courses_method(self):
        """Test programmatic course search."""
        component = ProgrammingCoursesComponent(self.root)
        
        # Search for Python courses
        results = component.search_courses("Python")
        
        # Verify results
        assert isinstance(results, list)
        for course in results:
            assert isinstance(course, CourseData)
            assert ("python" in course.title.lower() or 
                   "python" in course.description.lower() or 
                   "python" in course.language.lower())


class TestCourseData:
    """Test cases for CourseData class."""
    
    def test_course_data_creation(self):
        """Test creating CourseData instances."""
        course = CourseData(
            title="Test Course",
            provider="Test Provider",
            url="https://example.com",
            description="Test description",
            language="Python",
            level="Beginner",
            features=["Feature 1", "Feature 2"]
        )
        
        assert course.title == "Test Course"
        assert course.provider == "Test Provider"
        assert course.url == "https://example.com"
        assert course.description == "Test description"
        assert course.language == "Python"
        assert course.level == "Beginner"
        assert course.features == ["Feature 1", "Feature 2"]


# Integration test to ensure the component works with the main application
def test_integration_with_main_app():
    """Test that the component integrates properly with the main application."""
    try:
        root = tk.Tk()
        root.withdraw()
        
        # Test component creation
        component = ProgrammingCoursesComponent(root)
        component.pack()
        
        # Verify component is properly initialized
        assert component.winfo_exists()
        assert hasattr(component, 'course_tree')
        assert hasattr(component, 'details_text')
        assert hasattr(component, 'visit_button')
        
        root.destroy()
    except Exception as e:
        pytest.fail(f"Integration test failed: {e}")
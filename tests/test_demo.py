"""
Demo Tests for Professional Test Runner
=======================================

Simple tests to demonstrate the test runner's features:
- Passing tests (green)
- Failing tests (red)
- Error tests (red) 
- Skipped tests (yellow)
"""

import pytest
import time


def test_simple_pass():
    """This test should pass."""
    assert 1 + 1 == 2


def test_another_pass():
    """Another passing test."""
    assert "hello".upper() == "HELLO"


def test_simple_fail():
    """This test should fail."""
    assert 1 + 1 == 3, "Basic math failure for demo"


def test_assertion_fail():
    """Another failing test."""
    assert "hello" == "world", "String comparison failure for demo"


def test_will_error():
    """This test should error."""
    raise ValueError("Demo error for testing")


@pytest.mark.skip(reason="Demo skipped test")
def test_skipped():
    """This test should be skipped."""
    assert True


def test_slow_pass():
    """A slower passing test."""
    time.sleep(0.1)
    assert True


def test_with_output():
    """Test with some output."""
    print("This is some test output")
    print("Multiple lines of output")
    assert True


class TestClassDemo:
    """Demo test class."""
    
    def test_class_pass(self):
        """Passing test in a class."""
        assert len([1, 2, 3]) == 3
    
    def test_class_fail(self):
        """Failing test in a class."""
        assert len([1, 2, 3]) == 5, "List length mismatch"

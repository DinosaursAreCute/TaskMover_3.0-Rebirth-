#!/usr/bin/env python3
"""
Test script for Rule Management UI components.
"""

import tkinter as tk
from pathlib import Path
from uuid import UUID

# Mock services for testing
class MockRuleService:
    def __init__(self):
        pass
    
    def list_rules(self, include_disabled=True):
        from taskmover.core.rules.models import Rule
        return [
            Rule(
                id=UUID(int=1),
                name="Test Rule 1",
                description="Test rule for demonstration",
                pattern_id=UUID(int=100),
                destination_path=Path("test/destination"),
                is_enabled=True,
                priority=10
            )
        ]
    
    def get_rule(self, rule_id):
        rules = self.list_rules()
        return next((r for r in rules if r.id == rule_id), None)
    
    def validate_rule(self, rule):
        from taskmover.core.rules.models import RuleValidationResult
        return RuleValidationResult(rule_id=rule.id, is_valid=True)

class MockPatternService:
    def __init__(self):
        pass
    
    def list_patterns(self):
        return []

def main():
    """Test Rule Management components."""
    from taskmover.ui.rule_management_components import RuleManagementView
    
    root = tk.Tk()
    root.title("Rule Management Test")
    root.geometry("1000x700")
    
    # Create mock services
    rule_service = MockRuleService()
    pattern_service = MockPatternService()
    
    # Create rule management view
    rule_view = RuleManagementView(
        root,
        rule_service=rule_service,
        pattern_service=pattern_service
    )
    rule_view.pack(fill="both", expand=True, padx=20, pady=20)
    
    print("Rule Management UI test started...")
    print("This will test the rule management components with mock data.")
    
    root.mainloop()

if __name__ == "__main__":
    main()

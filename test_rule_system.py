"""
Rule System Test

Basic test to verify rule system functionality.
"""

import tempfile
from pathlib import Path
from uuid import uuid4

from taskmover.core.patterns import PatternSystem
from taskmover.core.conflict_resolution import ConflictManager
from taskmover.core.rules import RuleService, Rule, ErrorHandlingBehavior


def test_rule_system():
    """Test basic rule system functionality."""
    print("Testing Rule System...")
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        storage_path = temp_path / "storage"
        source_dir = temp_path / "source"
        dest_dir = temp_path / "destination"
        
        # Create directories
        storage_path.mkdir(parents=True)
        source_dir.mkdir(parents=True)
        dest_dir.mkdir(parents=True)
        
        # Create test files
        test_files = [
            source_dir / "document1.txt",
            source_dir / "document2.txt", 
            source_dir / "image.jpg",
            source_dir / "data.csv"
        ]
        
        for file_path in test_files:
            file_path.write_text(f"Test content for {file_path.name}")
        
        print(f"Created {len(test_files)} test files")
        
        # Initialize services
        pattern_system = PatternSystem(storage_path / "patterns")
        pattern_system.initialize()
        
        conflict_manager = ConflictManager()
        
        rule_service = RuleService(
            pattern_system=pattern_system,
            conflict_manager=conflict_manager,
            storage_path=storage_path / "rules"
        )
        
        print("Initialized services")
        
        # Create a pattern
        pattern = pattern_system.create_pattern(
            user_expression="*.txt",
            name="Text Files",
            description="All text files"
        )
        
        print(f"Created pattern: {pattern.name}")
        
        # Create a rule
        rule = rule_service.create_rule(
            name="Move Text Files",
            pattern_id=pattern.id,
            destination_path=dest_dir,
            description="Move all text files to destination",
            priority=10
        )
        
        print(f"Created rule: {rule.name}")
        
        # Test rule validation
        validation_result = rule_service.validate_rule(rule)
        print(f"Rule validation: {'PASSED' if validation_result.is_valid else 'FAILED'}")
        
        if not validation_result.is_valid:
            for error in validation_result.errors:
                print(f"  Error: {error}")
        
        # Execute rule (dry run first)
        print("\nExecuting rule (dry run)...")
        dry_result = rule_service.execute_rule(rule.id, source_dir, dry_run=True)
        
        print(f"Dry run result: {dry_result.summary}")
        print(f"Files that would be moved: {len(dry_result.matched_files)}")
        
        # Execute rule for real
        print("\nExecuting rule (actual)...")
        exec_result = rule_service.execute_rule(rule.id, source_dir, dry_run=False)
        
        print(f"Execution result: {exec_result.summary}")
        print(f"Files moved: {exec_result.files_moved}")
        print(f"Files failed: {exec_result.files_failed}")
        
        # Check destination
        moved_files = list(dest_dir.glob("*"))
        print(f"Files in destination: {len(moved_files)}")
        
        for moved_file in moved_files:
            print(f"  {moved_file.name}")
        
        # Test conflict detection
        print("\nTesting conflict detection...")
        
        # Create another rule with same pattern
        rule2 = rule_service.create_rule(
            name="Another Text Rule",
            pattern_id=pattern.id,
            destination_path=dest_dir,
            description="Another rule using same pattern",
            priority=5
        )
        
        conflicts = rule_service.detect_rule_conflicts()
        print(f"Detected {len(conflicts)} conflicts")
        
        for conflict in conflicts:
            print(f"  {conflict.conflict_type}: {conflict.message}")
        
        # Test rule listing
        all_rules = rule_service.list_rules()
        active_rules = rule_service.list_rules(active_only=True)
        
        print(f"\nTotal rules: {len(all_rules)}")
        print(f"Active rules: {len(active_rules)}")
        
        # Get statistics
        stats = rule_service.get_statistics()
        print(f"\nRule service statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print("\n✅ Rule system test completed successfully!")


if __name__ == "__main__":
    test_rule_system()

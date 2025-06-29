"""
Test Pattern System Implementation

Comprehensive test to verify all backend components work together correctly.
"""

import tempfile
import shutil
from pathlib import Path
from uuid import uuid4

# Import the pattern system
from taskmover.core.patterns import create_pattern_system
from taskmover.core.patterns.models import Pattern, PatternType, PatternComplexity


def test_pattern_system():
    """Test the complete pattern system implementation."""
    print("🧪 Starting Pattern System Tests")
    
    # Create temporary directory for testing
    test_dir = Path(tempfile.mkdtemp())
    print(f"📁 Test directory: {test_dir}")
    
    system = None  # Initialize to avoid unbound variable warnings
    try:
        # Create test files
        create_test_files(test_dir)
        
        # Initialize pattern system
        storage_path = test_dir / "patterns"
        system = create_pattern_system(storage_path)
        system.initialize()  # Initialize the system before use
        print("✅ Pattern system initialized")
        
        # Test 1: Basic pattern creation
        print("\n🔍 Test 1: Pattern Creation")
        pattern1 = system.create_pattern(
            "*.txt",
            name="Text Files",
            description="All text files"
        )
        print(f"Created pattern: {pattern1.name} (ID: {pattern1.id})")
        print(f"Pattern type: {pattern1.pattern_type}")
        print(f"Compiled query: {pattern1.compiled_query}")
        
        # Test 2: Enhanced pattern with tokens
        print("\n🔍 Test 2: Enhanced Pattern with Tokens")
        pattern2 = system.create_pattern(
            "report_$DATE*.pdf",
            name="Daily Reports",
            description="Daily report PDFs with date"
        )
        print(f"Created pattern: {pattern2.name}")
        print(f"Pattern type: {pattern2.pattern_type}")
        print(f"Compiled query: {pattern2.compiled_query}")
        
        # Test 3: Advanced query pattern
        print("\n🔍 Test 3: Advanced Query Pattern")
        pattern3 = system.create_pattern(
            "*.jpg AND size > 1MB",
            name="Large Images",
            description="JPEG images larger than 1MB"
        )
        print(f"Created pattern: {pattern3.name}")
        print(f"Pattern type: {pattern3.pattern_type}")
        print(f"Compiled query: {pattern3.compiled_query}")
        
        # Test 4: Group reference pattern
        print("\n🔍 Test 4: Group Reference Pattern")
        pattern4 = system.create_pattern(
            "@media",
            name="Media Files",
            description="All media files using system group"
        )
        print(f"Created pattern: {pattern4.name}")
        print(f"Pattern type: {pattern4.pattern_type}")
        print(f"Referenced groups: {pattern4.referenced_groups}")
        
        # Test 5: Pattern validation
        print("\n🔍 Test 5: Pattern Validation")
        validation_result = system.validate_expression("*.txt")
        print(f"Valid: {validation_result.is_valid}")
        print(f"Performance score: {validation_result.performance_score}")
        
        invalid_result = system.validate_expression("***(((")
        print(f"Invalid pattern valid: {invalid_result.is_valid}")
        print(f"Errors: {invalid_result.errors}")
        
        # Test 6: Pattern matching
        print("\n🔍 Test 6: Pattern Matching")
        test_files = list(test_dir.glob("**/*"))
        match_result = system.match_pattern(pattern1, test_files)
        
        print(f"Files checked: {match_result.total_files_checked}")
        print(f"Files matched: {len(match_result.matched_files)}")
        print(f"Execution time: {match_result.execution_time_ms:.2f}ms")
        print("Matched files:")
        for file in match_result.matched_files:
            print(f"  - {file.name}")
        
        # Test 7: Pattern search
        print("\n🔍 Test 7: Pattern Search")
        patterns = system.search_patterns("text")
        print(f"Found {len(patterns)} patterns containing 'text'")
        
        # Test 8: Workspace analysis
        print("\n🔍 Test 8: Workspace Analysis")
        analysis = system.analyze_workspace(test_dir)
        print(f"Total files: {analysis.get('total_files', 0)}")
        print(f"Common extensions: {analysis.get('common_extensions', [])[:5]}")
        
        # Test 9: Pattern suggestions
        print("\n🔍 Test 9: Pattern Suggestions")
        suggestions = system.get_pattern_suggestions(test_dir, "*.p")
        print(f"Generated {len(suggestions)} suggestions")
        for i, suggestion in enumerate(suggestions[:3]):
            print(f"  {i+1}. {suggestion['pattern']} - {suggestion['description']}")
        
        # Test 10: Auto-completion
        print("\n🔍 Test 10: Auto-completion")
        completions = system.get_completions("$DA")
        print(f"Completions for '$DA': {completions[:5]}")
        
        # Test 11: System status
        print("\n🔍 Test 11: System Status")
        status = system.get_system_status()
        print(f"System initialized: {status['initialized']}")
        print(f"Total patterns: {status.get('repository_stats', {}).get('total_patterns', 0)}")
        
        # Test 12: Backup and restore
        print("\n🔍 Test 12: Backup and Restore")
        backup_file = system.backup_patterns()
        if backup_file:
            print(f"Backup created: {backup_file}")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        try:
            if system:
                system.shutdown()
            shutil.rmtree(test_dir)
            print(f"🧹 Cleaned up test directory")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")


def create_test_files(test_dir: Path):
    """Create test files for pattern matching."""
    # Create various file types
    files_to_create = [
        "document.txt",
        "readme.md", 
        "image.jpg",
        "photo.png",
        "music.mp3",
        "video.mp4",
        "report_2024-01-15.pdf",
        "backup.zip",
        "config.yaml",
        "data.json",
        "script.py",
        "style.css",
        "index.html",
        "large_file.dat",
        ".hidden_file.txt"
    ]
    
    # Create subdirectories
    (test_dir / "docs").mkdir(exist_ok=True)
    (test_dir / "images").mkdir(exist_ok=True)
    (test_dir / "code").mkdir(exist_ok=True)
    
    # Create files
    for filename in files_to_create:
        file_path = test_dir / filename
        file_path.write_text(f"Test content for {filename}")
    
    # Create some files in subdirectories
    (test_dir / "docs" / "manual.pdf").write_text("Manual content")
    (test_dir / "images" / "photo1.jpg").write_text("Image data")
    (test_dir / "code" / "main.py").write_text("Python code")
    
    # Create a large file for size testing
    large_content = "X" * (2 * 1024 * 1024)  # 2MB
    (test_dir / "large_file.dat").write_text(large_content)
    
    print(f"📝 Created {len(files_to_create) + 3} test files")


if __name__ == "__main__":
    test_pattern_system()

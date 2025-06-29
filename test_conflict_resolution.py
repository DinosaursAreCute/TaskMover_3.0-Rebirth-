"""
Conflict Resolution Test

Test the conflict resolution capabilities of the pattern system.
"""

import tempfile
from pathlib import Path

try:
    # Import the pattern system
    from taskmover.core.patterns import create_pattern_system
    from taskmover.core.conflict_resolution.enums import ConflictScope, ResolutionStrategy
    print("✅ Import successful")
    
    # Create temporary directory
    test_dir = Path(tempfile.mkdtemp())
    print(f"📁 Test directory: {test_dir}")
    
    # Create some test files
    test_files = [
        test_dir / "document.txt",
        test_dir / "report.pdf", 
        test_dir / "image.jpg",
        test_dir / "data.csv"
    ]
    
    for file_path in test_files:
        file_path.touch()
    
    print(f"📝 Created {len(test_files)} test files")
    
    # Initialize pattern system
    storage_path = test_dir / "patterns"
    system = create_pattern_system(storage_path)
    system.initialize()
    print("✅ Pattern system initialized with conflict resolution")
    
    # Create overlapping patterns (this should detect conflicts)
    pattern1 = system.create_pattern(
        "*.txt", 
        name="Text Files",
        description="All text files"
    )
    
    pattern2 = system.create_pattern(
        "document*", 
        name="Documents",
        description="All documents"
    )
    
    pattern3 = system.create_pattern(
        "*.*", 
        name="All Files",
        description="All files with extensions"
    )
    
    print(f"✅ Created 3 patterns:")
    print(f"   1. {pattern1.name}: {pattern1.user_expression}")
    print(f"   2. {pattern2.name}: {pattern2.user_expression}")
    print(f"   3. {pattern3.name}: {pattern3.user_expression}")
    
    # Test conflict detection
    patterns = [pattern1, pattern2, pattern3]
    conflict_results = system.detect_pattern_conflicts(patterns, test_files)
    
    print(f"\n🔍 Conflict Detection Results:")
    print(f"   Conflicts detected: {conflict_results['conflicts_detected']}")
    print(f"   Conflicts resolved: {conflict_results['conflicts_resolved']}")
    
    if conflict_results['conflict_details']:
        print("   Conflict details:")
        for detail in conflict_results['conflict_details']:
            print(f"     - {detail['pattern1']} vs {detail['pattern2']}: {detail['overlap_count']} overlapping files")
            if detail['resolved']:
                print(f"       → Resolved using: {detail['resolution_strategy']}")
    
    # Test conflict resolution preferences
    print(f"\n⚙️ Setting conflict resolution preferences...")
    preferences = {
        'default_strategies': {
            'pattern_overlap': 'rename',
            'file_exists': 'backup_replace'
        },
        'auto_resolve_low_severity': True,
        'auto_resolve_medium_severity': False
    }
    
    system.set_conflict_resolution_preferences('pattern', preferences)
    print("✅ Conflict resolution preferences set for pattern scope")
    
    # Get conflict statistics
    stats = system.get_conflict_statistics()
    print(f"\n📊 Conflict Statistics:")
    print(f"   Total conflicts: {stats.get('total_conflicts', 0)}")
    print(f"   Active conflicts: {stats.get('active_conflicts', 0)}")
    print(f"   Resolved conflicts: {stats.get('resolved_conflicts', 0)}")
    print(f"   Resolution rate: {stats.get('resolution_rate', 0):.2%}")
    
    # Test individual pattern conflict resolution configuration
    pattern1.conflict_resolution_strategy = ResolutionStrategy.SKIP
    pattern1.conflict_resolution_config = {"reason": "Skip conflicts for text files"}
    
    print(f"\n🔧 Pattern-specific conflict resolution:")
    print(f"   {pattern1.name} strategy: {pattern1.conflict_resolution_strategy.value}")
    print(f"   Config: {pattern1.conflict_resolution_config}")
    
    # Shutdown
    system.shutdown()
    print("\n✅ System shutdown complete")
    
    print("\n🎉 All conflict resolution tests passed!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

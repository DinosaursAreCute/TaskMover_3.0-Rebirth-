"""
Simple Pattern System Test

Quick test to verify basic functionality.
"""

import tempfile
from pathlib import Path

try:
    # Import the pattern system
    from taskmover.core.patterns import create_pattern_system
    print("✅ Import successful")
    
    # Create temporary directory
    test_dir = Path(tempfile.mkdtemp())
    print(f"📁 Test directory: {test_dir}")
    
    # Initialize pattern system
    storage_path = test_dir / "patterns"
    system = create_pattern_system(storage_path)
    system.initialize()
    print("✅ Pattern system created and initialized")
    
    # Test basic pattern creation
    pattern = system.create_pattern(
        "*.txt", 
        name="Text Files",
        description="All text files"
    )
    print(f"✅ Pattern created: {pattern.name}")
    print(f"   Type: {pattern.pattern_type}")
    print(f"   Query: {pattern.compiled_query}")
    
    # Test pattern validation
    result = system.validate_expression("*.pdf")
    print(f"✅ Validation result: valid={result.is_valid}, score={result.performance_score}")
    
    # Test system status
    status = system.get_system_status()
    print(f"✅ System status: initialized={status['initialized']}")
    
    # Shutdown
    system.shutdown()
    print("✅ System shutdown complete")
    
    print("\n🎉 All basic tests passed!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

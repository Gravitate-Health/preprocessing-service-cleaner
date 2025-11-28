#!/usr/bin/env python3
"""
Test script to verify feature flags work correctly
"""

import os
import sys
from pathlib import Path

# Test different environment configurations
test_cases = [
    {
        'name': 'Both features enabled (default)',
        'env': {},
        'expected_optimization': True,
        'expected_cleanup': True
    },
    {
        'name': 'HTML optimization disabled',
        'env': {'ENABLE_HTML_OPTIMIZATION': 'false'},
        'expected_optimization': False,
        'expected_cleanup': True
    },
    {
        'name': 'Link cleanup disabled',
        'env': {'ENABLE_LINK_CLEANUP': 'false'},
        'expected_optimization': True,
        'expected_cleanup': False
    },
    {
        'name': 'Both features disabled (passthrough)',
        'env': {'ENABLE_HTML_OPTIMIZATION': 'false', 'ENABLE_LINK_CLEANUP': 'false'},
        'expected_optimization': False,
        'expected_cleanup': False
    },
]

print("="*70)
print("FEATURE FLAG CONFIGURATION TEST")
print("="*70)

for test in test_cases:
    print(f"\n📋 Test: {test['name']}")
    print(f"   Environment: {test['env'] if test['env'] else 'defaults'}")
    
    # Set environment variables
    for key, value in test['env'].items():
        os.environ[key] = value
    
    # Remove previously imported module to force reload
    if 'preprocessor.controllers.preprocess_controller' in sys.modules:
        del sys.modules['preprocessor.controllers.preprocess_controller']
    
    # Import the controller (will read env vars)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from preprocessor.controllers import preprocess_controller
    
    # Check the flags
    optimization_enabled = preprocess_controller.ENABLE_HTML_OPTIMIZATION
    cleanup_enabled = preprocess_controller.ENABLE_LINK_CLEANUP
    
    print(f"   ENABLE_HTML_OPTIMIZATION: {optimization_enabled}")
    print(f"   ENABLE_LINK_CLEANUP: {cleanup_enabled}")
    
    # Verify
    if optimization_enabled == test['expected_optimization'] and cleanup_enabled == test['expected_cleanup']:
        print(f"   ✅ PASS")
    else:
        print(f"   ❌ FAIL - Expected optimization={test['expected_optimization']}, cleanup={test['expected_cleanup']}")
    
    # Clean up for next test
    for key in test['env'].keys():
        if key in os.environ:
            del os.environ[key]

print("\n" + "="*70)
print("Test complete!")
print("="*70)

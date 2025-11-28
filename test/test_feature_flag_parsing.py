#!/usr/bin/env python3
"""
Test script to verify feature flag parsing logic
"""

import os

def parse_feature_flag(env_var, default='true'):
    """Test the feature flag parsing logic"""
    value = os.getenv(env_var, default)
    return value.lower() in ('true', '1', 'yes', 'on')

print("="*70)
print("FEATURE FLAG PARSING TEST")
print("="*70)

test_cases = [
    ('true', True),
    ('True', True),
    ('TRUE', True),
    ('1', True),
    ('yes', True),
    ('YES', True),
    ('on', True),
    ('ON', True),
    ('false', False),
    ('False', False),
    ('FALSE', False),
    ('0', False),
    ('no', False),
    ('off', False),
    ('', False),  # empty string
    ('random', False),  # invalid value
]

print("\nTesting value parsing:")
all_passed = True
for value, expected in test_cases:
    os.environ['TEST_FLAG'] = value
    result = parse_feature_flag('TEST_FLAG', 'false')
    status = '✅' if result == expected else '❌'
    if result != expected:
        all_passed = False
    print(f"  {status} '{value}' -> {result} (expected {expected})")

print("\nTesting defaults:")
# Test default when env var not set
if 'TEST_FLAG' in os.environ:
    del os.environ['TEST_FLAG']

result_default_true = parse_feature_flag('TEST_FLAG', 'true')
result_default_false = parse_feature_flag('TEST_FLAG', 'false')

print(f"  {'✅' if result_default_true else '❌'} No env var, default='true' -> {result_default_true}")
print(f"  {'✅' if not result_default_false else '❌'} No env var, default='false' -> {result_default_false}")

if not result_default_true or result_default_false:
    all_passed = False

print("\n" + "="*70)
if all_passed:
    print("✅ All feature flag tests PASSED")
else:
    print("❌ Some tests FAILED")
print("="*70)

# Show example usage
print("\nExample Docker commands:")
print("  # Default (both enabled):")
print("  docker run -p 8080:8080 preprocessing-service")
print("\n  # Disable HTML optimization:")
print("  docker run -p 8080:8080 -e ENABLE_HTML_OPTIMIZATION=false preprocessing-service")
print("\n  # Disable link cleanup:")
print("  docker run -p 8080:8080 -e ENABLE_LINK_CLEANUP=false preprocessing-service")
print("\n  # Disable both (passthrough mode):")
print("  docker run -p 8080:8080 -e ENABLE_HTML_OPTIMIZATION=false -e ENABLE_LINK_CLEANUP=false preprocessing-service")

#!/bin/bash
# Test script for token diagnostics

echo "=== CDP Runbooker Token Diagnostics Test ==="
echo

# Test 1: Diagnose stored token
echo "Test 1: Diagnosing stored token..."
python cdpRunbooker.py --diagnose-token
echo

# Test 2: Diagnose a specific token (example - user should replace with actual token)
echo "Test 2: To test a specific token, run:"
echo "python cdpRunbooker.py --diagnose-token YOUR_TOKEN_HERE"
echo

# Test 3: Enable debug mode for more details
echo "Test 3: To run with debug logging enabled:"
echo "CDP_DEBUG=true python cdpRunbooker.py --diagnose-token"
echo

# Test 4: Generate debug report
echo "Test 4: To generate a comprehensive debug report:"
echo "python cdpRunbooker.py --debug-report"

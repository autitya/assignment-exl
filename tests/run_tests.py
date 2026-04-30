"""
Test runner for the chatbot application.

Run all tests with:
    python tests/run_tests.py

Or run specific test file:
    python tests/run_tests.py test_config
"""

import unittest
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import all test modules
from tests import (
    test_config,
    test_graph,
    test_pdf_service,
    test_integration
)


def run_all_tests():
    """Run all tests in the test suite"""
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all tests
    suite.addTests(loader.loadTestsFromModule(test_config))
    suite.addTests(loader.loadTestsFromModule(test_graph))
    suite.addTests(loader.loadTestsFromModule(test_pdf_service))
    suite.addTests(loader.loadTestsFromModule(test_integration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


def run_specific_test(test_name):
    """Run specific test module or test case"""
    
    loader = unittest.TestLoader()
    
    try:
        # Try to load as module
        suite = loader.loadTestsFromName(f'tests.{test_name}')
    except (ImportError, AttributeError):
        print(f"Error: Could not find test '{test_name}'")
        return 1
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run specific test
        exit_code = run_specific_test(sys.argv[1])
    else:
        # Run all tests
        exit_code = run_all_tests()
    
    sys.exit(exit_code)

# Test Documentation

## Running Tests

### Run All Tests
```bash
python tests/run_tests.py
```

### Run Specific Test Module
```bash
python tests/run_tests.py test_config
python tests/run_tests.py test_graph
python tests/run_tests.py test_pdf_service
python tests/run_tests.py test_integration
```

### Run with Verbose Output
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## Test Coverage

### test_config.py
- Configuration module initialization
- LLM API selection (OpenAI/Gemini)
- Vector database setup
- Settings attributes validation

### test_graph.py
- GraphState TypedDict structure
- Router node logic
- Tool node functionality
- Direct node functionality
- Route decision logic
- Document formatting

### test_pdf_service.py
- File hashing (SHA-256)
- Duplicate detection
- PDF processing
- Metadata handling
- Text extraction and chunking

### test_integration.py
- End-to-end workflows
- Module imports
- Error handling
- API integration

## Test Structure

Each test file follows this pattern:

```python
"""Tests for module_name."""

import unittest
from unittest.mock import Mock, patch

class TestFeature(unittest.TestCase):
    """Test cases for feature"""
    
    def setUp(self):
        """Setup before each test"""
        pass
    
    def test_specific_behavior(self):
        """Test description"""
        # Arrange
        # Act
        # Assert
        pass
```

## Mocking Strategy

- **External APIs**: Mock LLM calls and vector database
- **File I/O**: Mock file operations
- **PDF Processing**: Mock PDF parsing libraries

## Expected Test Results

All tests should pass with output similar to:

```
test_calculate_file_hash_consistency (test_pdf_service.TestPdfService) ... ok
test_can_import_config_settings (test_integration.TestApplicationModules) ... ok
test_router_node_routes_to_tool (test_graph.TestRouterNode) ... ok

Ran 25 tests in 0.234s

OK
```

## Continuous Integration

For CI/CD pipelines, use:

```bash
python -m pytest tests/ --cov=src --cov-report=html
```

## Adding New Tests

1. Create test file in `tests/` directory
2. Follow naming convention: `test_*.py`
3. Inherit from `unittest.TestCase`
4. Use `setUp()` and `tearDown()` methods
5. Write descriptive test names
6. Use mocking for external dependencies

## Troubleshooting Tests

### Import Errors
- Ensure `tests/__init__.py` exists
- Check Python path includes project root

### Mock Not Working
- Use `@patch` decorator or context manager
- Verify patch path matches actual import location

### Tests Fail Intermittently
- Check for timing issues
- Mock time-dependent code
- Ensure test isolation

"""Unit tests for config module."""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestConfigSettings(unittest.TestCase):
    """Test cases for config/settings.py"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock environment variables
        self.original_env = os.environ.copy()
    
    def tearDown(self):
        """Clean up after tests"""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    @patch.dict(os.environ, {'LLM_API': 'OPENAI'})
    def test_default_llm_api_is_openai(self):
        """Test that OPENAI is the default LLM API"""
        # Reload module to pick up new env var
        if 'config.settings' in sys.modules:
            del sys.modules['config.settings']
        
        from config import settings
        self.assertEqual(settings.LLM_API, 'OPENAI')
    
    @patch.dict(os.environ, {'LLM_API': 'GEMINI'})
    def test_can_switch_to_gemini(self):
        """Test that we can switch to GEMINI API"""
        if 'config.settings' in sys.modules:
            del sys.modules['config.settings']
        
        from config import settings
        self.assertEqual(settings.LLM_API, 'GEMINI')
    
    def test_settings_module_has_required_attributes(self):
        """Test that settings module has all required attributes"""
        from config import settings
        
        required_attrs = ['LLM_API', 'llm', 'embedding', 'vectordb', 'prompt']
        for attr in required_attrs:
            self.assertTrue(hasattr(settings, attr), 
                          f"Missing attribute: {attr}")
    
    def test_vector_db_persistence_path_exists(self):
        """Test that vector database persistence path is valid"""
        from config import settings
        
        persist_dir = settings.vectordb.persist_directory
        self.assertIsNotNone(persist_dir)
        self.assertTrue(len(persist_dir) > 0)


if __name__ == '__main__':
    unittest.main()

"""Integration tests for the chatbot application."""

import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestEndToEndWorkflow(unittest.TestCase):
    """End-to-end integration tests"""
    
    @patch('src.routes.graph.vectordb')
    @patch('src.routes.graph.llm')
    def test_document_question_workflow(self, mock_llm, mock_vectordb):
        """Test complete workflow for document question"""
        from src.routes.graph import graph, GraphState
        
        # Mock the router decision to go to tool
        mock_response = Mock()
        mock_response.content = "tool"
        mock_llm.invoke.side_effect = [mock_response, "Answer from documents"]
        
        # Mock retriever
        mock_doc = Mock()
        mock_doc.page_content = "Relevant document content"
        mock_vectordb.as_retriever.return_value.invoke = Mock(
            return_value=[mock_doc]
        )
        
        # Execute workflow
        result = graph.invoke({"question": "What is in my PDF?"})
        
        self.assertIn("answer", result)
        self.assertEqual(result["route"], "tool")
    
    @patch('src.routes.graph.llm')
    def test_general_knowledge_workflow(self, mock_llm):
        """Test complete workflow for general knowledge question"""
        from src.routes.graph import graph
        
        # Mock responses
        router_response = Mock()
        router_response.content = "direct"
        
        direct_response = Mock()
        direct_response.content = "General knowledge answer"
        
        mock_llm.invoke.side_effect = [router_response, direct_response]
        
        # Execute workflow
        result = graph.invoke({"question": "What is AI?"})
        
        self.assertIn("answer", result)
        self.assertEqual(result["route"], "direct")


class TestApplicationModules(unittest.TestCase):
    """Test that all modules can be imported"""
    
    def test_can_import_config_settings(self):
        """Test that config.settings can be imported"""
        try:
            from config import settings
            self.assertIsNotNone(settings)
        except ImportError as e:
            self.fail(f"Failed to import config.settings: {e}")
    
    def test_can_import_graph(self):
        """Test that src.routes.graph can be imported"""
        try:
            from src.routes import graph as graph_module
            self.assertTrue(hasattr(graph_module, 'graph'))
        except ImportError as e:
            self.fail(f"Failed to import src.routes.graph: {e}")
    
    def test_can_import_pdf_service(self):
        """Test that src.services.pdf_service can be imported"""
        try:
            from src.services import pdf_service
            self.assertTrue(hasattr(pdf_service, 'process_pdf'))
        except ImportError as e:
            self.fail(f"Failed to import src.services.pdf_service: {e}")


class TestErrorHandling(unittest.TestCase):
    """Test error handling in the application"""
    
    @patch('src.routes.graph.llm')
    def test_handles_llm_error(self, mock_llm):
        """Test graceful handling of LLM errors"""
        from src.routes.graph import router_node, GraphState
        
        mock_llm.invoke.side_effect = Exception("API Error")
        
        state = GraphState(question="Test", route=None, answer=None)
        
        with self.assertRaises(Exception):
            router_node(state)
    
    def test_handles_missing_file(self):
        """Test handling of missing PDF file"""
        from src.services.pdf_service import process_pdf
        
        mock_file = Mock()
        mock_file.read.side_effect = FileNotFoundError("File not found")
        
        with self.assertRaises(FileNotFoundError):
            calculate_file_hash(mock_file)


if __name__ == '__main__':
    unittest.main()

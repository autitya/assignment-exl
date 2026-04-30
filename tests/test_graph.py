"""Unit tests for LangGraph router module."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path
from typing import TypedDict, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestGraphState(unittest.TestCase):
    """Test cases for GraphState TypedDict"""
    
    def test_graph_state_has_required_fields(self):
        """Test that GraphState has required fields"""
        from src.routes.graph import GraphState
        
        # Check type annotations
        annotations = GraphState.__annotations__
        self.assertIn('question', annotations)
        self.assertIn('route', annotations)
        self.assertIn('answer', annotations)
    
    def test_graph_state_creation(self):
        """Test that GraphState can be instantiated"""
        from src.routes.graph import GraphState
        
        state = GraphState(
            question="Test question",
            route="tool",
            answer="Test answer"
        )
        
        self.assertEqual(state['question'], "Test question")
        self.assertEqual(state['route'], "tool")
        self.assertEqual(state['answer'], "Test answer")


class TestFormatDocs(unittest.TestCase):
    """Test cases for format_docs function"""
    
    def test_format_docs_joins_with_double_newlines(self):
        """Test that format_docs joins documents with double newlines"""
        from src.routes.graph import format_docs
        
        doc1 = Mock()
        doc1.page_content = "Document 1"
        
        doc2 = Mock()
        doc2.page_content = "Document 2"
        
        result = format_docs([doc1, doc2])
        
        self.assertEqual(result, "Document 1\n\nDocument 2")
    
    def test_format_docs_empty_list(self):
        """Test format_docs with empty document list"""
        from src.routes.graph import format_docs
        
        result = format_docs([])
        
        self.assertEqual(result, "")
    
    def test_format_docs_single_document(self):
        """Test format_docs with single document"""
        from src.routes.graph import format_docs
        
        doc = Mock()
        doc.page_content = "Single document"
        
        result = format_docs([doc])
        
        self.assertEqual(result, "Single document")


class TestSearchDocs(unittest.TestCase):
    """Test cases for search_docs tool"""
    
    @patch('src.routes.graph.rag_chain')
    def test_search_docs_invokes_rag_chain(self, mock_rag_chain):
        """Test that search_docs invokes the RAG chain"""
        from src.routes.graph import search_docs
        
        mock_rag_chain.invoke.return_value = "Test answer"
        
        result = search_docs.invoke("Test query")
        
        self.assertEqual(result, "Test answer")
        mock_rag_chain.invoke.assert_called_once_with("Test query")
    
    def test_search_docs_is_a_tool(self):
        """Test that search_docs is properly decorated as a tool"""
        from src.routes.graph import search_docs
        
        # Tool decorator should add these attributes
        self.assertTrue(hasattr(search_docs, 'name'))
        self.assertTrue(hasattr(search_docs, 'invoke'))


class TestRouterNode(unittest.TestCase):
    """Test cases for router_node function"""
    
    @patch('src.routes.graph.llm')
    def test_router_node_routes_to_tool(self, mock_llm):
        """Test router_node routes to tool when appropriate"""
        from src.routes.graph import router_node, GraphState
        
        # Mock LLM response containing 'tool'
        mock_message = Mock()
        mock_message.content = "tool"
        mock_llm.invoke.return_value = mock_message
        
        state = GraphState(question="Document question?", route=None, answer=None)
        result = router_node(state)
        
        self.assertEqual(result['route'], 'tool')
    
    @patch('src.routes.graph.llm')
    def test_router_node_routes_to_direct(self, mock_llm):
        """Test router_node routes to direct when appropriate"""
        from src.routes.graph import router_node, GraphState
        
        # Mock LLM response not containing 'tool'
        mock_message = Mock()
        mock_message.content = "direct"
        mock_llm.invoke.return_value = mock_message
        
        state = GraphState(question="General knowledge?", route=None, answer=None)
        result = router_node(state)
        
        self.assertEqual(result['route'], 'direct')


class TestToolNode(unittest.TestCase):
    """Test cases for tool_node function"""
    
    @patch('src.routes.graph.search_docs')
    def test_tool_node_returns_answer(self, mock_search_docs):
        """Test that tool_node returns answer from search_docs"""
        from src.routes.graph import tool_node, GraphState
        
        mock_search_docs.invoke.return_value = "Search result"
        
        state = GraphState(question="Test question", route="tool", answer=None)
        result = tool_node(state)
        
        self.assertEqual(result['answer'], "Search result")


class TestDirectNode(unittest.TestCase):
    """Test cases for direct_node function"""
    
    @patch('src.routes.graph.llm')
    def test_direct_node_returns_answer(self, mock_llm):
        """Test that direct_node returns LLM answer"""
        from src.routes.graph import direct_node, GraphState
        
        mock_message = Mock()
        mock_message.content = "Direct answer"
        mock_llm.invoke.return_value = mock_message
        
        state = GraphState(question="General question", route="direct", answer=None)
        result = direct_node(state)
        
        self.assertEqual(result['answer'], "Direct answer")


class TestRouteDecision(unittest.TestCase):
    """Test cases for route_decision function"""
    
    def test_route_decision_returns_route(self):
        """Test that route_decision returns the route from state"""
        from src.routes.graph import route_decision, GraphState
        
        state = GraphState(question="Test", route="tool", answer=None)
        result = route_decision(state)
        
        self.assertEqual(result, "tool")
    
    def test_route_decision_with_direct(self):
        """Test route_decision with direct route"""
        from src.routes.graph import route_decision, GraphState
        
        state = GraphState(question="Test", route="direct", answer=None)
        result = route_decision(state)
        
        self.assertEqual(result, "direct")


class TestGraphCompilation(unittest.TestCase):
    """Test cases for compiled graph"""
    
    def test_graph_is_compiled(self):
        """Test that graph is properly compiled"""
        from src.routes.graph import graph
        
        self.assertTrue(hasattr(graph, 'invoke'))
        self.assertIsNotNone(graph)


if __name__ == '__main__':
    unittest.main()

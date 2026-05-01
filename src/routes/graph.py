"""Router module for LangGraph-based chatbot workflow.

This module implements a routing system that directs user queries to either
direct LLM responses or document search via RAG (Retrieval Augmented Generation).
It uses LangGraph to manage the workflow state and routing logic.
"""
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from langchain_core.tools import tool
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from config.settings import llm, vectordb, prompt
import logging
from langsmith import Client

# Configure logging
logger = logging.getLogger(__name__)


class LLMException(Exception):
    """Base exception for LLM-related errors."""
    pass


class LLMInvocationError(LLMException):
    """Raised when LLM invocation fails."""
    pass


class RAGChainError(LLMException):
    """Raised when RAG chain execution fails."""
    pass


class RoutingError(LLMException):
    """Raised when routing decision fails."""
    pass


class FleetAgentError(LLMException):
    """Raised when fleet agent execution fails."""
    pass


def format_docs(docs):
    """Format retrieved documents into a single context string.
    
    Args:
        docs: List of document objects from vector store retrieval
        
    Returns:
        str: Formatted documents joined by double newlines
    """
    print(docs)
    return "\n\n".join(doc.page_content for doc in docs)


# Create retriever that fetches top 3 most relevant documents
retriever = vectordb.as_retriever(search_kwargs={"k": 3})


# Build RAG chain: retrieve docs -> format -> prompt -> LLM -> parse output
rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
)


@tool
def search_docs(query: str) -> str:
    """Search and retrieve relevant information from PDF documents using RAG.
    
    This tool uses the RAG chain to search through indexed documents and
    return contextually relevant answers to the user's query.
    
    Args:
        query (str): The user's search query or question
        
    Returns:
        str: The LLM-generated answer based on retrieved document context
        
    Raises:
        RAGChainError: If the RAG chain invocation fails
    """
    try:
        result = rag_chain.invoke(query)
        return result
    except Exception as e:
        error_msg = f"RAG chain execution failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise RAGChainError(error_msg) from e


client = Client()
@tool
def fleet_agent(query: str):
    """Fleet agent for analysis."""
    response = client.run_agent(
        agent_id="fleet-agent-01",
        inputs={"content": query}
    )
    return response.outputs['output']

class GraphState(TypedDict):
    """Represents the state of the LangGraph workflow.
    
    Attributes:
        question (str): The user's input question or query
        route (Optional[str]): The routing decision ('tool' or 'direct')
        answer (Optional[str]): The final generated answer to the question
    """
    question: str
    route: Optional[str]
    answer: Optional[str]


def router_node(state: GraphState):
    """Route node that determines whether to use document search or direct LLM response.
    
    Analyzes the user's question and decides if it requires document retrieval
    or can be answered with general knowledge.
    
    Args:
        state (GraphState): Current workflow state containing the question
        
    Returns:
        dict: Updated state with routing decision ('tool' or 'direct')
        
    Raises:
        RoutingError: If the routing decision cannot be made
    """
    try:
        question = state["question"]

        # Create decision prompt for LLM to classify the query
        decision_prompt = f"""
    Decide:
    - "tool" → if question needs document search
    - "direct" → if general knowledge
    - "fleet" → if question needs fleet agent analysis

    Question: {question}
    """

        # Invoke LLM to make routing decision
        decision = llm.invoke(decision_prompt).content.lower()

        # Return routing decision
        if "tool" in decision:
            return {"route": "tool"}
        elif "fleet" in decision:
            return {"route": "fleet"}
        else:
            return {"route": "direct"}
    except AttributeError as e:
        error_msg = f"Failed to parse LLM routing response: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise RoutingError(error_msg) from e
    except Exception as e:
        error_msg = f"LLM routing invocation failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise RoutingError(error_msg) from e


def tool_node(state: GraphState):
    """Tool node that searches PDF documents for relevant information.
    
    Executes the document search tool when the router determines
    that the query requires document retrieval.
    
    Args:
        state (GraphState): Current workflow state containing the question
        
    Returns:
        dict: Updated state with the answer from document search
        
    Raises:
        RAGChainError: If document search fails
    """
    try:
        # Invoke the search_docs tool to find relevant documents
        answer = search_docs.invoke(state["question"])
        return {"answer": answer}
    except RAGChainError:
        raise
    except Exception as e:
        error_msg = f"Tool node execution failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise RAGChainError(error_msg) from e


def direct_node(state: GraphState):
    """Direct node that generates answer using LLM without document retrieval.
    
    Processes general knowledge questions directly with the LLM,
    bypassing the document search tool.
    
    Args:
        state (GraphState): Current workflow state containing the question
        
    Returns:
        dict: Updated state with the LLM-generated answer
        
    Raises:
        LLMInvocationError: If LLM invocation fails
    """
    try:
        # Invoke LLM directly with the user's question
        answer = llm.invoke(state["question"]).content
        return {"answer": answer}
    except AttributeError as e:
        error_msg = f"Failed to parse LLM response: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise LLMInvocationError(error_msg) from e
    except Exception as e:
        error_msg = f"Direct LLM invocation failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise LLMInvocationError(error_msg) from e


def fleet_node(state: GraphState):
    """Fleet node that delegates query to fleet agent for analysis.
    
    Executes the fleet agent tool when the router determines
    that the query requires fleet-specific analysis.
    
    Args:
        state (GraphState): Current workflow state containing the question
        
    Returns:
        dict: Updated state with the answer from fleet agent
        
    Raises:
        FleetAgentError: If fleet agent execution fails
    """
    try:
        # Invoke the fleet_agent tool for fleet-specific analysis
        answer = fleet_agent.invoke(state["question"])
        return {"answer": answer}
    except Exception as e:
        error_msg = f"Fleet agent execution failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise FleetAgentError(error_msg) from e


def route_decision(state: GraphState):
    """Determine which node to execute based on routing decision.
    
    This is a conditional routing function that uses the router node's
    decision to determine whether to execute the tool_node or direct_node.
    
    Args:
        state (GraphState): Current workflow state containing the routing decision
        
    Returns:
        str: The routing decision ('tool' or 'direct')
    """
    return state["route"]


# Initialize LangGraph state graph with GraphState schema
builder = StateGraph(GraphState)

# Add nodes to the graph
builder.add_node("router", router_node)
builder.add_node("tool", tool_node)
builder.add_node("direct", direct_node)
builder.add_node("fleet", fleet_node)

# Set the entry point to start with router node
builder.set_entry_point("router")

# Add conditional edges based on routing decision
builder.add_conditional_edges(
    "router",
    route_decision,
    {
        "tool": "tool",
        "direct": "direct",
        "fleet": "fleet"
    }
)

# Add edges to END from tool, direct, and fleet nodes
builder.add_edge("tool", END)
builder.add_edge("direct", END)
builder.add_edge("fleet", END)

# Compile the graph into a runnable workflow
graph = builder.compile()


# Create a separate router-only graph to determine routing first
router_builder = StateGraph(GraphState)
router_builder.add_node("router", router_node)
router_builder.set_entry_point("router")
router_builder.add_edge("router", END)
router_graph = router_builder.compile()


# Test the graph locally
if __name__ == "__main__":
    response = graph.invoke({
        "question": "What is mentioned in my PDF?"
    })

    print(response["answer"])

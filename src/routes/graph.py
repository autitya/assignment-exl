"""Router module for LangGraph-based chatbot workflow.

This module implements a routing system that directs user queries to either
direct LLM responses or document search via RAG (Retrieval Augmented Generation).
It uses LangGraph to manage the workflow state and routing logic.
"""
import streamlit as st
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from langchain_core.tools import tool
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from config.settings import llm, vectordb, prompt


def format_docs(docs):
    """Format retrieved documents into a single context string.
    
    Args:
        docs: List of document objects from vector store retrieval
        
    Returns:
        str: Formatted documents joined by double newlines
    """
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
    """
    st.spinner("fetching relevant documents...")
    return rag_chain.invoke(query)


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
    """
    question = state["question"]

    # Create decision prompt for LLM to classify the query
    decision_prompt = f"""
    Decide:
    - "tool" → if question needs document search
    - "direct" → if general knowledge

    Question: {question}
    """

    # Invoke LLM to make routing decision
    decision = llm.invoke(decision_prompt).content.lower()

    # Return routing decision
    if "tool" in decision:
        return {"route": "tool"}
    else:
        return {"route": "direct"}


def tool_node(state: GraphState):
    """Tool node that searches PDF documents for relevant information.
    
    Executes the document search tool when the router determines
    that the query requires document retrieval.
    
    Args:
        state (GraphState): Current workflow state containing the question
        
    Returns:
        dict: Updated state with the answer from document search
    """
    # Invoke the search_docs tool to find relevant documents
    answer = search_docs.invoke(state["question"])
    return {"answer": answer}


def direct_node(state: GraphState):
    """Direct node that generates answer using LLM without document retrieval.
    
    Processes general knowledge questions directly with the LLM,
    bypassing the document search tool.
    
    Args:
        state (GraphState): Current workflow state containing the question
        
    Returns:
        dict: Updated state with the LLM-generated answer
    """
    # Invoke LLM directly with the user's question
    answer = llm.invoke(state["question"]).content
    return {"answer": answer}


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

# Set the entry point to start with router node
builder.set_entry_point("router")

# Add conditional edges based on routing decision
builder.add_conditional_edges(
    "router",
    route_decision,
    {
        "tool": "tool",
        "direct": "direct"
    }
)

# Add edges to END from both tool and direct nodes
builder.add_edge("tool", END)
builder.add_edge("direct", END)

# Compile the graph into a runnable workflow
graph = builder.compile()


# Test the graph locally
if __name__ == "__main__":
    response = graph.invoke({
        "question": "What is mentioned in my PDF?"
    })

    print(response["answer"])

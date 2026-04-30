"""Main Streamlit application for the chatbot interface.

This module sets up the Streamlit UI for a conversational chatbot that uses
LangGraph for routing and document retrieval capabilities.
"""

import streamlit as st
from dotenv import load_dotenv
import os
import sys
from pathlib import Path

# Add parent directory to path to import src module
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()

from src.services.pdf_service import process_pdf
from src.routes.graph import graph

# Configure Streamlit page settings
st.set_page_config(page_title="Chatbot", layout="wide")

# Display main title
st.title("Chatbot")

# Initialize chat history in session state if not exists
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history from session state
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Get user input and process if provided
if prompt := st.chat_input("Ask something...", accept_file='multiple', file_type=["pdf"]):
    if prompt["files"]:
        file = prompt["files"][0]
        num_chunks = process_pdf(file)
        st.success(f"Processed PDF with {num_chunks} chunks added to vector database.")
    if prompt.text:
        # Append user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt.text})
        
        # Display user message in UI
        with st.chat_message("user"):
            st.write(prompt.text)

        # Invoke the LangGraph routing engine to process the query
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Pass user question to the graph for routing and processing
                result = graph.invoke({"question": prompt.text})
                answer = result["answer"]

                # Display assistant response
                st.write(answer)

        # Append assistant response to chat history for persistence
        st.session_state.messages.append({"role": "assistant", "content": answer})

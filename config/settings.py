"""Configuration settings for the chatbot application.

This module manages LLM API selection, embedding models initialization,
and vector database setup.
"""

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
import os
from langchain_core.prompts import ChatPromptTemplate


# Determine which LLM API to use from environment variable
LLM_API = os.getenv('LLM_API', 'OPENAI')

# Initialize LLM and embedding models based on API selection
if LLM_API == 'OPENAI':
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    embedding = OpenAIEmbeddings()
elif LLM_API == 'GEMINI':
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0
    )
    embedding = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001"
    )

# Initialize Chroma vector database for document storage and retrieval
vectordb = Chroma(
    persist_directory="./db",
    embedding_function=embedding
)

# Define the RAG prompt template that instructs the LLM how to answer questions
prompt = ChatPromptTemplate.from_template("""
Answer ONLY using the context below.
If not found, say "I don't know".

Context:
{context}

Question:
{question}
""")

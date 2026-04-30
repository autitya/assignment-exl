"""PDF processing service for extracting and indexing document content.

This module handles PDF uploads, text extraction, chunking, and vector
database indexing with duplicate detection.
"""

import pdfplumber
import hashlib
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import vectordb


def calculate_file_hash(file):
    """Generates a SHA-256 hash for the file content.
    
    Args:
        file: File object to hash
        
    Returns:
        str: Hexadecimal hash of file content
    """
    sha256_hash = hashlib.sha256()
    # Read the file in chunks to handle large PDFs efficiently
    for byte_block in iter(lambda: file.read(4096), b""):
        sha256_hash.update(byte_block)
    file.seek(0)  # Reset file pointer to the beginning after reading
    return sha256_hash.hexdigest()


def is_already_uploaded(file_hash):
    """Checks the vector DB metadata to see if the hash exists.
    
    Args:
        file_hash (str): SHA-256 hash of the file
        
    Returns:
        bool: True if file is already in vector database, False otherwise
    """
    # We search the vector store for any document matching this hash
    results = vectordb.get(
        where={"file_hash": file_hash},
        limit=1
    )
    return len(results['ids']) > 0


def process_pdf(file):
    """Process and index a PDF file into the vector database.
    
    Extracts text and tables from PDF, chunks the content, and stores it
    in the vector database with metadata. Skips already-uploaded files.
    
    Args:
        file: File object containing PDF data
        
    Returns:
        int: Number of chunks added to vector database (0 if already uploaded)
    """
    # 1. Generate unique hash for the file
    file_hash = calculate_file_hash(file)

    # 2. Check if it exists in the Vector DB
    if is_already_uploaded(file_hash):
        print(f"Skipping '{file.name}': Already indexed.")
        return 0  # Return 0 chunks added

    print(f"Processing '{file.name}'...")
    
    text_content = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            
            # Extract tables as Markdown
            tables = page.extract_tables()
            for table in tables:
                markdown_table = ""
                for row in table:
                    row_str = "| " + " | ".join([str(cell).replace('\n', ' ') if cell else "" for cell in row]) + " |"
                    markdown_table += row_str + "\n"
                if markdown_table:
                    page_text += "\n\n### Table Data ###\n" + markdown_table + "\n"
            
            text_content.append(page_text)

    # Join all pages with page break markers
    full_text = "\n\n--- Page Break ---\n\n".join(text_content)

    # Split text into manageable chunks for embedding
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500, 
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = splitter.split_text(full_text)

    # 3. Add to Vector DB with hash in metadata
    vectordb.add_texts(
        texts=chunks,
        metadatas=[{
            "source": file.name,
            "file_hash": file_hash  # This allows us to verify it later
        }] * len(chunks)
    )

    # Persist the vector database if method is available
    if hasattr(vectordb, 'persist'):
        vectordb.persist()

    return len(chunks)

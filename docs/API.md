# API Reference

## Configuration Module (`config/settings.py`)

### Global Variables

#### `LLM_API`
```python
LLM_API: str
```
- **Description**: Determines which LLM provider to use
- **Values**: `'OPENAI'` or `'GEMINI'`
- **Default**: `'OPENAI'`
- **Source**: Environment variable `LLM_API`

#### `llm`
```python
llm: ChatOpenAI | ChatGoogleGenerativeAI
```
- **Description**: Initialized language model instance
- **Type**: Depends on `LLM_API` selection

#### `embedding`
```python
embedding: OpenAIEmbeddings | GoogleGenerativeAIEmbeddings
```
- **Description**: Embedding model for document vectorization

#### `vectordb`
```python
vectordb: Chroma
```
- **Description**: Vector database instance for document storage
- **Persistence**: `./db/` directory

#### `prompt`
```python
prompt: ChatPromptTemplate
```
- **Description**: RAG prompt template instructing LLM behavior

---

## Routes Module (`src/routes/graph.py`)

### Functions

#### `format_docs(docs)`
```python
def format_docs(docs) -> str
```
**Format retrieved documents into a single context string.**

- **Parameters**:
  - `docs` (List): Document objects from vector store
  
- **Returns**: 
  - `str`: Formatted documents joined by double newlines

- **Example**:
```python
docs = [doc1, doc2, doc3]
formatted = format_docs(docs)
```

---

#### `search_docs(query)`
```python
@tool
def search_docs(query: str) -> str
```
**Search and retrieve relevant information from PDF documents using RAG.**

- **Parameters**:
  - `query` (str): User search query or question
  
- **Returns**:
  - `str`: LLM-generated answer based on document context

- **Example**:
```python
answer = search_docs.invoke("What is mentioned about AI?")
print(answer)
```

---

#### `router_node(state)`
```python
def router_node(state: GraphState) -> dict
```
**Route node that determines whether to use document search or direct LLM response.**

- **Parameters**:
  - `state` (GraphState): Current workflow state
  
- **Returns**:
  - `dict`: `{"route": "tool"}` or `{"route": "direct"}`

- **Logic**:
  - Analyzes question complexity
  - Returns "tool" for document-related queries
  - Returns "direct" for general knowledge

---

#### `tool_node(state)`
```python
def tool_node(state: GraphState) -> dict
```
**Tool node that searches PDF documents for relevant information.**

- **Parameters**:
  - `state` (GraphState): Current workflow state with question
  
- **Returns**:
  - `dict`: `{"answer": response_text}`

- **Process**:
  1. Extracts question from state
  2. Invokes search_docs tool
  3. Returns LLM answer from documents

---

#### `direct_node(state)`
```python
def direct_node(state: GraphState) -> dict
```
**Direct node that generates answer using LLM without document retrieval.**

- **Parameters**:
  - `state` (GraphState): Current workflow state
  
- **Returns**:
  - `dict`: `{"answer": response_text}`

- **Process**:
  1. Sends question directly to LLM
  2. Returns response without document search

---

#### `route_decision(state)`
```python
def route_decision(state: GraphState) -> str
```
**Determine which node to execute based on routing decision.**

- **Parameters**:
  - `state` (GraphState): Current workflow state with routing decision
  
- **Returns**:
  - `str`: `"tool"` or `"direct"`

---

### Classes

#### `GraphState`
```python
class GraphState(TypedDict):
    question: str
    route: Optional[str]
    answer: Optional[str]
```

**Represents the state of the LangGraph workflow.**

- **Attributes**:
  - `question` (str): User's input question
  - `route` (Optional[str]): Routing decision ("tool" or "direct")
  - `answer` (Optional[str]): Final generated answer

---

### Graph Compilation

#### `graph`
```python
graph: CompiledGraph
```
**Compiled LangGraph workflow ready for execution.**

- **Entry Point**: `router` node
- **Possible Paths**:
  - `router → tool → END`
  - `router → direct → END`

- **Usage**:
```python
result = graph.invoke({"question": "What is AI?"})
answer = result["answer"]
```

---

## Services Module (`src/services/pdf_service.py`)

### Functions

#### `calculate_file_hash(file)`
```python
def calculate_file_hash(file) -> str
```
**Generate SHA-256 hash of file content for duplicate detection.**

- **Parameters**:
  - `file`: File object
  
- **Returns**:
  - `str`: Hexadecimal hash string

---

#### `is_already_uploaded(file_hash)`
```python
def is_already_uploaded(file_hash: str) -> bool
```
**Check if file is already in vector database.**

- **Parameters**:
  - `file_hash` (str): SHA-256 hash of file
  
- **Returns**:
  - `bool`: `True` if exists, `False` otherwise

---

#### `process_pdf(file)`
```python
def process_pdf(file) -> int
```
**Process and index a PDF file into the vector database.**

- **Parameters**:
  - `file`: File object containing PDF data
  
- **Returns**:
  - `int`: Number of chunks added (0 if already uploaded)

- **Process**:
  1. Calculate file hash
  2. Check for duplicates
  3. Extract text and tables
  4. Split into chunks
  5. Generate embeddings
  6. Store in vector database

- **Example**:
```python
uploaded_file = st.file_uploader("Choose PDF", type="pdf")
if uploaded_file:
    chunks = process_pdf(uploaded_file)
    print(f"Added {chunks} chunks")
```

---

## Streamlit App (`app/main.py`)

### Configuration

```python
st.set_page_config(page_title="Chatbot", layout="wide")
```

### Session State

```python
st.session_state.messages
```
- **Type**: List of dicts
- **Format**: `[{"role": "user"|"assistant", "content": str}, ...]`
- **Persistence**: Per session (browser)

### Components

#### Chat Input
```python
st.chat_input(
    prompt="Ask something...",
    accept_file='multiple',
    file_type=["pdf"]
)
```

#### Chat Message Display
```python
with st.chat_message(role):
    st.write(content)
```

#### Spinner
```python
with st.spinner("Thinking..."):
    # Long operation
```

---

## Type Definitions

### GraphState
```python
TypedDict with fields:
- question: str
- route: Optional[str]
- answer: Optional[str]
```

### File Metadata
```python
{
    "source": str,           # Original filename
    "file_hash": str         # SHA-256 hash for deduplication
}
```

---

## Error Handling

### Common Exceptions

| Exception | Cause | Solution |
|-----------|-------|----------|
| `ModuleNotFoundError` | Missing package | `pip install -r requirements.txt` |
| `FileNotFoundError` | Missing .env | Create `.env` with API keys |
| `ValueError` | Invalid API key | Check API key in `.env` |
| `ChromaException` | DB corruption | Delete `db/` directory |

---

## Performance Notes

- **Embedding Generation**: ~100-500ms per document
- **RAG Search**: ~1-3 seconds
- **Direct LLM Call**: ~2-5 seconds
- **Optimal Chunk Size**: 1500 characters
- **Max Retrieval**: 3 documents

---

## Configuration Examples

### OpenAI Setup
```python
from config.settings import llm, embedding, vectordb

# LLM is already initialized as ChatOpenAI
response = llm.invoke("Hello")
```

### Custom Temperature
```python
# To modify, edit config/settings.py
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
```

### Vector DB Reset
```bash
# Delete database
rmdir /s db\
# Restart app to recreate
```

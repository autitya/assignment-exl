# User Usage Guide

## Getting Started

### First-Time Setup

1. Start the application:
   ```bash
   streamlit run app/main.py
   ```

2. The chatbot interface will load with:
   - Chat input field
   - Chat history display
   - File upload capability

## Uploading Documents

### Step 1: Click File Upload
Click the chat input area and select "Upload file"

### Step 2: Choose PDF Files
Select one or multiple PDF files to upload

### Step 3: Wait for Processing
The system will:
- Extract text from pages
- Identify and format tables
- Create document embeddings
- Store in vector database

### Step 4: Confirmation
You'll see a success message with the number of chunks added

## Asking Questions

### Types of Questions

**General Knowledge Questions**
```
"What is machine learning?"
"Explain quantum computing"
"How does photosynthesis work?"
```
→ Answered directly by LLM

**Document-Related Questions**
```
"What is mentioned about AI in my document?"
"Summarize the findings in the PDF"
"List the key points from page 3"
```
→ Answered using document search

### How the System Routes Queries

The system automatically analyzes your question and routes it:
- **Direct Route**: For general knowledge questions
- **Document Route**: For questions that need specific information

## Chat Features

### View Chat History
- All messages are displayed in order
- Shows both your questions and AI responses

### Clear History
- Refresh the page to clear chat history
- Close the browser tab to reset

### Copy Responses
- Click on responses to select and copy
- Use standard copy shortcuts (Ctrl+C)

## Tips for Best Results

### PDF Preparation
- ✅ Use clear, well-scanned PDFs
- ❌ Avoid heavily compressed images
- ✅ Ensure text is readable
- ❌ Avoid corrupted or password-protected files

### Effective Questions
- **Be specific**: "What are the main findings?" (better than "What's in this PDF?")
- **Use context**: Reference document content if known
- **Ask one thing**: Multiple questions in separate messages work better

### Document Management
- ✅ Upload related documents together
- ✅ Use meaningful file names
- ❌ Avoid uploading duplicate documents
- ❌ Don't mix unrelated content

## Common Tasks

### Task 1: Upload and Search Multiple Documents

1. Upload Document A
2. Upload Document B
3. Ask question that might span both documents
4. System searches across all indexed documents

### Task 2: Get Detailed Answers

1. Upload document
2. Ask broad question: "What are the key topics?"
3. Ask follow-up questions: "Tell me more about [topic]"

### Task 3: Extract Specific Information

1. Upload document with tables
2. Ask: "What data is in the table?"
3. System extracts and formats table data

## FAQ

**Q: Can I upload multiple PDFs at once?**
A: Yes, select multiple files in the file dialog.

**Q: What happens if I upload the same PDF twice?**
A: The system detects duplicates and skips re-indexing.

**Q: How long does PDF processing take?**
A: Typically 5-30 seconds depending on PDF size.

**Q: Can I delete specific documents?**
A: Currently, reset the database by deleting the `db/` folder.

**Q: What's the maximum PDF size?**
A: Tested up to 100MB, but 10-50MB recommended for best performance.

**Q: Can I switch LLM providers mid-conversation?**
A: Changes require restarting the app.

**Q: Where are my documents stored?**
A: Embedded in the `db/` directory as vectors, not as original files.

**Q: Is my data private?**
A: Local storage only. Documents are not sent to external servers except for LLM processing.

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Shift+Enter | Submit message (in some interfaces) |
| Ctrl+C | Copy selected text |
| F5 | Refresh page/reset chat |

## Support & Troubleshooting

### Error: "No module named src"
- Ensure you're in the project directory
- Restart the Streamlit app

### Error: "API Key Invalid"
- Check `.env` file
- Verify key is active in LLM provider dashboard

### PDF won't upload
- Check file format (must be PDF)
- Verify file isn't corrupted
- Try a different PDF

### Slow responses
- Check internet connection (for LLM API)
- Reduce number of documents in database
- Consider using faster model

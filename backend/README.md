# Backend - Multimodal Knowledge Extraction

Phase 1-3 backend for file upload, text extraction, chunking, and knowledge base generation.

## Features
- Upload and extract text from: .vtt, .docx, .pptx, .pdf, .png, .jpg
- OCR for images using Tesseract
- Fixed-size chunking with sentence-aware boundaries
- Knowledge base generation with LangChain refine chain
- Outputs stored as JSON under extracted/, chunks/, and knowledge_base/

## Project Structure
backend/
  app/
    api/
    services/
    schemas/
    models/
    utils/
  uploads/
  extracted/
  chunks/
  knowledge_base/
  tests/

## Requirements
- Python 3.12+
- Tesseract OCR (for image extraction)

## Setup
```powershell
# From backend/
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Install Tesseract OCR (Windows):
- https://github.com/UB-Mannheim/tesseract/wiki
- Verify: `tesseract --version`

## Environment
Create .env in backend/ with:
```
OPENROUTER_API_KEY=your_key_here
```

## API Endpoints
Base URL: http://127.0.0.1:8000/api/v1

API docs:
- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

- GET /health (root)
  - Health check
  - Response: {"status": "ok"}

- POST /upload
  - Upload a file and return extracted text
  - Form field: file
  - Supported: .vtt, .docx, .pptx, .pdf, .png, .jpg
  - Response schema: UploadResponse
  - Errors: 400 invalid file, 500 extraction failure

- POST /chunks/from-text
  - Chunk raw text into fixed-size segments
  - Request schema: ChunkFromTextRequest
  - Response schema: ChunkResponse
  - Errors: 400 validation, 500 chunking failure

- POST /chunks/from-extracted
  - Chunk an extracted JSON file from Phase 1
  - Request schema: ChunkFromExtractedRequest
  - Response schema: ChunkResponse
  - Errors: 404 missing extracted file, 400 validation, 500 chunking failure

- POST /knowledge/from-text
  - Generate knowledge base content from raw text
  - Request schema: KnowledgeFromTextRequest
  - Response schema: KnowledgeResponse
  - Errors: 400 validation, 500 knowledge extraction failure

- POST /knowledge/from-extracted
  - Generate knowledge base content from extracted JSON
  - Request schema: KnowledgeFromExtractedRequest
  - Response schema: KnowledgeResponse
  - Errors: 404 missing extracted file, 400 validation, 500 knowledge extraction failure

- POST /knowledge/approve
  - Save an edited knowledge base draft
  - Request schema: KnowledgeApproveRequest
  - Response schema: KnowledgeApproveResponse
  - Errors: 400 validation, 500 knowledge approval failure

- POST /knowledge/assets
  - Upload an image asset for knowledge base content
  - Form field: file (.png, .jpg)
  - Response schema: KnowledgeAssetResponse
  - Errors: 400 validation, 500 asset upload failure

- POST /chatbot/query
  - Ask the local RAG chatbot a question
  - Request schema: ChatbotQueryRequest
  - Response schema: ChatbotQueryResponse
  - Errors: 400 validation, 500 chatbot query failure

- POST /auth/signup
  - Create a user account

- POST /auth/login
  - Authenticate and return JWT access token

- GET /auth/me
  - Return the current user profile (JWT required)

- POST /kb/create
  - Create a KB owned by the current user

- PUT /kb/{id}
  - Update KB (owner only)

- DELETE /kb/{id}
  - Delete KB (owner only)

- GET /kb/my-kbs
  - List current user's KBs

- GET /kb/{id}
  - Get KB (owner or published)

- POST /kb/{id}/publish
  - Publish KB (owner only) and sync vector store

- POST /kb/{id}/unpublish
  - Unpublish KB (owner only) and sync vector store

### Example curl
Health:
```bash
curl -X GET "http://127.0.0.1:8000/health"
```

Upload:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/upload" \
  -F "file=@sample.pdf"
```

Chunk from extracted:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chunks/from-extracted" \
  -H "Content-Type: application/json" \
  -d '{"extracted_filename":"sample.json","chunk_size":800,"chunk_overlap":100,"save":true}'
```

Chunk from text:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chunks/from-text" \
  -H "Content-Type: application/json" \
  -d '{"source":"doc.txt","text":"...","chunk_size":800,"chunk_overlap":100,"save":true}'
```

Knowledge from text:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/knowledge/from-text" \
  -H "Content-Type: application/json" \
  -d '{"source":"doc.txt","text":"...","chunk_size":1200,"chunk_overlap":150,"max_parts":10,"save_output":true}'
```

Knowledge from extracted:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/knowledge/from-extracted" \
  -H "Content-Type: application/json" \
  -d '{"extracted_filename":"sample.json","chunk_size":1200,"chunk_overlap":150,"max_parts":10,"save_output":true}'
```

Knowledge approve:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/knowledge/approve" \
  -H "Content-Type: application/json" \
  -d '{"source":"doc.pdf","title":"Final KB","content":"# Overview\n..."}'
```

Knowledge asset upload:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/knowledge/assets" \
  -F "file=@diagram.png"
```

Chatbot query:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chatbot/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is IAFB pruning?","top_k":5,"min_score":0.2}'
```

### Example frontend fetch
```javascript
const res = await fetch("http://127.0.0.1:8000/api/v1/upload", {
  method: "POST",
  body: (() => {
    const data = new FormData();
    data.append("file", fileInput.files[0]);
    return data;
  })(),
});
const payload = await res.json();
```

## Run API
```powershell
# From backend/
uvicorn app.main:app --reload
```

## Frontend (Streamlit)
```powershell
# From backend/
streamlit run frontend/streamlit_app.py
```

Optional environment variable:
```
API_BASE_URL=http://127.0.0.1:8000/api/v1
```

## Phase 1 Test
```powershell
python tests/test_phase1.py
```
- Generates sample files, uploads them, prints extracted text.

## Phase 2 Test
```powershell
python tests/test_phase2.py
```
- Loads extracted JSON, chunks it, prints chunk sizes, validates order and overlap.

## Phase 3 Test
Default uses the provided TXT transcript:
```powershell
python tests/test_phase3.py
```

Run against a PDF or DOCX directly:
```powershell
python tests/test_phase3.py "C:\path\to\file.pdf"
python tests/test_phase3.py "C:\path\to\file.docx"
```

Phase 3 output is saved to:
- backend/knowledge_base/<source>_knowledge.json

Images uploaded via the frontend are saved to:
- backend/knowledge_base/assets/
- Markdown will reference them as assets/<filename>

Assets are served by the API at:
- http://127.0.0.1:8000/assets/<filename>

## Notes
- OCR relies on Tesseract binary being installed and accessible.
- OpenRouter API key is required for Phase 3.

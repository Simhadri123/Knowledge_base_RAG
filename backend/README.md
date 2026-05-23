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
Base URL: http://127.0.0.1:8000

- GET /health
  - Health check
  - Response: {"status": "ok"}

- POST /upload
  - Upload a file and return extracted text
  - Form field: file
  - Supported: .vtt, .docx, .pptx, .pdf, .png, .jpg
  - Response:
    {
      "filename": "...",
      "stored_path": "...",
      "extracted_path": "...",
      "file_type": ".pdf",
      "text": "...",
      "metadata": {"pages": "1"}
    }

## Run API
```powershell
# From backend/
uvicorn app.main:app --reload
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

## Notes
- OCR relies on Tesseract binary being installed and accessible.
- OpenRouter API key is required for Phase 3.

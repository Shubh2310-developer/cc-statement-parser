cc-statement-parser/
│
├── README.md                          # Project overview, setup instructions, architecture diagram
├── ARCHITECTURE.md                    # Detailed architecture documentation
├── LICENSE                            # License file
├── .gitignore                         # Git ignore patterns
├── .env.example                       # Environment variables template
├── docker-compose.yml                 # Local development orchestration
├── docker-compose.prod.yml            # Production deployment configuration
├── Makefile                           # Common commands (setup, test, run, clean)
│
├── docs/                              # Documentation
│   ├── api/
│   │   ├── openapi.yaml              # API specification
│   │   └── endpoints.md              # API endpoint documentation
│   ├── architecture/
│   │   ├── diagrams/                 # Architecture diagrams (PNG/SVG)
│   │   ├── design-decisions.md       # ADRs (Architecture Decision Records)
│   │   └── data-flow.md             # Data flow documentation
│   ├── deployment/
│   │   ├── deployment-guide.md       # Deployment instructions
│   │   └── environment-setup.md      # Environment configuration guide
│   └── user-guide.md                 # End-user documentation
│
├── backend/                           # Backend service
│   ├── Dockerfile                    # Backend container definition
│   ├── requirements.txt              # Python dependencies (pinned versions)
│   ├── requirements-dev.txt          # Development dependencies
│   ├── pytest.ini                    # Pytest configuration
│   ├── .pylintrc                     # Linting configuration
│   │
│   ├── app/                          # Main application package
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI application entry point
│   │   ├── config.py                 # Configuration management
│   │   ├── dependencies.py           # Dependency injection
│   │   │
│   │   ├── api/                      # API layer
│   │   │   ├── __init__.py
│   │   │   ├── v1/                   # API version 1
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py         # Main router aggregation
│   │   │   │   └── endpoints/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── parse.py      # Document parsing endpoints
│   │   │   │       ├── jobs.py       # Job management endpoints
│   │   │   │       └── health.py     # Health check endpoints
│   │   │   │
│   │   │   └── middleware/
│   │   │       ├── __init__.py
│   │   │       ├── error_handler.py  # Global error handling
│   │   │       ├── logging.py        # Request/response logging
│   │   │       └── security.py       # Security middleware
│   │   │
│   │   ├── core/                     # Core business logic
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── document/             # Document processing
│   │   │   │   ├── __init__.py
│   │   │   │   ├── ingestion.py      # Upload and validation
│   │   │   │   ├── preprocessor.py   # Document preprocessing
│   │   │   │   ├── classifier.py     # Issuer classification
│   │   │   │   └── quality_checker.py # Quality assessment
│   │   │   │
│   │   │   ├── extraction/           # Extraction engine
│   │   │   │   ├── __init__.py
│   │   │   │   ├── orchestrator.py   # Extraction workflow orchestration
│   │   │   │   ├── text_extractor.py # Text extraction (PyMuPDF/pdfplumber)
│   │   │   │   ├── ocr_engine.py     # OCR processing
│   │   │   │   ├── table_extractor.py # Table extraction
│   │   │   │   ├── layout_analyzer.py # Layout analysis
│   │   │   │   └── field_mapper.py   # Field mapping coordination
│   │   │   │
│   │   │   ├── parsers/              # Issuer-specific parsers
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py           # Abstract base parser interface
│   │   │   │   ├── factory.py        # Parser factory (strategy pattern)
│   │   │   │   ├── hdfc_parser.py    # HDFC-specific parser
│   │   │   │   ├── icici_parser.py   # ICICI-specific parser
│   │   │   │   ├── sbi_parser.py     # SBI-specific parser
│   │   │   │   ├── axis_parser.py    # Axis-specific parser
│   │   │   │   └── amex_parser.py    # American Express parser
│   │   │   │
│   │   │   ├── validation/           # Data validation
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schema_validator.py # Schema validation
│   │   │   │   ├── business_rules.py  # Business logic validation
│   │   │   │   ├── confidence_scorer.py # Confidence calculation
│   │   │   │   └── anomaly_detector.py # Anomaly detection
│   │   │   │
│   │   │   └── ml/                   # Machine learning components (optional)
│   │   │       ├── __init__.py
│   │   │       ├── layout_model.py   # LayoutLM integration
│   │   │       ├── entity_recognizer.py # NER for financial entities
│   │   │       └── model_loader.py   # Model loading and caching
│   │   │
│   │   ├── models/                   # Data models and schemas
│   │   │   ├── __init__.py
│   │   │   ├── domain/               # Domain models
│   │   │   │   ├── __init__.py
│   │   │   │   ├── document.py       # Document entity
│   │   │   │   ├── extraction_result.py # Extraction result entity
│   │   │   │   ├── job.py            # Job entity
│   │   │   │   └── field.py          # Field models (card, transaction, etc.)
│   │   │   │
│   │   │   ├── schemas/              # Pydantic schemas (API contracts)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── request.py        # Request schemas
│   │   │   │   ├── response.py       # Response schemas
│   │   │   │   └── internal.py       # Internal data transfer objects
│   │   │   │
│   │   │   └── enums.py              # Enumerations (status, issuer, etc.)
│   │   │
│   │   ├── services/                 # Service layer (business orchestration)
│   │   │   ├── __init__.py
│   │   │   ├── parsing_service.py    # Main parsing service
│   │   │   ├── job_service.py        # Job management service
│   │   │   └── result_service.py     # Result retrieval service
│   │   │
│   │   ├── repositories/             # Data access layer
│   │   │   ├── __init__.py
│   │   │   ├── base.py               # Base repository pattern
│   │   │   ├── job_repository.py     # Job data access
│   │   │   ├── document_repository.py # Document storage access
│   │   │   └── result_repository.py  # Result data access
│   │   │
│   │   ├── storage/                  # Storage abstraction
│   │   │   ├── __init__.py
│   │   │   ├── base.py               # Storage interface
│   │   │   ├── local_storage.py      # Local file system
│   │   │   └── s3_storage.py         # S3-compatible storage (future)
│   │   │
│   │   ├── database/                 # Database management
│   │   │   ├── __init__.py
│   │   │   ├── connection.py         # Database connection management
│   │   │   ├── models.py             # ORM models (SQLAlchemy)
│   │   │   └── migrations/           # Database migrations (Alembic)
│   │   │       └── versions/
│   │   │
│   │   └── utils/                    # Utility functions
│   │       ├── __init__.py
│   │       ├── logger.py             # Structured logging setup
│   │       ├── security.py           # Security utilities (PII masking)
│   │       ├── file_utils.py         # File handling utilities
│   │       ├── date_parser.py        # Date parsing utilities
│   │       ├── currency_parser.py    # Currency normalization
│   │       └── exceptions.py         # Custom exception classes
│   │
│   ├── tests/                        # Test suite
│   │   ├── __init__.py
│   │   ├── conftest.py               # Pytest fixtures and configuration
│   │   │
│   │   ├── unit/                     # Unit tests
│   │   │   ├── __init__.py
│   │   │   ├── core/
│   │   │   │   ├── test_text_extractor.py
│   │   │   │   ├── test_table_extractor.py
│   │   │   │   └── test_parsers.py
│   │   │   ├── services/
│   │   │   │   └── test_parsing_service.py
│   │   │   └── utils/
│   │   │       └── test_date_parser.py
│   │   │
│   │   ├── integration/              # Integration tests
│   │   │   ├── __init__.py
│   │   │   ├── test_api_endpoints.py
│   │   │   └── test_full_pipeline.py
│   │   │
│   │   ├── e2e/                      # End-to-end tests
│   │   │   ├── __init__.py
│   │   │   └── test_complete_flow.py
│   │   │
│   │   └── fixtures/                 # Test data and mocks
│   │       ├── sample_pdfs/          # Sample statements per issuer
│   │       │   ├── hdfc_sample.pdf
│   │       │   ├── icici_sample.pdf
│   │       │   ├── sbi_sample.pdf
│   │       │   ├── axis_sample.pdf
│   │       │   └── amex_sample.pdf
│   │       ├── expected_results/     # Ground truth for validation
│   │       │   └── *.json
│   │       └── edge_cases/           # Edge case PDFs (scanned, rotated, etc.)
│   │
│   └── scripts/                      # Utility scripts
│       ├── init_db.py                # Database initialization
│       ├── seed_data.py              # Test data seeding
│       └── benchmark.py              # Performance benchmarking
│
├── frontend/                         # Frontend application
│   ├── Dockerfile                    # Frontend container definition
│   ├── package.json                  # Node dependencies
│   ├── package-lock.json
│   ├── vite.config.js                # Vite configuration
│   ├── tailwind.config.js            # Tailwind CSS configuration
│   ├── .eslintrc.json                # ESLint configuration
│   ├── .prettierrc                   # Prettier configuration
│   │
│   ├── public/                       # Static assets
│   │   ├── favicon.ico
│   │   └── robots.txt
│   │
│   ├── src/                          # Source code
│   │   ├── main.jsx                  # Application entry point
│   │   ├── App.jsx                   # Root component
│   │   │
│   │   ├── components/               # React components
│   │   │   ├── common/               # Reusable components
│   │   │   │   ├── Button.jsx
│   │   │   │   ├── Card.jsx
│   │   │   │   ├── Spinner.jsx
│   │   │   │   └── Alert.jsx
│   │   │   │
│   │   │   ├── upload/               # Upload-related components
│   │   │   │   ├── FileUploader.jsx
│   │   │   │   └── UploadProgress.jsx
│   │   │   │
│   │   │   ├── results/              # Results display components
│   │   │   │   ├── ResultCard.jsx
│   │   │   │   ├── FieldDisplay.jsx
│   │   │   │   ├── TransactionTable.jsx
│   │   │   │   └── ConfidenceIndicator.jsx
│   │   │   │
│   │   │   └── preview/              # PDF preview components
│   │   │       ├── PDFViewer.jsx
│   │   │       └── HighlightOverlay.jsx
│   │   │
│   │   ├── services/                 # API services
│   │   │   ├── api.js                # API client configuration
│   │   │   └── parsingService.js     # Parsing API calls
│   │   │
│   │   ├── hooks/                    # Custom React hooks
│   │   │   ├── useFileUpload.js
│   │   │   └── usePolling.js
│   │   │
│   │   ├── utils/                    # Utility functions
│   │   │   ├── formatters.js         # Data formatting
│   │   │   └── validators.js         # Client-side validation
│   │   │
│   │   └── styles/                   # Global styles
│   │       └── index.css             # Tailwind imports and custom styles
│   │
│   └── tests/                        # Frontend tests
│       └── components/
│           └── FileUploader.test.jsx
│
├── config/                           # Configuration files
│   ├── issuer_templates/             # Issuer-specific configuration
│   │   ├── hdfc.yaml                 # HDFC parsing rules and patterns
│   │   ├── icici.yaml                # ICICI parsing rules and patterns
│   │   ├── sbi.yaml                  # SBI parsing rules and patterns
│   │   ├── axis.yaml                 # Axis parsing rules and patterns
│   │   └── amex.yaml                 # American Express parsing rules
│   │
│   ├── logging/
│   │   └── logging_config.yaml       # Logging configuration
│   │
│   └── models/                       # ML model configurations (if applicable)
│       └── layout_model_config.json
│
├── data/                             # Runtime data (gitignored)
│   ├── uploads/                      # Temporary upload storage
│   ├── processed/                    # Processed documents
│   └── db/                           # Database files (SQLite)
│
├── logs/                             # Application logs (gitignored)
│   └── .gitkeep
│
├── models/                           # ML models (gitignored, downloaded at runtime)
│   └── .gitkeep
│
├── scripts/                          # Project-level scripts
│   ├── setup.sh                      # Initial setup script
│   ├── run_tests.sh                  # Test execution script
│   ├── docker_build.sh               # Docker build script
│   └── deploy.sh                     # Deployment script
│
└── .github/                          # GitHub specific files
    ├── workflows/                    # CI/CD pipelines
    │   ├── ci.yml                    # Continuous integration
    │   ├── lint.yml                  # Code quality checks
    │   └── deploy.yml                # Deployment workflow
    │
    ├── ISSUE_TEMPLATE/               # Issue templates
    │   ├── bug_report.md
    │   └── feature_request.md
    │
    └── pull_request_template.md      # PR template

Here’s a complete, production-grade plan you can implement in VSCode and demo by Oct 15. Actionable, technical, and minimal noise.

Summary

Build a microservice-based PDF statement parser. Backend in Python (FastAPI). Frontend minimal React for upload + results. Use hybrid rule-based + ML layout parsing to handle 5 issuers reliably. Deliverables: runnable repo, Docker containers, test PDFs, README, short demo video.

Tech stack (best tradeoffs)

Backend: Python 3.11, FastAPI (async, easy APIs, swagger).

PDF & layout: PyMuPDF (fitz) + pdfplumber (text extraction) + pdfminer.six (fallback).

OCR: Tesseract via pytesseract for scanned PDFs.

Table extraction: Camelot (lattice/stream) + tabula-py fallback.

Layout/ML (optional but recommended): LayoutLMv3 or Donut-like small model via Hugging Face for robust field extraction.

Regex & heuristics: Python re and deterministic parsers.

Storage: local for internship. Use SQLite for metadata, S3-compatible (minio) for files if needed.

Frontend: React (Vite) + Tailwind CSS minimal UI for upload and results.

Orchestration: Docker Compose for local dev. CI: GitHub Actions (lint, tests, build).

Testing: pytest, sample PDFs, unit + integration tests.

Logging/Observability: structlog + request ids. Optionally Sentry.

Security: HTTPS in prod, encryption at rest for PDFs, mask PII in logs.

Dev tools: VSCode + Python extension, Prettier/ESLint, FastAPI plugin.

Architecture (high-level)

Client (React) uploads PDF → POST /parse.

FastAPI receives file. Save to temp store. Create job id.

Worker pipeline (same process or background worker):

Step A: classify issuer (model + heuristics).

Step B: extract text + layout (PyMuPDF/pdfplumber).

Step C: if scanned or poor text: run Tesseract OCR.

Step D: run table extractor (Camelot/Tabula) for transaction tables.

Step E: run per-issuer extraction pipeline:

Layout/ML field extraction (LayoutLM) OR

Heuristic + regex templates + table mapping.

Step F: validate extracted fields via schema and confidence scoring.

Step G: return JSON with extracted 5 fields + confidence + raw snippets + coordinates for traceability.

Response delivered synchronously for small files. For heavy jobs use background queue (RabbitMQ) and polling endpoint.

DB logs job, status, raw outputs, sanitized extract for audit.

Components & responsibilities

API service: upload, status, fetch results.

Parser core: modular extractors per issuer. Expose common interface: parse(pdf_bytes) -> ParseResult.

OCR module: configurable language and DPI settings.

Issuer classifier: fast heuristic (logo, issuer name) plus small classifier if ambiguous.

Rule engine: templates per issuer using XPath-like coordinates + regex.

ML extractor (optional): finetune LayoutLM on a few labeled statements per issuer for robustness.

Tests & sample data: 5 issuer PDFs × variations (scanned, rotated, watermarks).

Frontend: file chooser, display JSON, highlight bounding boxes overlay on a rendered PDF (for demo).

CI/CD: run unit tests and lint on push. Build Docker images.

Fields to extract (recommended)

Pick 5 required fields. Example set to maximize impact:

Card last 4 digits (metadata)

Card variant (e.g., Platinum)

Billing cycle start/end (dates)

Payment due date

Transaction table (date, description, amount) — return top N + table link

Parsing strategy (robust)

Detect text vs scanned: quick pdfplumber text length heuristic. If text length < threshold, OCR.

Normalize: unify whitespace, replace unicode dashes, normalize dates with dateutil.

Issuer detection:

Search header for known issuer names/addresses.

Fallback: logo image template matching via SIFT/ORB or simple fuzzy string match on first page text.

Field extraction:

Deterministic: regex + proximity to label tokens ("Payment Due", "Amount Due").

Spatial: identify coordinates (x0,y0,x1,y1). Use nearest label for ambiguous fields.

Tables: Camelot lattice first; stream fallback. Post-process cell merging and currency detection.

Confidence: compute rule coverage score. If < threshold, mark low confidence and include snippet.

ML fallback: LayoutLM for documents where heuristic fails. Train on ~50 labeled pages per issuer for good results.

Post-processing: date parsing, currency normalization, negative vs credit indicator.

Implementation plan (MVP in 3 days, polish by Oct 15)

Day 1 (MVP):

Scaffold FastAPI app + React upload page.

Implement single-file upload and store.

Implement text extraction (PyMuPDF) + simple issuer detection (name-based).

Implement simple regex-based extraction for 5 fields for 2 issuers.

Demo working flow with sample PDFs.

Day 2 (stabilize + more issuers):

Add OCR fallback with Tesseract.

Add Camelot table extraction.

Add two more issuer templates.

Add unit tests and basic logging.

Containerize with Docker Compose.

Day 3 (polish + demo prep):

Add issuer classifier improvements.

Add confidence scoring and result JSON format.

Build frontend PDF preview + highlighting of extracted fields.

Write README, run tests, record 3–5 minute demo video.

Prepare short slide with architecture diagram and evaluation.

Optional Day 4–5 (stretch before Oct 15):

Add LayoutLM model finetune for one issuer.

Add RabbitMQ background queue for heavy OCR.

Add sample dataset and evaluation metrics.

Data model (JSON)
{
  "job_id": "uuid",
  "issuer": "HDFC",
  "fields": {
    "card_last4": {"value":"1234","confidence":0.98,"snippet":"Card ending 1234","coords":[...]},
    "card_variant":{"value":"Platinum","confidence":0.9},
    "billing_cycle":{"start":"2025-09-01","end":"2025-09-30"},
    "due_date":{"value":"2025-10-05"},
    "transactions":{"rows":[{"date":"2025-09-05","desc":"AMAZON","amount":-799.0}], "confidence":0.85}
  },
  "raw_text_snippets": [...],
  "status":"done"
}

Repo layout (suggested)
/cc-stmt-parser
├─ backend/
│  ├─ app/
│  │  ├─ main.py        # FastAPI app
│  │  ├─ parsers/
│  │  │  ├─ __init__.py
│  │  │  ├─ base.py     # Parser interface
│  │  │  ├─ issuer_hdfc.py
│  │  │  └─ issuer_icici.py
│  │  ├─ ocr.py
│  │  ├─ table_extractor.py
│  │  └─ utils.py
│  ├─ tests/
│  └─ Dockerfile
├─ frontend/
│  ├─ src/
│  └─ Dockerfile
├─ docker-compose.yml
├─ README.md
└─ samples/   # PDFs for testing

Implementation details & code snippets

Use pipenv or poetry.

FastAPI endpoint example:

from fastapi import FastAPI, File, UploadFile
from app.parsers.factory import parse_pdf

app = FastAPI()
@app.post("/parse")
async def parse(file: UploadFile = File(...)):
    data = await file.read()
    result = parse_pdf(data)
    return result


PDF text extraction (PyMuPDF):

import fitz
def extract_text(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]
    return page.get_text("dict")  # gives blocks with coords


OCR fallback example:

from PIL import Image
import pytesseract
def ocr_image(pil_img):
    return pytesseract.image_to_string(pil_img, lang='eng')

Evaluation & metrics

Accuracy per field: compare against ground truth. Target >90% for deterministic fields (card last4, due date).

Table extraction accuracy: row-level match F1.

Latency: target <3s for text PDFs, <8s for OCR.

Robustness: test on scanned, rotated, low-contrast PDFs.

Demo plan (what to show)

Upload 5 sample PDFs (one per issuer) via UI.

Show parsed JSON and highlighted fields on PDF preview.

Show confidence scores and raw snippets.

Show test suite passing and Docker Compose bringing system up.

Explain fallback flows and edge cases.

Risks & mitigations

Scanned low-quality PDFs → Use OCR + image preprocessing (binarization, deskew).

Diverse layouts → Use hybrid approach: deterministic rules + ML layout model.

PII handling → Encrypt storage and redact logs.

Time → Prioritize 2 issuers + table extraction for MVP; add rest on Day 2.

Security & privacy

Do not log full PDF contents.

Mask card numbers leaving only last 4.

Use HTTPS in deployment.

Add access control for API.

What I will deliver if you want me to implement now

Full backend repo (FastAPI) with 3 issuer parsers.

React minimal UI for upload + preview.

Docker Compose and sample PDFs.

Tests and README with run steps and demo script.

If you want that, tell me: which 5 issuers to support (I recommend HDFC, SBI Card, ICICI, Axis Bank, American Express). I will produce the repo structure, core parser code, and a runnable Docker Compose setup you can open in VSCode.

Objective
Build a PDF parser that extracts 5 key data points from credit card statements across 5 major
credit card issuers.
Requirements
Scope:
● Support statements from 5 different credit card providers (you may choose which ones)
● Extract any 5 data points of your choice (examples: transaction info, card variant, card
last 4 digits, billing cycle, payment due date, total balance)
● Handle real-world PDF statement formats
Deliverable: Submit your solution in whatever format you believe best demonstrates your work.
Be prepared to demonstrate your work.
Evaluation: Your submission will be assessed on functionality, implementation quality, and how
effectively you present your solution.
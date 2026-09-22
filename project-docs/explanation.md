# Document Intelligence & RAG Platform - Architecture and Design Explanation

This document explains the technical decisions, architecture, and tradeoffs of the Document Intelligence & RAG Platform.

## Architecture Decisions

The system is built as a decoupled monolith for the backend (Django + DRF) and an SPA for the frontend (React). 
We use Redis and Celery for asynchronous processing because document ingestion (text extraction, chunking, and embedding generation) is computationally intensive and should not block the main request/response cycle.

### Database Design

The PostgreSQL database is designed to handle multi-tenant data securely:
- **Workspace**: The top-level grouping for isolation.
- **Document**: Represents the logical file uploaded by a user.
- **DocumentVersion**: Allows for future updates to the same document.
- **DocumentChunk**: The processed segments of a document. We only store metadata here; the vectors are in ChromaDB.
- **Task**: Tracks background jobs (Celery task IDs) for UI polling.

### Ingestion Flow

1. User uploads a file via the API.
2. The API validates the file, creates a `Document` record in PostgreSQL, and saves the file via the S3 abstraction.
3. The API kicks off a Celery task and returns the `Task` ID to the user.
4. The Celery worker downloads the file, extracts text based on mime-type (PDF, DOCX, TXT), splits it into chunks using a text splitter.
5. `sentence-transformers` generates embeddings for each chunk.
6. The chunks and vectors are inserted into ChromaDB. The `Document` status is updated to `READY`.

### RAG Pipeline

The RAG implementation follows a standard retrieve-then-generate pattern:
1. User submits a query.
2. The query is embedded using the same model as ingestion.
3. ChromaDB performs similarity search, filtered by workspace/document metadata.
4. Top-K chunks are retrieved and used to construct a prompt.
5. The prompt is sent to the LLM Provider abstraction.
6. A response is generated and linked to the source chunks as `Citations`.

### Abstractions

- **Storage**: Provides a clean interface `save()`, `get_url()`, `read()`. For local dev, a `MockStorage` saves to the filesystem. For production, `S3Storage` uses boto3.
- **LLM Provider**: Interface `generate_response()`. A mock provider returns static/simulated responses, while a real implementation can wrap OpenAI or Anthropic SDKs.

### Security Considerations

- Workspaces isolate data. Every query checks the user's membership to the workspace.
- Secrets are not hardcoded.
- File uploads are validated to prevent malicious payloads.

# Document Intelligence & RAG Platform

A production-quality Document Intelligence platform allowing users to upload documents, extract text, perform semantic searches, and interact with an AI through a Retrieval-Augmented Generation (RAG) architecture.

## Architecture & Features

- **Backend**: Django, Django REST Framework, Celery, Redis, PostgreSQL
- **Frontend**: React, TypeScript, Vite, CSS Modules
- **AI/ML**: `sentence-transformers` for embeddings, ChromaDB for vector storage
- **Features**:
  - Secure JWT Authentication
  - Workspace-based multi-tenancy
  - Asynchronous background document ingestion (PDF, DOCX, TXT)
  - Semantic similarity search using ChromaDB
  - RAG chat interface with document citations

## Setup and Local Development

### Prerequisites

- Docker and Docker Compose
- Node.js (v18+)

### Environment Variables

Copy the `.env.example` file to `.env` and fill in the required values.

```bash
cp .env.example .env
```

### Starting the Infrastructure

Start PostgreSQL, Redis, and ChromaDB:

```bash
docker-compose up -d
```

### Backend Setup (Local)

1. Create a virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run migrations:
   ```bash
   python manage.py migrate
   ```
4. Start the Celery worker:
   ```bash
   celery -A config worker --loglevel=info
   ```
5. Start the API server:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Start the development server:
   ```bash
   npm run dev
   ```

## Testing

Run backend tests using `pytest`:
```bash
cd backend
pytest
```

## API Overview

- `POST /api/auth/register/` - Register a new user
- `POST /api/auth/login/` - Obtain JWT tokens
- `GET /api/auth/workspaces/` - List user workspaces
- `POST /api/documents/` - Upload a document
- `GET /api/documents/tasks/<id>/` - Poll processing status
- `POST /api/conversations/<id>/messages/` - Send a RAG query

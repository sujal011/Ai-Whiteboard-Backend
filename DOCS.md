# AI Whiteboard Backend API

A complete, production-ready Python backend designed to support an AI-native whiteboard application. This system supports secure user authentication, distinct workspaces, file vectorization for RAG, and an intelligent chatbot layer utilizing LangChain and Gemini/Groq LLMs.

## Core Features

-   **User Authentication**: JWT-based authentication using bcrypt hashing. Access boundaries are protected on all user-facing endpoints.
-   **Workspace Management**: RESTful API enabling the creation and modification of isolated Workspaces. Designed to handle state persistence (via JSON-B storage) for rich frontend applications like Excalidraw and Editor.js.
-   **Document Integration & Async Processing (RAG)**: Users can upload PDF and TXT files, which are chunked, embedded using Google GenAI, and pushed to a localized vector database (PGVector) for subsequent search queries.
-   **Langchain Centralized Intelligence layer**: Centralized LLM logic replacing previously scattered inference scripts, enabling:
    -   Natural language to Mermaid chart conversion (`/generate`).
    -   RAG context querying over workspace documents (`/ask`).
    -   General chat with multimodal visual understanding of base64 whiteboard views (`/general`).

## Technical Architecture

-   **Framework**: FastAPI
-   **Datastore**: PostgreSQL (Relational + Vector Store)
-   **Vector Extension**: `pgvector`
-   **ORM & Migrations**: SQLAlchemy & Alembic
-   **AI Operations Orchestrator**: LangChain

## Getting Started

### 1. Environment Setup

Create a `.env` file at the root of the project with your secrets:

```env
# API Keys for AI Generation
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Security
SECRET_KEY=a_very_secret_key_change_me_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080 # 7 days

# Database Configurations
DATABASE_URL=postgresql://admin:adminpassword@localhost:5432/whiteboard_db
```

### 2. Stand up PostgreSQL (with PGVector)

Use the provided docker compose file to instantiate the backend data tier, mapped to port `5432`.

```bash
docker-compose up -d
```

### 3. Install Python Dependencies

(It is highly recommended to do this within a localized virtual environment `venv`)

```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations

Use Alembic to synchronize the underlying PostgreSQL container schema to your Python Data Models:

```bash
alembic upgrade head
```

### 5. Start the Server

Start up the API using uvicorn:

```bash
uvicorn app.main:app --reload
```

You can now interact with the FastAPI Swagger dashboard at `http://127.0.0.1:8000/docs`.

See `API_DOCS.md` for a comprehensive overview of all exposed endpoints.

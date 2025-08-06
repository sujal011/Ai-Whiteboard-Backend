# Workspace Backend API

A powerful Bun + Hono backend for managing workspaces with AI-powered RAG capabilities, file processing, and vector search.

## Features

- 🔐 **Authentication**: JWT-based auth with login/register
- 🏢 **Workspaces**: Users can create up to 5 workspaces
- 📝 **Content Management**: 
  - Excalidraw drawings storage
  - EditorJS markdown content
- 📁 **File Processing**: 
  - Upload up to 3 files per workspace
  - Automatic vectorization and storage in Qdrant
  - Support for PDF, DOC/DOCX, TXT, MD, XLS/XLSX
- 🤖 **AI Integration**: 
  - RAG-powered Q&A with workspace content
  - Support for multiple AI models (GPT-4, Claude, Gemini)
  - Streaming and non-streaming responses
- 🔍 **Vector Search**: Isolated Qdrant collections per workspace

## Tech Stack

- **Runtime**: Bun
- **Framework**: Hono
- **Database**: PostgreSQL
- **Vector DB**: Qdrant
- **AI**: Vercel AI SDK with multiple providers
- **File Processing**: PDF-parse, Mammoth, XLSX
- **Authentication**: JWT + bcrypt

## Quick Start

### 1. Prerequisites

- Bun installed
- Docker and Docker Compose
- API keys for AI providers (OpenAI required, others optional)

### 2. Setup

```bash
# Clone and install dependencies
git clone <your-repo>
cd workspace-backend
bun install

# Copy environment file
cp .env.example .env
# Edit .env with your API keys and configuration

# Start databases
docker-compose up -d postgres qdrant

# Run database migration
bun run db:migrate

# Start development server
bun run dev
```

### 3. Environment Variables

Create a `.env` file with:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=workspace_app
DB_USER=postgres
DB_PASSWORD=password

# JWT
JWT_SECRET=your-super-secret-jwt-key

# Vector Database
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=optional-api-key

# AI Providers (OpenAI required for embeddings)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=your-key  # Optional
GOOGLE_GENERATIVE_AI_API_KEY=your-key  # Optional

# Server
PORT=3001
NODE_ENV=development
```

## API Endpoints

### Authentication

```bash
# Register
POST /auth/register
{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe"
}

# Login
POST /auth/login
{
  "email": "user@example.com",
  "password": "password123"
}

# Get profile
GET /auth/me
Authorization: Bearer <token>
```

### Workspaces

```bash
# Get all workspaces
GET /workspaces
Authorization: Bearer <token>

# Create workspace
POST /workspaces
Authorization: Bearer <token>
{
  "name": "My Workspace",
  "description": "Optional description"
}

# Get workspace with content
GET /workspaces/:id
Authorization: Bearer <token>

# Update workspace content
PUT /workspaces/:id/content
Authorization: Bearer <token>
{
  "excalidrawData": {...},
  "editorjsData": {...}
}

# Delete workspace
DELETE /workspaces/:id
Authorization: Bearer <token>
```

### File Management

```bash
# Upload file (multipart/form-data)
POST /workspaces/:id/files
Authorization: Bearer <token>
Content-Type: multipart/form-data

# Delete file
DELETE /workspaces/:id/files/:fileId
Authorization: Bearer <token>
```

### AI Chat

```bash
# Streaming AI response
POST /ai/ask
Authorization: Bearer <token>
{
  "message": "What does the uploaded document say about...?",
  "workspaceId": "uuid",
  "model": "gpt-4",
  "includeContext": true,
  "maxTokens": 1000
}

# Non-streaming AI response
POST /ai/ask-sync
Authorization: Bearer <token>
{
  "message": "Summarize the key points from my files",
  "workspaceId": "uuid",
  "model": "claude-3-sonnet",
  "includeContext": true
}

# Get conversation history
GET /ai/conversations/:workspaceId
Authorization: Bearer <token>

# Get available models
GET /ai/models
```

## Database Schema

### Core Tables

- **users**: User accounts and authentication
- **workspaces**: User workspaces (max 5 per user)
- **workspace_content**: Excalidraw and EditorJS data
- **processed_files**: File metadata and vector counts
- **ai_conversations**: Chat history (optional)

### Vector Storage

- Each workspace gets its own Qdrant collection: `workspace_{id}`
- Automatic cleanup when workspace is deleted
- Embeddings generated using OpenAI's text-embedding-3-small

## File Processing Flow

1. **Upload**: File uploaded via multipart form
2. **Validation**: Check file type and workspace limits
3. **Text Extraction**: 
   - PDF → pdf-parse
   - DOC/DOCX → mammoth
   - XLS/XLSX → xlsx
   - TXT/MD → direct read
4. **Chunking**: Split text using LangChain's RecursiveCharacterTextSplitter
5. **Vectorization**: Generate embeddings using OpenAI
6. **Storage**: Store vectors in workspace-specific Qdrant collection
7. **Metadata**: Save file info in PostgreSQL

## RAG Implementation

1. **Query Processing**: User asks question about workspace
2. **Vector Search**: Find similar content chunks in Qdrant
3. **Context Assembly**: Combine relevant chunks with workspace content
4. **AI Generation**: Send context + query to chosen AI model
5. **Response**: Return AI response with source citations

## Supported AI Models

- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude 3 Sonnet, Claude 3 Haiku
- **Google**: Gemini Pro, Gemini 1.5 Pro

## Security Features

- JWT authentication with 7-day expiry
- Password hashing with bcrypt
- User isolation (users can only access their own workspaces)
- Vector isolation (each workspace has separate Qdrant collection)
- Input validation with Zod schemas
- CORS configuration for frontend integration

## Development

```bash
# Install dependencies
bun install

# Start development server with hot reload
bun run dev

# Run database migration
bun run db:migrate

# Start only databases
docker-compose up -d postgres qdrant

# View logs
docker-compose logs -f
```

## Production Deployment

1. Set `NODE_ENV=production` in environment
2. Use strong `JWT_SECRET`
3. Configure production database URLs
4. Set up proper CORS origins
5. Consider using managed Qdrant cloud service
6. Implement rate limiting and monitoring

## Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres
```

### Qdrant Issues
```bash
# Check Qdrant health
curl http://localhost:6333/health

# View Qdrant collections
curl http://localhost:6333/collections
```

### File Processing Errors
- Ensure all AI provider API keys are set
- Check file size limits and supported formats
- Verify Qdrant connection for vector storage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details

### Upcoming changes - 
Yes, you can safely use direct SQL without an ORM if you follow proper security practices. The code I provided is actually quite secure, but here are the key steps to ensure your backend remains secure:

## ✅ Current Security (Already Implemented)

1. **Parameterized Queries**: Using `postgres` library with template literals (`sql\`query\``) which automatically prevents SQL injection
2. **Input Validation**: Zod schemas validate all inputs before database operations
3. **Authentication**: JWT tokens with proper verification
4. **Authorization**: User isolation - users can only access their own data

## 🔒 Additional Security Steps to Consider

### 1. Database Level Security
```sql
-- Create dedicated database user with limited permissions
CREATE USER app_user WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE workspace_app TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO app_user;
```

### 2. Environment & Configuration
- Use strong `JWT_SECRET` (minimum 32 characters)
- Set proper CORS origins (not `*` in production)
- Use environment variables for all secrets
- Enable SSL/TLS for database connections in production

### 3. Rate Limiting
```typescript
// Add to your Hono app
import { rateLimiter } from 'hono/rate-limiter';

app.use('*', rateLimiter({
  windowMs: 15 * 60 * 1000, // 15 minutes
  limit: 100, // requests per window
  message: 'Too many requests'
}));
```

### 4. Input Sanitization
```typescript
// Add HTML sanitization for content fields
import DOMPurify from 'isomorphic-dompurify';

// Sanitize before saving to database
const sanitizedContent = DOMPurify.sanitize(userContent);
```

### 5. Security Headers
```typescript
// Add security headers
app.use('*', async (c, next) => {
  await next();
  c.header('X-Content-Type-Options', 'nosniff');
  c.header('X-Frame-Options', 'DENY');
  c.header('X-XSS-Protection', '1; mode=block');
});
```

### 6. File Upload Security
```typescript
// Add file validation (already partially implemented)
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const ALLOWED_MIME_TYPES = ['application/pdf', 'text/plain', ...];

// Validate file size and type
if (file.size > MAX_FILE_SIZE) {
  return c.json({ error: 'File too large' }, 400);
}
```

### 7. Database Connection Security
```typescript
// Use connection pooling and SSL
const sql = postgres({
  ssl: process.env.NODE_ENV === 'production' ? 'require' : false,
  max: 20, // connection pool size
  idle_timeout: 20,
  connect_timeout: 10,
});
```

### 8. Logging & Monitoring
```typescript
// Log security events
const securityLogger = {
  logFailedLogin: (email: string, ip: string) => {
    console.log(`Failed login attempt: ${email} from ${ip}`);
  },
  logUnauthorizedAccess: (userId: string, resource: string) => {
    console.log(`Unauthorized access: User ${userId} to ${resource}`);
  }
};
```

## 📊 Security Checklist

- ✅ Parameterized queries (SQL injection protection)
- ✅ Input validation with Zod
- ✅ JWT authentication
- ✅ User authorization checks
- ⚠️ Add rate limiting
- ⚠️ Add security headers
- ⚠️ Use dedicated DB user with limited permissions
- ⚠️ Add request logging
- ⚠️ File size/type validation
- ⚠️ HTTPS in production

The direct SQL approach with `postgres` library is actually very secure when used correctly (as in your code). The template literal syntax prevents SQL injection, and combined with proper validation, it's often more secure than some ORM configurations.

**Bottom line**: Your current approach is secure. Just add the additional layers above for production hardening.
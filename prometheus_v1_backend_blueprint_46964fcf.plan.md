---
name: Prometheus v1 Backend Blueprint and Setup Plan
overview: Create a complete production-grade backend blueprint and setup plan for Prometheus v1, including architecture, folder structure, database models, API specifications, security requirements, and execution milestones.
todos:
  - id: setup-project-structure
    content: "Create complete folder structure at repository root: app/ (with core/, db/, models/, schemas/, api/, services/, agents/, jobs/, utils/), tests/ (with test_api/, test_services/, test_agents/, test_jobs/), alembic/ directory, and root files (requirements.txt, .gitignore, .env.example, README.md). Note: repository root IS the backend directory"
    status: pending
  - id: setup-dependencies
    content: Create requirements.txt at repository root (requirements.txt) with all pinned versions from version matrix (FastAPI 0.115.0, SQLAlchemy 2.0.36, Alembic 1.13.2, OpenAI 1.51.0, LangChain 0.3.0, LangGraph 0.2.0, etc.). Create .gitignore at repository root (.gitignore) with Python, IDE, environment, database, logs, testing, and build patterns
    status: pending
  - id: create-env-template
    content: "Create .env.example at repository root (.env.example) with all required environment variables: Supabase (URL, ANON_KEY, SERVICE_ROLE_KEY), DATABASE_URL, REDIS_URL, OPENAI_API_KEY, ENCRYPTION_KEY, Slack OAuth (CLIENT_ID, CLIENT_SECRET, REDIRECT_URI), Telegram via Telethon (API_ID, API_HASH), Outlook OAuth (CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, TENANT_ID), and application settings (ENVIRONMENT, LOG_LEVEL, API_HOST, API_PORT)"
    status: pending
  - id: implement-core-modules
    content: "Implement app/core/ modules: config.py (Pydantic Settings for all environment variables), logging.py (structured JSON logging configuration), security.py (Supabase JWT validation, token extraction, user authentication), crypto.py (AES-256-GCM encryption/decryption for OAuth tokens with key management)"
    status: pending
    dependencies:
      - setup-project-structure
  - id: implement-db-layer
    content: "Implement app/db/ modules: engine.py (SQLAlchemy async engine creation with connection pooling), session.py (async session management and dependency injection), base.py (DeclarativeBase for models), rls.py (helper functions for RLS policy enforcement and user context)"
    status: pending
    dependencies:
      - setup-project-structure
  - id: create-database-models
    content: "Create all SQLAlchemy 2.0 style models in app/models/: user.py (User model with timezone), linked_account.py (LinkedAccount model with provider/provider_account_id), oauth_token.py (OAuthToken model with token_type bearer|bot), thread.py (Thread model for conversation threads), event.py (Event model with source, thread_id, text_for_embedding), entity.py (Entity model for person/org/project/topic), note.py (Note model), task.py (Task model with status/priority), calendar_event.py (CalendarEvent model with start_at/end_at), summary.py (Summary model with window_start/window_end), proposal.py (Proposal model), draft.py (Draft model), embedding.py (Embedding model with object_type/object_id/chunk_index). All models must include proper relationships, indexes, constraints, and RLS-ready user_id foreign keys"
    status: pending
    dependencies:
      - implement-db-layer
  - id: create-alembic-migration
    content: "Create initial Alembic migration (001_initial_schema) with all tables: users, linked_accounts, oauth_tokens, threads, events, entities, notes, tasks, calendar_events, summaries, proposals, drafts, embeddings (with pgvector Vector(1536) and HNSW/IVFFlat index). Include all foreign keys, unique constraints, indexes (including composite indexes), and pgvector extension. Ensure downgrade() is fully reversible"
    status: pending
    dependencies:
      - create-database-models
  - id: implement-connectors
    content: "Implement connector services: app/services/connector/base.py (BaseConnector abstract interface), slack.py (Slack OAuth flow with initiate/callback endpoints, event polling via Slack Web API, thread creation), telegram.py (Telethon library for Telegram Client API - phone auth with OTP, message ingestion from user's personal chats using MTProto, (use of Bot API is prohibited)), outlook.py (Microsoft Graph OAuth flow, calendar/mail event ingestion). All connectors must encrypt tokens before storage using crypto service. Store tokens with token_type (bearer|bot) and handle thread creation for conversations"
    status: pending
    dependencies:
      - create-database-models
      - implement-core-modules
  - id: implement-vector-service
    content: "Implement app/services/vector.py as the Prometheus v1 vector abstraction layer, using pgvector inside Supabase Postgres as the primary vector store. This layer must support semantic similarity search scoped by user_id, time windows, and source filters to power free-text user prompts (examples include but are not limited to: 'summarize last 2 hours' and 'what needs action?') across Slack, Telegram, and Outlook events. It must handle embedding storage and retrieval for multiple object types (event, thread, note, draft, entity), support multi-chunk embeddings via chunk_index, and ensure vector records remain consistent with the 30-day event retention policy. The interface must be defined behind a stable VectorStore abstraction so the underlying implementation can be swapped in the future to an external vector database (Qdrant, Pinecone, or Weaviate) without requiring changes to application or agent code"
    status: pending
    dependencies:
      - create-database-models
  - id: implement-embedding-service
    content: "Implement app/services/embedding.py: OpenAI embedding generation service using text-embedding-ada-002 model, batch processing support, error handling and retries. Store embeddings via VectorStore abstraction layer (not direct database access) to ensure future compatibility with external vector databases"
    status: pending
    dependencies:
      - implement-vector-service
  - id: implement-agents
    content: "Implement LangGraph agents: app/agents/base.py (shared utilities, LLM client setup with JSON mode), prompt_router.py (LangGraph workflow that classifies free-text user prompts and routes to appropriate specialized agents), summarize_graph.py (specialized LangGraph workflow for summarization queries - example: 'summarize last 2 hours' - uses VectorStore abstraction to query events with user_id, time window, and source filters across Slack/Telegram/Outlook, generates structured JSON summary stored in summaries table with content_json and source_refs, validated by Pydantic), task_graph.py (specialized LangGraph workflow for task/action queries - example: 'what needs action?' - uses VectorStore abstraction to query actionable events with semantic similarity search, identifies actionable items, creates tasks with status/priority, returns structured JSON). All LLM outputs must be validated by Pydantic models. Agents must use VectorStore interface, not direct database access. The prompt router must handle arbitrary user queries and determine appropriate handling strategy"
    status: pending
    dependencies:
      - implement-vector-service
      - implement-embedding-service
  - id: implement-api-endpoints
    content: "Implement all API endpoints in app/api/v1/: connectors.py (Slack/Outlook OAuth initiate/callback, Telethon-based Telegram phone auth with OTP verification, connector management), prompts.py (POST /prompts - main endpoint accepting free-text user queries, routes to prompt router agent which determines intent and invokes appropriate specialized agent, returns structured JSON response. Examples: 'summarize last 2 hours', 'what needs action?', but supports any user query), tasks.py (GET /tasks with filtering by status/priority - for querying existing tasks), calendar.py (CRUD endpoints: GET/POST/PUT/DELETE /calendar/events with start_at/end_at). All endpoints require Supabase JWT authentication via deps.py"
    status: pending
    dependencies:
      - implement-agents
      - implement-connectors
  - id: implement-background-jobs
    content: Implement background jobs under app/jobs/ using Redis Queue (RQ) with Redis (Upstash-compatible) as the queue backend. Provide a dedicated worker.py to bootstrap and run RQ workers. Implement ingestion.py as a scheduled polling job that runs every 5 minutes to ingest new events from Slack, Telegram, and Outlook using official APIs only, normalizes them into unified event records, and stores them with an expires_at value set to 30 days from ingestion. Implement embedding.py as a chained background job triggered after ingestion that generates embeddings for newly ingested or updated objects (event, thread, note, draft, entity) in batches, supports multi-chunk embeddings via chunk_index, and skips re-embedding using content hashes. Implement summarization.py to generate summaries and action proposals on demand (and optionally via schedule) using strict JSON outputs validated by Pydantic models. Implement retention.py as a daily cleanup job running at 2 AM UTC that deletes expired events and reliably cleans up associated embeddings, summaries, and proposals in bounded batches to avoid long-running locks. All jobs must include retry policies, idempotency safeguards, structured error logging, and failure handling appropriate for production workloads
    status: pending
    dependencies:
      - implement-vector-service
      - implement-connectors
      - implement-embedding-service
  - id: setup-rls-policies
    content: Create and test Supabase RLS policies for all user-owned tables (users, linked_accounts, oauth_tokens, events, embeddings, summaries, actions, calendar_events). Policies must use auth.uid() for user isolation. Test with multiple users to ensure data isolation. Document all policies in migration or separate SQL file
    status: pending
    dependencies:
      - create-alembic-migration
  - id: create-main-app
    content: "Create app/main.py with FastAPI application setup: include all v1 routers, CORS configuration, health check endpoint (/health), OpenAPI documentation setup, exception handlers, middleware for logging and error handling"
    status: pending
    dependencies:
      - implement-api-endpoints
  - id: create-setup-documentation
    content: "Create docs/SETUP.md at repository root with complete blueprint: architecture diagrams, folder structure, database models, API specifications with request/response examples, setup procedure (virtual env, dependencies, Alembic init/upgrade, pgvector setup, RLS policies), version matrix, security checklist, production readiness checklist, Week 1-4 execution milestones, and all file contents (requirements.txt, .gitignore, .env.example, example migration)"
    status: pending
    dependencies:
      - setup-dependencies
      - create-env-template
---

# Prometheus v1 Backend Blueprint and Setup Plan

## 1. Architecture Overview

### 1.1 System Architecture Diagram

```mermaid
graph TB
    subgraph ClientLayer["Client Layer"]
        APIClient["API Client<br/>Frontend/Mobile"]
    end
    
    subgraph APILayer["FastAPI Application Layer"]
        APIRouter["API Routers<br/>/api/v1/*"]
        AuthMiddleware["Auth Middleware<br/>Supabase JWT"]
        Deps["Dependencies<br/>DB Session User"]
    end
    
    subgraph ServiceLayer["Service Layer"]
        ConnectorService["Connector Service<br/>Slack Telegram Outlook"]
        EmbeddingService["Embedding Service<br/>OpenAI"]
        PromptService["Prompt Service<br/>Query Processing"]
        CalendarService["Calendar Service<br/>CRUD"]
        VectorService["Vector Service<br/>pgvector"]
    end
    
    subgraph AgentLayer["Agent Layer LangGraph"]
        PromptRouter["Prompt Router<br/>Query Classifier"]
        SummarizeAgent["Summarize Agent<br/>Example Handler"]
        TaskAgent["Task Agent<br/>Example Handler"]
    end
    
    subgraph DataLayer["Data Layer"]
        Postgres["Supabase Postgres<br/>RLS + pgvector"]
        Redis["Redis<br/>Cache + Jobs"]
    end
    
    subgraph JobLayer["Background Jobs"]
        EventIngestion["Event Ingestion Job"]
        EmbeddingJob["Embedding Generation Job"]
        SummarizationJob["Summarization Job"]
        RetentionJob["Retention Cleanup Job"]
    end
    
    subgraph ExternalAPIs["External APIs"]
        SlackAPI["Slack API"]
        TelegramAPI["Telegram API<br/>via Telethon"]
        OutlookAPI["Microsoft Graph API"]
        OpenAIAPI["OpenAI API"]
    end
    
    APIClient -->|HTTPS + JWT| AuthMiddleware
    AuthMiddleware --> APIRouter
    APIRouter --> Deps
    APIRouter --> ServiceLayer
    
    ServiceLayer --> ConnectorService
    ServiceLayer --> EmbeddingService
    ServiceLayer --> PromptService
    ServiceLayer --> CalendarService
    ServiceLayer --> VectorService
    
    PromptService --> PromptRouter
    PromptRouter --> SummarizeAgent
    PromptRouter --> TaskAgent
    
    ServiceLayer --> Postgres
    ServiceLayer --> Redis
    AgentLayer --> Postgres
    AgentLayer --> OpenAIAPI
    
    ConnectorService --> SlackAPI
    ConnectorService --> TelegramAPI
    ConnectorService --> OutlookAPI
    EmbeddingService --> OpenAIAPI
    
    JobLayer --> Postgres
    JobLayer --> Redis
    JobLayer --> ConnectorService
    JobLayer --> EmbeddingService
    JobLayer --> PromptService
    
    EventIngestion -.->|Triggers| EmbeddingJob
    EmbeddingJob -.->|Triggers| SummarizationJob
```

### 1.2 Data Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Connector
    participant DB
    participant Redis
    participant JobQueue
    participant Embedding
    participant Agent
    participant VectorDB
    
    User->>API: OAuth Flow (Slack/Telegram/Outlook)
    API->>Connector: Exchange Code for Token
    Connector->>DB: Store Encrypted Token
    API->>User: OAuth Success
    
    Note over Connector,JobQueue: Background Ingestion
    Connector->>DB: Store Raw Event
    Connector->>JobQueue: Queue Embedding Job
    JobQueue->>Embedding: Generate Embedding
    Embedding->>VectorDB: Store Vector (pgvector)
    Embedding->>DB: Link Embedding to Event
    
    User->>API: POST /prompts (free-text: "summarize last 2 hours")
    API->>PromptRouter: Route User Query
    PromptRouter->>OpenAI: Classify Intent
    PromptRouter->>SummarizeAgent: Invoke Summarize Handler
    SummarizeAgent->>VectorDB: Query Events (semantic + time filter)
    SummarizeAgent->>DB: Fetch Event Details
    SummarizeAgent->>OpenAI: Generate Summary (JSON)
    SummarizeAgent->>DB: Store Summary
    SummarizeAgent->>API: Return Structured JSON
    API->>User: Summary Response
    
    User->>API: POST /prompts (free-text: "what needs action?")
    API->>PromptRouter: Route User Query
    PromptRouter->>OpenAI: Classify Intent
    PromptRouter->>TaskAgent: Invoke Task Handler
    TaskAgent->>VectorDB: Query Actionable Events (semantic search)
    TaskAgent->>DB: Fetch Context
    TaskAgent->>OpenAI: Identify Tasks (JSON)
    TaskAgent->>DB: Store Tasks
    TaskAgent->>API: Return Tasks List
    API->>User: Tasks Response
```

## 2. Key Architectural Decisions

### 2.1 Vector Database Strategy

**Decision**: Use pgvector within Supabase Postgres as primary vector store, with stable VectorStore abstraction layer for future external DB swap.

**Justification**:

- Reduces infrastructure complexity (single database)

- Leverages Supabase's managed Postgres with built-in pgvector support

- Stable VectorStore abstraction (`app/services/vector.py`) allows swapping to Qdrant/Pinecone/Weaviate without requiring changes to application or agent code

- Embeddings stored in dedicated `embeddings` table, not inline, for easier migration

- Supports semantic similarity search scoped by user_id, time windows, and source filters to power free-text user prompts (examples: "summarize last 2 hours", "what needs action?") across Slack, Telegram, and Outlook events

- Handles multiple object types (event, thread, note, draft, entity) with multi-chunk support via chunk_index

- Ensures vector records remain consistent with 30-day event retention policy

### 2.2 LLM Output Validation

**Decision**: All LLM responses must be strict JSON validated by Pydantic models before processing.

**Justification**:

- Prevents injection attacks and malformed data

- Ensures type safety and predictable API responses

- Enables early error detection and retry logic

- Required for production-grade reliability

### 2.3 Token Encryption

**Decision**: Encrypt OAuth tokens and bot tokens at rest using AES-256-GCM before storing in database.

**Justification**:

- Even with RLS, defense-in-depth requires encryption

- Tokens are sensitive credentials that must be protected

- AES-256-GCM provides authenticated encryption

- Encryption keys stored in environment variables, not in code

### 2.4 Event Retention Policy

**Decision**: 30-day default retention via `expires_at` column, with user-initiated deletion supported.

**Justification**:

- Balances data utility with privacy compliance

- Automatic cleanup reduces storage costs

- User control ensures GDPR/privacy compliance

- Background job handles cleanup efficiently

### 2.5 Agent Architecture

**Decision**: Use LangGraph for agent orchestration with a prompt router/classifier that handles free-text user queries and routes to specialized agent graphs (summarize, task detection, etc.) based on intent.

**Justification**:

- LangGraph provides stateful, composable agent workflows

- Prompt router enables handling arbitrary user queries, not just hard-coded prompts

- Specialized agent graphs (summarize_graph, task_graph) handle specific intents but are invoked dynamically

- Examples like "summarize last 2 hours" and "what needs action?" demonstrate the system capabilities but are not the only supported prompts

- Enables future expansion (e.g., multi-step reasoning, new prompt types)

- Better error handling and observability

- VectorStore abstraction allows semantic search to power any time-windowed or source-filtered query

### 2.6 Background Job Processing

**Decision**: Use Redis Queue (RQ) with Redis (Upstash-compatible) as the queue backend for async processing.

**Justification**:

- Decouples API from heavy processing (embeddings, summarization)

- Improves API response times

- RQ provides built-in retry logic, job monitoring, and failure handling

- Redis (including Upstash) provides both cache and queue functionality

- All jobs include retry policies, idempotency safeguards, and structured error logging for production workloads

- Dedicated worker.py bootstraps RQ workers for reliable job execution

## 3. Backend Folder Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Settings (Pydantic Settings)
│   │   ├── logging.py          # Logging configuration
│   │   ├── security.py         # JWT validation, password hashing
│   │   └── crypto.py           # Token encryption/decryption
│   ├── db/
│   │   ├── __init__.py
│   │   ├── engine.py           # SQLAlchemy engine creation
│   │   ├── session.py          # Session management
│   │   ├── base.py             # Declarative base
│   │   └── rls.py              # RLS helper functions
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # User model
│   │   ├── linked_account.py   # Linked accounts
│   │   ├── oauth_token.py      # OAuth tokens
│   │   ├── thread.py           # Conversation threads
│   │   ├── event.py            # Events from connectors
│   │   ├── entity.py           # Entities (person/org/project/topic)
│   │   ├── note.py             # Notes
│   │   ├── task.py             # Tasks (what needs action)
│   │   ├── calendar_event.py   # Calendar events
│   │   ├── summary.py          # Summaries
│   │   ├── proposal.py         # Proposals
│   │   ├── draft.py            # Drafts
│   │   └── embedding.py        # Embeddings table
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py             # User Pydantic schemas
│   │   ├── connector.py        # Connector schemas
│   │   ├── thread.py           # Thread schemas
│   │   ├── event.py            # Event schemas
│   │   ├── entity.py           # Entity schemas
│   │   ├── note.py             # Note schemas
│   │   ├── task.py             # Task schemas
│   │   ├── summary.py          # Summary schemas (request/response)
│   │   ├── proposal.py         # Proposal schemas
│   │   ├── draft.py            # Draft schemas
│   │   └── calendar.py         # Calendar schemas
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py             # FastAPI dependencies (auth, DB session)
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py       # Main v1 router
│   │   │   ├── auth.py         # Auth endpoints
│   │   │   ├── connectors.py  # OAuth flows, connector management
│   │   │   ├── prompts.py     # Free-text prompt endpoint
│   │   │   ├── tasks.py        # Tasks query endpoint
│   │   │   └── calendar.py    # Calendar CRUD
│   ├── services/
│   │   ├── __init__.py
│   │   ├── connector/
│   │   │   ├── __init__.py
│   │   │   ├── base.py         # Base connector interface
│   │   │   ├── slack.py        # Slack connector
│   │   │   ├── telegram.py    # Telegram connector
│   │   │   └── outlook.py     # Outlook connector
│   │   ├── embedding.py        # OpenAI embedding generation
│   │   ├── vector.py           # VectorStore abstraction (pgvector implementation)
│   │   ├── prompt_service.py  # Prompt processing orchestration
│   │   └── calendar.py         # Calendar business logic
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py             # Base agent utilities
│   │   ├── prompt_router.py   # LangGraph prompt router/classifier
│   │   ├── summarize_graph.py  # LangGraph for summarization (example: "summarize last 2 hours")
│   │   └── task_graph.py        # LangGraph for task detection (example: "what needs action?")
│   ├── jobs/
│   │   ├── __init__.py
│   │   ├── worker.py           # RQ worker bootstrap and runner
│   │   ├── ingestion.py        # Scheduled polling job (5 min) - event ingestion
│   │   ├── embedding.py        # Chained job - embedding generation with content hash checking
│   │   ├── summarization.py    # On-demand/scheduled - summaries and proposals (Pydantic validated)
│   │   └── retention.py        # Daily cleanup (2 AM UTC) - bounded batch deletion
│   └── utils/
│       ├── __init__.py
│       └── datetime.py         # Timezone utilities
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures (DB, Redis, API mocks)
│   ├── test_api/
│   │   ├── test_connectors.py  # OAuth flows, connector management
│   │   ├── test_prompts.py     # Free-text prompt endpoint
│   │   ├── test_tasks.py       # Tasks query endpoint
│   │   └── test_calendar.py   # Calendar CRUD
│   ├── test_services/
│   │   ├── test_connector/     # Slack, Telegram, Outlook connectors
│   │   ├── test_vector.py      # VectorStore abstraction
│   │   ├── test_embedding.py   # Embedding generation
│   │   ├── test_crypto.py      # Token encryption
│   │   └── test_prompt_service.py
│   ├── test_agents/
│   │   ├── test_prompt_router.py
│   │   ├── test_summarize_graph.py
│   │   └── test_task_graph.py
│   ├── test_jobs/
│   │   ├── test_ingestion.py
│   │   ├── test_embedding.py
│   │   ├── test_summarization.py
│   │   └── test_retention.py
│   ├── test_models/            # Database model tests
│   ├── test_db/                # RLS policy tests
│   └── test_integration/       # End-to-end workflow tests
├── alembic/
│   ├── versions/               # Migration files
│   ├── env.py                  # Alembic environment
│   └── script.py.mako          # Migration template
├── alembic.ini                  # Alembic configuration
├── requirements.txt
├── .gitignore
├── .env.example
└── README.md
```

## 4. Database Models and Schema

### 4.1 Core Models

**users** (Supabase Auth integration)

- `id` (UUID, PK) - Supabase Auth user ID
- `email` (Text, nullable)
- `display_name` (Text, nullable)
- `timezone` (Text, NOT NULL, default 'UTC')
- `created_at` (Timestamptz, NOT NULL)
- `updated_at` (Timestamptz, NOT NULL)

**linked_accounts**

- `id` (UUID, PK)
- `user_id` (UUID, NOT NULL, FK → users.id, RLS, indexed)
- `provider` (Text, NOT NULL) - slack | telegram | outlook
- `provider_account_id` (Text, NOT NULL)
- `scopes` (Text, nullable)
- `status` (Text, NOT NULL, default 'active') - active | revoked | error
- `metadata` (JSONB, NOT NULL, default '{}')
- `created_at` (Timestamptz, NOT NULL)
- `updated_at` (Timestamptz, NOT NULL)
- **Constraints**: Unique (user_id, provider, provider_account_id)
- **Indexes**: (user_id, provider)

**oauth_tokens**

- `id` (UUID, PK)
- `user_id` (UUID, NOT NULL, FK → users.id, RLS, indexed)
- `linked_account_id` (UUID, NOT NULL, FK → linked_accounts.id, indexed)
- `token_type` (Text, NOT NULL) - bearer | bot
- `scopes` (Text, nullable)
- `access_token_enc` (Text, NOT NULL) - AES-256-GCM encrypted
- `refresh_token_enc` (Text, nullable) - AES-256-GCM encrypted
- `expires_at` (Timestamptz, nullable)
- `last_refreshed_at` (Timestamptz, nullable)
- `revoked_at` (Timestamptz, nullable)
- `token_fingerprint` (Text, nullable)
- `created_at` (Timestamptz, NOT NULL)
- `updated_at` (Timestamptz, NOT NULL)
- **Indexes**: (user_id, linked_account_id)

**threads**

- `id` (UUID, PK)
- `user_id` (UUID, NOT NULL, FK → users.id, RLS, indexed)
- `source` (Text, NOT NULL) - slack | telegram | outlook
- `external_id` (Text, NOT NULL)
- `subject` (Text, nullable)
- `participants` (JSONB, NOT NULL, default '[]')
- `content_preview` (Text, nullable)
- `content_hash` (Text, NOT NULL, default '')
- `last_event_at` (Timestamptz, nullable)
- `created_at` (Timestamptz, NOT NULL)
- `updated_at` (Timestamptz, NOT NULL)
- **Constraints**: Unique (user_id, source, external_id)
- **Indexes**: (user_id, source, last_event_at)

**events**

- `id` (UUID, PK)
- `user_id` (UUID, NOT NULL, FK → users.id, RLS, indexed)
- `source` (Text, NOT NULL) - slack | telegram | outlook | calendar
- `source_account_id` (UUID, nullable, FK → linked_accounts.id)
- `external_id` (Text, NOT NULL)
- `thread_id` (UUID, nullable, FK → threads.id)
- `event_type` (Text, NOT NULL) - message | reaction | mention | file | email | calendar_created etc.
- `title` (Text, nullable)
- `body` (Text, nullable)
- `url` (Text, nullable)
- `text_for_embedding` (Text, nullable)
- `content_hash` (Text, NOT NULL, default '')
- `importance_score` (Smallint, NOT NULL, default 0)
- `occurred_at` (Timestamptz, NOT NULL)
- `expires_at` (Timestamptz, NOT NULL)
- `deleted_at` (Timestamptz, nullable)
- `raw` (JSONB, NOT NULL, default '{}')
- `created_at` (Timestamptz, NOT NULL)
- `updated_at` (Timestamptz, NOT NULL)
- **Constraints**: Unique (user_id, source, external_id)
- **Indexes**: (user_id, source, occurred_at), (user_id, expires_at), optional (user_id, deleted_at)

**entities**

- `id` (UUID, PK)
- `user_id` (UUID, NOT NULL, FK → users.id, RLS, indexed)
- `kind` (Text, NOT NULL) - person | org | project | topic
- `name` (Text, NOT NULL)
- `aliases` (JSONB, NOT NULL, default '[]')
- `metadata` (JSONB, NOT NULL, default '{}')
- `created_at` (Timestamptz, NOT NULL)
- `updated_at` (Timestamptz, NOT NULL)
- **Indexes**: (user_id, kind, name)

**notes**

- `id` (UUID, PK)
- `user_id` (UUID, NOT NULL, FK → users.id, RLS, indexed)
- `title` (Text, nullable)
- `body` (Text, NOT NULL)
- `content_hash` (Text, NOT NULL, default '')
- `deleted_at` (Timestamptz, nullable)
- `created_at` (Timestamptz, NOT NULL)
- `updated_at` (Timestamptz, NOT NULL)
- **Indexes**: (user_id, updated_at)

**tasks**

- `id` (UUID, PK)
- `user_id` (UUID, NOT NULL, FK → users.id, RLS, indexed)
- `status` (Text, NOT NULL) - open | done | snoozed
- `priority` (Text, NOT NULL, default 'medium') - low | medium | high
- `title` (Text, NOT NULL)
- `details` (Text, nullable)
- `due_at` (Timestamptz, nullable)
- `source_event_id` (UUID, nullable, FK → events.id)
- `source_refs` (JSONB, NOT NULL, default '[]')
- `created_at` (Timestamptz, NOT NULL)
- `updated_at` (Timestamptz, NOT NULL)
- **Indexes**: (user_id, status, due_at)

**calendar_events** (in-app calendar)

- `id` (UUID, PK)
- `user_id` (UUID, NOT NULL, FK → users.id, RLS, indexed)
- `title` (Text, NOT NULL)
- `description` (Text, nullable)
- `start_at` (Timestamptz, NOT NULL)
- `end_at` (Timestamptz, NOT NULL)
- `location` (Text, nullable)
- `created_at` (Timestamptz, NOT NULL)
- `updated_at` (Timestamptz, NOT NULL)
- **Indexes**: (user_id, start_at)

**summaries**

- `id` (UUID, PK)
- `user_id` (UUID, NOT NULL, FK → users.id, RLS, indexed)
- `window_start` (Timestamptz, NOT NULL)
- `window_end` (Timestamptz, NOT NULL)
- `content_json` (JSONB, NOT NULL)
- `source_refs` (JSONB, NOT NULL, default '[]')
- `created_at` (Timestamptz, NOT NULL)
- `updated_at` (Timestamptz, NOT NULL)
- **Indexes**: (user_id, window_start, window_end)

**proposals**

- `id` (UUID, PK)
- `user_id` (UUID, NOT NULL, FK → users.id, RLS, indexed)
- `window_start` (Timestamptz, NOT NULL)
- `window_end` (Timestamptz, NOT NULL)
- `content_json` (JSONB, NOT NULL)
- `source_refs` (JSONB, NOT NULL, default '[]')
- `created_at` (Timestamptz, NOT NULL)
- `updated_at` (Timestamptz, NOT NULL)
- **Indexes**: (user_id, window_start, window_end)

**drafts**

- `id` (UUID, PK)
- `user_id` (UUID, NOT NULL, FK → users.id, RLS, indexed)
- `kind` (Text, NOT NULL) - slack_reply | telegram_reply | outlook_reply | note
- `content_json` (JSONB, NOT NULL)
- `content_hash` (Text, NOT NULL, default '')
- `source_refs` (JSONB, NOT NULL, default '[]')
- `created_at` (Timestamptz, NOT NULL)
- `updated_at` (Timestamptz, NOT NULL)
- **Indexes**: (user_id, kind, created_at)

**embeddings** (pgvector in Supabase)

- `id` (UUID, PK)
- `user_id` (UUID, NOT NULL, FK → users.id, RLS, indexed)
- `object_type` (Text, NOT NULL) - event | note | thread | draft | entity
- `object_id` (UUID, NOT NULL)
- `chunk_index` (Int, NOT NULL, default 0)
- `embedding_model` (Text, NOT NULL)
- `embedding_dim` (Int, NOT NULL)
- `distance_metric` (Text, NOT NULL, default 'cosine')
- `embedding` (Vector(1536), NOT NULL)
- `content_hash` (Text, NOT NULL)
- `metadata` (JSONB, NOT NULL, default '{}')
- `created_at` (Timestamptz, NOT NULL)
- `updated_at` (Timestamptz, NOT NULL)
- **Constraints**: Unique (user_id, object_type, object_id, chunk_index, embedding_model)
- **Indexes**: (user_id, object_type), (user_id, content_hash)
- **Vector Index**: HNSW or IVFFlat on embedding using cosine ops

### 4.2 RLS Policies (Supabase)

All user-owned tables require RLS policies:

- `users`: Users can only read/update their own record
- `linked_accounts`: Users can only access their own accounts
- `oauth_tokens`: Users can only access tokens for their accounts
- `threads`: Users can only access their own threads
- `events`: Users can only access their own events
- `entities`: Users can only access their own entities
- `notes`: Users can only access their own notes
- `tasks`: Users can only access their own tasks
- `calendar_events`: Users can only access their own calendar events
- `summaries`: Users can only access their own summaries
- `proposals`: Users can only access their own proposals
- `drafts`: Users can only access their own drafts
- `embeddings`: Users can only access their own embeddings

## 5. API Specification

### 5.1 Authentication

All endpoints (except OAuth callbacks) require `Authorization: Bearer <supabase_jwt_token>` header.

### 5.2 Connector OAuth Flows

#### 5.2.1 Slack OAuth

**Initiate OAuth:**

```javascript
GET /api/v1/connectors/slack/oauth/initiate
Response:
{
  "auth_url": "https://slack.com/oauth/v2/authorize?...",
  "state": "random_state_string"
}
```

**OAuth Callback:**

```javascript
GET /api/v1/connectors/slack/oauth/callback?code=...&state=...
Response:
{
  "linked_account_id": "uuid",
  "provider": "slack",
  "provider_account_id": "workspace_id",
  "status": "active"
}
```

#### 5.2.2 Telegram Setup (via Telethon)

**Note**: Telethon library is used to access user's personal messages via Telegram Client API (MTProto), not Bot API. This requires user authentication via phone number and OTP.

**Initiate Telegram Auth:**

```javascript
POST /api/v1/connectors/telegram/auth/initiate
Body:
{
  "phone_number": "+1234567890"
}
Response:
{
  "auth_session_id": "uuid",
  "phone_code_hash": "hash_string"
}
```

**Verify Telegram Code:**

```javascript
POST /api/v1/connectors/telegram/auth/verify
Body:
{
  "auth_session_id": "uuid",
  "phone_code": "12345",
  "phone_code_hash": "hash_string"
}
Response:
{
  "linked_account_id": "uuid",
  "provider": "telegram",
  "provider_account_id": "user_telegram_id",
  "status": "active"
}
```

**Note**: Telethon requires API credentials (api_id and api_hash) obtained from https://my.telegram.org/apps. The session file should be encrypted and stored securely.

#### 5.2.3 Outlook OAuth

**Initiate OAuth:**

```javascript
GET /api/v1/connectors/outlook/oauth/initiate
Response:
{
  "auth_url": "https://login.microsoftonline.com/...",
  "state": "random_state_string"
}
```

**OAuth Callback:**

```javascript
GET /api/v1/connectors/outlook/oauth/callback?code=...&state=...
Response:
{
  "linked_account_id": "uuid",
  "provider": "outlook",
  "provider_account_id": "user_id_or_email",
  "status": "active"
}
```

### 5.3 Free-Text Prompt Endpoint

**Note**: This is the primary endpoint for user queries. The system accepts arbitrary free-text prompts from users and processes them through a prompt router that classifies intent and routes to appropriate specialized agents. Examples like "summarize last 2 hours" and "what needs action?" demonstrate the system capabilities but any free-text query is supported. The prompt router uses LLM-based intent classification to determine the appropriate handler, and specialized agents use VectorStore semantic search to retrieve relevant events based on the query context.

```javascript
POST /api/v1/prompts
Headers:
  Authorization: Bearer <token>
Body:
{
  "prompt": "summarize last 2 hours",
  "context": {
    "sources": ["slack", "telegram", "outlook"],  // optional filter
    "time_window": null  // optional, inferred from prompt if not provided
  }
}
Response:
{
  "prompt_id": "uuid",
  "intent": "summarize",
  "response": {
    "summary_id": "uuid",
    "time_range": {
      "start": "2025-01-15T10:00:00Z",
      "end": "2025-01-15T12:00:00Z"
    },
    "content": {
      "overview": "Summary of the last 2 hours...",
      "key_events": [
        {
          "event_id": "uuid",
          "source": "slack",
          "title": "Message in #general",
          "timestamp": "2025-01-15T11:30:00Z"
        }
      ],
      "themes": ["project_discussion", "meeting_followup"],
      "statistics": {
        "total_events": 15,
        "by_source": {
          "slack": 10,
          "telegram": 3,
          "outlook": 2
        }
      }
    },
    "created_at": "2025-01-15T12:00:00Z"
  }
}
```

**Example: Task/Action Query**

```javascript
POST /api/v1/prompts
Body:
{
  "prompt": "what needs action?",
  "context": {
    "sources": ["slack"],  // optional filter
    "priority": "high"  // optional filter
  }
}
Response:
{
  "prompt_id": "uuid",
  "intent": "task_detection",
  "response": {
    "tasks": [
      {
        "id": "uuid",
        "status": "open",
        "priority": "high",
        "title": "Reply to message in #general",
        "details": "User asked about project timeline",
        "due_at": null,
        "source_event_id": "uuid",
        "source_refs": [
          {
            "type": "event",
            "id": "uuid",
            "source": "slack"
          }
        ],
        "created_at": "2025-01-15T11:46:00Z",
        "updated_at": "2025-01-15T11:46:00Z"
      }
    ],
    "total": 5,
    "by_priority": {
      "high": 2,
      "medium": 2,
      "low": 1
    }
  }
}
```

### 5.4 Query Existing Tasks

```javascript
GET /api/v1/tasks?status=open&priority=high
Headers:
  Authorization: Bearer <token>
Query Parameters:
  - status: open|done|snoozed (optional, default: open)
  - priority: low|medium|high (optional)
Response:
{
  "tasks": [
    {
      "id": "uuid",
      "status": "open",
      "priority": "high",
      "title": "Reply to message in #general",
      "details": "User asked about project timeline",
      "due_at": null,
      "source_event_id": "uuid",
      "source_refs": [
        {
          "type": "event",
          "id": "uuid",
          "source": "slack"
        }
      ],
      "created_at": "2025-01-15T11:46:00Z",
      "updated_at": "2025-01-15T11:46:00Z"
    }
  ],
  "total": 5,
  "by_priority": {
    "high": 2,
    "medium": 2,
    "low": 1
  }
}
```

### 5.5 Calendar CRUD

**List Calendar Events:**

```javascript
GET /api/v1/calendar/events?start_at=2025-01-15T00:00:00Z&end_at=2025-01-20T23:59:59Z
Response:
{
  "events": [
    {
      "id": "uuid",
      "title": "Team Meeting",
      "description": "Weekly sync",
      "start_at": "2025-01-15T14:00:00Z",
      "end_at": "2025-01-15T15:00:00Z",
      "location": "Conference Room A",
      "created_at": "2025-01-10T10:00:00Z",
      "updated_at": "2025-01-10T10:00:00Z"
    }
  ],
  "total": 1
}
```

**Create Calendar Event:**

```javascript
POST /api/v1/calendar/events
Body:
{
  "title": "Team Meeting",
  "description": "Weekly sync",
  "start_at": "2025-01-15T14:00:00Z",
  "end_at": "2025-01-15T15:00:00Z",
  "location": "Conference Room A"
}
Response:
{
  "id": "uuid",
  "title": "Team Meeting",
  ...
}
```

**Update Calendar Event:**

```javascript
PUT /api/v1/calendar/events/{event_id}
Body: (same as create, all fields optional)
Response: (updated event)
```

**Delete Calendar Event:**

```javascript
DELETE /api/v1/calendar/events/{event_id}
Response: 204 No Content
```

## 6. Background Jobs

All background jobs use Redis Queue (RQ) with Redis (Upstash-compatible) as the queue backend. A dedicated `worker.py` bootstraps and runs RQ workers. All jobs include retry policies, idempotency safeguards, structured error logging, and production-grade failure handling.

### 6.1 Event Ingestion Job (ingestion.py)

- **Trigger**: Scheduled polling job (every 5 minutes)

- **Function**: Poll connectors for new events from Slack, Telegram, and Outlook using official APIs only. Normalize events into unified event records. Create/update threads as needed. Store in `events` table with `source`, `source_account_id`, `thread_id`, `text_for_embedding`, `content_hash`, and `raw` JSONB. Set `expires_at` to 30 days from ingestion (not `occurred_at`).

- **Queue**: Redis Queue (RQ)

- **Retry Policy**: Exponential backoff with maximum retry attempts

- **Idempotency**: Use `content_hash` and `external_id` to prevent duplicate ingestion

- **Error Handling**: Structured logging for failed API calls, connector errors, and database failures

### 6.2 Embedding Generation Job (embedding.py)

- **Trigger**: Chained background job triggered after ingestion

- **Function**: Generate embeddings for newly ingested or updated objects (event, thread, note, draft, entity) in batches. Support multi-chunk embeddings via `chunk_index` for long content. Skip re-embedding using `content_hash` comparison - only generate embeddings when content has changed. Store via VectorStore abstraction layer with `object_type`, `object_id`, `chunk_index`, `embedding_model`, `embedding_dim`, `distance_metric`, `content_hash`. Ensure vector records are created with proper user_id scoping and time metadata for retention policy consistency.

- **Queue**: Redis Queue (RQ)

- **Batch**: Process up to 100 objects per job

- **Idempotency**: Content hash checking prevents duplicate embedding generation

- **Error Handling**: Structured logging for embedding generation failures, API rate limits, and storage errors

### 6.3 Summarization Job (summarization.py)

- **Trigger**: On-demand (via API prompt endpoint) or optionally scheduled (hourly)

- **Function**: Generate summaries and action proposals using strict JSON outputs validated by Pydantic models. For time ranges, use `window_start` and `window_end` (determined from user prompt or scheduled window). Store in `summaries` table with `content_json` (JSONB) and `source_refs` (JSONB array of event/thread references). Also generate `proposals` table entries for actionable items. This job is invoked by the prompt router when a summarization intent is detected. All LLM outputs must be validated by Pydantic schemas before storage.

- **Queue**: Redis Queue (RQ)

- **LLM**: OpenAI GPT-4 with JSON mode

- **Idempotency**: Check for existing summaries for the same time window to avoid duplicate generation

- **Error Handling**: Structured logging for LLM failures, validation errors, and storage issues

### 6.4 Retention Cleanup Job (retention.py)

- **Trigger**: Scheduled (daily at 2 AM UTC)

- **Function**: Delete expired events where `expires_at < NOW()`. Reliably clean up associated embeddings, summaries, and proposals in bounded batches to avoid long-running locks. Also handle soft deletes for events with `deleted_at` set. Ensure vector records are cleaned up via VectorStore abstraction to maintain consistency with 30-day retention policy. Delete embeddings for expired events, threads, notes, drafts, and entities.

- **Queue**: Redis Queue (RQ)

- **Batch**: Delete in bounded batches (e.g., 1000 records per batch) to avoid long-running database locks

- **Idempotency**: Track cleanup progress to allow safe retries

- **Error Handling**: Structured logging for cleanup failures, transaction errors, and partial cleanup scenarios

## 7. Security and Privacy Checklist

### 7.1 Supabase RLS Enforcement

- [ ] RLS enabled on all user-owned tables

- [ ] Policies defined for SELECT, INSERT, UPDATE, DELETE

- [ ] Policies use `auth.uid()` for user isolation

- [ ] Policies tested with multiple users

- [ ] Service role key never exposed to client

### 7.2 Token Encryption

- [ ] AES-256-GCM encryption for OAuth tokens

- [ ] Encryption key stored in environment variable

- [ ] Key rotation procedure documented

- [ ] Decryption only in backend service layer

- [ ] Encrypted tokens never logged

### 7.3 Key Management

- [ ] All secrets in environment variables

- [ ] `.env` files in `.gitignore`

- [ ] Production secrets in secure vault (e.g., AWS Secrets Manager)

- [ ] No hardcoded credentials in code

- [ ] Separate keys for dev/staging/prod

### 7.4 Retention Enforcement

- [ ] `expires_at` set on all events at creation (30 days default)

- [ ] Background job deletes expired data

- [ ] User-initiated deletion API endpoint

- [ ] Deletion cascades to related embeddings

- [ ] Audit log for deletions (optional, future)

### 7.5 Encryption in Transit

- [ ] HTTPS/TLS for all API endpoints

- [ ] Database connections use SSL

- [ ] Redis connections use TLS (if supported)

- [ ] External API calls use HTTPS

### 7.6 Encryption at Rest

- [ ] Supabase Postgres encryption at rest (managed)

- [ ] OAuth tokens encrypted before storage

- [ ] Backup encryption (if backups are taken)

- [ ] Log files do not contain sensitive data

## 8. Production Readiness Checklist

### 8.1 Code Quality

- [ ] Type hints on all functions

- [ ] Pydantic models for all API inputs/outputs

- [ ] Comprehensive error handling

- [ ] Logging at appropriate levels (INFO, WARNING, ERROR)

- [ ] No hardcoded values (use config)

### 8.2 Database

- [ ] All schema changes via Alembic migrations

- [ ] Migrations are reversible (downgrade works)

- [ ] Indexes on all foreign keys and query patterns

- [ ] RLS policies tested and verified

- [ ] Connection pooling configured

- [ ] Database backups enabled

### 8.3 API

- [ ] Rate limiting implemented

- [ ] Request validation (Pydantic)

- [ ] Response validation (Pydantic)

- [ ] Error responses are consistent

- [ ] API versioning in place (`/api/v1/`)

- [ ] CORS configured appropriately

### 8.4 Background Jobs

- [ ] Redis Queue (RQ) with Redis/Upstash as queue backend

- [ ] Dedicated worker.py for RQ worker bootstrap

- [ ] Retry policies with exponential backoff for all jobs

- [ ] Idempotency safeguards (content hash checking, duplicate prevention)

- [ ] Structured error logging for all job failures

- [ ] Production-grade failure handling (graceful degradation, partial failure recovery)

- [ ] Job monitoring/observability (RQ dashboard, job status tracking)

- [ ] Dead letter queue for failed jobs after max retries

- [ ] Bounded batch processing to avoid long-running locks

- [ ] Content hash checking to skip unnecessary re-embedding

### 8.5 Observability

- [ ] Structured logging (JSON format)

- [ ] Log aggregation (e.g., Datadog, CloudWatch)

- [ ] Error tracking (e.g., Sentry)

- [ ] Health check endpoint (`/health`)

- [ ] Metrics collection (request counts, latencies)

### 8.6 Security

- [ ] All endpoints require authentication

- [ ] JWT token validation on every request

- [ ] Input sanitization (SQL injection prevention via ORM)

- [ ] XSS prevention (API-only, but good practice)

- [ ] Secrets management in place

- [ ] Security headers (if serving web content)

### 8.7 Testing

- [ ] Unit tests for all services, models, and utilities (≥90% coverage required)

- [ ] Integration tests for all API endpoints (authentication, request/response validation, error handling)

- [ ] Tests for RLS policies (multi-user isolation, policy enforcement, edge cases)

- [ ] Tests for all background jobs (ingestion, embedding, summarization, retention) with mocked external APIs

- [ ] Tests for connector services (Slack, Telegram, Outlook) with mocked OAuth flows and API responses

- [ ] Tests for VectorStore abstraction layer (pgvector implementation, semantic search, multi-chunk embeddings)

- [ ] Tests for LangGraph agents (prompt router, summarize graph, task graph) with mocked LLM responses

- [ ] Tests for token encryption/decryption (crypto service)

- [ ] Tests for retention policy enforcement (30-day expiration, cleanup jobs)

- [ ] Tests for idempotency safeguards (content hash checking, duplicate prevention)

- [ ] Tests for error handling and retry logic in all jobs

- [ ] Load testing for critical endpoints (prompts, summarize, tasks)

- [ ] End-to-end tests for complete user workflows (OAuth → ingestion → embedding → query)

- [ ] Test fixtures for database, Redis, and external API mocking

- [ ] CI/CD pipeline includes test execution with coverage reporting (fail if <90%)

### 8.8 Documentation

- [ ] API documentation (OpenAPI/Swagger)

- [ ] Setup instructions in README

- [ ] Environment variables documented

- [ ] Deployment procedure documented

- [ ] Runbook for common issues

### 8.9 Deployment

- [ ] CI/CD pipeline configured

- [ ] Database migrations run automatically

- [ ] Zero-downtime deployment strategy

- [ ] Rollback procedure documented

- [ ] Environment-specific configs

### 8.10 Monitoring

- [ ] Database connection pool monitoring

- [ ] Redis connection monitoring

- [ ] Job queue depth monitoring

- [ ] API response time monitoring

- [ ] Error rate monitoring

- [ ] Alerting configured for critical failures

## 9. Version Matrix (Late 2025 / Early 2026)

**Compatibility Notes:**

- All packages are compatible with Python 3.11.x
- FastAPI 0.115.x requires Pydantic 2.x (2.9.2+ recommended)
- SQLAlchemy 2.0.36+ requires Alembic 1.13.2+ for migrations
- LangChain 0.3.x, LangGraph 0.2.x, and OpenAI 1.51.x are compatible together
- pgvector 0.4.2 requires PostgreSQL 13-19 (Supabase manages this)
- Telethon 1.42.0 is the latest stable release (avoid 2.0.0a0 alpha for production)

| Package | Version | Justification |

|---------|---------|---------------|

| Python | 3.11.x | LTS support, performance improvements, type hint enhancements. Compatible with all listed packages |

| FastAPI | 0.115.x | Latest stable (as of late 2025), async support, OpenAPI 3.1, compatible with Pydantic 2.x |

| SQLAlchemy | 2.0.36+ | Modern async support, improved type hints, mandatory for v1. Latest 2.0.x stable release |

| Alembic | 1.13.2+ | Compatible with SQLAlchemy 2.0.36+, migration tooling. Latest 1.13.x stable |

| Pydantic | 2.9.2+ | V2 provides better performance, JSON schema generation. Compatible with FastAPI 0.115+ |

| pydantic-settings | 2.5.2+ | Settings management for Pydantic 2.x. Compatible with Pydantic 2.9.x |

| Uvicorn | 0.32.0+ | ASGI server, compatible with FastAPI 0.115+. Latest stable release |

| Redis | 5.0.8+ | Latest stable Redis Python client. Compatible with RQ 1.15+ |

| rq | 1.15.1+ | Redis Queue for background jobs. Compatible with Redis 5.0.8+. Upstash-compatible |

| LangChain | 0.3.0+ | Stable API, LangGraph integration. Compatible with OpenAI 1.x |

| langchain-openai | 0.2.0+ | LangChain OpenAI integration. Compatible with LangChain 0.3.x and OpenAI 1.x |

| LangGraph | 0.2.0+ | Agent orchestration, state management. Compatible with LangChain 0.3.x |

| openai | 1.51.0+ | Official SDK, async support, latest API features. Compatible with LangChain 0.3.x |

| supabase-py | 2.7.0+ | Supabase client, auth integration. Latest stable release |

| pgvector | 0.4.2 | Postgres extension Python library (December 2025). Compatible with PostgreSQL 13-19 (Supabase manages extension) |

| python-jose | 3.3.0+ | JWT token validation. Compatible with cryptography 43.x |

| cryptography | 43.0.0+ | Token encryption (AES-256-GCM). Latest stable release |

| python-dotenv | 1.0.1+ | Environment variable management. Latest stable release |

| pytest | 8.3.0+ | Testing framework. Compatible with Python 3.11.x |

| pytest-asyncio | 0.24.0+ | Async testing support for pytest. Compatible with pytest 8.3.x |

| pytest-cov | 5.0.0+ | Coverage plugin for pytest. Compatible with pytest 8.3.x. Target: ≥90% coverage |

| pytest-mock | 3.14.0+ | Mocking library for external APIs and services. Compatible with pytest 8.3.x |

| pytest-xdist | 3.6.0+ | Parallel test execution for faster test runs. Compatible with pytest 8.3.x |

| psycopg2-binary | 2.9.10+ | PostgreSQL adapter. Compatible with SQLAlchemy 2.0.x and Python 3.11.x |

| black | 24.8.0+ | Code formatter. Compatible with Python 3.11.x |

| ruff | 0.6.0+ | Fast linter. Compatible with Python 3.11.x |

| mypy | 1.11.0+ | Type checker. Compatible with Python 3.11.x and SQLAlchemy 2.0.x |

| httpx | 0.27.0+ | Async HTTP client for testing. Compatible with FastAPI 0.115+ |

| telethon | 1.42.0 | Telegram Client API (MTProto) for accessing user messages. Latest stable (November 2025). Compatible with Python 3.11+ |

## 10. Setup Procedure

### 10.1 Initial Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# Required variables:
# - SUPABASE_URL
# - SUPABASE_SERVICE_ROLE_KEY
# - SUPABASE_ANON_KEY
# - DATABASE_URL (Supabase Postgres connection string)
# - REDIS_URL
# - OPENAI_API_KEY
# - ENCRYPTION_KEY (32-byte hex string for AES-256)
# - SLACK_CLIENT_ID
# - SLACK_CLIENT_SECRET
# - TELEGRAM_BOT_TOKEN (optional, per bot)
# - OUTLOOK_CLIENT_ID
# - OUTLOOK_CLIENT_SECRET
```

### 10.2 Database Setup

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Review migration file in alembic/versions/

# Apply migration
alembic upgrade head

# Verify migration
alembic current

# If needed, rollback
alembic downgrade -1
```

### 10.3 Enable pgvector in Supabase

```sql
-- Run in Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### 10.4 Set Up RLS Policies

```sql
-- Example for events table (run in Supabase SQL Editor)
ALTER TABLE events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own events"
  ON events FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own events"
  ON events FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Repeat for all user-owned tables
```

### 10.5 Run Development Server

```bash
# API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Worker (in separate terminal)
# RQ worker bootstrapped via worker.py
python -m app.jobs.worker
```

### 10.6 Verify Setup

```bash
# Health check
curl http://localhost:8000/health

# API docs
# Open http://localhost:8000/docs in browser

# Run tests with coverage (target: ≥90%)
pytest --cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=90

# View coverage report
# Open htmlcov/index.html in browser
```

## 11. Execution Milestones

### Week 1: Foundation

- [ ] Project structure created

- [ ] Dependencies installed and verified

- [ ] Database models defined

- [ ] Alembic initialized and first migration created

- [ ] Supabase connection tested

- [ ] RLS policies implemented

- [ ] Basic FastAPI app with health endpoint

- [ ] Authentication middleware (Supabase JWT)

### Week 2: Connectors

- [ ] Base connector interface implemented

- [ ] Slack OAuth flow (initiate + callback)
- [ ] Telegram connection via Telethon (phone auth)

- [ ] Outlook OAuth flow

- [ ] Token encryption/decryption service

- [ ] Event ingestion job (scheduled polling every 5 minutes, official APIs only)

- [ ] Event normalization into unified records

- [ ] Event storage with retention (`expires_at` = 30 days from ingestion)

- [ ] Idempotency safeguards for ingestion (content hash, external_id)

### Week 3: Vector & Embeddings

- [ ] pgvector extension enabled

- [ ] Embeddings table created (migration)

- [ ] OpenAI embedding service

- [ ] Vector service abstraction layer (VectorStore interface) with pgvector implementation

- [ ] Semantic similarity search with user_id, time window, and source filters (powers free-text prompt queries)

- [ ] Multi-chunk embedding support (chunk_index)

- [ ] Embedding generation job (chained after ingestion, content hash checking)

- [ ] Multi-chunk embedding support (chunk_index)

- [ ] Skip re-embedding using content hashes

- [ ] Vector retention policy enforcement (30-day consistency with events)

- [ ] Link embeddings to events, threads, notes, drafts, entities

- [ ] Prompt router implementation (classifies user queries and routes to appropriate handlers)

### Week 4: Agents & Features

- [ ] LangGraph setup

- [ ] Prompt router agent (classifies free-text queries)

- [ ] Summarize agent (handles summarization queries, example: "summarize last 2 hours")

- [ ] Task detection agent (handles action queries, example: "what needs action?")

- [ ] API endpoint for free-text prompts (/prompts)

- [ ] Calendar CRUD endpoints

- [ ] Background job orchestration (RQ worker setup, job chaining)

- [ ] Retention cleanup job (daily 2 AM UTC, bounded batches)

- [ ] All jobs with retry policies, idempotency, structured logging

- [ ] Comprehensive test suite (≥90% coverage)

- [ ] Unit tests for all services, models, utilities

- [ ] Integration tests for all API endpoints

- [ ] Tests for RLS policies, connectors, agents, jobs

- [ ] End-to-end workflow tests

- [ ] CI/CD with coverage enforcement (fail if <90%)

## 12. File Contents

### 12.1 requirements.txt

```javascript
# Core Framework
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.9.2
pydantic-settings==2.5.2

# Database
sqlalchemy==2.0.36
alembic==1.13.2
psycopg2-binary==2.9.10
pgvector==0.4.2  # Latest stable (December 2025)

# Supabase
supabase==2.7.0
python-jose[cryptography]==3.3.0

# Redis
redis==5.0.8
rq==1.15.1  # Redis Queue for background jobs (Upstash-compatible)

# LLM & Agents
openai==1.51.0
langchain==0.3.0
langchain-openai==0.2.0
langgraph==0.2.0

# Connectors
telethon==1.42.0  # Latest stable (November 2025) - Telegram Client API (MTProto)

# Utilities
python-dotenv==1.0.1
httpx==0.27.0
cryptography==43.0.0

# Testing
pytest==8.3.0
pytest-asyncio==0.24.0
pytest-cov==5.0.0  # Coverage reporting (target: ≥90%)
pytest-mock==3.14.0  # Mocking for external APIs and services
pytest-xdist==3.6.0  # Parallel test execution
# Note: httpx is listed in Utilities section above

# Development
black==24.8.0
ruff==0.6.0
mypy==1.11.0
```

### 12.2 .gitignore

```javascript
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local
.env.*.local

# Database
*.db
*.sqlite

# Logs
*.log
logs/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Alembic
# Keep alembic.ini and alembic/ directory, ignore temp files

# OS
.DS_Store
Thumbs.db

# Build
dist/
build/
*.egg-info/
```

### 12.3 .env.example

```javascript
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Database (Supabase Postgres)
DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres

# Redis
REDIS_URL=redis://localhost:6379/0
# Or Upstash:
# REDIS_URL=rediss://default:password@xxx.upstash.io:6379

# OpenAI
OPENAI_API_KEY=sk-...

# Encryption (32-byte hex string, generate with: openssl rand -hex 32)
ENCRYPTION_KEY=your-32-byte-hex-key-here

# Slack OAuth
SLACK_CLIENT_ID=your-slack-client-id
SLACK_CLIENT_SECRET=your-slack-client-secret
SLACK_REDIRECT_URI=http://localhost:8000/api/v1/connectors/slack/oauth/callback

# Telegram (via Telethon)
# Note: Uses phone number authentication via Telethon library, no bot token needed
# Telegram API credentials obtained from https://my.telegram.org/apps
TELEGRAM_API_ID=your-telegram-api-id
TELEGRAM_API_HASH=your-telegram-api-hash
# Telethon session files will be stored encrypted (managed by connector service)

# Outlook OAuth
OUTLOOK_CLIENT_ID=your-outlook-client-id
OUTLOOK_CLIENT_SECRET=your-outlook-client-secret
OUTLOOK_REDIRECT_URI=http://localhost:8000/api/v1/connectors/outlook/oauth/callback
OUTLOOK_TENANT_ID=common  # or your tenant ID

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
```

### 12.4 Example Alembic Migration (Initial Schema)

**Note**: This migration must match the complete schema defined in Section 4.1. Key changes from old schema:

- `users`: Add `display_name` (nullable), `timezone` (NOT NULL, default 'UTC')
- `linked_accounts`: `connector_type` → `provider`, `external_id` → `provider_account_id`, add `scopes`, `status` (default 'active'), `metadata` (JSONB), remove `display_name`, `is_active`, `expires_at`
- `oauth_tokens`: Add `user_id`, `token_type` (bearer|bot), `scopes`, rename to `access_token_enc`/`refresh_token_enc`, add `last_refreshed_at`, `revoked_at`, `token_fingerprint`
- New table: `threads` (for conversation threads)
- `events`: `linked_account_id` → `source_account_id` (nullable), `connector_type` → `source`, add `thread_id`, `event_type` expanded, `content` → `body`, add `url`, `text_for_embedding`, `content_hash`, `importance_score`, `deleted_at`, `raw` (JSONB), remove `ingested_at`
- New tables: `entities`, `notes`, `tasks` (replaces `actions`), `proposals`, `drafts`
- `calendar_events`: `start_time`/`end_time` → `start_at`/`end_at`, remove `timezone`, `metadata`
- `summaries`: `summary_type` removed, `content` → `content_json`, `time_range_start`/`time_range_end` → `window_start`/`window_end`, `event_ids` → `source_refs` (JSONB), remove `expires_at`
- `embeddings`: Complete restructure - `object_type`/`object_id`/`chunk_index` instead of `event_id`/`summary_id`, add `embedding_model`, `embedding_dim`, `distance_metric`, `content_hash`, `metadata`, unique constraint on (user_id, object_type, object_id, chunk_index, embedding_model)
```python
"""Initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Enable extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "vector"')
    
    # Users (reference Supabase Auth)
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.Text(), nullable=True),
        sa.Column('display_name', sa.Text(), nullable=True),
        sa.Column('timezone', sa.Text(), nullable=False, server_default='UTC'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    
    # Linked accounts
    op.create_table(
        'linked_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('connector_type', sa.Enum('slack', 'telegram', 'outlook', name='connector_type'), nullable=False),
        sa.Column('external_id', sa.String(255), nullable=False),
        sa.Column('display_name', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.UniqueConstraint('user_id', 'connector_type', 'external_id'),
    )
    op.create_index('idx_linked_accounts_user_id', 'linked_accounts', ['user_id'])
    
    # OAuth tokens
    op.create_table(
        'oauth_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('linked_account_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('linked_accounts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('encrypted_access_token', sa.Text(), nullable=False),
        sa.Column('encrypted_refresh_token', sa.Text(), nullable=True),
        sa.Column('token_type', sa.String(50), nullable=False),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )
    
    # Events
    op.create_table(
        'events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('linked_account_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('linked_accounts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('connector_type', sa.Enum('slack', 'telegram', 'outlook', name='connector_type'), nullable=False),
        sa.Column('external_id', sa.String(255), nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('title', sa.String(500), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('occurred_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('ingested_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.UniqueConstraint('connector_type', 'external_id'),
    )
    op.create_index('idx_events_user_occurred', 'events', ['user_id', 'occurred_at'])
    op.create_index('idx_events_user_connector', 'events', ['user_id', 'connector_type'])
    op.create_index('idx_events_expires', 'events', ['expires_at'])
    
    # Embeddings
    op.create_table(
        'embeddings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('events.id', ondelete='CASCADE'), nullable=True),
        sa.Column('summary_id', postgresql.UUID(as_uuid=True), nullable=True),  # FK added later
        sa.Column('embedding_type', sa.Enum('event', 'summary', name='embedding_type'), nullable=False),
        sa.Column('embedding_vector', Vector(1536), nullable=False),
        sa.Column('model', sa.String(100), default='text-embedding-ada-002'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('idx_embeddings_user', 'embeddings', ['user_id'])
    # Vector similarity index (HNSW)
    op.execute('CREATE INDEX idx_embeddings_vector ON embeddings USING hnsw (embedding_vector vector_cosine_ops)')
    
    # Summaries
    op.create_table(
        'summaries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('summary_type', sa.Enum('last_2_hours', 'custom', name='summary_type'), nullable=False),
        sa.Column('content', postgresql.JSONB(), nullable=False),
        sa.Column('event_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column('time_range_start', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('time_range_end', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index('idx_summaries_user_created', 'summaries', ['user_id', 'created_at'])
    
    # Actions
    op.create_table(
        'actions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('events.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action_type', sa.Enum('reply', 'follow_up', 'schedule', 'other', name='action_type'), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', name='priority'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'in_progress', 'completed', 'dismissed', name='action_status'), default='pending'),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index('idx_actions_user_status', 'actions', ['user_id', 'status'])
    op.create_index('idx_actions_user_priority', 'actions', ['user_id', 'priority'])
    
    # Calendar events
    op.create_table(
        'calendar_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_time', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('end_time', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('timezone', sa.String(50), default='UTC'),
        sa.Column('location', sa.String(500), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('idx_calendar_user_start', 'calendar_events', ['user_id', 'start_time'])
    
    # Add foreign key for summaries -> embeddings (deferred)
    op.create_foreign_key('fk_embeddings_summary', 'embeddings', 'summaries', ['summary_id'], ['id'], ondelete='CASCADE')

def downgrade():
    op.drop_table('calendar_events')
    op.drop_table('actions')
    op.drop_table('summaries')
    op.drop_table('embeddings')
    op.drop_table('events')
    op.drop_table('oauth_tokens')
    op.drop_table('linked_accounts')
    op.drop_table('users')
    op.execute('DROP EXTENSION IF EXISTS "vector"')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
    op.execute('DROP TYPE IF EXISTS connector_type')
    op.execute('DROP TYPE IF EXISTS embedding_type')
    op.execute('DROP TYPE IF EXISTS summary_type')
    op.execute('DROP TYPE IF EXISTS action_type')
    op.execute('DROP TYPE IF EXISTS priority')
    op.execute('DROP TYPE IF EXISTS action_status')
```


## 13. Next Steps

After reviewing this blueprint:

1. **Review and Approve**: Confirm architecture decisions align with requirements

2. **Environment Setup**: Create Supabase project, Redis instance, OpenAI API key

3. **Begin Implementation**: Start with Week 1 milestones

4. **Iterate**: Follow weekly milestones, adjust as needed
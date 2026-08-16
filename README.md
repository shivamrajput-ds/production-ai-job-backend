# Production AI Job Processing Backend

A progressively built, production-oriented backend for managing AI/ML processing jobs using **FastAPI**.

This project is being developed from the ground up to practice real backend engineering concepts through implementation rather than isolated theory. The final system will evolve into a database-backed API capable of managing users, projects, files, asynchronous AI/ML jobs, results, authentication, caching, testing, and production deployment.

> **Current status:** Early development — core FastAPI routing, validation, persistent job creation, retrieval, and HTTP error handling are implemented.

---

## Project Goal

The goal is to build the backend architecture commonly required by real AI/ML applications.

A typical final workflow will look like:

```text
Client
  │
  ▼
FastAPI API
  │
  ├── Authentication
  ├── Projects
  ├── File Uploads
  └── Job Creation
          │
          ▼
      Job Queue
          │
          ▼
        Worker
          │
          ▼
   AI / ML Processing
          │
          ▼
      Result Storage
          │
          ▼
   Job Status / Result API
```

The AI processing itself will initially remain lightweight so that the primary focus stays on **backend engineering and production design**.

---

## Current Features

* FastAPI application setup
* Health-check endpoint
* REST-style job endpoints
* Path parameters
* Query parameters
* JSON request bodies
* Pydantic request validation
* Automatic validation errors
* Job creation with generated IDs
* Persistent JSON-based job storage
* Job retrieval by ID
* `201 Created` responses
* `404 Not Found` handling
* FastAPI `HTTPException`
* Interactive Swagger/OpenAPI documentation

---

## Current API

### Health Check

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

---

### Create Job

```http
POST /jobs
```

Request:

```json
{
  "name": "Customer complaint analysis",
  "model_name": "sentiment-model-v1"
}
```

Example response:

```json
{
  "message": "Job created successfully",
  "job": {
    "name": "Customer complaint analysis",
    "model_name": "sentiment-model-v1",
    "status": "pending"
  }
}
```

Successful creation returns:

```text
201 Created
```

Incoming request bodies are validated using Pydantic.

---

### Retrieve Job

```http
GET /jobs/{job_id}
```

Example:

```http
GET /jobs/1
```

If the job exists, the stored job is returned.

If the job does not exist:

```text
404 Not Found
```

```json
{
  "detail": "Job not found"
}
```

---

## Current Persistence

Jobs are currently persisted in:

```text
data.json
```

Example structure:

```json
{
  "1": {
    "name": "Customer complaint analysis",
    "model_name": "sentiment-model-v1",
    "status": "pending"
  },
  "2": {
    "name": "Document classification",
    "model_name": "classifier-v2",
    "status": "pending"
  }
}
```

The backend uses:

```python
json.load(...)
```

to deserialize stored JSON into Python objects and:

```python
json.dump(...)
```

to persist updated Python objects back to disk.

### Why JSON for now?

JSON storage is intentionally temporary.

It provides a simple way to understand:

* application state
* persistence
* resource IDs
* reads and writes
* missing-resource handling

without hiding these concepts behind an ORM too early.

It will later be replaced by **PostgreSQL + SQLAlchemy**.

---

## Validation

Job creation currently uses a Pydantic request schema:

```python
class JobCreate(BaseModel):
    name: str
    model_name: str
```

Both fields are required.

An invalid body such as:

```json
{
  "name": "Test job"
}
```

is rejected automatically because `model_name` is missing.

FastAPI returns:

```text
422 Unprocessable Entity
```

before the route's business logic executes.

---

## Project Structure

Current structure is intentionally small:

```text
production-ai-job-backend/
│
├── main.py
├── data.json
├── pyproject.toml
├── uv.lock
├── README.md
└── .gitignore
```

The application is deliberately **not over-engineered yet**.

As responsibilities grow, the codebase will gradually evolve toward a structure similar to:

```text
app/
├── api/
├── core/
├── db/
├── models/
├── schemas/
├── repositories/
├── services/
└── tests/
```

These layers will only be introduced when the project creates a real need for them.

---

## Tech Stack

### Current

* Python
* FastAPI
* Pydantic
* Uvicorn
* JSON
* uv
* Git

### Planned

* PostgreSQL
* SQLAlchemy
* Alembic
* JWT authentication
* Password hashing
* Redis
* Background workers / task queues
* Pytest
* HTTPX
* Structured logging
* Docker
* Docker Compose

---

## Run Locally

### 1. Clone the repository

```bash
git clone <repository-url>
cd production-ai-job-backend
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Start the development server

```bash
uv run fastapi dev main.py
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

## Interactive API Documentation

FastAPI automatically exposes interactive OpenAPI documentation.

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Alternative API documentation:

```text
http://127.0.0.1:8000/redoc
```

---

## Development Roadmap

### Stage 1 — API Fundamentals

* [x] FastAPI application
* [x] GET endpoints
* [x] POST endpoints
* [x] Path parameters
* [x] Query parameters
* [x] Request bodies
* [x] HTTP status codes
* [x] Pydantic validation
* [x] Basic error handling

### Stage 2 — Job Management

* [x] Job creation
* [x] Persistent temporary storage
* [x] Retrieve job by ID
* [ ] List all jobs
* [ ] Update jobs
* [ ] Delete jobs
* [ ] Filtering
* [ ] Sorting
* [ ] Pagination

### Stage 3 — Clean Architecture

* [ ] APIRouter
* [ ] Modular application structure
* [ ] Schema separation
* [ ] Service layer
* [ ] Repository/data-access layer
* [ ] Central configuration

### Stage 4 — PostgreSQL

* [ ] PostgreSQL integration
* [ ] SQLAlchemy models
* [ ] Database sessions
* [ ] CRUD operations
* [ ] Relationships
* [ ] Constraints
* [ ] Transactions
* [ ] Indexes

### Stage 5 — Database Migrations

* [ ] Alembic setup
* [ ] Initial schema migration
* [ ] Schema upgrades
* [ ] Downgrades
* [ ] Safe schema evolution

### Stage 6 — Authentication & Authorization

* [ ] User registration
* [ ] Password hashing
* [ ] Login
* [ ] JWT access tokens
* [ ] Protected routes
* [ ] Current-user dependency
* [ ] Resource ownership
* [ ] Role-based permissions

### Stage 7 — AI/ML Job Workflow

* [ ] File uploads
* [ ] File validation
* [ ] Job lifecycle states
* [ ] Background processing
* [ ] Worker architecture
* [ ] Job results
* [ ] Failure tracking
* [ ] Retry-safe processing
* [ ] Idempotency

### Stage 8 — Production Engineering

* [ ] Redis
* [ ] Caching
* [ ] Logging
* [ ] Middleware
* [ ] Request IDs
* [ ] External API integration
* [ ] Async I/O
* [ ] Rate limiting
* [ ] Security improvements

### Stage 9 — Testing

* [ ] Pytest setup
* [ ] API tests
* [ ] Unit tests
* [ ] Validation tests
* [ ] Failure-path tests
* [ ] Authentication tests
* [ ] Database tests
* [ ] Mocked external services

### Stage 10 — Deployment Readiness

* [ ] Dockerfile
* [ ] Docker Compose
* [ ] FastAPI + PostgreSQL + Redis
* [ ] Environment-based configuration
* [ ] Health/readiness checks
* [ ] CI pipeline
* [ ] Production deployment preparation

---

## Engineering Principles

This project follows a few important rules:

* **Build before over-engineering**
* Understand code before abstracting it
* Introduce architecture only when complexity requires it
* Validate input at API boundaries
* Return meaningful HTTP status codes
* Keep business logic separate from transport logic as the system grows
* Persist important state outside process memory
* Treat failures as normal backend scenarios
* Write code that can be tested
* Never commit secrets
* Prefer understandable engineering over unnecessary complexity

---

## What This Project Is Not

This is not intended to be a collection of disconnected FastAPI tutorial snippets.

It is one continuously evolving backend system designed to move through the same engineering concerns encountered in real applications:

```text
Simple endpoint
      ↓
Validation
      ↓
Persistence
      ↓
Database
      ↓
Authentication
      ↓
Background processing
      ↓
Testing
      ↓
Caching
      ↓
Failure handling
      ↓
Containerization
      ↓
Production-oriented backend
```

---

## Learning Focus

The project is especially focused on backend skills relevant to:

* AI/ML applications
* Data Science platforms
* Model-serving systems
* Document-processing systems
* RAG applications
* Applied AI products
* Asynchronous processing APIs

The objective is not merely to know FastAPI syntax, but to understand how to independently design, build, debug, test, and reason about a complete backend system.

---

## Status

🚧 **Actively under development**

The backend is being developed incrementally, with each stage introducing a new production engineering concept only after the previous layer is understood.

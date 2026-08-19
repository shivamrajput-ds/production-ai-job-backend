# Production AI Job Processing Backend

A progressively built **FastAPI backend for managing AI/ML processing jobs**, developed with a build-first approach to backend engineering.

Rather than learning backend concepts as disconnected theory, this project evolves one production-style system step by step—from basic API routes to validation, persistence, modular architecture, databases, authentication, background processing, testing, caching, and deployment.

> **Current status:** Modular FastAPI application with JSON-backed job CRUD, Pydantic request/response contracts, job lifecycle validation, error handling, and OpenAPI documentation.

---

## Overview

AI/ML applications often need much more than a model.

A real system may need to:

* accept processing requests
* validate input
* create and track jobs
* persist state
* expose job status
* handle failures
* process files
* run long-running work asynchronously
* authenticate users
* store results
* support retries
* scale safely

This project is being built to understand those backend responsibilities through implementation.

The current system focuses on **job management**, while later stages will introduce PostgreSQL, authentication, file processing, workers, Redis, testing, and containerization.

---

## Long-Term Architecture

The backend will gradually evolve toward a workflow similar to:

```text
Client
  │
  ▼
FastAPI API
  │
  ├── Authentication
  ├── Authorization
  ├── Projects
  ├── File Uploads
  └── Job Management
          │
          ▼
      PostgreSQL
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

The AI/ML processing itself will initially remain lightweight so that the main focus stays on **backend architecture, reliability, persistence, validation, testing, and production engineering**.

---

# Current Capabilities

The backend currently supports:

* FastAPI application setup
* Modular application structure
* `APIRouter`-based job routing
* Health-check endpoint
* Job creation
* Job listing
* Individual job retrieval
* Job status updates
* Job deletion
* Generated job IDs
* JSON-based persistent storage
* Pydantic request validation
* Pydantic response models
* Nested response models
* Typed collection responses
* Job lifecycle validation with `Literal`
* Automatic request validation
* `201 Created`
* `404 Not Found`
* Automatic `422 Unprocessable Entity`
* FastAPI `HTTPException`
* Swagger UI
* ReDoc
* Automatic OpenAPI schema generation

---

# Current Project Structure

```text
production-ai-job-backend/
│
├── main.py
├── routes.py
├── schemas.py
├── storage.py
├── data.json
├── README.md
├── pyproject.toml
├── uv.lock
└── .gitignore
```

Each module now has a clearer responsibility.

### `main.py`

Application entry point.

Currently responsible for:

* creating the FastAPI application
* registering the job router
* root endpoint
* health-check endpoint

Conceptually:

```text
main.py
   │
   ├── create FastAPI app
   ├── include job router
   └── expose application-level endpoints
```

---

### `routes.py`

Contains job-related API endpoints.

```text
POST   /jobs
GET    /jobs
GET    /jobs/{job_id}
PATCH  /jobs/{job_id}
DELETE /jobs/{job_id}
```

The routes are grouped using FastAPI's `APIRouter`.

Conceptually:

```text
APIRouter
    │
    └── /jobs
          ├── POST
          ├── GET
          ├── GET /{job_id}
          ├── PATCH /{job_id}
          └── DELETE /{job_id}
```

---

### `schemas.py`

Contains the Pydantic request and response contracts used by the API.

Current schemas include:

```text
JobCreate
JobResponse
JobActionResponse
JobUpdate
```

This keeps API data contracts separate from route logic.

---

### `storage.py`

Contains JSON persistence helpers.

Responsibilities:

```text
load_data()
dump_data()
```

This prevents file I/O logic from being repeated directly inside the application entry point.

---

### `data.json`

Temporary persistent storage for jobs.

JSON is intentionally being used before introducing PostgreSQL so that persistence, CRUD operations, resource IDs, and state changes can be understood without immediately hiding them behind an ORM.

---

# API Endpoints

## Root

```http
GET /
```

Example response:

```json
{
  "message": "Welcome to FastAPI"
}
```

---

## Health Check

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

## Create Job

```http
POST /jobs
```

### Request

```json
{
  "name": "Fraud detection training",
  "model_name": "fraud-detector-v1"
}
```

### Response

```json
{
  "message": "Job created successfully",
  "job": {
    "job_id": 5,
    "name": "Fraud detection training",
    "model_name": "fraud-detector-v1",
    "status": "pending"
  }
}
```

Successful creation returns:

```text
201 Created
```

Every new job automatically receives:

* a generated `job_id`
* an initial status of `pending`

---

## List All Jobs

```http
GET /jobs
```

Example response:

```json
{
  "5": {
    "job_id": 5,
    "name": "Fraud detection training",
    "model_name": "fraud-detector-v1",
    "status": "running"
  },
  "6": {
    "job_id": 6,
    "name": "Invoice fraud detection",
    "model_name": "fraud-detector-v2",
    "status": "pending"
  }
}
```

The response contract is:

```python
dict[str, JobResponse]
```

Meaning:

```text
dictionary key   → job ID represented as a string
dictionary value → validated JobResponse object
```

---

## Retrieve Job

```http
GET /jobs/{job_id}
```

Example:

```http
GET /jobs/5
```

Response:

```json
{
  "job_id": 5,
  "name": "Fraud detection training",
  "model_name": "fraud-detector-v1",
  "status": "running"
}
```

If the requested job does not exist:

```text
404 Not Found
```

Example error:

```json
{
  "detail": "Job not found"
}
```

---

## Update Job Status

```http
PATCH /jobs/{job_id}
```

Example:

```http
PATCH /jobs/5
```

### Request

```json
{
  "status": "completed"
}
```

### Response

```json
{
  "message": "Job updated successfully",
  "job": {
    "job_id": 5,
    "name": "Fraud detection training",
    "model_name": "fraud-detector-v1",
    "status": "completed"
  }
}
```

A PATCH request is used because only part of the existing job resource is being changed.

---

## Delete Job

```http
DELETE /jobs/{job_id}
```

The endpoint:

1. loads persistent job data
2. verifies the requested job exists
3. removes it
4. persists the modified data
5. returns a success response

If the requested ID does not exist:

```text
404 Not Found
```

---

# Job Lifecycle

Jobs currently support four states:

```text
pending
running
completed
failed
```

The update schema restricts status to these values.

```python
class JobUpdate(BaseModel):
    status: Literal[
        "pending",
        "running",
        "completed",
        "failed",
    ]
```

For example, this is valid:

```json
{
  "status": "running"
}
```

But this:

```json
{
  "status": "banana"
}
```

is automatically rejected.

FastAPI/Pydantic returns:

```text
422 Unprocessable Entity
```

The invalid request is rejected **before the route's update logic executes**.

---

# Pydantic Schemas

## `JobCreate`

Defines the request body required to create a new job.

```python
class JobCreate(BaseModel):
    name: str
    model_name: str
```

Both fields are required.

Example invalid request:

```json
{
  "name": "Test job"
}
```

Because `model_name` is missing, request validation fails automatically.

---

## `JobResponse`

Defines the public representation of a job returned by the API.

```python
class JobResponse(BaseModel):
    job_id: int
    name: str
    model_name: str
    status: str
```

Example:

```json
{
  "job_id": 5,
  "name": "Fraud detection training",
  "model_name": "fraud-detector-v1",
  "status": "pending"
}
```

---

## `JobActionResponse`

Reusable nested response schema for operations that return a message together with a job.

```python
class JobActionResponse(BaseModel):
    message: str
    job: JobResponse
```

Currently used for operations such as:

```text
POST  /jobs
PATCH /jobs/{job_id}
```

Example structure:

```json
{
  "message": "Job updated successfully",
  "job": {
    "job_id": 5,
    "name": "Fraud detection training",
    "model_name": "fraud-detector-v1",
    "status": "completed"
  }
}
```

---

## `JobUpdate`

Defines the allowed job status update request.

```python
class JobUpdate(BaseModel):
    status: Literal[
        "pending",
        "running",
        "completed",
        "failed",
    ]
```

This moves validation away from manually written route checks and into the API schema.

---

# Request and Response Contracts

The project distinguishes between incoming request data and outgoing response data.

```text
Client
  │
  ▼
Request Schema
  │
  ▼
FastAPI Route
  │
  ▼
Application Logic
  │
  ▼
Response Schema
  │
  ▼
Client
```

Examples:

```text
POST /jobs

Request:
JobCreate

Response:
JobActionResponse
```

```text
GET /jobs/{job_id}

Response:
JobResponse
```

```text
GET /jobs

Response:
dict[str, JobResponse]
```

```text
PATCH /jobs/{job_id}

Request:
JobUpdate

Response:
JobActionResponse
```

Response models do more than improve Swagger documentation.

They create an explicit contract for what the API exposes to its clients and allow FastAPI to validate the outgoing response structure.

---

# Validation and Error Handling

## Missing Required Field

Request:

```json
{
  "name": "Test job"
}
```

If `model_name` is required but missing:

```text
422 Unprocessable Entity
```

FastAPI rejects the request automatically through Pydantic validation.

---

## Invalid Job Status

Request:

```json
{
  "status": "banana"
}
```

Because `banana` is not an allowed `Literal` value:

```text
422 Unprocessable Entity
```

The route's business logic does not execute.

---

## Missing Resource

Example:

```http
GET /jobs/999
```

If job `999` does not exist:

```text
404 Not Found
```

The application handles this using:

```python
HTTPException
```

---

# Persistence

Jobs currently survive server restarts because they are persisted in:

```text
data.json
```

Example:

```json
{
  "5": {
    "job_id": 5,
    "name": "Fraud detection training",
    "model_name": "fraud-detector-v1",
    "status": "running"
  },
  "6": {
    "job_id": 6,
    "name": "Invoice fraud detection",
    "model_name": "fraud-detector-v2",
    "status": "pending"
  }
}
```

---

## Reading Stored Data

The storage layer uses:

```python
json.load(...)
```

Conceptually:

```text
data.json
    ↓
Python dictionary
```

---

## Writing Stored Data

The storage layer uses:

```python
json.dump(...)
```

Conceptually:

```text
Python dictionary
    ↓
data.json
```

---

## Mutation Flow

Operations that change state follow a simple flow:

```text
Load existing state
        ↓
Validate resource
        ↓
Modify state
        ↓
Persist updated state
        ↓
Return response
```

For example:

```text
PATCH /jobs/5
      ↓
load_data()
      ↓
find job
      ↓
change status
      ↓
dump_data()
      ↓
return updated job
```

---

# Why JSON Storage Is Temporary

JSON is useful at this stage because it makes persistence visible and understandable.

It provides hands-on practice with:

* application state
* persistence
* serialization
* resource identifiers
* CRUD operations
* state mutation
* missing resources
* server restarts
* response contracts

without introducing database abstraction too early.

The planned progression is:

```text
JSON
  ↓
PostgreSQL
  ↓
SQLAlchemy
  ↓
Alembic
```

---

# Limitations of the Current Storage Layer

The JSON implementation is suitable for learning but **not suitable as a production database**.

Important limitations include:

* unsafe concurrent writes
* race conditions
* lack of transactions
* possible file corruption during failures
* inefficient large-scale querying
* no relationships
* no relational constraints
* no indexes
* weak filtering capabilities
* poor multi-process coordination

These limitations provide the natural motivation for introducing PostgreSQL.

---

# Why the Application Was Split Into Modules

The project originally started with most logic in `main.py`.

As functionality increased, the file started containing multiple responsibilities:

```text
main.py
├── schemas
├── storage logic
├── job routes
├── health route
└── application setup
```

The project has now been refactored to:

```text
main.py
   ↓
Application assembly

routes.py
   ↓
Job API endpoints

schemas.py
   ↓
Request / response contracts

storage.py
   ↓
Persistence helpers
```

This is an early step toward separation of concerns.

The system has **not** yet introduced service and repository layers because the current complexity does not justify them.

The architecture will continue evolving only when new responsibilities create a genuine need.

---

# APIRouter

Job endpoints are now grouped using FastAPI's `APIRouter`.

The job router uses the common:

```text
/jobs
```

resource prefix.

Conceptually:

```text
/jobs
  │
  ├── POST
  ├── GET
  └── /{job_id}
         ├── GET
         ├── PATCH
         └── DELETE
```

The router is registered with the main FastAPI application using:

```python
app.include_router(router)
```

This allows `main.py` to focus on assembling the application rather than containing every endpoint directly.

---

# Current Tech Stack

## Backend

* Python
* FastAPI
* Pydantic
* Uvicorn

## Persistence

* JSON

## Project Management

* uv
* Git
* GitHub

---

# Planned Technologies

Future stages are expected to introduce technologies only when their need becomes clear.

Planned components include:

* PostgreSQL
* SQLAlchemy
* Alembic
* secure password hashing
* JWT authentication
* Redis
* background workers
* task queues
* Pytest
* HTTPX
* Python logging
* Docker
* Docker Compose

---

# Running Locally

## 1. Clone the Repository

```bash
git clone <repository-url>
cd production-ai-job-backend
```

## 2. Install Dependencies

```bash
uv sync
```

## 3. Start the Development Server

```bash
uv run fastapi dev main.py
```

The API will normally be available at:

```text
http://127.0.0.1:8000
```

---

# API Documentation

FastAPI automatically generates OpenAPI documentation from the routes and Pydantic schemas.

## Swagger UI

```text
http://127.0.0.1:8000/docs
```

Swagger can be used to:

* inspect endpoints
* inspect request schemas
* inspect response schemas
* create jobs
* list jobs
* retrieve jobs
* update job status
* delete jobs
* observe status codes
* test validation failures

---

## ReDoc

```text
http://127.0.0.1:8000/redoc
```

---

# Development Roadmap

## Stage 1 — FastAPI Fundamentals

* [x] FastAPI application setup
* [x] GET endpoints
* [x] POST endpoints
* [x] PATCH endpoints
* [x] DELETE endpoints
* [x] Path parameters
* [x] Request bodies
* [x] HTTP status codes
* [x] Pydantic validation
* [x] Response models
* [x] Nested response models
* [x] HTTP exceptions
* [x] OpenAPI / Swagger documentation

---

## Stage 2 — Job Management

* [x] Job creation
* [x] Generated job IDs
* [x] Temporary persistent storage
* [x] Retrieve job by ID
* [x] List all jobs
* [x] Update job status
* [x] Delete jobs
* [x] Job lifecycle validation
* [ ] Filtering
* [ ] Sorting
* [ ] Pagination

---

## Stage 3 — Modular Application Structure

* [x] `APIRouter`
* [x] Route separation
* [x] Schema separation
* [x] Storage separation
* [x] Router registration in application entry point
* [ ] Service layer
* [ ] Repository/data-access layer
* [ ] Central configuration
* [ ] Application package structure
* [ ] Reusable dependencies

---

## Stage 4 — PostgreSQL

* [ ] PostgreSQL integration
* [ ] Database engine
* [ ] Database sessions
* [ ] SQLAlchemy ORM models
* [ ] Inserts
* [ ] Queries
* [ ] Updates
* [ ] Deletes
* [ ] Filtering
* [ ] Sorting
* [ ] Pagination
* [ ] Relationships
* [ ] Foreign keys
* [ ] Unique constraints
* [ ] Transactions
* [ ] Indexes

---

## Stage 5 — Database Migrations

* [ ] Alembic setup
* [ ] Initial migration
* [ ] Upgrade
* [ ] Downgrade
* [ ] Schema evolution
* [ ] Constraint changes

---

## Stage 6 — Configuration

* [ ] Environment variables
* [ ] `.env`
* [ ] Settings model
* [ ] Database URL configuration
* [ ] Development vs production settings
* [ ] Secret management

---

## Stage 7 — Authentication

* [ ] User model
* [ ] User registration
* [ ] Password hashing
* [ ] Login
* [ ] JWT access tokens
* [ ] Token expiration
* [ ] Current-user dependency
* [ ] Protected endpoints

---

## Stage 8 — Authorization

* [ ] Resource ownership
* [ ] User-specific jobs
* [ ] Roles
* [ ] Admin permissions
* [ ] `401 Unauthorized`
* [ ] `403 Forbidden`

---

## Stage 9 — File Processing

* [ ] File uploads
* [ ] `UploadFile`
* [ ] File validation
* [ ] Extension validation
* [ ] Size limits
* [ ] Safe filenames
* [ ] File-to-job association
* [ ] Persistent file storage strategy

---

## Stage 10 — Background Job Processing

* [ ] FastAPI background tasks
* [ ] Long-running processing flow
* [ ] Worker concept
* [ ] External task queue
* [ ] Job status transitions
* [ ] Result persistence
* [ ] Worker failures
* [ ] Retries
* [ ] Idempotency

---

## Stage 11 — Redis and Caching

* [ ] Redis connection
* [ ] Cache keys
* [ ] TTL
* [ ] Cache hit
* [ ] Cache miss
* [ ] Cache invalidation
* [ ] Appropriate endpoint caching

---

## Stage 12 — Logging and Middleware

* [ ] Python logging
* [ ] Structured messages
* [ ] Exception logging
* [ ] Request timing
* [ ] Request IDs
* [ ] CORS
* [ ] Middleware request/response flow

---

## Stage 13 — Testing

* [ ] Pytest setup
* [ ] FastAPI API tests
* [ ] Unit tests
* [ ] Integration tests
* [ ] Validation tests
* [ ] CRUD tests
* [ ] Failure-path tests
* [ ] Test database
* [ ] Fixtures
* [ ] Authentication tests
* [ ] Mocking external services

---

## Stage 14 — External Services and Async I/O

* [ ] HTTPX
* [ ] External API calls
* [ ] Timeouts
* [ ] Error handling
* [ ] Retries
* [ ] `async def`
* [ ] `await`
* [ ] Blocking vs non-blocking I/O

---

## Stage 15 — Security

* [ ] Secure password handling
* [ ] Authentication
* [ ] Authorization
* [ ] Input validation
* [ ] Secret protection
* [ ] SQL injection awareness
* [ ] CORS configuration
* [ ] Secure file uploads
* [ ] Sensitive logging prevention
* [ ] Rate limiting

---

## Stage 16 — Docker and Deployment

* [ ] Dockerfile
* [ ] `.dockerignore`
* [ ] Containerized FastAPI
* [ ] Docker Compose
* [ ] PostgreSQL service
* [ ] Redis service
* [ ] Environment variables
* [ ] Health/readiness checks
* [ ] CI pipeline
* [ ] Production deployment preparation

---

# Engineering Principles

This project follows several engineering rules.

### Build before abstracting

Architecture is introduced because the code creates a need for it—not because a complicated folder structure looks impressive.

### Understand before automating

Every new library or abstraction should solve a problem that is already understood.

### Explicit API contracts

Incoming and outgoing data should have predictable structures.

### Validate at boundaries

Invalid input should be rejected as early as practical.

### Persist important state

Application state that must survive restarts should not exist only in process memory.

### Treat failures as normal

Missing resources, malformed input, database failures, worker crashes, and network failures are normal backend scenarios.

### Prefer clear code

Working code is not automatically maintainable code.

### Keep components testable

Application design should gradually make it easier to test individual responsibilities.

### Never commit secrets

Credentials, database passwords, API keys, and other secrets must remain outside version control.

### Avoid premature complexity

A correctly engineered monolith is preferable to an architecture that cannot be explained or maintained.

---

# Development Philosophy

The project follows this progression:

```text
Routes
  ↓
Request Validation
  ↓
CRUD
  ↓
Persistence
  ↓
Response Contracts
  ↓
Modular Structure
  ↓
Database
  ↓
Migrations
  ↓
Configuration
  ↓
Authentication
  ↓
Authorization
  ↓
File Processing
  ↓
Background Jobs
  ↓
Testing
  ↓
Caching
  ↓
Failure Handling
  ↓
Docker
  ↓
Production-Oriented Backend
```

Each layer is introduced only after the previous one is understood.

---

# Learning Focus

The project is particularly relevant to backend engineering for:

* AI/ML applications
* Data Science platforms
* model-processing services
* Applied AI systems
* document-processing platforms
* RAG applications
* ML inference APIs
* asynchronous AI workloads
* workflow and job-processing systems

The objective is not simply to learn FastAPI syntax.

The goal is to become capable of independently:

* designing APIs
* defining request contracts
* defining response contracts
* validating inputs
* choosing HTTP methods
* selecting status codes
* implementing CRUD operations
* managing persistent state
* handling errors
* structuring Python backend projects
* understanding database interactions
* debugging failures
* writing tests
* integrating external services
* reasoning about concurrency
* containerizing services
* thinking about production failure scenarios

---

# Current Milestone

The project has progressed from a single-file FastAPI experiment into a small modular backend.

Current flow:

```text
Validated Client Request
          ↓
       Router
          ↓
   Job Operation
          ↓
   JSON Storage Layer
          ↓
  Persistent Job State
          ↓
 Response Model Validation
          ↓
        Client
```

The next major progression will continue improving the modular design before moving persistence from JSON files to a real **PostgreSQL-backed data layer**.

---

# Status

🚧 **Actively under development**

The backend is being developed incrementally with emphasis on understanding each engineering decision rather than rapidly assembling a large framework-heavy application.

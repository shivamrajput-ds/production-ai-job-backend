# Production AI Job Processing Backend

A progressively built, production-oriented backend for managing **AI/ML processing jobs** using FastAPI.

This project is being developed from the ground up with a **build-first backend engineering approach**. Instead of learning backend concepts as isolated theory, each concept is introduced by implementing it inside one continuously evolving system.

The backend currently supports persistent job creation, retrieval, updates, deletion, request validation, response schemas, HTTP error handling, and interactive API documentation.

> **Current status:** Core JSON-backed job CRUD API and Pydantic request/response contracts are implemented. PostgreSQL and a cleaner multi-module architecture will be introduced as the project grows.

---

## Project Goal

The long-term goal is to build a backend architecture suitable for real AI/ML applications where clients can create processing jobs, upload files, monitor execution, retrieve results, and manage authenticated resources.

The system will gradually evolve toward a workflow like:

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
  └── Job Creation
          │
          ▼
      Persistent Database
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

The AI/ML processing itself will initially remain lightweight so that the main focus stays on **backend architecture, reliability, validation, persistence, testing, and production engineering**.

---

# Current Features

* FastAPI application setup
* Health-check endpoint
* REST-style job resource endpoints
* JSON request bodies
* Pydantic request validation
* Pydantic response models
* Nested response schemas
* Automatic OpenAPI schema generation
* Generated job IDs
* Persistent JSON-based storage
* Create job
* List all jobs
* Retrieve job by ID
* Update job status
* Delete job
* Allowed job-status validation
* `201 Created`
* `400 Bad Request` concepts
* `404 Not Found`
* Automatic `422 Unprocessable Entity`
* FastAPI `HTTPException`
* Swagger UI and ReDoc documentation

---

# Current API

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

Request body:

```json
{
  "name": "Fraud detection training",
  "model_name": "fraud-detector-v1"
}
```

Example response:

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

New jobs automatically receive:

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

The endpoint uses the response contract:

```python
dict[str, JobResponse]
```

This means:

* dictionary keys are job IDs stored as strings
* every dictionary value must match the `JobResponse` schema

---

## Retrieve a Job

```http
GET /jobs/{job_id}
```

Example:

```http
GET /jobs/5
```

Successful response:

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

Response:

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

Request body:

```json
{
  "status": "completed"
}
```

Response:

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

Currently supported job states are:

```text
pending
running
completed
failed
```

Invalid values are rejected automatically by Pydantic before the route's update logic executes.

For example:

```json
{
  "status": "banana"
}
```

returns:

```text
422 Unprocessable Entity
```

---

## Delete Job

```http
DELETE /jobs/{job_id}
```

If the job exists, it is removed from persistent storage.

Example response:

```json
{
  "message": "Successfully Deleted"
}
```

If the requested job does not exist:

```text
404 Not Found
```

---

# Pydantic Schemas

The API currently separates incoming and outgoing data contracts.

## Job Creation Request

```python
class JobCreate(BaseModel):
    name: str
    model_name: str
```

This schema validates the incoming body for:

```http
POST /jobs
```

Both fields are required.

---

## Job Response

```python
class JobResponse(BaseModel):
    job_id: int
    name: str
    model_name: str
    status: str
```

This defines the structure of a job returned by the API.

It is used for endpoints such as:

```http
GET /jobs/{job_id}
```

and inside collection/nested responses.

---

## Job Action Response

```python
class JobActionResponse(BaseModel):
    message: str
    job: JobResponse
```

This is a nested response model reused by job actions such as:

```http
POST /jobs
PATCH /jobs/{job_id}
```

Example shape:

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

## Job Status Update

```python
class JobUpdate(BaseModel):
    status: Literal[
        "pending",
        "running",
        "completed",
        "failed"
    ]
```

Using `Literal` moves status validation into the request schema instead of manually checking values inside the route.

This keeps the endpoint logic smaller and ensures invalid requests are rejected before business logic executes.

---

# Request vs Response Models

The project now distinguishes between what the client **sends** and what the API **returns**.

```text
Client Request
      │
      ▼
JobCreate / JobUpdate
      │
      ▼
FastAPI Route
      │
      ▼
Application Logic
      │
      ▼
JobResponse / JobActionResponse
      │
      ▼
Client Response
```

Examples:

```text
POST /jobs
Request  → JobCreate
Response → JobActionResponse
```

```text
GET /jobs/{job_id}
Response → JobResponse
```

```text
GET /jobs
Response → dict[str, JobResponse]
```

```text
PATCH /jobs/{job_id}
Request  → JobUpdate
Response → JobActionResponse
```

Response models are not used only for documentation. They also define and validate the structure that the API exposes to clients.

---

# Validation and Error Handling

The backend currently demonstrates several HTTP failure scenarios.

## Missing Request Field

Example:

```json
{
  "name": "Test job"
}
```

If `model_name` is required but missing, FastAPI/Pydantic rejects the request automatically:

```text
422 Unprocessable Entity
```

---

## Invalid Status

Example:

```json
{
  "status": "banana"
}
```

Because the request model only allows:

```text
pending
running
completed
failed
```

Pydantic rejects the request automatically:

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

This is handled using FastAPI's:

```python
HTTPException
```

---

# Current Persistence

Jobs are currently persisted in:

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

The application currently uses two small persistence helpers.

Reading data:

```python
json.load(...)
```

Flow:

```text
data.json
    ↓
Python dictionary
```

Writing data:

```python
json.dump(...)
```

Flow:

```text
Python dictionary
    ↓
data.json
```

The typical mutation flow is:

```text
Load
  ↓
Modify
  ↓
Persist
  ↓
Return Response
```

For example:

```text
PATCH /jobs/5
     ↓
load_data()
     ↓
find job
     ↓
update status
     ↓
dump_data()
     ↓
return updated job
```

---

# Why JSON Storage for Now?

JSON persistence is intentionally temporary.

It provides a simple environment for understanding:

* process memory vs persistent state
* resource IDs
* reads and writes
* CRUD operations
* state changes
* missing resources
* persistence after server restarts
* API contracts

without introducing an ORM and database session management too early.

The project will later migrate to:

```text
PostgreSQL
    +
SQLAlchemy
    +
Alembic
```

---

# Current Storage Limitations

The current JSON implementation is suitable for learning but is **not intended as production database storage**.

Potential limitations include:

* concurrent writes
* race conditions
* file corruption during failures
* inefficient lookup at larger scale
* lack of transactions
* weak query capabilities
* no relational constraints
* no database indexes

These limitations create the natural motivation for introducing PostgreSQL later.

---

# Current Project Structure

The project is intentionally still small:

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

The backend is deliberately **not over-engineered** at this stage.

As the application grows, responsibilities will gradually be separated into modules.

A future structure may evolve toward:

```text
app/
├── main.py
├── api/
├── core/
├── db/
├── models/
├── schemas/
├── repositories/
├── services/
└── tests/
```

These layers will be introduced only when the current code creates a genuine need for them.

---

# Tech Stack

## Current

* Python
* FastAPI
* Pydantic
* Uvicorn
* JSON
* uv
* Git

## Planned

* PostgreSQL
* SQLAlchemy
* Alembic
* JWT authentication
* Password hashing
* Redis
* Background workers
* Task queues
* Pytest
* HTTPX
* Structured logging
* Docker
* Docker Compose

---

# Run Locally

## 1. Clone the repository

```bash
git clone <repository-url>
cd production-ai-job-backend
```

## 2. Install dependencies

```bash
uv sync
```

## 3. Start the development server

```bash
uv run fastapi dev main.py
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

# Interactive API Documentation

FastAPI automatically generates OpenAPI documentation.

## Swagger UI

```text
http://127.0.0.1:8000/docs
```

Swagger can currently be used to:

* inspect request schemas
* inspect response schemas
* create jobs
* retrieve jobs
* list jobs
* update statuses
* delete jobs
* observe HTTP status codes
* test validation failures

## ReDoc

```text
http://127.0.0.1:8000/redoc
```

---

# Development Roadmap

## Stage 1 — API Fundamentals

* [x] FastAPI application
* [x] GET endpoints
* [x] POST endpoints
* [x] PATCH endpoints
* [x] DELETE endpoints
* [x] Path parameters
* [x] Request bodies
* [x] HTTP status codes
* [x] Pydantic request validation
* [x] Response models
* [x] Nested response models
* [x] Basic error handling
* [x] OpenAPI / Swagger documentation

---

## Stage 2 — Job Management

* [x] Job creation
* [x] Generated job IDs
* [x] Persistent temporary storage
* [x] Retrieve job by ID
* [x] List all jobs
* [x] Update job status
* [x] Delete jobs
* [x] Job lifecycle validation
* [ ] Filtering
* [ ] Sorting
* [ ] Pagination

---

## Stage 3 — Clean Architecture

* [ ] APIRouter
* [ ] Modular application structure
* [ ] Schema separation
* [ ] Service layer
* [ ] Repository/data-access layer
* [ ] Central configuration
* [ ] Avoid giant application modules

---

## Stage 4 — PostgreSQL

* [ ] PostgreSQL integration
* [ ] SQLAlchemy models
* [ ] Database engine
* [ ] Database sessions
* [ ] CRUD operations
* [ ] Filtering
* [ ] Sorting
* [ ] Pagination
* [ ] Relationships
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

## Stage 6 — Authentication & Authorization

* [ ] User registration
* [ ] Password hashing
* [ ] Login
* [ ] JWT access tokens
* [ ] Token expiration
* [ ] Protected routes
* [ ] Current-user dependency
* [ ] Resource ownership
* [ ] Role-based permissions
* [ ] `401` vs `403`

---

## Stage 7 — AI/ML Job Workflow

* [ ] File uploads
* [ ] File validation
* [ ] File-to-job association
* [ ] Background processing
* [ ] Worker architecture
* [ ] Job lifecycle states
* [ ] Job results
* [ ] Failure tracking
* [ ] Retry-safe processing
* [ ] Idempotency

---

## Stage 8 — Production Engineering

* [ ] Environment-based configuration
* [ ] Logging
* [ ] Middleware
* [ ] Request IDs
* [ ] Redis
* [ ] Caching
* [ ] External API integration
* [ ] Async I/O
* [ ] Rate limiting
* [ ] Security improvements
* [ ] Retry handling

---

## Stage 9 — Testing

* [ ] Pytest setup
* [ ] API tests
* [ ] Unit tests
* [ ] Validation tests
* [ ] CRUD tests
* [ ] Failure-path tests
* [ ] Authentication tests
* [ ] Database tests
* [ ] Fixtures
* [ ] Mocked external services

---

## Stage 10 — Deployment Readiness

* [ ] Dockerfile
* [ ] Docker Compose
* [ ] FastAPI + PostgreSQL + Redis
* [ ] Environment variables
* [ ] Health/readiness checks
* [ ] CI pipeline
* [ ] Production deployment preparation

---

# Engineering Principles

This project follows several core engineering rules:

* **Build before over-engineering**
* Understand code before abstracting it
* Introduce architecture only when complexity justifies it
* Validate input at API boundaries
* Define explicit API response contracts
* Return meaningful HTTP status codes
* Keep resource behaviour predictable
* Persist important state outside process memory
* Treat failures as expected backend scenarios
* Keep code testable
* Never commit secrets
* Prefer clear engineering over unnecessary complexity

---

# What This Project Is Not

This is not intended to be a collection of unrelated FastAPI tutorial snippets.

It is one continuously evolving backend system.

The progression is intentional:

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
Clean Architecture
  ↓
PostgreSQL
  ↓
Authentication
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

---

# Learning Focus

The project is especially focused on backend engineering skills useful for:

* AI/ML applications
* Data Science platforms
* model-processing services
* document-processing systems
* RAG applications
* Applied AI products
* asynchronous job APIs
* ML inference and processing backends

The objective is not merely to memorize FastAPI syntax.

The goal is to become capable of independently:

* designing APIs
* defining request/response contracts
* validating input
* managing persistent state
* implementing CRUD behaviour
* selecting correct status codes
* debugging API failures
* handling errors
* structuring backend code
* testing endpoints
* reasoning about production failure scenarios

---

# Current Learning Milestone

The project has moved beyond simple FastAPI route demonstrations.

The current backend can now:

```text
Receive validated requests
        ↓
Create persistent jobs
        ↓
Generate resource IDs
        ↓
Expose typed responses
        ↓
Retrieve stored resources
        ↓
Update job state
        ↓
Reject invalid lifecycle values
        ↓
Delete resources
        ↓
Return meaningful HTTP errors
```

The next phase will gradually move the application from a single-file JSON-backed backend toward a **cleaner modular architecture and database-backed implementation**.

---

# Status

🚧 **Actively under development**

The backend is intentionally developed incrementally. Each new layer is introduced only after the previous concepts are implemented and understood.

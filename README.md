# Production AI Job Processing Backend

A progressively built, production-oriented **FastAPI backend for managing AI/ML processing jobs**.

This project is being developed using a **build-first backend engineering approach**. Instead of learning backend concepts as isolated theory, each concept is introduced by implementing it inside one continuously evolving backend system.

The project started as a small single-file FastAPI application and is gradually evolving into a modular, database-backed, tested, production-oriented backend suitable for AI/ML applications.

> **Current Status:** Modular FastAPI application with JSON-backed job CRUD, Pydantic request/response contracts, `APIRouter`-based routing, an initial service layer, lifecycle validation, HTTP error handling, and automatically generated OpenAPI documentation.

---

# Project Goal

Real AI/ML applications require much more than a trained model.

A production backend may need to:

* accept processing requests
* validate input
* create jobs
* track job status
* persist state
* upload files
* authenticate users
* authorize access
* execute long-running work
* process jobs in the background
* store results
* handle failures
* retry failed operations
* cache frequently accessed data
* expose reliable APIs
* run inside containers
* support production deployment

This project is designed to learn those backend engineering responsibilities by building them incrementally.

The AI/ML processing itself will initially remain lightweight so that the primary focus stays on:

* backend architecture
* API design
* persistence
* validation
* reliability
* testing
* failure handling
* maintainability
* production engineering

---

# Long-Term Architecture

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

---

# Current Features

The backend currently supports:

* FastAPI application setup
* Modular Python backend structure
* `APIRouter`-based job routing
* Root endpoint
* Health-check endpoint
* Job creation
* Job listing
* Individual job retrieval
* Job status updates
* Job deletion
* Generated job IDs
* Persistent JSON-based storage
* Pydantic request validation
* Pydantic response models
* Nested response models
* Typed collection responses
* Job lifecycle validation using `Literal`
* Initial service layer
* Separation of route and application logic
* Separation of persistence logic
* Automatic request validation
* Automatic response-model validation
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
├── services.py
├── schemas.py
├── storage.py
├── data.json
├── README.md
├── pyproject.toml
├── uv.lock
└── .gitignore
```

The project has intentionally evolved into this structure gradually rather than starting with unnecessary architectural complexity.

---

# Module Responsibilities

## `main.py`

The main application entry point.

Responsibilities:

* create the FastAPI application
* register routers
* expose the root endpoint
* expose the health-check endpoint

Conceptually:

```text
main.py
   │
   ├── FastAPI()
   ├── include_router(...)
   ├── GET /
   └── GET /health
```

Example application assembly:

```python
app = FastAPI()

app.include_router(router)
```

`app` is an instance of the `FastAPI` class and represents the running backend application.

---

## `routes.py`

Contains the HTTP-facing job endpoints.

Current job API:

```text
POST   /jobs
GET    /jobs
GET    /jobs/{job_id}
PATCH  /jobs/{job_id}
DELETE /jobs/{job_id}
```

The routes are grouped using FastAPI's `APIRouter`.

The route layer is responsible for HTTP concerns such as:

* receiving client requests
* receiving validated request models
* extracting path parameters
* calling service functions
* choosing HTTP responses
* raising `HTTPException`
* returning API responses

The goal is to keep routes thin instead of placing all application logic directly inside endpoint functions.

---

## `services.py`

Contains application-level job logic that should not depend directly on HTTP.

The service layer has started with functions for operations such as:

```text
get_job_by_id()
get_all_jobs()
create_job()
update_job_status()
delete_job_by_id()
```

Current responsibilities include:

* finding a job
* returning all jobs
* generating a new job ID
* constructing a new job
* assigning the initial status
* coordinating persistence for job creation

For example:

```text
routes.py
    ↓
create_job(job)
    ↓
services.py
    ↓
load existing data
generate ID
build job
persist job
return created job
```

The service layer does **not** decide HTTP status codes.

For example:

```text
services.py
job does not exist
→ return None

routes.py
receives None
→ return 404 Not Found
```

This separation makes application logic easier to reuse, test, and maintain.

---

## `schemas.py`

Contains Pydantic request and response contracts.

Current schemas include:

```text
JobCreate
JobResponse
JobActionResponse
JobUpdate
```

The schema layer answers:

> What should incoming and outgoing API data look like?

This keeps validation and API contracts separate from route and storage logic.

---

## `storage.py`

Contains low-level JSON persistence helpers.

Current responsibilities:

```text
load_data()
dump_data()
```

The storage layer handles:

```text
JSON file
    ↕
Python dictionary
```

It does not decide:

* HTTP status codes
* API response messages
* business rules

It only handles persistence.

---

## `data.json`

Temporary persistent storage for job records.

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

JSON storage is intentionally temporary and will later be replaced by PostgreSQL.

---

# Current Application Flow

The backend is gradually moving toward a layered flow:

```text
Client
  ↓
FastAPI Route
  ↓
Service Layer
  ↓
Storage Layer
  ↓
data.json
  ↓
Service Result
  ↓
Route
  ↓
Response Model
  ↓
Client
```

Each layer has a different responsibility:

```text
routes.py
→ understands HTTP

services.py
→ understands application operations

storage.py
→ understands persistence

schemas.py
→ understands data contracts
```

---

# Example: Retrieve a Job

Client request:

```http
GET /jobs/5
```

Flow:

```text
GET /jobs/5
      ↓
routes.py
      ↓
get_job_by_id(5)
      ↓
services.py
      ↓
load_data()
      ↓
storage.py
      ↓
data.json
      ↓
job dictionary or None
      ↓
routes.py
      ↓
200 OK or 404 Not Found
```

The service does not know what `404 Not Found` means.

That is an HTTP concern handled by the route layer.

---

# Example: Create a Job

Client sends:

```http
POST /jobs
```

Request:

```json
{
  "name": "Fraud detection training",
  "model_name": "fraud-detector-v1"
}
```

Flow:

```text
Client JSON
      ↓
JobCreate validation
      ↓
routes.py
      ↓
create_job(job)
      ↓
services.py
      ↓
load existing jobs
      ↓
generate next job_id
      ↓
construct new job
      ↓
set status = pending
      ↓
dump_data(...)
      ↓
return created job
      ↓
routes.py
      ↓
wrap response
      ↓
201 Created
```

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

# Create Job

```http
POST /jobs
```

## Request Body

```json
{
  "name": "Fraud detection training",
  "model_name": "fraud-detector-v1"
}
```

## Example Response

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

Every new job receives:

* a generated `job_id`
* the provided job name
* the selected model name
* initial status `pending`

---

# List All Jobs

```http
GET /jobs
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

The response contract is:

```python
dict[str, JobResponse]
```

Meaning:

```text
dictionary key
→ string job ID

dictionary value
→ validated JobResponse
```

If there are no jobs, an empty collection can be returned successfully rather than treating the collection itself as missing.

---

# Retrieve Job

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

Example:

```json
{
  "detail": "Job not found"
}
```

---

# Update Job Status

```http
PATCH /jobs/{job_id}
```

Example:

```http
PATCH /jobs/5
```

Request:

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

`PATCH` is appropriate because only part of the job resource is being modified.

---

# Delete Job

```http
DELETE /jobs/{job_id}
```

Current operation:

```text
load data
    ↓
verify job exists
    ↓
delete job
    ↓
persist modified data
    ↓
return success
```

If the job does not exist:

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

Valid:

```json
{
  "status": "running"
}
```

Invalid:

```json
{
  "status": "banana"
}
```

The invalid request is rejected automatically with:

```text
422 Unprocessable Entity
```

The route's update logic does not execute.

---

# Pydantic Schemas

## `JobCreate`

Defines the request body for creating a job.

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

Because `model_name` is missing, FastAPI/Pydantic rejects the request automatically.

---

## `JobResponse`

Defines the public representation of a job.

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

Reusable nested response model.

```python
class JobActionResponse(BaseModel):
    message: str
    job: JobResponse
```

Used by actions such as:

```text
POST  /jobs
PATCH /jobs/{job_id}
```

Example:

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

Defines the job status update contract.

```python
class JobUpdate(BaseModel):
    status: Literal[
        "pending",
        "running",
        "completed",
        "failed",
    ]
```

This moves status validation into the schema rather than manually validating allowed strings inside the route.

---

# Request vs Response Models

The API separates what the client sends from what the backend returns.

```text
Client
  ↓
Request Schema
  ↓
Route
  ↓
Service
  ↓
Application Logic
  ↓
Response Schema
  ↓
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

Response models are not only Swagger documentation.

They also provide an explicit contract for the structure returned by the API.

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

FastAPI rejects the request before the route logic executes.

---

## Invalid Job Status

Request:

```json
{
  "status": "banana"
}
```

Because the value does not match the allowed `Literal` values:

```text
422 Unprocessable Entity
```

---

## Missing Job

Example:

```http
GET /jobs/999
```

If the requested job does not exist:

```text
404 Not Found
```

This is handled at the route layer using FastAPI's:

```python
HTTPException
```

---

# Persistence

Jobs currently survive application restarts because they are written to:

```text
data.json
```

The storage layer uses:

```python
json.load(...)
```

for:

```text
JSON
 ↓
Python object
```

and:

```python
json.dump(...)
```

for:

```text
Python object
 ↓
JSON
```

---

# Current Mutation Flow

Operations that modify state follow:

```text
Load
  ↓
Validate
  ↓
Modify
  ↓
Persist
  ↓
Return
```

For example:

```text
POST /jobs
    ↓
load_data()
    ↓
generate ID
    ↓
construct job
    ↓
add job
    ↓
dump_data()
    ↓
return created job
```

---

# Why JSON Storage Is Temporary

JSON persistence is intentionally being used before PostgreSQL.

It makes important backend concepts visible:

* process memory vs persistent state
* serialization
* resource IDs
* CRUD operations
* state mutation
* persistence after restart
* missing-resource handling
* request/response contracts

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

# Limitations of JSON Storage

The current implementation is useful for learning but is **not intended as a production database**.

Important limitations include:

* unsafe concurrent writes
* race conditions
* lack of transactions
* possible corruption during failures
* inefficient large-scale querying
* no relational constraints
* no relationships
* no indexes
* weak filtering capabilities
* poor multi-process coordination

These limitations create the natural need for PostgreSQL later.

---

# Why the Application Was Split Into Modules

The project originally started with most code inside `main.py`.

Initial structure:

```text
main.py
├── schemas
├── JSON storage
├── job routes
├── health route
└── application setup
```

As responsibilities increased, they were gradually separated.

Evolution:

```text
main.py only
    ↓
schemas.py
    ↓
storage.py
    ↓
routes.py
    ↓
services.py
```

Current responsibility split:

```text
main.py
→ application assembly

routes.py
→ HTTP/API handling

services.py
→ application/business operations

schemas.py
→ validation and API contracts

storage.py
→ persistence operations

data.json
→ temporary persistent state
```

This is an incremental application of **separation of concerns**.

---

# Why a Service Layer?

A route should not eventually contain every step required to perform an operation.

Without a service layer, a future route could become:

```text
receive request
↓
check user
↓
check permissions
↓
check project
↓
validate file
↓
generate job ID
↓
create job
↓
save database row
↓
start worker
↓
log operation
↓
return response
```

That would make endpoint functions large and difficult to maintain.

The service layer allows routes to remain focused on HTTP.

Example:

```text
Route
↓
create_job(job)
↓
Service
↓
actual job creation logic
```

Simple mental model:

```text
Route
= client/API se baat karta hai

Service
= application ka actual kaam karta hai

Storage
= data read/write karta hai
```

---

# APIRouter

Job endpoints are grouped using FastAPI's `APIRouter`.

Conceptually:

```text
/jobs
  │
  ├── POST
  ├── GET
  │
  └── /{job_id}
         ├── GET
         ├── PATCH
         └── DELETE
```

The job router is registered with the main FastAPI application using:

```python
app.include_router(router)
```

This allows the application entry point to remain small while job-specific APIs remain grouped together.

---

# Current Tech Stack

## Backend

* Python
* FastAPI
* Pydantic
* Uvicorn

## Persistence

* JSON

## Project Tooling

* uv
* Git
* GitHub

---

# Planned Technologies

Future components will be introduced only when the project creates a genuine need for them.

Planned:

* PostgreSQL
* SQLAlchemy
* Alembic
* environment-based configuration
* password hashing
* JWT authentication
* Redis
* background processing
* task queues
* Pytest
* HTTPX
* Python logging
* Docker
* Docker Compose

---

# Running Locally

## 1. Clone Repository

```bash
git clone <repository-url>
cd production-ai-job-backend
```

## 2. Install Dependencies

```bash
uv sync
```

## 3. Run Development Server

```bash
uv run fastapi dev main.py
```

The API will normally be available at:

```text
http://127.0.0.1:8000
```

---

# API Documentation

FastAPI automatically generates OpenAPI documentation.

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
* test status codes
* test validation failures

## ReDoc

```text
http://127.0.0.1:8000/redoc
```

---

# Development Roadmap

## Stage 1 — FastAPI Fundamentals

* [x] FastAPI application
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
* [x] Swagger / OpenAPI documentation

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

## Stage 3 — Modular Backend Architecture

* [x] `APIRouter`
* [x] Route separation
* [x] Schema separation
* [x] Storage separation
* [x] Router registration
* [x] Initial service layer
* [x] Service-based job retrieval
* [x] Service-based job listing
* [x] Service-based job creation
* [x] Move PATCH logic into service layer
* [x] Move DELETE logic into service layer
* [ ] Repository/data-access layer
* [ ] Central configuration
* [ ] Application package structure
* [ ] Reusable dependencies

---

## Stage 4 — PostgreSQL

* [ ] PostgreSQL setup
* [ ] Database connection
* [ ] SQLAlchemy
* [ ] Engine
* [ ] Database sessions
* [ ] ORM models
* [ ] Inserts
* [ ] Queries
* [ ] Updates
* [ ] Deletes
* [ ] Filtering
* [ ] Sorting
* [ ] Pagination
* [ ] Foreign keys
* [ ] Relationships
* [ ] Unique constraints
* [ ] Transactions
* [ ] Indexes

---

## Stage 5 — Database Migrations

* [ ] Alembic
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
* [ ] Development settings
* [ ] Production settings
* [ ] Secret management

---

## Stage 7 — Authentication

* [ ] User model
* [ ] Registration
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

* [ ] `UploadFile`
* [ ] File uploads
* [ ] Extension validation
* [ ] Size limits
* [ ] Safe filenames
* [ ] File-to-job association
* [ ] Persistent storage strategy

---

## Stage 10 — Background Job Processing

* [ ] FastAPI background tasks
* [ ] Long-running processing
* [ ] Worker concept
* [ ] Task queue
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

---

## Stage 12 — Logging and Middleware

* [ ] Python logging
* [ ] Structured logging
* [ ] Exception logging
* [ ] Middleware
* [ ] Request timing
* [ ] Request IDs
* [ ] CORS

---

## Stage 13 — Testing

* [ ] Pytest
* [ ] FastAPI API tests
* [ ] Unit tests
* [ ] Integration tests
* [ ] Validation tests
* [ ] CRUD tests
* [ ] Failure-path tests
* [ ] Fixtures
* [ ] Test database
* [ ] Authentication tests
* [ ] Mocking

---

## Stage 14 — External APIs and Async

* [ ] HTTPX
* [ ] External API calls
* [ ] Timeouts
* [ ] Retries
* [ ] Error handling
* [ ] `async def`
* [ ] `await`
* [ ] Blocking vs non-blocking I/O

---

## Stage 15 — Security

* [ ] Password security
* [ ] Authentication
* [ ] Authorization
* [ ] Input validation
* [ ] Secret protection
* [ ] SQL injection awareness
* [ ] CORS configuration
* [ ] File upload security
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

## Build Before Over-Engineering

Architecture is introduced only when the project creates a real need for it.

## Understand Before Abstracting

Every abstraction should solve a problem that has already been observed.

## Keep Routes Thin

Routes should focus primarily on HTTP concerns rather than containing large amounts of application logic.

## Separate Responsibilities

Different parts of the backend should have clear responsibilities.

```text
routes
→ HTTP

services
→ application logic

schemas
→ contracts

storage
→ persistence
```

## Validate at Boundaries

Invalid client input should be rejected before reaching deeper application logic whenever practical.

## Explicit API Contracts

Request and response structures should be predictable.

## Persist Important State

State that must survive server restart should not live only in Python process memory.

## Treat Failure as Normal

Real backends must expect:

* malformed requests
* missing resources
* database failures
* API timeouts
* worker crashes
* retries
* partial failures

## Keep Code Testable

Architecture should gradually make individual components easier to test independently.

## Never Commit Secrets

API keys, database credentials, passwords, and other secrets must stay outside version control.

## Avoid Premature Complexity

A clean monolithic backend is preferable to unnecessary microservices or infrastructure that cannot be properly understood.

---

# Development Philosophy

The project is intentionally progressing through:

```text
Routes
  ↓
Validation
  ↓
CRUD
  ↓
Persistence
  ↓
Response Contracts
  ↓
Modular Structure
  ↓
Service Layer
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

Each new layer is introduced only after the previous layer has been implemented and understood.

---

# Current Learning Milestone

The project has progressed from a basic single-file FastAPI application into a small layered backend.

Current architecture:

```text
Validated Client Request
          ↓
       Route Layer
          ↓
      Service Layer
          ↓
      Storage Layer
          ↓
       data.json
          ↓
      Service Result
          ↓
       Route Layer
          ↓
 Response Model Validation
          ↓
         Client
```

The project currently demonstrates:

```text
Route
→ HTTP concerns

Service
→ application operations

Storage
→ persistence

Schema
→ request/response contracts
```

The next step is to move the remaining **PATCH and DELETE application logic into the service layer**, completing the initial route → service → storage separation before moving toward a database-backed architecture.

---

# Learning Focus

This project is especially relevant to backend engineering for:

* AI/ML applications
* Data Science platforms
* Applied AI systems
* model-processing services
* document-processing applications
* RAG systems
* ML inference APIs
* asynchronous AI workloads
* job-processing systems

The goal is not merely to memorize FastAPI syntax.

The objective is to become capable of independently:

* designing APIs
* creating request schemas
* creating response schemas
* validating input
* choosing HTTP methods
* selecting status codes
* implementing CRUD operations
* managing state
* designing modular backend code
* separating HTTP from application logic
* handling persistence
* debugging API failures
* building database-backed systems
* testing endpoints
* handling authentication
* integrating external services
* reasoning about concurrency
* containerizing services
* thinking about production failure scenarios

---

# Status

🚧 **Actively Under Development**

This backend is being developed incrementally with emphasis on understanding every major engineering decision rather than rapidly assembling a large framework-heavy application.

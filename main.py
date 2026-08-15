from fastapi import FastAPI, status
from pydantic import BaseModel


class JobCreate(BaseModel):
    name: str
    model_name: str


app = FastAPI()

jobs = []

@app.get("/")
def home():
    return {"message": "Welcome to FastAPI"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/jobs",status_code=status.HTTP_201_CREATED)
def create_jobs(job:JobCreate):
    prev = len(jobs)
    job_id = prev + 1
    
    message = {
        "job_id": job_id,
        "name": job.name,
        "model_name": job.model_name,
        "status": "pending"
    }
    
    jobs.append(message)
    
    return message 

@app.get("/jobs/{job_id}")
def get_job(job_id: int):
    return {
        "job_id":job_id,
        "status":"pending"
            }    
    
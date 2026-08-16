from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
import json


class JobCreate(BaseModel):
    name: str
    model_name: str


app = FastAPI()

def load_data():
    with open ("data.json","r") as file:
        data = json.load(file)
    return data  

def dump_data(data):
    with open("data.json","w") as file:
        json.dump(data,file) 
    
    
@app.get("/")
def home():
    return {"message": "Welcome to FastAPI"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/jobs",status_code=status.HTTP_201_CREATED)
def create_jobs(job:JobCreate):
    data = load_data()
    
    if not data:
        job_id = 1
    else:
        key = max(int(key) for key in data.keys())
        job_id = key + 1
     
    message = {
        "name": job.name,
        "model_name": job.model_name,
        "status": "pending"
    }
    
    data[str(job_id)] = message
    
    dump_data(data)
    
    return {
    "message": "Job created successfully",
    "job": message
}

@app.get("/jobs/{job_id}",status_code = status.HTTP_200_OK)
def get_job(job_id: int):
    data = load_data()
    
    if str(job_id) in data:
        return data[str(job_id)]
      
    
    raise HTTPException(
        detail="Job not found",
        status_code = status.HTTP_404_NOT_FOUND
    )      
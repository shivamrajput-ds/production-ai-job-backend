from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
import json


class JobCreate(BaseModel):
    name: str
    model_name: str
    
class JobUpdate(BaseModel):
    status: str        


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
        "job_id":job_id,
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
    
@app.get("/jobs")
def get_jobs():
    data = load_data()
    return data    

@app.get("/jobs/{job_id}",status_code = status.HTTP_200_OK)
def get_job(job_id: int):
    data = load_data()
    
    if str(job_id) in data:
        return data[str(job_id)]
      
    
    raise HTTPException(
        detail="Job not found",
        status_code = status.HTTP_404_NOT_FOUND
    )    

@app.delete("/jobs/{job_id}")
def delete_job(job_id: int):
    data = load_data()

    if str(job_id) in data:
        del data[str(job_id)]
    else:
        raise HTTPException(
            detail="Id Not Found",
            status_code=status.HTTP_404_NOT_FOUND
        )

    dump_data(data)

    return {"message": "Succesfully Deleted"}    

@app.patch("/jobs/{job_id}")
def update_status(job_id:int,x: JobUpdate):
    data = load_data()
    valid = {"pending","running","completed","failed"}
    message = None
    
    if str(job_id) in data:
        if x.status in valid:
            data[str(job_id)]["status"] = x.status
            message = data[str(job_id)]
            
        else:
            raise HTTPException(
                        detail="Please Enter valid Status",
                        status_code=status.HTTP_400_BAD_REQUEST
                        )          
    else:
        raise HTTPException(
            detail="Id Not Found",
            status_code=status.HTTP_404_NOT_FOUND
            )
    
    dump_data(data)
    
    return {
  "message": "Job updated successfully",
  "job": message
}
    
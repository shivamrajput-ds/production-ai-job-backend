from fastapi import APIRouter, status, HTTPException

from typing import Dict

from schemas import JobCreate, JobResponse, JobUpdate, JobActionResponse
from storage import load_data, dump_data   

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)
@router.post("/",status_code=status.HTTP_201_CREATED,response_model= JobActionResponse)
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
    
@router.get("/",response_model= Dict[str,JobResponse])
def get_jobs():
    data = load_data()
    return data    

@router.get("/{job_id}",status_code = status.HTTP_200_OK,response_model = JobResponse)
def get_job(job_id: int):
    data = load_data()
    
    if str(job_id) in data:
        return data[str(job_id)]
      
    
    raise HTTPException(
        detail="Job not found",
        status_code = status.HTTP_404_NOT_FOUND
    )    

@router.delete("/{job_id}")
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

@router.patch("/{job_id}", response_model=JobActionResponse)
def update_status(job_id: int, x: JobUpdate):
    data = load_data()

    if str(job_id) in data:
        data[str(job_id)]["status"] = x.status
        message = data[str(job_id)]

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
    
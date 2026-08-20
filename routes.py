from fastapi import APIRouter, status, HTTPException

from typing import Dict

from schemas import JobCreate, JobResponse, JobUpdate, JobActionResponse
from storage import load_data, dump_data   
from services import get_job_by_id,get_all_jobs,create_job

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)
@router.post("/",status_code=status.HTTP_201_CREATED,response_model= JobActionResponse)
def create_jobs(job:JobCreate):
    message = create_job(job)
    return {"message":"Job Created Succesfully",
            "job":message}
        
    
@router.get("/",response_model= Dict[str,JobResponse],status_code = status.HTTP_200_OK)
def get_jobs():
    data = get_all_jobs()
    return data
    

@router.get("/{job_id}",status_code = status.HTTP_200_OK,response_model = JobResponse)
def get_job(job_id:int):
    job = get_job_by_id(job_id)
    if job is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail="Job Not Found")
    return job
    
      

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
    
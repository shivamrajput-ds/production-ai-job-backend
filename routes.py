from fastapi import APIRouter, status, HTTPException

from typing import Dict

from schemas import JobCreate, JobResponse, JobUpdate, JobActionResponse
from services import get_job_by_id,get_all_jobs,create_job,update_job_status,delete_job_by_id
from typing import Literal

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
def get_jobs(status: Literal["pending", "running", "completed", "failed"] | None = None)-> dict:
    data = get_all_jobs(status)
    return data
    

@router.get("/{job_id}",status_code = status.HTTP_200_OK,response_model = JobResponse)
def get_job(job_id:int):
    job = get_job_by_id(job_id)
    if job is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail="Job Not Found")
    return job
    
      

@router.delete("/{job_id}",status_code = status.HTTP_200_OK)
def delete_job(job_id: int):
    if delete_job_by_id(job_id):
        return {"message":"Successfully Deleted ID"}
    else:
        raise HTTPException(
            detail ="Job Id Not Found",
            status_code = status.HTTP_404_NOT_FOUND
        )

@router.patch("/{job_id}", response_model=JobActionResponse,status_code = status.HTTP_200_OK)
def update_status(job_id: int, x: JobUpdate):
    Updated_data = update_job_status(job_id,x.status)
    if not Updated_data:
        raise HTTPException(
            detail = "Job ID Not Found",
            status_code= status.HTTP_404_NOT_FOUND       
        )
    else:
        return {"message" : "Successfully Updated",
                "job": Updated_data
                }    
        
    
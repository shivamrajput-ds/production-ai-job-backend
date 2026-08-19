from pydantic import BaseModel
from typing import Literal

class JobCreate(BaseModel):
    name: str
    model_name: str
    
class JobResponse(BaseModel):
    job_id: int
    name: str
    model_name: str
    status: str  
       

class JobActionResponse(BaseModel):
    message: str
    job: JobResponse
    
class JobUpdate(BaseModel):
    status: Literal["pending", "running", "completed", "failed"]       

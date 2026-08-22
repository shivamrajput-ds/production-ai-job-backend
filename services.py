from storage import load_data,dump_data
from schemas import JobCreate

def create_job(job:JobCreate)-> dict:
    data = load_data()
        
    if not data:
        job_id = 1
    else:
        key = max(int(key) for key in data.keys())
        job_id = key + 1
    
    created_job = {
        "job_id":job_id,
        "name": job.name,
        "model_name": job.model_name,
        "status": "pending"
    }
    
    data[str(job_id)] = created_job
    
    dump_data(data)
    
    return created_job

def get_job_by_id(job_id: int)-> dict | None:
    data = load_data()
    
    if str(job_id) in data:
        return data[str(job_id)]
    return None    
    
def get_all_jobs(status : str | None = None)-> dict:
    data = load_data()
    if status is None:
        return data
    else:
        res = {}
        for key,val in data.items():
            if val["status"] ==  status:
                res[key] = val
        
        return res        
        
         
    
    


def update_job_status(job_id:int,new_status:str)-> dict | None:
    data = load_data()
    
    if str(job_id) in data:
        data[str(job_id)]["status"] = new_status
        updated_job = data[str(job_id)]
        dump_data(data)
        return updated_job
    
    return None  
    
def delete_job_by_id(job_id: int)-> bool:
    data = load_data() 
    if str(job_id) in data:
        del data[str(job_id)]
        dump_data(data)
        return True
    
    return False


    



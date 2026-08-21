from storage import load_data,dump_data
from schemas import JobCreate,JobUpdate

def create_job(job:JobCreate):
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
    
    return message

def get_job_by_id(job_id: int):
    data = load_data()
    
    if str(job_id) in data:
        return data[str(job_id)]
    return None    
    
def get_all_jobs():
    data = load_data()   
    return data 


def update_job_status(job_id:int,new_status:str):
    data = load_data()
    
    if str(job_id) in data:
        data[str(job_id)]["status"] = new_status
        updated_data = data[str(job_id)]
        dump_data(data)
        return updated_data
    
    return False    
    
def delete_job_by_id(job_id: int):
    data = load_data() 
    if str(job_id) in data:
        del data[str(job_id)]
        dump_data(data)
        return True
    
    return False


    



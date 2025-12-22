import random
import json
from typing import Dict

def generate_instance(num_jobs: int, num_machines: int, num_resources: int, 
                      max_duration: int = 10, max_resource_qty: int = 5,
                      resource_capacity_factor: float = 1.5) -> Dict:
    """
    Generates a random problem instance.
    :param resource_capacity_factor: Multiplier for resource capacity relative to average demand.
    """
    
    # 1. Define Resources and Capacities
    resources = {}
    for r in range(1, num_resources + 1):
        # Allow some capacity, maybe proportional to number of machines?
        # If we have M machines, max demand at once could be M * max_req
        # Let's set capacity to something ensuring contention but not impossibility
        # Capacity = random between max_resource_qty and M * max_resource_qty
        cap = random.randint(max_resource_qty, int(max_resource_qty * num_machines * 0.8) + 1)
        resources[str(r)] = cap

    # 2. Generate Jobs
    jobs = []
    for j in range(1, num_jobs + 1):
        duration = random.randint(1, max_duration)
        requirements = {}
        
        # Each job needs some subset of resources
        num_reqs = random.randint(0, num_resources) # 0 means no specialized tools needed
        if num_reqs > 0:
            req_resources = random.sample(range(1, num_resources + 1), num_reqs)
            for r in req_resources:
                # Requirement must be <= capacity
                max_allowed = resources[str(r)]
                # Req is random between 1 and min(max_resource_qty, max_allowed)
                qty = random.randint(1, min(max_resource_qty, max_allowed))
                requirements[str(r)] = qty
                
        jobs.append({
            "id": j,
            "duration": duration,
            "requirements": requirements
        })

    data = {
        "num_machines": num_machines,
        "resources": resources,
        "jobs": jobs
    }
    return data

def save_instance(data: Dict, filename: str):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

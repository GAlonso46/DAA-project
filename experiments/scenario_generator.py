import random
from typing import List, Dict, Any



def generate_bottleneck(num_instances: int) -> List[tuple]:
    """
    Resource Bottleneck (Mini):
    6 jobs, 1 resource with capacity 2. 5 machines.
    All jobs require the resource.
    """
    instances = []
    for i in range(num_instances):
        jobs = []
        for j in range(1, 7):
            jobs.append({
                "id": j,
                "duration": random.randint(6, 15),
                "requirements": {"CommonTool": 1}
            })
        
        data = {
            "num_machines": 5,
            "resources": {"CommonTool": 2},
            "jobs": jobs
        }
        instances.append((f"bottleneck_gen_{i+1}", data))
    return instances

def generate_high_contention(num_instances: int) -> List[tuple]:
    """
    High Contention (Mini):
    Chain of dependencies. 6 jobs. 5 machines.
    J_i needs R_i and R_{i+1}.
    """
    instances = []
    for i in range(num_instances):
        jobs = []
        # Create 6 resources
        resources = {f"R{r}": 1 for r in range(1, 7)}
        
        for j in range(1, 7):
            if j < 6:
                reqs = {f"R{j}": 1, f"R{j+1}": 1}
            else:
                 reqs = {f"R{j}": 1, f"R{j-1}": 1} # Matches R6, R5
            
            jobs.append({
                "id": j,
                "duration": random.randint(8, 12),
                "requirements": reqs
            })
            
        data = {
            "num_machines": 5,
            "resources": resources,
            "jobs": jobs
        }
        instances.append((f"high_contention_gen_{i+1}", data))
    return instances

def generate_rock_sand(num_instances: int) -> List[tuple]:
    """
    The Rock & Sand (Mini):
    1 Long job (Rock) with resource.
    5 Short jobs (Sand) without resource.
    5 Machines.
    """
    instances = []
    for i in range(num_instances):
        jobs = []
        # The Rock
        jobs.append({
            "id": 1,
            "duration": random.randint(90, 110), 
            "requirements": {"HeavyTool": 1}
        })
        # The Sand
        for j in range(2, 7):
            jobs.append({
                "id": j,
                "duration": random.randint(3, 7),
                "requirements": {}
            })
            
        data = {
            "num_machines": 5,
            "resources": {"HeavyTool": 1},
            "jobs": jobs
        }
        instances.append((f"rock_sand_gen_{i+1}", data))
    return instances

def generate_irrelevant(num_instances: int) -> List[tuple]:
    """
    Irrelevant Resources (Mini):
    Capacity (5) == Machines (5).
    6 Jobs, all need resource.
    """
    instances = []
    for i in range(num_instances):
        jobs = []
        for j in range(1, 7):
            jobs.append({
                "id": j,
                "duration": random.randint(14, 25),
                "requirements": {"BasicTool": 1}
            })
            
        data = {
            "num_machines": 5,
            "resources": {"BasicTool": 5},
            "jobs": jobs
        }
        instances.append((f"irrelevant_gen_{i+1}", data))
    return instances

def generate_greedy_killer(num_instances: int) -> List[tuple]:
    """
    Greedy Killer (Mini):
    2 Machines.
    Jobs 1-3: Short, need CriticalTool.
    Job 4: Long, free.
    Jobs 5-6: Tiny, free.
    """
    instances = []
    for i in range(num_instances):
        jobs = []
        # 1-3: Duration ~5, need tool
        for j in range(1, 4):
            jobs.append({
                "id": j,
                "duration": random.randint(4, 6), 
                "requirements": {"CriticalTool": 1}
            })
        
        # 4: Duration ~25, free
        jobs.append({
            "id": 4,
            "duration": random.randint(23, 27), 
            "requirements": {}
        })
        
        # 5-6: Duration ~1, free
        for j in range(5, 7):
            jobs.append({
                "id": j,
                "duration": 1, 
                "requirements": {}
            })
            
        data = {
            "num_machines": 2,
            "resources": {"CriticalTool": 1},
            "jobs": jobs
        }
        instances.append((f"greedy_killer_gen_{i+1}", data))
    return instances

def generate_all_scenarios(num_per_type: int = 1) -> List[tuple]:
    """Generate all scenario types."""
    all_instances = []
    all_instances.extend(generate_bottleneck(num_per_type))
    all_instances.extend(generate_high_contention(num_per_type))
    all_instances.extend(generate_rock_sand(num_per_type))
    all_instances.extend(generate_irrelevant(num_per_type))
    all_instances.extend(generate_greedy_killer(num_per_type))
    return all_instances

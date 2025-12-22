from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Job:
    id: int
    duration: int
    resource_requirements: Dict[int, int]  # Resource ID -> Quantity required
    start_time: Optional[int] = None
    assigned_machine: Optional[int] = None

@dataclass
class Solution:
    jobs: List[Job]
    makespan: int = 0
    valid: bool = True

class ProblemInstance:
    def __init__(self, num_machines: int, resources: Dict[int, int], jobs: List[Job]):
        """
        :param num_machines: Number of identical machines (m)
        :param resources: Dictionary Resource ID -> Total Capacity (Q_k)
        :param jobs: List of Job objects
        """
        self.num_machines = num_machines
        self.resources = resources
        self.jobs = jobs

    def validate_solution(self, solution: Solution) -> bool:
        # 1. Check if all jobs are assigned
        for job in solution.jobs:
            if job.start_time is None or job.assigned_machine is None:
                print(f"Job {job.id} not assigned.")
                return False

        # 2. Check machine overlap
        machine_schedules = {i: [] for i in range(1, self.num_machines + 1)}
        for job in solution.jobs:
            machine_schedules[job.assigned_machine].append((job.start_time, job.start_time + job.duration))
        
        for m_id, intervals in machine_schedules.items():
            intervals.sort()
            for i in range(len(intervals) - 1):
                if intervals[i][1] > intervals[i+1][0]:
                    print(f"Overlap on machine {m_id}")
                    return False

        # 3. Check resource availability at every time step
        # This is a discrete time check. For optimization, we only check start/end events, but brute force is ok for now.
        max_time = solution.makespan
        for t in range(max_time + 1):
            current_usage = {r_id: 0 for r_id in self.resources}
            for job in solution.jobs:
                if job.start_time <= t < job.start_time + job.duration:
                    for r_id, qty in job.resource_requirements.items():
                        current_usage[r_id] += qty
            
            for r_id, capacity in self.resources.items():
                if current_usage[r_id] > capacity:
                    print(f"Resource {r_id} violation at time {t}. Used {current_usage[r_id]}, Cap {capacity}")
                    return False
        
        return True

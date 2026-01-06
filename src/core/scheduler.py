from typing import List, Dict, Tuple
from src.core.model import Job, Solution, ProblemInstance

class SolutionBuilder:
    """
    Centralized logic for building a schedule from a sequence of jobs.
    Implements Event-Based Time optimization to avoid t+=1 bottleneck.
    """
    def __init__(self, problem: ProblemInstance):
        self.problem = problem

    def build_from_sequence(self, sequence: List[Job]) -> Solution:
        """
        Constructs a schedule by assigning jobs in the given order 
        to the earliest available feasible slot.
        """
        # Machine availability times (when does each machine become free?)
        machine_free_time = {i: 0 for i in range(1, self.problem.num_machines + 1)}
        
        # Resource availability tracking
        # We need to track strictly when resources are used.
        # Since we use Event-Based Time, we can just query a usage map.
        resource_timeline = {} # t -> {r_id -> qty}

        solution_jobs = []
        global_makespan = 0
        
        # We start with 0 as a candidate time
        # Completion times of scheduled jobs will be added to this set
        completion_times = {0} 

        for job in sequence:
            # Clone job to avoid side effects on the original object in multiple runs
            job_node = Job(
                id=job.id,
                duration=job.duration,
                resource_requirements=job.resource_requirements
            )
            
            best_machine = -1
            best_start_time = float('inf')
            
            # Find earliest slot across all machines
            # We check candidate start times.
            # A valid start time is likely to be:
            # 1. When a machine becomes free
            # 2. When a resource is released (which is a job completion time)
            
            # Optimization: 
            # We only need to check time points >= machine_free_time[m]
            # that match a completion_time (or the machine_free_time itself).
            
            # Collect all relevant time points
            # 1. Current free times of machines are critical candidates
            # (already implicitly in completion_times if we update it correctly, 
            # but let's be explicit)
            
            current_candidates = sorted([t for t in completion_times])
            
            possible_starts = []
            
            for m_id in range(1, self.problem.num_machines + 1):
                m_free = machine_free_time[m_id]
                
                # Filter candidates: must be >= machine availability
                # And we also add m_free as a candidate itself if not present
                valid_candidates = [t for t in current_candidates if t >= m_free]
                if m_free not in completion_times:
                     # This handles case where machine free time is not a job end (e.g. t=0)
                     # Or if we want to be safe, just add m_free to the check list
                     valid_candidates.insert(0, m_free)
                     valid_candidates.sort()

                # Find first valid time 
                found_t = -1
                for t in valid_candidates:
                     if self._check_resources(t, job_node.duration, job_node.resource_requirements, resource_timeline):
                         found_t = t
                         break
                
                # Fallback: if no existing candidate works (unlikely if we track all ends), 
                # strictly speaking, resources become free at completion times.
                # So if it doesn't fit at any completion time, it won't fit in between 
                # (unless duration is 0, but duration >= 1).
                # Actually, resource usage is constant intervals [S, E).
                # Availability changes ONLY at S and E.
                # Since we want to START, we look for a time T such that for [T, T+dur), R is ok.
                # If R is not ok at T, it means some overlapping job is using it.
                # We only need to check T when some job ends.
                
                if found_t != -1:
                    possible_starts.append((found_t, m_id))

            # Si no encontramos ningún start entre los completion_times, hacemos fallback
            if not possible_starts:
                # Limite superior razonable: último completion + suma de duraciones pendientes
                sorted_ct = sorted(completion_times)
                last_ct = sorted_ct[-1] if sorted_ct else 0
                remaining_horizon = last_ct + sum(j.duration for j in sequence)
                for m_id in range(1, self.problem.num_machines + 1):
                    m_free = machine_free_time[m_id]
                    t0 = max(m_free, 0)
                    # probeando tiempos desde t0 hasta remaining_horizon
                    for t_candidate in range(t0, remaining_horizon + 1):
                        if self._check_resources(t_candidate, job_node.duration, job_node.resource_requirements, resource_timeline):
                            possible_starts.append((t_candidate, m_id))
                            break    
            
            # Pick best machine (earliest start)
            possible_starts.sort()
            start_t, m_id = possible_starts[0]
            
            # Assign
            job_node.start_time = start_t
            job_node.assigned_machine = m_id
            solution_jobs.append(job_node)
            
            finish_t = start_t + job_node.duration
            machine_free_time[m_id] = finish_t
            global_makespan = max(global_makespan, finish_t)
            
            # Update structures
            completion_times.add(finish_t)
            self._mark_resources_used(start_t, finish_t, job_node.resource_requirements, resource_timeline)
            
        return Solution(jobs=solution_jobs, makespan=global_makespan)

    def _check_resources(self, start: int, duration: int, requirements: Dict[int, int], timeline: Dict) -> bool:
        # Check every time unit? 
        # CAUTION: If we jump large gaps, checking every unit is still slow (O(Duration)).
        # But we can optimize: resources change state only at keys of 'timeline'?
        # In this simple implementation 'timeline' is still discrete t -> usage.
        # To truly optimize, we should check intervals.
        # But given the problem constraints (Machine Scheduling usually short to medium horizon), 
        # and User feedback "skip to next release", the big gain is NOT checking start times 1,2,3,4... 
        # but jumping t=10, t=50.
        # Once we pick a candidate T, checking [T, T+dur] linearly is acceptable if Dur is not massive.
        # If Dur is massive, we need Segment Tree.
        # Let's keep linear check over duration for now, as User emphasized "Time Jumping" for the SEARCH loop.
        
        for t in range(start, start + duration):
            # If t not in timeline, usage is 0.
            # Only check if t in timeline to save dict lookups
            if t in timeline: # Optimization
                t_usage = timeline[t]
                for r_id, req_qty in requirements.items():
                    used = t_usage.get(r_id, 0)
                    if used + req_qty > self.problem.resources.get(r_id, 0):
                        return False
        return True

    def _mark_resources_used(self, start: int, end: int, requirements: Dict[int, int], timeline: Dict):
        for t in range(start, end):
            if t not in timeline:
                timeline[t] = {}
            for r_id, qty in requirements.items():
                timeline[t][r_id] = timeline[t].get(r_id, 0) + qty

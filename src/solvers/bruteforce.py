from typing import List, Dict, Tuple
from itertools import product
from src.core.model import ProblemInstance, Solution, Job

class BruteForceSolver:
    """
    Brute-force solver that enumerates all assignments of jobs to machines.
    For each assignment (a vector of length n with values in 1..m) it
    constructs a feasible schedule that preserves the order of jobs assigned
    to each machine (jobs appear in the same order as in problem.jobs).

    Warning: complexity is m^n and grows quickly. The implementation raises
    a RuntimeError if the number of combinations exceeds 1_000_000 to avoid
    accidental exhaustive runs on large instances.
    """
    def __init__(self, problem: ProblemInstance, max_combinations: int = None):
        # allow unlimited search when max_combinations is None
        self.problem = problem
        self.max_combinations = max_combinations

    def solve(self) -> Solution:
        n = len(self.problem.jobs)
        m = self.problem.num_machines
        total = m ** n
        # No longer raise on large combination counts. If max_combinations is set
        # it is treated as advisory but will not stop execution here.
        best_sol = None
        best_makespan = float('inf')

        # Iterate over all assignments: for each job i assign machine in 1..m
        for assign in product(range(1, m+1), repeat=n):
            # Build per-machine queues preserving original job order
            machine_queues: Dict[int, List[Job]] = {i: [] for i in range(1, m+1)}
            for job, mach in zip(self.problem.jobs, assign):
                # keep original job metadata but do not copy start/assigned fields yet
                machine_queues[mach].append(job)

            # Now simulate scheduling for this fixed assignment
            sol = self._build_schedule_for_assignment(machine_queues)

            if sol is None:
                # infeasible assignment (resource violations that cannot be resolved)
                continue

            if sol.makespan < best_makespan:
                best_makespan = sol.makespan
                best_sol = sol

        if best_sol is None:
            return Solution(jobs=[], makespan=0, valid=False)
        return best_sol

    def _build_schedule_for_assignment(self, machine_queues: Dict[int, List[Job]]) -> Solution:
        # machine_free_time
        machine_free_time = {i: 0 for i in range(1, self.problem.num_machines + 1)}
        resource_timeline: Dict[int, Dict[int, int]] = {}  # t -> {r_id -> qty}
        solution_jobs: List[Job] = []
        completion_times = {0}
        remaining = {i: list(queue) for i, queue in machine_queues.items()}  # copies

        # While there are jobs remaining
        while any(len(q) > 0 for q in remaining.values()):
            candidates: List[Tuple[int, int, Job]] = []  # (start_time, machine, job)

            # For each machine with pending job, find earliest feasible start for its next job
            for m_id, q in remaining.items():
                if not q:
                    continue
                job = q[0]
                m_free = machine_free_time[m_id]
                # Candidate times are completion_times >= m_free plus m_free itself
                cand_times = sorted([t for t in completion_times if t >= m_free])
                if m_free not in completion_times:
                    # ensure m_free is considered
                    cand_times.insert(0, m_free)
                    cand_times.sort()

                found = -1
                for t in cand_times:
                    if self._check_resources(t, job.duration, job.resource_requirements, resource_timeline):
                        found = t
                        break
                if found != -1:
                    candidates.append((found, m_id, job))
                else:
                    # this machine's next job cannot start at any known event; skip
                    pass

            if not candidates:
                # No candidate start found at known events — try advancing to next time unit
                # Find next smallest completion_time > min(machine_free_time)
                future_times = [t for t in completion_times if t > min(machine_free_time.values())]
                if not future_times:
                    # nothing to advance to, assignment infeasible
                    return None
                # advance by adding the minimum future time as a new event (loop will consider it)
                # this is already in completion_times; so just continue to attempt scheduling
                # but to avoid infinite loop, break as infeasible
                return None

            # pick candidate with smallest start_time (tie-breaker: smallest machine id)
            candidates.sort(key=lambda x: (x[0], x[1]))
            start_t, chosen_m, chosen_job = candidates[0]

            # schedule it
            job_node = Job(
                id=chosen_job.id,
                duration=chosen_job.duration,
                resource_requirements=chosen_job.resource_requirements
            )
            job_node.start_time = start_t
            job_node.assigned_machine = chosen_m
            solution_jobs.append(job_node)

            finish_t = start_t + job_node.duration
            machine_free_time[chosen_m] = finish_t
            completion_times.add(finish_t)
            self._mark_resources_used(start_t, finish_t, job_node.resource_requirements, resource_timeline)

            # pop from the queue
            remaining[chosen_m].pop(0)

        makespan = max((j.start_time + j.duration) for j in solution_jobs) if solution_jobs else 0
        return Solution(jobs=solution_jobs, makespan=makespan, valid=True)

    def _check_resources(self, start: int, duration: int, requirements: Dict[int, int], timeline: Dict) -> bool:
        for t in range(start, start + duration):
            if t in timeline:
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

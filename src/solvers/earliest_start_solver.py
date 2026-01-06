from typing import List, Dict, Tuple, Optional
from src.core.model import ProblemInstance, Solution, Job
from src.core.scheduler import SolutionBuilder

class EarliestStartSolver:
    """
    Solver that iteratively places the job that can start at the earliest time among
    all not-yet-assigned jobs. Ties are broken arbitrarily (first encountered).

    Algorithm (per iteration):
    - For each unassigned job compute its earliest feasible (start_time, machine)
      using event-based candidate times (completion times and machine free times)
      and a small fallback search up to the latest machine-free time.
    - Select the job with minimal earliest start and place it; update data structures.
    - Repeat until all jobs are assigned.
    """

    def __init__(self, problem: ProblemInstance):
        self.problem = problem
        self.builder = SolutionBuilder(problem)

    def solve(self) -> Solution:
        # state similar to SolutionBuilder.build_from_sequence
        machine_free_time: Dict[int, int] = {i: 0 for i in range(1, self.problem.num_machines + 1)}
        resource_timeline: Dict[int, Dict] = {}  # t -> {r_id -> qty}
        completion_times = {0}

        unassigned: List[Job] = [job for job in self.problem.jobs]
        assigned_jobs: List[Job] = []
        global_makespan = 0

        # Quick feasibility check: any job requiring more than capacity -> impossible
        for job in unassigned:
            for r_id, qty in job.resource_requirements.items():
                cap = self.problem.resources.get(r_id, 0)
                if qty > cap:
                    raise ValueError(f"Job {job.id} requires {qty} of resource {r_id}, but capacity is {cap}.")

        while unassigned:
            # For each unassigned job, compute earliest feasible (start, machine).
            earliest_for_job: List[Tuple[int, int, Job]] = []  # (start_time, machine_id, job)

            current_candidates = sorted(list(completion_times))
            latest_machine_free = max(machine_free_time.values())

            for job in unassigned:
                found_pair: Optional[Tuple[int, int]] = None

                # Try event-based candidates for each machine
                best_start_for_this_job = None
                best_machine_for_this_job = None

                for m_id in range(1, self.problem.num_machines + 1):
                    m_free = machine_free_time[m_id]
                    valid_candidates = [t for t in current_candidates if t >= m_free]
                    if m_free not in current_candidates:
                        # ensure we try starting at machine free time as well
                        valid_candidates.insert(0, m_free)
                        valid_candidates.sort()

                    found_t = -1
                    for t in valid_candidates:
                        if self.builder._check_resources(t, job.duration, job.resource_requirements, resource_timeline):
                            found_t = t
                            break

                    # fallback: scan forward until latest_machine_free (inclusive)
                    if found_t == -1:
                        t0 = max(m_free, 0)
                        for t_candidate in range(t0, latest_machine_free + 1):
                            if self.builder._check_resources(t_candidate, job.duration, job.resource_requirements, resource_timeline):
                                found_t = t_candidate
                                break

                    if found_t != -1:
                        if best_start_for_this_job is None or found_t < best_start_for_this_job:
                            best_start_for_this_job = found_t
                            best_machine_for_this_job = m_id

                if best_start_for_this_job is not None:
                    earliest_for_job.append((best_start_for_this_job, best_machine_for_this_job, job))
                else:
                    # Shouldn't happen because latest_machine_free is a safe upper bound
                    raise RuntimeError(f"No feasible start found for job {job.id} within considered horizon.")

            # Choose job with minimal earliest start (ties: first found)
            earliest_for_job.sort(key=lambda x: x[0])
            start_t, chosen_m, chosen_job = earliest_for_job[0]

            # Assign chosen job
            job_node = Job(
                id=chosen_job.id,
                duration=chosen_job.duration,
                resource_requirements=chosen_job.resource_requirements
            )
            job_node.start_time = start_t
            job_node.assigned_machine = chosen_m

            assigned_jobs.append(job_node)
            finish_t = start_t + job_node.duration
            machine_free_time[chosen_m] = finish_t
            global_makespan = max(global_makespan, finish_t)

            completion_times.add(finish_t)
            self.builder._mark_resources_used(start_t, finish_t, job_node.resource_requirements, resource_timeline)

            # remove from unassigned
            unassigned = [j for j in unassigned if j.id != chosen_job.id]

        return Solution(jobs=assigned_jobs, makespan=global_makespan)

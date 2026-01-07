from typing import List, Dict, Tuple, Generator
from itertools import permutations
from src.core.model import ProblemInstance, Solution, Job

class BruteForceSolver:
    def __init__(self, problem: ProblemInstance, max_combinations: int = None):
        self.problem = problem
        self.max_combinations = max_combinations

    def solve(self) -> Solution:
        n = len(self.problem.jobs)
        m = self.problem.num_machines
        
        best_sol = None
        best_makespan = float('inf')

        # 1. Permutamos el orden de los trabajos (n!)
        for job_order in permutations(self.problem.jobs):
            
            # 2. Generamos solo asignaciones ÚNICAS de máquinas (evitando simetría)
            for assign in self._get_unique_assignments(n, m):
                
                machine_queues: Dict[int, List[Job]] = {i: [] for i in range(1, m + 1)}
                
                # Asignamos trabajos a máquinas según la partición generada
                for job, mach in zip(job_order, assign):
                    machine_queues[mach].append(job)

                sol = self._build_schedule_for_assignment(machine_queues)

                if sol is None:
                    continue

                if sol.makespan < best_makespan:
                    best_makespan = sol.makespan
                    best_sol = sol

        if best_sol is None:
            return Solution(jobs=[], makespan=0, valid=False)
        return best_sol

    def _get_unique_assignments(self, n: int, m: int) -> Generator[Tuple[int, ...], None, None]:
        """
        Genera asignaciones de n trabajos a m máquinas idénticas evitando simetrías.
        Utiliza una técnica de backtracking para generar particiones de un conjunto.
        """
        def backtrack(current_assignment: List[int], max_machine_used: int):
            if len(current_assignment) == n:
                yield tuple(current_assignment)
                return

            # Opción A: Asignar a cualquiera de las máquinas ya "abiertas"
            for i in range(1, max_machine_used + 1):
                yield from backtrack(current_assignment + [i], max_machine_used)
            
            # Opción B: Abrir una máquina nueva (si no hemos llegado al límite m)
            if max_machine_used < m:
                yield from backtrack(current_assignment + [max_machine_used + 1], max_machine_used + 1)

        yield from backtrack([], 0)

    def _build_schedule_for_assignment(self, machine_queues: Dict[int, List[Job]]) -> Solution:
        # Mantiene tu lógica original de simulación
        machine_free_time = {i: 0 for i in range(1, self.problem.num_machines + 1)}
        resource_timeline: Dict[int, Dict[int, int]] = {}
        solution_jobs: List[Job] = []
        completion_times = {0}
        remaining = {i: list(queue) for i, queue in machine_queues.items()}

        while any(len(q) > 0 for q in remaining.values()):
            candidates: List[Tuple[int, int, Job]] = []

            for m_id, q in remaining.items():
                if not q:
                    continue
                job = q[0]
                m_free = machine_free_time[m_id]
                cand_times = sorted([t for t in completion_times if t >= m_free])
                if m_free not in completion_times:
                    cand_times.insert(0, m_free)
                    cand_times.sort()

                found = -1
                for t in cand_times:
                    if self._check_resources(t, job.duration, job.resource_requirements, resource_timeline):
                        found = t
                        break
                if found != -1:
                    candidates.append((found, m_id, job))

            if not candidates:
                return None

            candidates.sort(key=lambda x: (x[0], x[1]))
            start_t, chosen_m, chosen_job = candidates[0]

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
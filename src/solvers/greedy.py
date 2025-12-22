from typing import List, Dict
from src.core.model import ProblemInstance, Solution, Job
from src.core.scheduler import SolutionBuilder

class GreedySolver:
    def __init__(self, problem: ProblemInstance):
        self.problem = problem
        self.scheduler = SolutionBuilder(problem)

    def solve(self, sort_strategy: str = None) -> Solution:
        """
        Solves using List Scheduling.
        If sort_strategy is provided, uses that specific one.
        If not, tries multiple strategies and picks the best.
        """
        
        strategies = []
        if sort_strategy:
            strategies.append(sort_strategy)
        else:
            strategies = ['LPT', 'SPT', 'HeavyResource', 'MostTotalResources']

        best_solution = None
        best_makespan = float('inf')
        
        print(f"Greedy Solver trying strategies: {strategies}")

        for strat in strategies:
            # Sort jobs
            jobs_ordered = self._sort_jobs(self.problem.jobs[:], strat)
            
            # Build schedule
            sol = self.scheduler.build_from_sequence(jobs_ordered)
            
            if sol.makespan < best_makespan:
                best_makespan = sol.makespan
                best_solution = sol
        
        return best_solution

    def _sort_jobs(self, jobs: List[Job], strategy: str) -> List[Job]:
        if strategy == 'LPT':
            jobs.sort(key=lambda x: x.duration, reverse=True)
        elif strategy == 'SPT':
            jobs.sort(key=lambda x: x.duration)
        elif strategy == 'HeavyResource':
            # Count number of specialized tools required (diversity)
            jobs.sort(key=lambda x: len(x.resource_requirements), reverse=True)
        elif strategy == 'MostTotalResources':
            # Count total quantity of all resources (intensity)
            jobs.sort(key=lambda x: sum(x.resource_requirements.values()), reverse=True)
        return jobs

from typing import List, Deque
from collections import deque
from src.core.model import ProblemInstance, Solution, Job
from src.core.scheduler import SolutionBuilder
import random

class TabuSearchSolver:
    def __init__(self, problem: ProblemInstance, max_iter: int = 1000, tabu_tenure: int = 20):
        self.problem = problem
        self.max_iter = max_iter
        self.tabu_tenure = tabu_tenure
        self.scheduler = SolutionBuilder(problem)

    def solve(self) -> Solution:
        # Initial Solution (Greedy LPT to start strong)
        # Or random? Let's do random to compare fairness with others, 
        # but Tabu works best with good initialization.
        current_sequence = self.problem.jobs[:]
        random.shuffle(current_sequence)
        
        current_sol = self.scheduler.build_from_sequence(current_sequence)
        best_sol = current_sol
        best_makespan = current_sol.makespan
        
        # Tabu List: Stores moves (indices swapped) or solution hashes?
        # Store (job_id_1, job_id_2) pairs that are banned
        tabu_list: Deque[tuple] = deque(maxlen=self.tabu_tenure)
        
        self.history = []

        for it in range(self.max_iter):
            # Generate Neighborhood (Swaps)
            # Evaluate a subset of neighbors to save time
            num_neighbors = 20
            best_neighbor_seq = None
            best_neighbor_makespan = float('inf')
            move_made = None
            
            for _ in range(num_neighbors):
                # Random swap
                idx1, idx2 = random.sample(range(len(current_sequence)), 2)
                # Ensure ordered for consistency in tabu check
                if idx1 > idx2: idx1, idx2 = idx2, idx1
                
                # Check Tabu
                move = (current_sequence[idx1].id, current_sequence[idx2].id)
                is_tabu = move in tabu_list
                
                # Apply Swap
                neighbor_seq = current_sequence[:]
                neighbor_seq[idx1], neighbor_seq[idx2] = neighbor_seq[idx2], neighbor_seq[idx1]
                
                # Evaluate
                sol = self.scheduler.build_from_sequence(neighbor_seq)
                ms = sol.makespan
                
                # Aspiration Criterion: If better than global best, ignore Tabu
                if is_tabu and ms >= best_makespan:
                    continue
                
                if ms < best_neighbor_makespan:
                    best_neighbor_makespan = ms
                    best_neighbor_seq = neighbor_seq
                    move_made = move
            
            # Move to best neighbor (even if worse than current) - Exploitation
            if best_neighbor_seq:
                current_sequence = best_neighbor_seq
                
                # Update Global Best
                if best_neighbor_makespan < best_makespan:
                    best_makespan = best_neighbor_makespan
                    best_sol = self.scheduler.build_from_sequence(best_neighbor_seq) # Rebuild to get object
                
                # Update Tabu List
                tabu_list.append(move_made)
            
            self.history.append(best_makespan)
            
        return best_sol

import random
import math
from typing import List
from src.core.model import ProblemInstance, Solution, Job
from src.core.scheduler import SolutionBuilder

class SimulatedAnnealingSolver:
    def __init__(self, problem: ProblemInstance, 
                 initial_temp: float = 1000.0, 
                 cooling_rate: float = 0.995, 
                 max_iter: int = 5000):
        self.problem = problem
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.max_iter = max_iter
        self.scheduler = SolutionBuilder(problem)

    def solve(self) -> Solution:
        # 1. Initial Solution (Random)
        current_sequence = self.problem.jobs[:]
        random.shuffle(current_sequence)
        
        current_sol = self.scheduler.build_from_sequence(current_sequence)
        current_makespan = current_sol.makespan
        
        best_sol = current_sol
        best_makespan = current_makespan
        
        temp = self.initial_temp
        self.history = []
        
        for i in range(self.max_iter):
            # 2. Generate Neighbor (Swap)
            neighbor_sequence = current_sequence[:]
            idx1, idx2 = random.sample(range(len(neighbor_sequence)), 2)
            neighbor_sequence[idx1], neighbor_sequence[idx2] = neighbor_sequence[idx2], neighbor_sequence[idx1]
            
            neighbor_sol = self.scheduler.build_from_sequence(neighbor_sequence)
            neighbor_makespan = neighbor_sol.makespan
            
            # 3. Acceptance Probability
            delta = neighbor_makespan - current_makespan
            
            accept = False
            if delta < 0:
                accept = True
            else:
                # Avoid overflow with very low temp
                if temp > 1e-10:
                    prob = math.exp(-delta / temp)
                    if random.random() < prob:
                        accept = True
            
            if accept:
                current_sequence = neighbor_sequence
                current_makespan = neighbor_makespan
                current_sol = neighbor_sol
                
                # Update Best
                if current_makespan < best_makespan:
                    best_makespan = current_makespan
                    best_sol = current_sol
            
            # 4. Cool Down
            temp *= self.cooling_rate
            self.history.append(best_makespan)
            
            # Optional: Restart if stuck? SA usually doesn't restart explicitly but relies on reheating.
            # We keep it simple for now.
            
        return best_sol

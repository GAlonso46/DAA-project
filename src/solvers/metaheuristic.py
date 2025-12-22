import random
from typing import List, Tuple
from src.core.model import ProblemInstance, Solution, Job
from src.core.scheduler import SolutionBuilder

class GeneticSolver:
    def __init__(self, problem: ProblemInstance, 
                 pop_size: int = 100, 
                 generations: int = 300, 
                 mutation_rate: float = 0.25,
                 crossover_rate: float = 0.9,
                 restart_threshold: int = 40): # Restart if no improvement for X gens
        self.problem = problem
        self.pop_size = pop_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.restart_threshold = restart_threshold
        
        self.scheduler = SolutionBuilder(problem)

    def solve(self) -> Solution:
        # Initial Population: Random Permutations
        base_jobs = self.problem.jobs[:]
        population = []
        for _ in range(self.pop_size):
            perm = base_jobs[:]
            random.shuffle(perm)
            population.append(perm)
            
        best_sol = None
        best_makespan = float('inf')
        
        generations_without_improvement = 0
        self.history = []
        
        for gen in range(self.generations):
            # Evaluate
            pop_fitness = []
            for indiv in population:
                sol = self.scheduler.build_from_sequence(indiv)
                pop_fitness.append((sol.makespan, indiv, sol))
                
                if sol.makespan < best_makespan:
                    best_makespan = sol.makespan
                    best_sol = sol
                    generations_without_improvement = 0 # Reset counter
            
            current_avg = sum(f[0] for f in pop_fitness) / len(pop_fitness)
            self.history.append(best_makespan)
            if not hasattr(self, 'history_avg'): self.history_avg = []
            self.history_avg.append(current_avg)
            
            # Restart Mechanism (Apocalypse)
            generations_without_improvement += 1
            if generations_without_improvement >= self.restart_threshold:
                print(f"Gen {gen}: Stagnation detected. Restarting population...")
                # Keep elite (top 10% or just 1?) 
                # Let's keep best solution found so far + top 5 current
                pop_fitness.sort(key=lambda x: x[0])
                elite_count = max(1, int(self.pop_size * 0.1))
                new_pop = [x[1] for x in pop_fitness[:elite_count]]
                
                # Fill rest with random
                while len(new_pop) < self.pop_size:
                    perm = base_jobs[:]
                    random.shuffle(perm)
                    new_pop.append(perm)
                
                population = new_pop
                generations_without_improvement = 0
                continue
            
            # Normal Evolution
            # Sort by fitness (makespan asc)
            pop_fitness.sort(key=lambda x: x[0])
            
            # Elitism
            new_pop = [x[1] for x in pop_fitness[:2]]
            
            # Selection & Crossover
            while len(new_pop) < self.pop_size:
                p1 = self._tournament(pop_fitness)
                p2 = self._tournament(pop_fitness)
                
                if random.random() < self.crossover_rate:
                    c1 = self._ox_crossover(p1, p2)
                    c2 = self._ox_crossover(p2, p1)
                else:
                    c1, c2 = p1[:], p2[:]
                
                new_pop.append(self._mutate(c1))
                if len(new_pop) < self.pop_size:
                    new_pop.append(self._mutate(c2))
            
            population = new_pop
            if (gen+1) % 10 == 0:
                print(f"Gen {gen+1}, Best: {best_makespan}")
                
        return best_sol

    def _tournament(self, pop_fitness, k=3):
        candidates = random.sample(pop_fitness, k)
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1] # Return sequence

    def _ox_crossover(self, p1: List[Job], p2: List[Job]) -> List[Job]:
        # Optimized Order Crossover (OX) with Set lookup
        size = len(p1)
        start, end = sorted(random.sample(range(size), 2))
        
        child = [None] * size
        # Copy subsegment from p1
        child[start:end+1] = p1[start:end+1]
        
        # Create set for fast lookup of jobs already in child
        # Note: Job objects might not be hashable by default or hashing id?
        # dataclass is not hashable strictly if not frozen. 
        # But we can use job.id for set.
        jobs_in_child = {job.id for job in child if job is not None}
        
        current_p2_idx = 0
        for i in range(size):
            if child[i] is None:
                # Find next job in p2 that is not in child
                while current_p2_idx < size and p2[current_p2_idx].id in jobs_in_child:
                    current_p2_idx += 1
                
                if current_p2_idx < size:
                    child[i] = p2[current_p2_idx]
                    jobs_in_child.add(p2[current_p2_idx].id)
                
        return child

    def _mutate(self, sequence: List[Job]) -> List[Job]:
        if random.random() < self.mutation_rate:
            idx1, idx2 = random.sample(range(len(sequence)), 2)
            sequence[idx1], sequence[idx2] = sequence[idx2], sequence[idx1]
        return sequence

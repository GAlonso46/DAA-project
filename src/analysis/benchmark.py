import time
import pandas as pd
import random
import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.model import ProblemInstance, Job
from src.solvers.greedy import GreedySolver
from src.solvers.metaheuristic import GeneticSolver
from src.solvers.simulated_annealing import SimulatedAnnealingSolver
from src.core.generator import generate_instance

def run_benchmark(num_runs=1, jobs=[30, 60], machines=[4, 8]):
    results = []
    
    for n_jobs in jobs:
        for n_m in machines:
            res_count = max(2, int(n_m * 0.5))
            print(f"Benchmarking: {n_jobs} Jobs, {n_m} Machines, {res_count} Resources")
            
            for run_id in range(num_runs):
                # Unique instance per run
                data = generate_instance(num_jobs=n_jobs, num_machines=n_m, num_resources=res_count)
                
                # Reconstruct ProblemInstance (Manual mapping usually done in load_problem)
                from src.core.model import Job
                jobs_obj = []
                for j in data['jobs']:
                    jobs_obj.append(Job(
                        id=j['id'], 
                        duration=j['duration'], 
                        resource_requirements={int(k): v for k, v in j['requirements'].items()}
                    ))
                resources = {int(k): v for k, v in data['resources'].items()}
                problem = ProblemInstance(data['num_machines'], resources, jobs_obj)
                
                # 1. Greedy LPT (Baseline)
                start = time.time()
                g_solver = GreedySolver(problem)
                sol_lpt = g_solver.solve(sort_strategy='LPT')
                time_lpt = time.time() - start
                
                 # 2. Greedy SPT (New Baseline)
                start = time.time()
                sol_spt = g_solver.solve(sort_strategy='SPT')
                time_spt = time.time() - start

                # 3. Simulated Annealing (New Metaheuristic)
                start = time.time()
                sa_solver = SimulatedAnnealingSolver(problem, max_iter=5000)
                sol_sa = sa_solver.solve()
                time_sa = time.time() - start

                # 4. Metaheuristic (GA)
                start = time.time()
                m_solver = GeneticSolver(problem, pop_size=200, generations=500, mutation_rate=0.2) 
                sol_ga = m_solver.solve()
                time_ga = time.time() - start
                
                # 5. Random Search (Baseline)
                start = time.time()
                best_random = float('inf')
                # Run 1000 samples for better baseline
                for _ in range(1000):
                    perm = jobs_obj[:]
                    random.shuffle(perm)
                    # Reuse scheduler from m_solver or sa_solver
                    s_rnd = m_solver.scheduler.build_from_sequence(perm)
                    if s_rnd.makespan < best_random:
                        best_random = s_rnd.makespan
                time_random = time.time() - start

                results.append({
                    "Jobs": n_jobs,
                    "Machines": n_m,
                    "Run": run_id,
                    "LPT_Makespan": sol_lpt.makespan,
                    "SPT_Makespan": sol_spt.makespan,
                    "Random_Makespan": best_random,
                    "SA_Makespan": sol_sa.makespan,
                    "GA_Makespan": sol_ga.makespan,
                    "Run_Time_GA": time_ga,
                    "Run_Time_SA": time_sa,
                    "Improvement_GA_vs_LPT": round(100 * (sol_lpt.makespan - sol_ga.makespan) / sol_lpt.makespan, 2)
                })

    df = pd.DataFrame(results)
    print("\nBenchmark Results Summary:")
    print(df.groupby(["Jobs", "Machines"]).mean(numeric_only=True)[["LPT_Makespan", "SPT_Makespan", "Random_Makespan", "SA_Makespan", "GA_Makespan"]])
    
    output_file = "benchmark_results_advanced.csv"
    df.to_csv(output_file, index=False)
    print(f"\nFull results saved to {output_file}")

if __name__ == "__main__":
    run_benchmark()

import time
import pandas as pd
import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.generator import generate_instance
from src.core.model import ProblemInstance, Job
from src.solvers.greedy import GreedySolver
from src.solvers.metaheuristic import GeneticSolver
from src.solvers.simulated_annealing import SimulatedAnnealingSolver
from src.solvers.tabu_search import TabuSearchSolver

def run_showdown():
    print("--- 🏁 METAHEURISTIC SHOWDOWN (FAST TRACK) 🏁 ---")
    print("Generating challenging instance (50 Jobs, 5 Machines, 3 Resources)...")
    
    data = generate_instance(num_jobs=50, num_machines=5, num_resources=3)
    
    # Init Problem
    jobs_obj = []
    for j in data['jobs']:
        jobs_obj.append(Job(j['id'], j['duration'], {int(k): v for k, v in j['requirements'].items()}))
    resources = {int(k): v for k, v in data['resources'].items()}
    problem = ProblemInstance(data['num_machines'], resources, jobs_obj)
    
    results = []
    
    # 1. Greedy (Reference)
    print("1. Running Greedy LPT (Baseline)...")
    start = time.time()
    greedy = GreedySolver(problem)
    sol_greedy = greedy.solve('LPT')
    t_greedy = time.time() - start
    print(f"   -> Makespan: {sol_greedy.makespan} (Time: {t_greedy:.3f}s)")
    
    results.append({'Algorithm': 'Greedy LPT', 'Makespan': sol_greedy.makespan, 'Time': t_greedy})

    # 2. Genetic Algorithm
    print("2. Running Genetic Algorithm (Pop=200, Gen=200)...")
    start = time.time()
    ga = GeneticSolver(problem, pop_size=200, generations=200)
    sol_ga = ga.solve()
    t_ga = time.time() - start
    print(f"   -> Makespan: {sol_ga.makespan} (Time: {t_ga:.3f}s)")
    results.append({'Algorithm': 'Genetic Alg', 'Makespan': sol_ga.makespan, 'Time': t_ga})
    
    # 3. Simulated Annealing
    print("3. Running Simulated Annealing (Iter=5000)...")
    start = time.time()
    sa = SimulatedAnnealingSolver(problem, max_iter=5000)
    sol_sa = sa.solve()
    t_sa = time.time() - start
    print(f"   -> Makespan: {sol_sa.makespan} (Time: {t_sa:.3f}s)")
    results.append({'Algorithm': 'Sim. Annealing', 'Makespan': sol_sa.makespan, 'Time': t_sa})
    
    # 4. Tabu Search (The New Challenger)
    print("4. Running Tabu Search (Iter=2000, Tenure=20)...")
    start = time.time()
    tabu = TabuSearchSolver(problem, max_iter=2000, tabu_tenure=20)
    sol_tabu = tabu.solve()
    t_tabu = time.time() - start
    print(f"   -> Makespan: {sol_tabu.makespan} (Time: {t_tabu:.3f}s)")
    results.append({'Algorithm': 'Tabu Search', 'Makespan': sol_tabu.makespan, 'Time': t_tabu})

    # Analysis
    df = pd.DataFrame(results)
    df['Gap_vs_Greedy'] = ((sol_greedy.makespan - df['Makespan']) / sol_greedy.makespan) * 100
    
    print("\n--- 🏆 FINAL RANKING ---")
    df_sorted = df.sort_values(by='Makespan')
    print(df_sorted[['Algorithm', 'Makespan', 'Time', 'Gap_vs_Greedy']])
    
    winner = df_sorted.iloc[0]
    print(f"\n🌟 WINNER: {winner['Algorithm']} with Makespan {winner['Makespan']}")

if __name__ == "__main__":
    run_showdown()


import random
import json
import csv
import time
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Ensure src is in path
ROOT = Path(__file__).resolve().parents[1]
# Aggressively insert ROOT at start
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
else:
    # Move to front if already there
    sys.path.remove(str(ROOT))
    sys.path.insert(0, str(ROOT))

# Attempt to remove 'src' from sys.modules to force fresh import from correct location
# in case it was loaded from a diverse site-packages or environment
if 'src' in sys.modules:
    del sys.modules['src']

import src
print(f"Loaded src from: {src.__file__}")

from src.core.model import ProblemInstance, Job
from src.solvers.earliest_start_solver import EarliestStartSolver
from src.solvers.metaheuristic import GeneticSolver

# --- Generators ---

def generate_large_bottleneck(num_jobs: int, num_machines: int) -> Dict:
    """
    Large Scale Bottleneck:
    Many jobs competing for 1 critical resource.
    """
    jobs = []
    # Resource capacity is low compared to demand
    res_cap = max(1, int(num_machines * 0.2)) 
    
    for j in range(1, num_jobs + 1):
        jobs.append({
            "id": j,
            "duration": random.randint(10, 50),
            "requirements": {"CriticalRes": 1}
        })
    
    return {
        "num_machines": num_machines,
        "resources": {"CriticalRes": res_cap},
        "jobs": jobs
    }

def generate_large_high_contention(num_jobs: int, num_machines: int) -> Dict:
    """
    Large Scale High Contention:
    Chain of dependencies.
    """
    jobs = []
    # Create N resources
    resources = {f"R{r}": 1 for r in range(1, num_jobs + 1)}
    
    for j in range(1, num_jobs + 1):
        if j < num_jobs:
            reqs = {f"R{j}": 1, f"R{j+1}": 1}
        else:
            reqs = {f"R{j}": 1, f"R{j-1}": 1}
            
        jobs.append({
            "id": j,
            "duration": random.randint(10, 20),
            "requirements": reqs
        })
        
    return {
        "num_machines": num_machines,
        "resources": resources,
        "jobs": jobs
    }

def generate_large_rock_sand(num_jobs: int, num_machines: int) -> Dict:
    """
    Large Scale Rock & Sand:
    1 Very Long Job (Rock).
    N-1 Short Jobs (Sand).
    """
    jobs = []
    # Rock
    jobs.append({
        "id": 1,
        "duration": num_jobs * 2, # Proportional to N
        "requirements": {"HeavyTool": 1}
    })
    # Sand
    for j in range(2, num_jobs + 1):
        jobs.append({
            "id": j,
            "duration": random.randint(5, 10),
            "requirements": {}
        })
        
    return {
        "num_machines": num_machines,
        "resources": {"HeavyTool": 1},
        "jobs": jobs
    }

def generate_large_irrelevant(num_jobs: int, num_machines: int) -> Dict:
    """
    Large Scale Irrelevant:
    Resources abundant.
    """
    jobs = []
    for j in range(1, num_jobs + 1):
        jobs.append({
            "id": j,
            "duration": random.randint(20, 40),
            "requirements": {"BasicTool": 1}
        })
        
    return {
        "num_machines": num_machines,
        "resources": {"BasicTool": num_machines}, # Non-binding
        "jobs": jobs
    }

def generate_large_greedy_killer(num_jobs: int, num_machines: int) -> Dict:
    """
    Large Scale Greedy Killer:
    Many short jobs blocking critical resource.
    One long job that could fit free but gets blocked or delayed if resources misused?
    Actually for large scale, we simulate:
    Half jobs short+critical.
    One long free job.
    Rest tiny free jobs.
    """
    jobs = []
    
    # 40% Short Critical
    num_critical = int(num_jobs * 0.4)
    for j in range(1, num_critical + 1):
        jobs.append({
            "id": j,
            "duration": 10,
            "requirements": {"Crit": 1}
        })
        
    # 1 Long Free
    long_job_id = num_critical + 1
    jobs.append({
        "id": long_job_id,
        "duration": 100,
        "requirements": {}
    })
    
    # Rest Tiny Free
    for j in range(long_job_id + 1, num_jobs + 1):
        jobs.append({
            "id": j,
            "duration": 2,
            "requirements": {}
        })
        
    return {
        "num_machines": num_machines, # Low machine count aggravates this
        "resources": {"Crit": 1},
        "jobs": jobs
    }

def generate_large_random(num_jobs: int, num_machines: int) -> Dict:
    from src.core.generator import generate_instance
    # Wrapper around existing random generator
    return generate_instance(num_jobs, num_machines, num_resources=5, max_resource_qty=3)


# --- Runner ---


def create_problem_instance(data: Dict) -> ProblemInstance:
    jobs_data = data["jobs"]
    job_objects = []
    for j in jobs_data:
        # data["jobs"] has "id", "duration", "requirements"
        job_objects.append(Job(
            id=j["id"],
            duration=j["duration"],
            resource_requirements=j["requirements"]
        ))
    
    return ProblemInstance(
        num_machines=data["num_machines"],
        resources=data["resources"],
        jobs=job_objects
    )

def solve_with_earliest_start(instance_data):
    try:
        problem = create_problem_instance(instance_data)
        solver = EarliestStartSolver(problem)
        start_t = time.time()
        solution = solver.solve()
        runtime = time.time() - start_t
        return solution.makespan, runtime, "ok"
    except Exception as e:
        return None, time.time() - start_t if 'start_t' in locals() else 0, str(e)

def solve_with_genetic(instance_data):
    try:
        problem = create_problem_instance(instance_data)
        # Reduce gens/pop for quicker large scale test if needed, or keep robust
        solver = GeneticSolver(problem, pop_size=50, generations=100) 
        start_t = time.time()
        solution = solver.solve()
        runtime = time.time() - start_t
        return solution.makespan, runtime, "ok"
    except Exception as e:
        return None, time.time() - start_t if 'start_t' in locals() else 0, str(e)


def run_comparison():
    # Parameters
    NUM_JOBS = 50
    NUM_MACHINES_NORMAL = 10
    NUM_MACHINES_TIGHT = 4 # For Greedy Killer
    
    scenarios = [
        ("Bottleneck", generate_large_bottleneck(NUM_JOBS, NUM_MACHINES_NORMAL)),
        ("HighContention", generate_large_high_contention(NUM_JOBS, NUM_MACHINES_NORMAL)),
        ("RockSand", generate_large_rock_sand(NUM_JOBS, NUM_MACHINES_NORMAL)),
        ("Irrelevant", generate_large_irrelevant(NUM_JOBS, NUM_MACHINES_NORMAL)),
        ("GreedyKiller", generate_large_greedy_killer(NUM_JOBS, NUM_MACHINES_TIGHT)),
        ("Random1", generate_large_random(NUM_JOBS, NUM_MACHINES_NORMAL)),
        ("Random2", generate_large_random(NUM_JOBS, NUM_MACHINES_NORMAL)),
    ]
    
    results = []
    dataset = {}
    
    print(f"Running comparison on {len(scenarios)} large instances...")
    
    for name, data in scenarios:
        dataset[name] = data
        print(f"--> Scenario: {name}")
        
        # Earliest Start
        m_es, t_es, stat_es = solve_with_earliest_start(data)
        results.append({
            "scenario": name,
            "solver": "EarliestStart",
            "makespan": m_es,
            "runtime": t_es,
            "status": stat_es
        })
        print(f"    EarliestStart: {m_es} (t={t_es:.4f}s)")
        
        # Genetic
        m_ga, t_ga, stat_ga = solve_with_genetic(data)
        results.append({
            "scenario": name,
            "solver": "Genetic",
            "makespan": m_ga,
            "runtime": t_ga,
            "status": stat_ga
        })
        print(f"    Genetic:       {m_ga} (t={t_ga:.4f}s)")
        
    return results, dataset

def save_and_plot(results, dataset):
    output_dir = ROOT / 'scripts'
    plots_dir = output_dir / 'plots'
    plots_dir.mkdir(exist_ok=True)
    
    # Save Dataset
    with open(output_dir / 'comparison_dataset.json', 'w') as f:
        json.dump(dataset, f, indent=4)
        
    # Save Results
    df = pd.DataFrame(results)
    csv_path = output_dir / 'comparison_results.csv'
    df.to_csv(csv_path, index=False)
    print(f"\nSaved dataset to {output_dir / 'comparison_dataset.json'}")
    print(f"Saved results to {csv_path}")
    
    # Plotting
    sns.set(style="whitegrid")
    
    # Filter valid results
    valid_df = df[df['status'] == 'ok'].copy()
    
    if valid_df.empty:
        print("No valid results to plot.")
        return

    # Makespan Comparison
    plt.figure(figsize=(12, 6))
    sns.barplot(data=valid_df, x='scenario', y='makespan', hue='solver')
    plt.title('Makespan Comparison (Lower is Better)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(plots_dir / 'comparison_makespan.png')
    plt.close()
    
    # Runtime Comparison
    plt.figure(figsize=(12, 6))
    sns.barplot(data=valid_df, x='scenario', y='runtime', hue='solver')
    plt.title('Runtime Comparison (Log Scale)')
    plt.yscale('log')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(plots_dir / 'comparison_runtime.png')
    plt.close()
    
    print(f"Plots saved to {plots_dir}")

def main():
    results, dataset = run_comparison()
    save_and_plot(results, dataset)

if __name__ == "__main__":
    main()

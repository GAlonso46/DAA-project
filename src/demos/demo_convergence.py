import matplotlib.pyplot as plt
import numpy as np
import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.generator import generate_instance
from src.core.model import ProblemInstance, Job
from src.solvers.metaheuristic import GeneticSolver
from src.solvers.simulated_annealing import SimulatedAnnealingSolver
from src.utils.advanced_visualizer import AdvancedVisualizer

def run_demo():
    print("Running Demo for Convergence Plot...")
    # Generate one instance
    data = generate_instance(num_jobs=50, num_machines=5, num_resources=3)
    
    jobs_obj = []
    for j in data['jobs']:
        jobs_obj.append(Job(j['id'], j['duration'], {int(k): v for k, v in j['requirements'].items()}))
    resources = {int(k): v for k, v in data['resources'].items()}
    problem = ProblemInstance(data['num_machines'], resources, jobs_obj)
    
    # Run GA
    print("Running GA...")
    ga = GeneticSolver(problem, pop_size=100, generations=200, mutation_rate=0.2)
    best_ga_sol = ga.solve()
    
    # Run SA
    print("Running SA...")
    sa = SimulatedAnnealingSolver(problem, max_iter=2000)
    sa.solve()
    
    # Plot Convergence
    plt.figure(figsize=(10, 6))
    plt.plot(ga.history, label='GA Best Makespan', linewidth=2)
    if hasattr(ga, 'history_avg'):
        plt.plot(ga.history_avg, label='GA Avg Makespan', linestyle='--', alpha=0.7)
    
    # Plot SA? SA has different X axis (iterations vs generations).
    # We can try to map them or just plot GA as requested.
    # User asked for "Convergence Plot (For Genetic)". Let's stick to that clearly.
    # But adding SA best so far line would be cool.
    # SA history is length 2000. GA is 200.
    # We can sample SA history to match GA? or just plot on secondary axis?
    # Let's just plot GA for clarity as per "Wow factor C".
    
    plt.xlabel('Generations')
    plt.ylabel('Makespan')
    plt.title('Genetic Algorithm Convergence Profile')
    plt.legend()
    plt.grid(True)
    plt.savefig('convergence_plot.png')
    print("Saved convergence_plot.png")

    # Generate Advanced Plots
    print("Generating Advanced Visualizations...")
    viz = AdvancedVisualizer(best_ga_sol, problem)
    viz.plot_rich_gantt(save_path="rich_gantt.png")
    viz.plot_resource_profile(save_path="resource_profile.png")

if __name__ == "__main__":
    run_demo()

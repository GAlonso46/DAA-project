from src.core.generator import generate_instance
from src.core.model import Job, ProblemInstance
from src.solvers.greedy import GreedySolver
from src.solvers.metaheuristic import GeneticSolver
from src.solvers.simulated_annealing import SimulatedAnnealingSolver
from src.solvers.tabu_search import TabuSearchSolver
from src.utils.advanced_visualizer import AdvancedVisualizer

def main():
    print("--- 🏭 TecnoPlecision Scheduling System v2.0 ---")
    
    # Configuration
    N_JOBS = 20
    N_MACHINES = 3
    N_RESOURCES = 2
    
    print(f"Generating instance: {N_JOBS} jobs, {N_MACHINES} machines...")
    data = generate_instance(num_jobs=N_JOBS, num_machines=N_MACHINES, num_resources=N_RESOURCES)
    
    # Reconstruct objects
    jobs = []
    for j in data['jobs']:
        jobs.append(Job(j['id'], j['duration'], {int(k): v for k, v in j['requirements'].items()}))
    resources = {int(k): v for k, v in data['resources'].items()}
    problem = ProblemInstance(data['num_machines'], resources, jobs)
    
    # Solver Selection
    print("\nSelect Solver:")
    print("1. Greedy LPT (Fastest)")
    print("2. Genetic Algorithm (Robust)")
    print("3. Simulated Annealing (Recommended - Fast & Optimal)")
    print("4. Tabu Search (Memory-based)")
    
    choice = input("Enter choice (1-4, default 3): ") or "3"
    
    if choice == "1":
        solver = GreedySolver(problem)
        solution = solver.solve('LPT')
        name = "Greedy LPT"
    elif choice == "2":
        solver = GeneticSolver(problem, pop_size=100, generations=100)
        solution = solver.solve()
        name = "Genetic Algorithm"
    elif choice == "4":
        solver = TabuSearchSolver(problem, max_iter=1000)
        solution = solver.solve()
        name = "Tabu Search"
    else:
        solver = SimulatedAnnealingSolver(problem, max_iter=3000)
        solution = solver.solve()
        name = "Simulated Annealing"
        
    print(f"\n--- Results for {name} ---")
    print(f"Makespan: {solution.makespan}")
    
    # Visualization
    print("\nGenerating final visualizations...")
    viz = AdvancedVisualizer(solution, problem)
    viz.plot_rich_gantt(save_path="final_gantt.png")
    viz.plot_resource_profile(save_path="final_resource_profile.png")
    
    print("Done! Check 'final_gantt.png' and 'final_resource_profile.png'.")

if __name__ == "__main__":
    main()

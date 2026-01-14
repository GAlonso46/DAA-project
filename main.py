from src.core.generator import generate_instance
from src.core.model import Job, ProblemInstance
from src.solvers.greedy import GreedySolver
from src.solvers.metaheuristic import GeneticSolver
from src.solvers.simulated_annealing import SimulatedAnnealingSolver
from src.utils.advanced_visualizer import AdvancedVisualizer
from src.solvers.bruteforce import BruteForceSolver
from src.solvers.earliest_start_solver import EarliestStartSolver

def main():
    print("--- 🏭 TecnoPlecision Scheduling System v2.0 ---")
    
    # Configuration (allow user to customize instance size)
    print("\nInstance configuration (press Enter to use defaults):")
    default_N_JOBS = 10
    default_N_MACHINES = 3
    default_N_RESOURCES = 2

    def _read_int(prompt: str, default: int) -> int:
        val = input(f"{prompt} [{default}]: ").strip()
        if val == "":
            return default
        try:
            return int(val)
        except ValueError:
            print(f"Invalid input, using default {default}.")
            return default

    N_JOBS = _read_int("Number of jobs", default_N_JOBS)
    N_MACHINES = _read_int("Number of machines", default_N_MACHINES)
    N_RESOURCES = _read_int("Number of resources", default_N_RESOURCES)

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
    print("5. Brute Force (Exhaustive - small instances only)")
    print("6. Earliest Start (Iterative earliest-placement)")

    choice = input("Enter choice (1-6, default 3): ") or "3"

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
    elif choice == "5":
        # Safety: compute number of combinations and ask confirmation for large runs
        n = len(problem.jobs)
        m = problem.num_machines
        total = m ** n
        if total > 1_000_000:
            yn = input(f"Brute-force will evaluate {total} combinations. Continue? (y/N): ").lower()
            if yn != 'y':
                print("Operation cancelled by user.")
                return
        try:
            solver = BruteForceSolver(problem, max_combinations=total)
            solution = solver.solve()
            name = "Brute Force"
        except RuntimeError as e:
            print(f"Brute-force aborted: {e}")
            return
    elif choice == "6":
        solver = EarliestStartSolver(problem)
        solution = solver.solve()
        name = "Earliest Start Solver"
    else:
        solver = SimulatedAnnealingSolver(problem, max_iter=3000)
        solution = solver.solve()
        name = "Simulated Annealing"
        
    print(f"\n--- Results for {name} ---")
    print(f"Makespan: {solution.makespan}")
    
    # Visualization: ask user before generating potentially expensive plots
    view = input("Generate visualizations? (y/N): ").strip().lower() or "n"
    if view == 'y':
        print("\nGenerating final visualizations...")
        viz = AdvancedVisualizer(solution, problem)
        viz.plot_rich_gantt(save_path="artifacts/final_gantt.png")
        viz.plot_resource_profile(save_path="artifacts/final_resource_profile.png")
        print("Done! Check 'artifacts/final_gantt.png' and 'artifacts/final_resource_profile.png'.")
    else:
        print("Skipping visualizations.")

    
if __name__ == "__main__":
    main()

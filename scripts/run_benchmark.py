import os
import sys
import time
import json
import csv
import random

# Ensure project root is on sys.path (one level up from scripts/)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.generator import generate_random_instance
from src.core.model import Job, ProblemInstance
from src.solvers.greedy import GreedySolver
from src.solvers.metaheuristic import GeneticSolver
from src.solvers.simulated_annealing import SimulatedAnnealingSolver
from src.solvers.tabu_search import TabuSearchSolver
from src.solvers.bruteforce import BruteForceSolver
from src.solvers.earliest_start_solver import EarliestStartSolver


def pretty_print_instance(data, idx):
    print(f"\n=== Instance {idx} ===")
    n_jobs = len(data['jobs'])
    n_machines = data['num_machines']
    n_resources = len(data['resources'])
    print(f"Jobs: {n_jobs}, Machines: {n_machines}, Resources: {n_resources}")
    print("Resource capacities:")
    for k, v in data['resources'].items():
        print(f"  R{k}: {v}")
    print("Jobs detail (id, duration, requirements):")
    for j in data['jobs']:
        print(f"  id={j['id']}, dur={j['duration']}, reqs={j['requirements']}")


def main():
    OUT_DIR = os.path.join('artifacts', 'benchmarks')
    os.makedirs(OUT_DIR, exist_ok=True)

    csv_path = os.path.join(OUT_DIR, 'results.csv')
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['instance_id', 'n_jobs', 'n_machines', 'n_resources',
                                                     'solver', 'makespan', 'time_s', 'valid', 'error'])
        writer.writeheader()

        # Generate 10 instances with bounds: max 10 jobs, max 3 machines, max 3 resources
        for i in range(1, 11):
            seed = 1000 + i
            random.seed(seed)

            data = generate_random_instance(max_jobs=12, max_machines=4, max_resources=4)

            # Save raw instance for reference
            inst_file = os.path.join(OUT_DIR, f'instance_{i}.json')
            with open(inst_file, 'w') as f:
                json.dump({'seed': seed, 'data': data}, f, indent=4)

            # Print instance summary
            pretty_print_instance(data, i)

            # Reconstruct objects (convert resource keys to int)
            jobs = []
            for j in data['jobs']:
                jobs.append(Job(j['id'], j['duration'], {int(k): v for k, v in j['requirements'].items()}))
            resources = {int(k): v for k, v in data['resources'].items()}
            problem = ProblemInstance(data['num_machines'], resources, jobs)

            # Prepare solvers to run
            n = len(problem.jobs)
            m = problem.num_machines
            total = m ** n

            solvers = []
            solvers.append(('Greedy LPT', GreedySolver(problem), lambda s: s.solve('LPT')))
            solvers.append(('Genetic', GeneticSolver(problem, pop_size=100, generations=100), lambda s: s.solve()))
            solvers.append(('SimulatedAnnealing', SimulatedAnnealingSolver(problem, max_iter=1000), lambda s: s.solve()))
            #solvers.append(('TabuSearch', TabuSearchSolver(problem, max_iter=500), lambda s: s.solve()))
            # Brute Force: allow full enumeration (no cap) so we can measure full runtime
            print(f"Total brute-force combinations for instance {i}: {total}")
            solvers.append(('BruteForce', BruteForceSolver(problem, max_combinations=100000000), lambda s: s.solve()))
            solvers.append(('EarliestStart', EarliestStartSolver(problem), lambda s: s.solve()))

            # Run each solver and record results
            for name, solver_obj, run_fn in solvers:
                print(f"\nRunning solver: {name} on instance {i}...")
                row = {'instance_id': i, 'n_jobs': n, 'n_machines': m, 'n_resources': len(resources),
                       'solver': name, 'makespan': None, 'time_s': None, 'valid': False, 'error': ''}
                try:
                    t0 = time.time()
                    sol = run_fn(solver_obj)
                    t1 = time.time()
                    elapsed = t1 - t0

                    row['time_s'] = round(elapsed, 4)
                    row['makespan'] = sol.makespan if sol is not None else None

                    # validate solution
                    valid = problem.validate_solution(sol) if sol is not None else False
                    row['valid'] = bool(valid)

                    print(f"Solver {name} finished: makespan={row['makespan']}, time={row['time_s']}s, valid={row['valid']}")
                except Exception as e:
                    row['error'] = str(e)
                    print(f"Solver {name} failed with error: {e}")

                writer.writerow(row)
                csvfile.flush()

    print(f"\nBenchmark finished. Results saved to {csv_path}")


if __name__ == '__main__':
    main()

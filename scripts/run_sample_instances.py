import os
import sys
import time
import json
import csv

# add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.model import Job, ProblemInstance
from src.solvers.greedy import GreedySolver
from src.solvers.metaheuristic import GeneticSolver
from src.solvers.simulated_annealing import SimulatedAnnealingSolver
from src.solvers.earliest_start_solver import EarliestStartSolver


def load_instances(file_path: str):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data


def build_problem_from_data(data_block: dict) -> ProblemInstance:
    # data_block expected to contain keys: num_machines, resources, jobs
    raw_resources = data_block.get('resources', {})
    # Map resource names (strings) to integer ids starting at 1
    name_to_id = {name: idx+1 for idx, name in enumerate(raw_resources.keys())}
    resources = {name_to_id[name]: qty for name, qty in raw_resources.items()}

    jobs = []
    for j in data_block.get('jobs', []):
        # Map job requirements keys to integer ids
        reqs = {}
        for rname, qty in j.get('requirements', {}).items():
            if rname in name_to_id:
                reqs[name_to_id[rname]] = qty
            else:
                # if resource name not known, skip
                continue
        jobs.append(Job(j['id'], j['duration'], reqs))

    num_machines = data_block.get('num_machines', 1)
    return ProblemInstance(num_machines, resources, jobs)


def pretty_print_instance(name: str, data_block: dict):
    print(f"\n--- Instance: {name} ---")
    n_jobs = len(data_block.get('jobs', []))
    n_machines = data_block.get('num_machines', 1)
    print(f"Machines: {n_machines}, Jobs: {n_jobs}")
    print("Resources:")
    for rname, cap in data_block.get('resources', {}).items():
        print(f"  {rname}: {cap}")
    print("Jobs:")
    for j in data_block.get('jobs', []):
        print(f"  id={j['id']}, dur={j['duration']}, req={j.get('requirements', {})}")


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sample_file = os.path.join(repo_root, 'data', 'sample.json')
    instances = load_instances(sample_file)

    out_dir = os.path.join(repo_root, 'artifacts', 'sample_runs')
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, 'results.csv')

    fieldnames = ['instance', 'solver', 'n_jobs', 'n_machines', 'n_resources', 'makespan', 'time_s', 'valid', 'error']
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for inst_name, inst_obj in instances.items():
            data_block = inst_obj.get('data', inst_obj) if isinstance(inst_obj, dict) else inst_obj
            pretty_print_instance(inst_name, data_block)

            try:
                problem = build_problem_from_data(data_block)
            except Exception as e:
                print(f"Failed to build ProblemInstance for {inst_name}: {e}")
                continue

            # Prepare solvers
            solvers = [
                ('EarliestStart', EarliestStartSolver(problem), lambda s: s.solve()),
                ('Greedy LPT', GreedySolver(problem), lambda s: s.solve('LPT')),
                ('Genetic', GeneticSolver(problem, pop_size=100, generations=100), lambda s: s.solve()),
                ('SimulatedAnnealing', SimulatedAnnealingSolver(problem, max_iter=1000), lambda s: s.solve()),
            ]

            for name, solver_obj, run_fn in solvers:
                print(f"\nRunning {name} on {inst_name}...")
                row = {'instance': inst_name, 'solver': name, 'n_jobs': len(problem.jobs),
                       'n_machines': problem.num_machines, 'n_resources': len(problem.resources),
                       'makespan': None, 'time_s': None, 'valid': False, 'error': ''}
                try:
                    t0 = time.time()
                    sol = run_fn(solver_obj)
                    t1 = time.time()
                    elapsed = t1 - t0

                    row['makespan'] = sol.makespan if sol is not None else None
                    row['time_s'] = round(elapsed, 4)
                    row['valid'] = bool(problem.validate_solution(sol)) if sol is not None else False

                    print(f"Result -> makespan: {row['makespan']}, time: {row['time_s']}s, valid: {row['valid']}")
                except Exception as e:
                    row['error'] = str(e)
                    print(f"Solver {name} failed: {e}")

                writer.writerow(row)
                csvfile.flush()

    print(f"\nAll runs finished. Results saved to {csv_path}")


if __name__ == '__main__':
    main()

import os
import sys
import time
import json
import csv

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.generator import generate_instance
from src.core.model import Job, ProblemInstance
from src.solvers.bruteforce import BruteForceSolver


def build_problem_from_generated(data):
    jobs = []
    for j in data['jobs']:
        jobs.append(Job(j['id'], j['duration'], {int(k): v for k, v in j['requirements'].items()}))
    resources = {int(k): v for k, v in data['resources'].items()}
    return ProblemInstance(data['num_machines'], resources, jobs)


def main():
    out_dir = os.path.join('artifacts', 'bruteforce_scale')
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, 'bruteforce_scaling.csv')

    fieldnames = ['iteration', 'n_jobs', 'n_machines', 'n_resources', 'estimated_combinations', 'time_s', 'success', 'error', 'instance_file']

    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        iteration = 0
        # We'll grow number of jobs until brute force takes > 300s
        # Growth strategy: increase jobs by 1 each iteration, and set machines/resources proportional to jobs
        max_time_seconds = 300.0

        n_jobs = 1
        while True:
            iteration += 1
            # Define proportional machines and resources
            n_machines = max(1, n_jobs // 3)  # roughly one machine per 3 jobs
            n_resources = max(0, n_jobs // 5)  # roughly one resource per 5 jobs

            print(f"\nIteration {iteration}: jobs={n_jobs}, machines={n_machines}, resources={n_resources}")

            # Generate deterministic instance (seeded by iteration)
            data = generate_instance(num_jobs=n_jobs, num_machines=n_machines, num_resources=n_resources)

            # Save instance
            inst_file = os.path.join(out_dir, f'instance_iter_{iteration}_j{n_jobs}_m{n_machines}_r{n_resources}.json')
            with open(inst_file, 'w') as f:
                json.dump(data, f, indent=4)

            # Build ProblemInstance
            problem = build_problem_from_generated(data)

            # Estimate combinations
            try:
                estimated = problem.num_machines ** len(problem.jobs)
            except OverflowError:
                estimated = float('inf')

            row = {'iteration': iteration, 'n_jobs': n_jobs, 'n_machines': n_machines, 'n_resources': n_resources,
                   'estimated_combinations': estimated, 'time_s': None, 'success': False, 'error': '', 'instance_file': inst_file}

            # Run brute force and time it
            solver = BruteForceSolver(problem, max_combinations=None)
            print(f"Estimated brute-force combinations: {estimated}")
            t0 = time.time()
            try:
                sol = solver.solve()
                t1 = time.time()
                elapsed = t1 - t0
                row['time_s'] = round(elapsed, 4)
                row['success'] = True
                print(f"Brute force finished in {elapsed:.2f}s, makespan={sol.makespan}")
            except Exception as e:
                t1 = time.time()
                elapsed = t1 - t0
                row['time_s'] = round(elapsed, 4)
                row['error'] = str(e)
                row['success'] = False
                print(f"Brute force failed after {elapsed:.2f}s with error: {e}")

            writer.writerow(row)
            csvfile.flush()

            # Stop condition
            if row['time_s'] is not None and row['time_s'] > max_time_seconds:
                print(f"Stopping: brute force took {row['time_s']}s (> {max_time_seconds}s) at iteration {iteration}")
                break

            # Increment job count for next iteration
            n_jobs += 1

            # Safety cap to avoid infinite loops
            if n_jobs > 20:
                print("Reached job cap (20). Stopping.")
                break

    print(f"\nScaling test finished. Results saved to {csv_path}")


if __name__ == '__main__':
    main()

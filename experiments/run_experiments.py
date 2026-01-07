"""Runner for experiments: executes solvers over instances and records results.

Behavior:
- Generates 25 random instances using src.core.generator.generate_instance (max 30 jobs, 9 machines, 10 resources).
- Loads 5 fixed instances from data/sample.json (takes first 5 keys present there).
- For each instance runs each solver 10 times with different seeds.
- Applies a timeout per solver run (default 300s).
- Records: instance_id, solver, run_id, seed, makespan, runtime, status.
- Writes results to experiments/results.csv

This script imports solvers as Python modules. It expects the solvers to expose a function `solve_instance(data, seed, timeout)` that returns a dict with keys {"makespan", "runtime", "status"}.
If such API is not present, the helper `_run_solver_via_cli` tries to call a CLI script `python -m src.solvers.<solver_module> --instance <json>` which should be adapted as needed.
"""

import os
import json
import time
import csv
import random
import signal
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any

# Constants
ROOT = Path(__file__).resolve().parents[1]
# Ensure local 'src' package is importable when running the script directly
import sys
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
DATA_DIR = ROOT / 'data'
RESULTS_CSV = Path(__file__).resolve().parent / 'results.csv'
SAMPLE_JSON = DATA_DIR / 'sample.json'
GENERATOR_MODULE = 'src.core.generator'

# Experiment parameters
NUM_RANDOM = 25
RANDOM_MAX_JOBS = 11
RANDOM_MAX_MACHINES = 5
RANDOM_MAX_RESOURCES = 5
RUNS_PER_INSTANCE = 1
TIMEOUT = 600  # seconds per run

# Solvers to test: map logical name -> (importable module under src.solvers, SolverClassName)
SOLVERS = {
    'bruteforce': ('src.solvers.bruteforce', 'BruteForceSolver'),
    'earliest_start': ('src.solvers.earliest_start_solver', 'EarliestStartSolver'),
    'genetic': ('src.solvers.metaheuristic', 'GeneticSolver'),
    #'greedy': ('src.solvers.greedy', 'GreedySolver'),
    #'simulated_annealing': ('src.solvers.simulated_annealing', 'SimulatedAnnealingSolver')
}


# Utility: load generator
def _import_generator():
    try:
        gen_mod = __import__(GENERATOR_MODULE, fromlist=['generate_random_instance'])
        return gen_mod
    except Exception as e:
        print('Error importing generator module:', e)
        return None


# Utility: load sample instances (take first k entries)
def load_sample_instances(k: int = 5):
    try:
        with open(SAMPLE_JSON, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f'Error reading sample.json: {e}')
        return []
    items = list(data.items())[:k]
    instances = []
    for name, content in items:
        # support either {"data": {...}} or direct structure
        inst_data = content.get('data') if isinstance(content, dict) and 'data' in content else content
        instances.append((name, inst_data))
    return instances


# Helper: run solver by invoking experiments/solver_runner.py which instantiates solver classes safely
def _run_solver_via_module(module_path: str, instance_data: Dict[str, Any], class_name: str, seed: int, timeout: int) -> Dict[str, Any]:
    """Invoke experiments/solver_runner.py as subprocess and parse JSON output."""
    try:
        # write instance to a unique temp file per call
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.json') as tf:
            json.dump(instance_data, tf)
            tmp_path = Path(tf.name)

        runner = Path(__file__).resolve().parent / 'solver_runner.py'
        cmd = [sys.executable, str(runner), module_path, str(tmp_path), class_name, str(seed)]
        start = time.time()
        env = os.environ.copy()
        # ensure subprocess can import local package 'src'
        env['PYTHONPATH'] = str(ROOT)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        try:
            out, err = p.communicate(timeout=timeout)
            runtime = time.time() - start
            # attempt to parse stdout as json
            try:
                parsed = json.loads(out.decode()) if out else {}
                # merge stderr into parsed error if present
                if err and not parsed.get('error'):
                    parsed['stderr'] = err.decode()
                parsed.setdefault('runtime', runtime)
                return parsed
            except Exception:
                return {'status': 'error', 'makespan': None, 'runtime': runtime, 'error': err.decode(), 'stdout': out.decode()}
        except subprocess.TimeoutExpired:
            p.kill()
            return {'status': 'timeout', 'makespan': None, 'runtime': timeout}
        finally:
            try:
                tmp_path.unlink()
            except Exception:
                pass
    except Exception as e:
        return {'status': 'error', 'makespan': None, 'runtime': 0, 'error': str(e)}


def main():
    # prepare results file
    RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ['instance_id', 'solver', 'run_id', 'seed', 'makespan', 'runtime', 'status', 'error']
    with open(RESULTS_CSV, 'w', newline='') as csvf:
        writer = csv.DictWriter(csvf, fieldnames=fieldnames)
        writer.writeheader()

    # import generator
    gen = _import_generator()
    random_instances = []
    if gen is not None:
        for i in range(NUM_RANDOM):
            d = gen.generate_random_instance(
                max_jobs=RANDOM_MAX_JOBS,
                max_machines=RANDOM_MAX_MACHINES,
                max_resources=RANDOM_MAX_RESOURCES,
                max_duration=20,
                max_resource_qty=3
            )
            random_instances.append((f'random_{i+1}', d))
    else:
        print('Generator not available; no random instances created.')

    sample_instances = load_sample_instances(5)

    instances = random_instances + sample_instances
    print(f'Running experiments on {len(instances)} instances')

    # main loop
    for inst_id, inst_data in instances:
        for solver_name, solver_info in SOLVERS.items():
            module_path, class_name = solver_info
            for run_id in range(1, RUNS_PER_INSTANCE + 1):
                seed = random.randint(0, 2**31 - 1)
                print(f'Instance {inst_id} | Solver {solver_name} | run {run_id} | seed {seed}')
                res = _run_solver_via_module(module_path, inst_data, class_name, seed, TIMEOUT)
                row = {
                    'instance_id': inst_id,
                    'solver': solver_name,
                    'run_id': run_id,
                    'seed': seed,
                    'makespan': res.get('makespan'),
                    'runtime': res.get('runtime'),
                    'status': res.get('status'),
                    'error': res.get('error') or res.get('stderr') or None
                }
                with open(RESULTS_CSV, 'a', newline='') as csvf:
                    writer = csv.DictWriter(csvf, fieldnames=fieldnames)
                    writer.writerow(row)

    print('Experiments finished. Results in', RESULTS_CSV)


if __name__ == '__main__':
    main()

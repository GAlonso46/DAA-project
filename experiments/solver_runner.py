#!/usr/bin/env python3
"""Helper runner invoked by experiments/run_experiments.py.
Usage: solver_runner.py <module_path> <instance_json> <class_name> <seed>
If <class_name> is empty string, the runner will pick the first class name containing 'Solver'.
Outputs a single JSON line with keys: status, makespan, runtime, error (optional), log (captured stdout/stderr from solver).
"""
import sys
import json
import time
import random
import traceback
import io
import contextlib

from pathlib import Path

# Make project root importable (so 'src' package can be imported when running this script directly)
ROOT = Path(__file__).resolve().parents[1]
import sys
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def build_problem_from_data(data):
    # Import here to ensure correct PYTHONPATH
    from src.core.model import ProblemInstance, Job
    num_machines = data.get('num_machines')
    resources = data.get('resources', {})
    jobs_raw = data.get('jobs', [])
    jobs = []
    for j in jobs_raw:
        jid = j.get('id')
        dur = j.get('duration')
        req = j.get('requirements', {})
        jobs.append(Job(id=jid, duration=dur, resource_requirements=req))
    return ProblemInstance(num_machines=num_machines, resources=resources, jobs=jobs)


def main():
    if len(sys.argv) < 4:
        print(json.dumps({'status': 'error', 'error': 'Usage: solver_runner.py <module_path> <instance_json> <class_name> <seed>'}))
        sys.exit(1)
    module_path = sys.argv[1]
    instance_file = sys.argv[2]
    class_name = sys.argv[3]
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else None

    random.seed(seed)

    try:
        data = json.loads(Path(instance_file).read_text())
    except Exception as e:
        print(json.dumps({'status': 'error', 'error': f'Cannot read instance: {e}'}))
        sys.exit(1)

    # If user passed a file containing many instances (like sample.json), extract first 'data' block
    if isinstance(data, dict) and 'num_machines' not in data:
        for v in data.values():
            if isinstance(v, dict) and 'data' in v:
                data = v['data']
                break

    try:
        mod = __import__(module_path, fromlist=['*'])
    except Exception as e:
        print(json.dumps({'status': 'error', 'error': f'Cannot import module {module_path}: {e}'}))
        sys.exit(1)

    # Determine class name
    if not class_name:
        # pick first attribute with 'Solver' in name
        candidates = [name for name in dir(mod) if 'Solver' in name]
        if not candidates:
            print(json.dumps({'status': 'error', 'error': f'No Solver class found in {module_path}'}))
            sys.exit(1)
        class_name = candidates[0]

    if not hasattr(mod, class_name):
        print(json.dumps({'status': 'error', 'error': f'Module {module_path} has no class {class_name}'}))
        sys.exit(1)

    SolverClass = getattr(mod, class_name)

    try:
        problem = build_problem_from_data(data)
    except Exception as e:
        print(json.dumps({'status': 'error', 'error': f'Cannot build ProblemInstance: {e}'}))
        sys.exit(1)

    try:
        solver = SolverClass(problem)
    except TypeError:
        # try with different constructor signature (max_combinations for brute force)
        try:
            solver = SolverClass(problem, max_combinations=1000000)
        except Exception as e:
            print(json.dumps({'status': 'error', 'error': f'Cannot instantiate solver class: {e}'}))
            sys.exit(1)

    start = time.time()
    try:
        # Capture any stdout/stderr from solver.solve
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            sol = solver.solve()
        runtime = time.time() - start
        makespan = None
        try:
            makespan = getattr(sol, 'makespan', None)
        except Exception:
            makespan = None
        log = buf.getvalue()
        print(json.dumps({'status': 'ok', 'makespan': makespan, 'runtime': runtime, 'log': log}))
    except Exception as e:
        tb = traceback.format_exc()
        # include captured logs as well
        try:
            log = buf.getvalue()
        except Exception:
            log = ''
        print(json.dumps({'status': 'error', 'error': str(e), 'traceback': tb, 'log': log}))
        sys.exit(1)

if __name__ == '__main__':
    main()

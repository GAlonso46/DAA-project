"""Simple analysis and plotting for experiments/results.csv

Generates:
 - experiments/plots/box_relative_error.png  (boxplot of relative error per solver)
 - experiments/plots/box_runtime.png         (boxplot of runtime per solver, log scale)
 - experiments/plots/scatter_runtime_quality.png (scatter runtime vs relative error)
 - experiments/plots/summary_by_solver.csv   (aggregated statistics)

Usage:
  python experiments/analysis.py

Requirements: pandas, seaborn, matplotlib
Install with: pip install pandas seaborn matplotlib
"""
import os
from pathlib import Path
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
RESULTS_CSV = ROOT / 'results.csv'
PLOTS_DIR = ROOT / 'plots'
PLOTS_DIR.mkdir(exist_ok=True)

if not RESULTS_CSV.exists():
    raise SystemExit(f"Results file not found: {RESULTS_CSV}")

# Read results
df = pd.read_csv(RESULTS_CSV)
# Normalize column names
df.columns = [c.strip() for c in df.columns]

# Convert numeric columns
df['runtime'] = pd.to_numeric(df['runtime'], errors='coerce')
# makespan may be string if missing
df['makespan'] = pd.to_numeric(df['makespan'], errors='coerce')

# Filter successful runs
ok = df[df['status'] == 'ok'].copy()
if ok.empty:
    print('No successful runs found in results.csv')

# Compute per-instance best known makespan (oracle = minimal observed among successful runs)
best_per_instance = ok.groupby('instance_id')['makespan'].min().rename('best_makespan')
ok = ok.join(best_per_instance, on='instance_id')

# Compute relative error = (makespan / best) - 1
ok['relative_error'] = (ok['makespan'] / ok['best_makespan']) - 1.0

# Save summary statistics per solver
agg = ok.groupby('solver').agg(
    runs=('run_id','count'),
    median_rel_error=('relative_error','median'),
    mean_rel_error=('relative_error','mean'),
    std_rel_error=('relative_error','std'),
    median_runtime=('runtime','median'),
    mean_runtime=('runtime','mean'),
    std_runtime=('runtime','std')
).reset_index()
agg.to_csv(PLOTS_DIR / 'summary_by_solver.csv', index=False)
print('Summary written to', PLOTS_DIR / 'summary_by_solver.csv')

sns.set(style='whitegrid')

# Boxplot of relative error per solver
plt.figure(figsize=(10,6))
ax = sns.boxplot(data=ok, x='solver', y='relative_error')
ax.set_ylabel('Relative error (makespan / best - 1)')
ax.set_title('Relative solution quality by solver')
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(PLOTS_DIR / 'box_relative_error.png', dpi=200)
plt.close()
print('Saved', PLOTS_DIR / 'box_relative_error.png')

# Boxplot of runtime per solver (log scale)
plt.figure(figsize=(10,6))
ax = sns.boxplot(data=ok, x='solver', y='runtime')
ax.set_yscale('log')
ax.set_ylabel('Runtime (s) [log scale]')
ax.set_title('Runtime by solver (log scale)')
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(PLOTS_DIR / 'box_runtime.png', dpi=200)
plt.close()
print('Saved', PLOTS_DIR / 'box_runtime.png')

# Scatter runtime vs relative_error (per run)
plt.figure(figsize=(8,6))
# limit extreme relative errors for plotting clarity
plot_df = ok.copy()
plot_df = plot_df.replace([np.inf, -np.inf], np.nan).dropna(subset=['relative_error','runtime'])
plot_df['rel_clip'] = plot_df['relative_error'].clip(upper=5)
ax = sns.scatterplot(data=plot_df, x='runtime', y='rel_clip', hue='solver', alpha=0.7)
ax.set_xscale('log')
ax.set_xlabel('Runtime (s) [log scale]')
ax.set_ylabel('Relative error (clipped at 5)')
ax.set_title('Runtime vs Solution Quality')
plt.legend(bbox_to_anchor=(1.05,1), loc='upper left')
plt.tight_layout()
plt.savefig(PLOTS_DIR / 'scatter_runtime_quality.png', dpi=200)
plt.close()
print('Saved', PLOTS_DIR / 'scatter_runtime_quality.png')

print('Done.')

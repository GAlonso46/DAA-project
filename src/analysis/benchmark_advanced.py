
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.patches as patches

from src.core.generator import generate_instance
from src.core.model import Job, ProblemInstance
from src.solvers.greedy import GreedySolver
from src.solvers.metaheuristic import GeneticSolver
from src.solvers.simulated_annealing import SimulatedAnnealingSolver
from src.solvers.tabu_search import TabuSearchSolver
from src.utils.advanced_visualizer import AdvancedVisualizer

def run_advanced_benchmark():
    print("--- 🚀 Iniciando Benchmark Comparativo Completo ---")
    
    # 1. Configuración del problema (Instancia Retadora)
    data = generate_instance(num_jobs=300, num_machines=10, num_resources=5)
    
    jobs = [Job(j['id'], j['duration'], {int(k): v for k, v in j['requirements'].items()}) for j in data['jobs']]
    resources = {int(k): v for k, v in data['resources'].items()}
    problem = ProblemInstance(data['num_machines'], resources, jobs)
    
    # 2. Configurar Solvers
    ga_solver = GeneticSolver(problem, pop_size=100, generations=200, mutation_rate=0.25)
    sa_solver = SimulatedAnnealingSolver(problem, max_iter=2000)
    tabu_solver = TabuSearchSolver(problem, max_iter=800)
    greedy_solver = GreedySolver(problem)
    
    solvers = [
        ('Greedy', greedy_solver, lambda s: s.solve('LPT')),
        ('GeneticAlgo', ga_solver, lambda s: s.solve()),
        ('SimAnnealing', sa_solver, lambda s: s.solve()),
        ('TabuSearch', tabu_solver, lambda s: s.solve())
    ]
    
    results_data = []      
    solutions_map = {}     
    histories_map = {}     
    
    print("Ejecutando algoritmos...")
    
    for name, solver_obj, solve_func in solvers:
        print(f"  > {name}...", end=" ")
        start_t = time.time()
        
        try:
            solution = solve_func(solver_obj)
            elapsed = time.time() - start_t
            print(f"Makespan: {solution.makespan} ({elapsed:.2f}s)")
            
            results_data.append({
                'Algoritmo': name,
                'Makespan': solution.makespan,
                'Tiempo': elapsed
            })
            solutions_map[name] = solution
            
            if hasattr(solver_obj, 'history'):
                histories_map[name] = solver_obj.history
        except Exception as e:
            print(f"Error en {name}: {e}")

    # 3. Generación de Gráficos "Comparativos"
    print("\nGenerando Paneles Comparativos...")
    
    # A. Panel de GANNTs
    plot_comparative_gantts(solutions_map, problem, "comparativa_A_gantts.png")
    
    # B. Panel de RECURSOS
    if 'GeneticAlgo' in solutions_map:
        critical_res_id = find_critical_resource(problem, solutions_map['GeneticAlgo']) 
        plot_comparative_resources(solutions_map, problem, critical_res_id, "comparativa_B_recursos.png")
    
    # Crear DataFrame PRIMERO
    df = pd.DataFrame(results_data)

    # C. Convergencia Combinada (Ahora pasamos el DF correcto)
    plot_combined_convergence(histories_map, df, "comparativa_C_convergencia.png")
    
    # D. Resumen de Barras
    plot_summary_bars(df, "comparativa_D_resumen.png")
    
    # 4. Generar Informe
    generate_comparative_report(df)
    print("\n¡Proceso Finalizado!")

def plot_comparative_gantts(solutions_map, problem, filename):
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    axes = axes.flatten()
    
    cmap = plt.get_cmap('tab10')
    res_colors = {i: cmap(i % 10) for i in range(1, 11)}
    
    algo_names = list(solutions_map.keys())
    for i in range(len(algo_names), 4):
        fig.delaxes(axes[i])
    
    max_ms = max((s.makespan for s in solutions_map.values()), default=100)
    
    for idx, name in enumerate(algo_names):
        if idx >= 4: break 
        ax = axes[idx]
        sol = solutions_map[name]
        
        for job in sol.jobs:
            dom_res = max(job.resource_requirements, key=job.resource_requirements.get) if job.resource_requirements else 0
            color = res_colors.get(dom_res, 'lightgray')
            y_pos = job.assigned_machine - 1
            rect = patches.Rectangle((job.start_time, y_pos+0.1), job.duration, 0.8, 
                                     facecolor=color, edgecolor='white', alpha=0.9)
            ax.add_patch(rect)
        
        ax.set_title(f"{name} (Makespan: {sol.makespan})", fontsize=12, weight='bold')
        ax.set_yticks(range(problem.num_machines))
        ax.set_yticklabels([f"M{i+1}" for i in range(problem.num_machines)])
        ax.set_ylim(-0.2, problem.num_machines)
        ax.set_xlim(0, max_ms + 5)
        ax.grid(True, axis='x', linestyle='--', alpha=0.3)
        
    handles = [patches.Patch(color=res_colors[i], label=f"Recurso {i}") for i in problem.resources]
    fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, 0.05), ncol=len(problem.resources), title="Recursos")
    
    plt.suptitle("Comparativa Visual de Planificación (Gantt)", fontsize=16)
    plt.tight_layout(rect=[0, 0.06, 1, 0.95])
    plt.savefig(filename, dpi=150)
    print(f"Generado: {filename}")
    plt.close()

def plot_comparative_resources(solutions_map, problem, res_id, filename):
    fig, axes = plt.subplots(2, 2, figsize=(16, 8))
    axes = axes.flatten()
    cap = problem.resources[res_id]
    
    algo_names = list(solutions_map.keys())
    max_time = max((s.makespan for s in solutions_map.values()), default=100) + 5
    
    for i in range(len(algo_names), 4):
        fig.delaxes(axes[i])

    for idx, name in enumerate(algo_names):
        if idx >= 4: break 
        ax = axes[idx]
        sol = solutions_map[name]
        
        usage = np.zeros(int(max_time))
        for job in sol.jobs:
            start = int(job.start_time)
            end = int(job.start_time + job.duration)
            if end > len(usage):
                usage = np.pad(usage, (0, end - len(usage)))
            
            qty = job.resource_requirements.get(res_id, 0)
            if qty > 0:
                usage[start:end] += qty
                
        ax.step(range(len(usage)), usage, where='post', color='#2980b9', lw=2)
        ax.axhline(cap, color='red', ls='--', lw=2, label='Capacidad')
        ax.fill_between(range(len(usage)), usage, step='post', alpha=0.3, color='#3498db')
        
        ax.set_title(f"{name} - Uso Recurso {res_id}", fontsize=11)
        ax.set_ylim(0, cap * 1.5)
        ax.set_xlim(0, max_time)
        ax.grid(True, alpha=0.3)
        
    plt.suptitle(f"Perfil de Carga: Recurso Crítico {res_id} (Capacidad: {cap})", fontsize=16)
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    print(f"Generado: {filename}")
    plt.close()

def plot_combined_convergence(histories, results_df, filename):
    plt.figure(figsize=(12, 6))
    
    colors = {'GeneticAlgo': '#2ecc71', 'SimAnnealing': '#e74c3c', 'TabuSearch': '#9b59b6'}
    
    for name, history in histories.items():
        if name not in colors: continue
        plt.plot(history, label=name, color=colors[name], lw=2)
        
    if not results_df.empty and 'Makespan' in results_df.columns:
        greedy_rows = results_df.loc[results_df['Algoritmo'] == 'Greedy']
        if not greedy_rows.empty:
            greedy_val = greedy_rows['Makespan'].values[0]
            plt.axhline(greedy_val, color='gray', linestyle='--', label=f'Greedy Baseline ({greedy_val})', lw=2)
    
    plt.xlabel("Iteraciones / Generaciones")
    plt.ylabel("Makespan (Menor es Mejor)")
    plt.title("Comparativa de Convergencia: Velocidad de Mejora", fontsize=16)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    
    plt.savefig(filename, dpi=150)
    print(f"Generado: {filename}")
    plt.close()

def plot_summary_bars(df, filename):
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Algoritmo', y='Makespan', data=df, palette='viridis')
    plt.title("Resumen Final: ¿Quién ganó?", fontsize=16)
    plt.savefig(filename)
    plt.close()

def find_critical_resource(problem, solution):
    total_usage = {r: 0 for r in problem.resources}
    for job in solution.jobs:
        for r, q in job.resource_requirements.items():
            total_usage[r] += q * job.duration
    return max(total_usage, key=total_usage.get)

def generate_comparative_report(df):
    if df.empty:
        print("No results to report.")
        return

    best = df.loc[df['Makespan'].idxmin()]
    md = f"""# Informe Comparativo Completo
    
## Resumen Ejecutivo
El algoritmo ganador fue **{best['Algoritmo']}** con un makespan de **{best['Makespan']}**.

{df.to_markdown(index=False)}

## Análisis de Gráficos

### 1. Comparativa de Gantts (`comparativa_A_gantts.png`)
Este panel 2x2 muestra la estrategia de cada algoritmo.
*   Compara la longitud total de los bloques (Makespan).
*   Observa cómo *Greedy* suele apilar bloques sin optimizar huecos ("tetris" desordenado), mientras que *GeneticAlgo* y *SimAnnealing* logran arreglos más compactos.

### 2. Comparativa de Recursos (`comparativa_B_recursos.png`)
Muestra el uso del recurso crítico (Cuello de Botella) por algoritmo.
*   El objetivo ideal es una "meseta" constante justo por debajo de la línea roja (saturación óptima).
*   Si ves muchos valles en el Greedy, significa que máquinas están paradas esperando recursos innecesariamente.

### 3. Convergencia Combinada (`comparativa_C_convergencia.png`)
Muestra la "carrera" entre metaheurísticas.
*   **Simulated Annealing** suele bajar muy rápido al principio.
*   **Genetic Algo** baja más suavemente pero a menudo llega a mejores óptimos finales si se le da tiempo.
*   La línea punteada gris es la referencia del **Greedy**: todo lo que esté por debajo es ganancia pura.
"""
    with open("Informe_Comparativo_Full.md", "w", encoding='utf-8') as f:
        f.write(md)
    print("Informe generado: Informe_Comparativo_Full.md")

if __name__ == "__main__":
    run_advanced_benchmark()

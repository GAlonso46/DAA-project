import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from src.core.model import Solution, ProblemInstance

class AdvancedVisualizer:
    def __init__(self, solution: Solution, problem: ProblemInstance):
        self.solution = solution
        self.problem = problem

    def plot_rich_gantt(self, save_path="rich_gantt.png"):
        """
        Plots Gantt chart colored by the primary resource used by each job.
        (Versión en Español)
        """
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Define colors for Resource IDs
        cmap = plt.get_cmap('tab10')
        res_colors = {i: cmap(i % 10) for i in range(1, 11)}
        
        for job in self.solution.jobs:
            if job.resource_requirements:
                dominant_res = max(job.resource_requirements, key=job.resource_requirements.get)
            else:
                dominant_res = 0 # No resource
            
            color = res_colors.get(dominant_res, 'gray')
            if dominant_res == 0: color = 'lightgray'

            y_pos = job.assigned_machine - 1
            
            # Draw Job Bar
            rect = patches.Rectangle(
                (job.start_time, y_pos + 0.1), 
                job.duration, 
                0.8, 
                linewidth=1, 
                edgecolor='white', 
                facecolor=color, 
                alpha=0.9
            )
            ax.add_patch(rect)
            
            # Label: JobID (DomRes)
            if job.duration >= 2:
                cx = job.start_time + job.duration / 2.0
                cy = y_pos + 0.5
                label = f"T{job.id}\n(R{dominant_res})"
                ax.annotate(label, (cx, cy), color='white', weight='bold', 
                            fontsize=8, ha='center', va='center')

        # Formatting
        ax.set_yticks(range(self.problem.num_machines))
        ax.set_yticklabels([f"Máquina {i+1}" for i in range(self.problem.num_machines)], fontsize=11)
        ax.set_xlabel("Tiempo (Unidades)", fontsize=12)
        ax.set_title("Diagrama de Gantt 'Rico' (Coloreado por Recurso Principal)", fontsize=16, pad=20)
        ax.grid(True, axis='x', linestyle='--', alpha=0.3)
        
        ax.set_xlim(0, max(self.solution.makespan + 5, 20))
        ax.set_ylim(-0.2, self.problem.num_machines)
        
        # Legend (Español)
        handles = [patches.Patch(color=res_colors[i], label=f"Recurso {i}") 
                   for i in self.problem.resources.keys()]
        ax.legend(handles=handles, title="Tipo de Herramienta", loc='upper right', bbox_to_anchor=(1.1, 1))
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300)
            print(f"Gráfico guardado: {save_path}")
        else:
            plt.show()
        plt.close()

    def plot_resource_profile(self, save_path="resource_profile.png"):
        """
        Plots the usage profile vs capacity.
        (Versión en Español: Perfil de Carga)
        """
        msg_len = int(self.solution.makespan + 5)
        usage_data = {r_id: np.zeros(msg_len) for r_id in self.problem.resources}
        
        for job in self.solution.jobs:
            start = int(job.start_time)
            end = int(start + job.duration)
            for r_id, qty in job.resource_requirements.items():
                if r_id in usage_data:
                    usage_data[r_id][start:end] += qty

        num_res = len(self.problem.resources)
        fig, axes = plt.subplots(num_res, 1, figsize=(12, 3 * num_res), sharex=True)
        if num_res == 1: axes = [axes]
        
        for idx, r_id in enumerate(self.problem.resources):
            ax = axes[idx]
            capacity = self.problem.resources[r_id]
            
            # Step Plot
            ax.step(range(msg_len), usage_data[r_id], where='post', label=f'Uso Real R{r_id}', color='#2980b9', linewidth=2)
            
            # Capacity Line (Red)
            ax.axhline(y=capacity, color='#c0392b', linestyle='--', linewidth=2.5, label=f'Capacidad Máx ({capacity})')
            
            # Fill Area
            ax.fill_between(range(msg_len), usage_data[r_id], step='post', alpha=0.25, color='#3498db')
            
            ax.set_ylabel(f"Cant. Recurso {r_id}", fontsize=11)
            ax.set_title(f"Perfil de Uso: Recurso Especializado {r_id}", fontsize=13)
            ax.legend(loc='upper right')
            ax.grid(True, alpha=0.3)
            
            # Check for violations visually
            max_usage = np.max(usage_data[r_id])
            if max_usage > capacity:
                 ax.text(0.01, 0.9, '⚠️ SOBRECARGA DETECTADA', transform=ax.transAxes, color='red', weight='bold')

            if idx == num_res - 1:
                ax.set_xlabel("Tiempo (h)", fontsize=12)

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300)
            print(f"Gráfico guardado: {save_path}")
        else:
            plt.show()
        plt.close()

    @staticmethod
    def plot_convergence(history_best, history_avg=None, save_path="convergence.png"):
        """
        Plot Genetic Algorithm convergence.
        """
        plt.figure(figsize=(10, 6))
        
        plt.plot(history_best, label='Mejor Makespan (Líder)', linewidth=2.5, color='#2ecc71')
        if history_avg:
            plt.plot(history_avg, label='Makespan Promedio (Población)', linestyle='--', alpha=0.6, color='#27ae60')
            
        plt.xlabel('Generaciones', fontsize=12)
        plt.ylabel('Makespan (Menor es Mejor)', fontsize=12)
        plt.title('Curva de Convergencia del Algoritmo Genético', fontsize=16)
        plt.legend(fontsize=11)
        plt.grid(True, linestyle='--', alpha=0.5)
        
        # Annotate start and end
        start_val = history_best[0]
        end_val = history_best[-1]
        plt.scatter([0], [start_val], color='black')
        plt.text(0, start_val + 2, f'{start_val:.0f}', ha='center')
        
        plt.scatter([len(history_best)-1], [end_val], color='red')
        plt.text(len(history_best)-1, end_val - 5, f'{end_val:.0f}', ha='center', weight='bold', color='red')
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300)
            print(f"Gráfico guardado: {save_path}")
        else:
            plt.show()
        plt.close()

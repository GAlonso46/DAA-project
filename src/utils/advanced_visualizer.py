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
        """
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Define colors for Resource IDs (assuming IDs 1..5 for simplicity)
        # Tab10 palette
        cmap = plt.get_cmap('tab10')
        res_colors = {i: cmap(i % 10) for i in range(1, 11)}
        
        for job in self.solution.jobs:
            # Determine dominant resource (max qty)
            if job.resource_requirements:
                dominant_res = max(job.resource_requirements, key=job.resource_requirements.get)
            else:
                dominant_res = 0 # No resource
            
            color = res_colors.get(dominant_res, 'gray')
            if dominant_res == 0: color = 'lightgray'

            y_pos = job.assigned_machine - 1
            
            rect = patches.Rectangle(
                (job.start_time, y_pos + 0.1), 
                job.duration, 
                0.8, 
                linewidth=1, 
                edgecolor='white', 
                facecolor=color, 
                alpha=0.85
            )
            ax.add_patch(rect)
            
            # Label: JobID (ResID)
            cx = job.start_time + job.duration / 2.0
            cy = y_pos + 0.5
            label = f"J{job.id}\n(R{dominant_res})"
            if job.duration >= 2: # Only label if big enough
                ax.annotate(label, (cx, cy), color='white', weight='bold', 
                            fontsize=8, ha='center', va='center')

        ax.set_yticks(range(self.problem.num_machines))
        ax.set_yticklabels([f"Mach {i+1}" for i in range(self.problem.num_machines)])
        ax.set_xlabel("Time")
        ax.set_title("Rich Gantt Chart (Colored by Dominant Resource)")
        ax.grid(True, axis='x', linestyle='--', alpha=0.3)
        
        ax.set_xlim(0, self.solution.makespan + 2)
        ax.set_ylim(-0.2, self.problem.num_machines)
        
        # Legend
        handles = [patches.Patch(color=res_colors[i], label=f"Resource {i}") 
                   for i in self.problem.resources.keys()]
        ax.legend(handles=handles, loc='upper right')
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path)
            print(f"Rich Gantt saved to {save_path}")
        else:
            plt.show()

    def plot_resource_profile(self, save_path="resource_profile.png"):
        """
        Plots the usage profile for each resource over time vs capacity.
        """
        # 1. Calculate usage timeline
        msg_len = self.solution.makespan + 5
        # Dictionary of ResourceID -> Array of usage over time
        usage_data = {r_id: np.zeros(msg_len) for r_id in self.problem.resources}
        
        for job in self.solution.jobs:
            start = job.start_time
            end = start + job.duration
            for r_id, qty in job.resource_requirements.items():
                if r_id in usage_data:
                    usage_data[r_id][start:end] += qty

        # 2. Plot subplots for each resource
        num_res = len(self.problem.resources)
        fig, axes = plt.subplots(num_res, 1, figsize=(10, 3 * num_res), sharex=True)
        if num_res == 1: axes = [axes]
        
        for idx, r_id in enumerate(self.problem.resources):
            ax = axes[idx]
            capacity = self.problem.resources[r_id]
            
            # Step plot
            ax.step(range(msg_len), usage_data[r_id], where='post', label=f'Usage R{r_id}', color='#3498db')
            ax.axhline(y=capacity, color='red', linestyle='--', linewidth=2, label='Capacity')
            
            # Fill under area
            ax.fill_between(range(msg_len), usage_data[r_id], step='post', alpha=0.3, color='#3498db')
            
            ax.set_ylabel(f"Resource {r_id} Qty")
            ax.set_title(f"Resource {r_id} Utilization Profile")
            ax.legend(loc='upper right')
            ax.grid(True, alpha=0.3)
            
            if idx == num_res - 1:
                ax.set_xlabel("Time")

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path)
            print(f"Resource Profile saved to {save_path}")
        else:
            plt.show()

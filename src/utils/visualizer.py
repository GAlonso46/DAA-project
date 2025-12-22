import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
from src.core.model import Solution

def plot_gantt(solution: Solution, num_machines: int, title: str = "Schedule Gantt Chart", save_path: str = None):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Colors for jobs
    colors = {}
    
    # Track max time for x-axis limit
    max_time = solution.makespan
    
    for job in solution.jobs:
        if job.id not in colors:
            colors[job.id] = (random.random(), random.random(), random.random())
            
        # Machine ID is 1-based, map to y-axis
        # We plot Machine 1 at y=num_machines-1, Machine M at y=0 so M1 is top?
        # Or standard y=axis. Let's do Machine 1 at bottom (y=0).
        y_pos = job.assigned_machine - 1
        
        # Draw rectangle
        # (x, y), width, height
        rect = patches.Rectangle(
            (job.start_time, y_pos + 0.1), 
            job.duration, 
            0.8, 
            linewidth=1, 
            edgecolor='black', 
            facecolor=colors[job.id], 
            alpha=0.7
        )
        ax.add_patch(rect)
        
        # Add text
        rx, ry = rect.get_xy()
        cx = rx + rect.get_width() / 2.0
        cy = ry + rect.get_height() / 2.0
        ax.annotate(f"J{job.id}", (cx, cy), color='black', weight='bold', 
                    fontsize=9, ha='center', va='center')

    ax.set_yticks(range(num_machines))
    ax.set_yticklabels([f"Machine {i+1}" for i in range(num_machines)])
    ax.set_xlabel("Time")
    ax.set_title(title)
    ax.grid(True, axis='x', linestyle='--', alpha=0.5)
    
    ax.set_xlim(0, max_time + 2)
    ax.set_ylim(-0.2, num_machines)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
        print(f"Chart saved to {save_path}")
    else:
        plt.show()

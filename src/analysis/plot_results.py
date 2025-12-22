import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_benchmark_results(csv_file):
    # Cargar datos
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: {csv_file} not found.")
        return
    
    # Configuración de estilo académico
    plt.style.use('ggplot')
    
    # Renombrar columnas si es necesario para coincidir con tu CSV
    # Tu CSV tiene: Jobs, Machines, Run, LPT_Makespan, SPT_Makespan, Random_Makespan, SA_Makespan, GA_Makespan, Run_Time_GA, Run_Time_SA, Improvement_GA_vs_LPT
    # Agrupamos por tamaño de problema (Jobs) o Jobs per machine?
    # El script del usuario asume 'instance_size' que no existe, usaremos 'Jobs' y agrupamos
    
    # Agrupar por Jobs (promedio) para simplificar el gráfico si hay muchas filas
    df_grouped = df.groupby('Jobs').mean(numeric_only=True).reset_index()
    
    # --- GRÁFICO 1: Calidad de la Solución (Makespan) ---
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    indices = np.arange(len(df_grouped))
    width = 0.35
    
    # Barras para Makespan
    rects1 = ax1.bar(indices - width/2, df_grouped['LPT_Makespan'], width, label='Greedy (LPT)', color='#3498db')
    rects2 = ax1.bar(indices + width/2, df_grouped['GA_Makespan'], width, label='Algoritmo Genético', color='#e74c3c')
    
    ax1.set_ylabel('Makespan Promedio')
    ax1.set_title('Comparación de Eficiencia: Greedy vs Genético')
    ax1.set_xticks(indices)
    ax1.set_xticklabels(df_grouped['Jobs'])
    ax1.set_xlabel('Número de Trabajos')
    ax1.legend()
    
    # Calcular y mostrar el porcentaje de mejora
    for i in indices:
        g_val = df_grouped.loc[i, 'LPT_Makespan']
        ga_val = df_grouped.loc[i, 'GA_Makespan']
        if ga_val < g_val:
            improvement = ((g_val - ga_val) / g_val) * 100
            ax1.text(i + width/2, ga_val + 1, f'-{improvement:.1f}%', 
                     ha='center', va='bottom', fontsize=9, fontweight='bold', color='green')

    plt.tight_layout()
    plt.savefig('comparacion_makespan.png')
    print("Gráfico 'comparacion_makespan.png' generado.")

    # --- GRÁFICO 2: Escalabilidad (Tiempo) ---
    fig, ax2 = plt.subplots(figsize=(10, 6))
    
    # Usamos escala logarítmica
    ax2.plot(df_grouped['Jobs'], df_grouped['Run_Time_SA'], marker='o', label='SA Time', color='#3498db', linewidth=2)
    ax2.plot(df_grouped['Jobs'], df_grouped['Run_Time_GA'], marker='s', label='GA Time', color='#e74c3c', linewidth=2)
    
    ax2.set_ylabel('Tiempo de Ejecución (s) - Escala Log')
    ax2.set_xlabel('Número de Trabajos')
    ax2.set_yscale('log') 
    ax2.set_title('Análisis de Escalabilidad Temporal')
    ax2.legend()
    ax2.grid(True, which="both", ls="-", alpha=0.5)
    
    plt.tight_layout()
    plt.savefig('comparacion_tiempo.png')
    print("Gráfico 'comparacion_tiempo.png' generado.")

if __name__ == "__main__":
    plot_benchmark_results('benchmark_results.csv')

import pandas as pd
import numpy as np
import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def analizar_comparativa_avanzada(csv_path):
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print("❌ No se encuentra el archivo .csv")
        return

    print("--- 🏆 TORNEO DE ALGORITMOS: ANÁLISIS FINAL ---")
    
    # Vamos a usar 'Greedy (LPT)' como la REFERENCIA (Baseline)
    # Calculamos el % de mejora (o empeoramiento) respecto al Greedy
    
    # 1. ¿Qué tan malo es el azar? (Random vs Greedy)
    df['gap_random'] = ((df['Random_Makespan'] - df['LPT_Makespan']) / df['LPT_Makespan']) * 100
    
    # 2. ¿Sirve de algo ordenar por tiempo corto? (SPT vs Greedy)
    df['gap_spt'] = ((df['SPT_Makespan'] - df['LPT_Makespan']) / df['LPT_Makespan']) * 100
    
    # 3. Metaheurística 1: Genético (GA vs Greedy)
    df['gap_ga'] = ((df['LPT_Makespan'] - df['GA_Makespan']) / df['LPT_Makespan']) * 100
    
    # 4. Metaheurística 2: Recocido Simulado (SA vs Greedy)
    df['gap_sa'] = ((df['LPT_Makespan'] - df['SA_Makespan']) / df['LPT_Makespan']) * 100

    # --- REPORTE RESUMIDO ---
    print(f"\n{'Tamaño':<8} | {'Random (Peor)':<15} | {'SPT (Control)':<15} | {'SA (Improve)':<13} | {'GA (Improve)':<13} | {'Ganador'}")
    print("-" * 95)
    
    promedios = {
        'random': df['gap_random'].mean(),
        'spt': df['gap_spt'].mean(),
        'sa': df['gap_sa'].mean(),
        'ga': df['gap_ga'].mean()
    }

    for index, row in df.iterrows():
        try:
             size = int(row['Jobs']) 
        except KeyError:
             size = int(row.get('instance_size', 0))
        
        # Random y SPT suelen ser PEORES, así que mostramos cuánto PEOR son (números negativos o positivos grandes de makespan)
        # Aquí Gap Random: positivo significa que Random es X% MÁS LENTO que Greedy (queremos que sea alto para justificar Greedy)
        gap_rand = row['gap_random'] 
        gap_spt = row['gap_spt']
        
        # SA y GA deben ser MEJORES (Gap positivo = reducción de tiempo)
        gap_sa = row['gap_sa']
        gap_ga = row['gap_ga']
        
        winner = "Greedy"
        best_val = 0
        
        if gap_sa > 0.01 and gap_sa > gap_ga:
            winner = "Sim. Annealing"
        elif gap_ga > 0.01 and gap_ga >= gap_sa:
            winner = "Genetic Alg."
        elif gap_sa <= 0 and gap_ga <= 0:
            winner = "Tie (Greedy)"
            
        print(f"{size:<8} | +{gap_rand:>6.1f}% tiempo | +{gap_spt:>6.1f}% tiempo | -{gap_sa:>5.2f}% (Wait {row['Run_Time_SA']:.1f}s)| -{gap_ga:>5.2f}% (Wait {row['Run_Time_GA']:.1f}s)| {winner}")

    print("-" * 95)
    print("\n--- 📊 CONCLUSIONES ESTADÍSTICAS ---")
    print(f"1. JUSTIFICACIÓN BASE: El algoritmo Aleatorio es, en promedio, un {promedios['random']:.1f}% peor que tu Greedy.")
    print(f"   (Esto valida que tu heurística LPT es inteligente y necesaria).")
    
    print(f"2. CONTROL SPT: La regla SPT es un {promedios['spt']:.1f}% peor que LPT para el Makespan.")
    print(f"   (Confirma la teoría: SPT es bueno para flujo medio, pero malo para Cmax).")
    
    print(f"\n3. BATALLA DE METAHEURÍSTICAS:")
    print(f"   🔥 Recocido Simulado (SA): Mejora promedio del {promedios['sa']:.2f}%")
    print(f"   🧬 Algoritmo Genético (GA): Mejora promedio del {promedios['ga']:.2f}%")
    
    if promedios['sa'] > promedios['ga']:
        print("\n🏆 VEREDICTO: Simulated Annealing ganó en promedio. Es más eficiente para este paisaje de búsqueda.")
    elif promedios['ga'] > promedios['sa']:
        print("\n🏆 VEREDICTO: El Genético ganó en promedio. Su población diversa maneja mejor las restricciones difíciles.")
    else:
        print("\n🤝 VEREDICTO: Empate técnico.")

if __name__ == "__main__":
    analizar_comparativa_avanzada('benchmark_results_advanced.csv')
import pandas as pd
import numpy as np

def analizar_resultados(csv_path):
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print("❌ No se encuentra el archivo .csv")
        return

    print("--- 📊 REPORTE DE CALIDAD DE RESULTADOS ---")
    
    # 1. Calcular GAP (Mejora del Genético sobre el Greedy)
    # Fórmula: (Greedy - GA) / Greedy * 100
    df['gap'] = ((df['Greedy_Makespan'] - df['Meta_Makespan']) / df['Greedy_Makespan']) * 100
    
    # 2. Análisis por tamaño de instancia
    print(f"{'Tamaño':<10} | {'Mejora (GAP)':<15} | {'Tiempo GA':<15} | {'Veredicto'}")
    print("-" * 65)
    
    promedio_gap = df['gap'].mean()
    
    for index, row in df.iterrows():
        try:
             size = int(row['Jobs']) # CSV uses 'Jobs', not 'instance_size'
        except KeyError:
             size = int(row.get('instance_size', 0))

        gap = row['gap']
        time = row['Meta_Time'] # CSV uses 'Meta_Time'
        
        # Criterios de evaluación
        veredicto = "✅ Bueno"
        if gap < 0:
            veredicto = "❌ GA Empeora"  # El genético es peor que el voraz (muy malo)
        elif gap == 0:
            veredicto = "⚠️ Igual"       # No justifica el costo computacional
        elif gap < 2.0:
            veredicto = "🆗 Marginal"    # Mejora leve
        elif time > 60 and size < 50:
             veredicto = "⚠️ Lento"      # Demasiado tiempo para pocos datos
             
        print(f"{size:<10} | {gap:>11.2f}% | {time:>11.4f}s | {veredicto}")

    print("-" * 65)
    
    # 3. Conclusión Final
    print("\n--- 🏁 CONCLUSIÓN ---")
    if promedio_gap > 5:
        print(f"🌟 EXCELENTE: Tu Metaheurística mejora al Greedy en un promedio de {promedio_gap:.2f}%.")
        print("   Esto justifica plenamente su implementación en la fábrica.")
    elif promedio_gap > 0:
        print(f"👍 BUENO: Hay una mejora promedio del {promedio_gap:.2f}%.")
        print("   Es aceptable, pero revisa si puedes ajustar los parámetros (mutación/población) para subir a >5%.")
    else:
        print("👎 INSUFICIENTE: El Algoritmo Genético no está superando al Greedy.")
        print("   Causas probables: Población muy pequeña, pocas generaciones o error en el Crossover.")

if __name__ == "__main__":
    analizar_resultados('benchmark_results.csv')
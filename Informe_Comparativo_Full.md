# Informe Comparativo Completo
    
## Resumen Ejecutivo
El algoritmo ganador fue **GeneticAlgo** con un makespan de **421**.

| Algoritmo    |   Makespan |       Tiempo |
|:-------------|-----------:|-------------:|
| Greedy       |        429 |    0.0671151 |
| GeneticAlgo  |        421 | 1166.56      |
| SimAnnealing |        424 |  115.454     |
| TabuSearch   |        422 |  921.575     |

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

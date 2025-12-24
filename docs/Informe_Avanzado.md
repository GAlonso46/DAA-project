# Informe de Resultados Avanzados

## Resumen de Rendimiento
Se ejecutaron 4 algoritmos sobre una instancia compleja (60 trabajos, 5 máquinas, 3 tipos de recursos).

El ganador fue: **GeneticAlgo** con un Makespan de **71**.

### Tabla de Resultados
| Algoritmo    |   Makespan |      Tiempo |
|:-------------|-----------:|------------:|
| Greedy       |         79 |  0.00100255 |
| GeneticAlgo  |         71 | 30.9859     |
| SimAnnealing |         71 |  4.46613    |
| TabuSearch   |         71 | 29.3921     |

## Análisis Visual

### A. Diagrama de Gantt Rico (`grafico_A_gantt_rico.png`)
Este gráfico muestra la programación detallada.
*   **Color**: Indica qué recurso especializado está consumiendo principalmente esa tarea.
*   **Huecos**: Espacios en blanco pueden deberse a falta de máquinas O falta de recursos (cuellos de botella).

### B. Perfil de Carga de Recursos (`grafico_B_perfil_recursos.png`)
Muestra el consumo de cada herramienta especializada en el tiempo.
*   **Línea Roja**: Capacidad máxima.
*   **Interpretación**: Si la curva azul toca la roja frecuentemente, ese recurso es el limitante principal de la fábrica.

### C. Convergencia del Algoritmo Genético (`grafico_C_convergencia_GA.png`)
Muestra cómo evoluciona la solución generación tras generación.
*   Una caída rápida indica buen aprendizaje inicial.
*   Una meseta larga sugiere que el algoritmo llegó a un óptimo local y necesita mecanismos de reinicio (implementados y visibles como picos).

### D. Mapa de Calor de Máquinas (`grafico_D_heatmap_maquinas.png`)
Visualización extra para ver rápidamente qué tan "llenas" están las líneas de producción a lo largo del tiempo.

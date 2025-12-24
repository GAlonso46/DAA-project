# Informe de Comparación de Algoritmos de Scheduling

## Resumen Ejecutivo

Este informe detalla el rendimiento de cuatro algoritmos de optimización aplicados al problema de programación de la producción en **TecnoPlecision Global LLC**. Se han evaluado los algoritmos en tres escenarios de dificultad creciente.

## Algoritmos Evaluados

1.  **Greedy (LPT):** Una heurística constructiva rápida que ordena tareas por duración.
2.  **Algoritmo Genético:** Una metaheurística inspirada en la evolución biológica.
3.  **Simulated Annealing (Recocido Simulado):** Inspirado en el enfriamiento de metales.
4.  **Tabu Search:** Búsqueda local con memoria a corto plazo para evitar ciclos.

## Resultados Cuantitativos

A continuación se presentan los resultados obtenidos en las pruebas:

| Escenario   |   Trabajos | Algoritmo           |   Makespan |    Tiempo (s) | Valido   |
|:------------|-----------:|:--------------------|-----------:|--------------:|:---------|
| Pequeño     |         50 | Greedy (LPT)        |         54 |    0.0012238  | True     |
| Pequeño     |         50 | Genético            |         53 |    6.25827    | True     |
| Pequeño     |         50 | Simulated Annealing |         53 |    2.36288    | True     |
| Pequeño     |         50 | Tabu Search         |         53 |   11.0002     | True     |
| Mediano     |        100 | Greedy (LPT)        |        111 |    0.00614071 | True     |
| Mediano     |        100 | Genético            |        105 |   35.1133     | True     |
| Mediano     |        100 | Simulated Annealing |        105 |   12.9046     | True     |
| Mediano     |        100 | Tabu Search         |        104 |   64.1515     | True     |
| Grande      |       1500 | Greedy (LPT)        |        861 |    0.301316   | True     |
| Grande      |       1500 | Genético            |        855 | 1649          | True     |
| Grande      |       1500 | Simulated Annealing |        859 |  649.259      | True     |
| Grande      |       1500 | Tabu Search         |        856 | 3324.63       | True     |

## Análisis de Resultados

### Calidad de la Solución (Makespan)
El objetivo principal es minimizar el *makespan* (tiempo total de producción).
- El mejor resultado global fue obtenido por **Genético** en el escenario Pequeño.
- Como se observa en el gráfico `comparacion_makespan.png`, las metaheurísticas (Genético, SA, Tabu) generalmente superan al enfoque Greedy en instancias medianas y grandes, demostrando su capacidad para escapar de óptimos locales.

### Eficiencia Computacional
- **Greedy** es consistentemente el más rápido, con tiempos casi instantáneos.
- **Simulated Annealing** suele ofrecer un excelente balance entre calidad y tiempo.
- **Genetic Algorithm** y **Tabu Search** requieren más tiempo de cómputo, pero esta inversión se justifica si la reducción del makespan en planta representa un ahorro significativo de costos operativos.

## Conclusión y Recomendación

Para la implementación en planta:
*   Si la prioridad es **obtener un plan en milisegundos**, usar **Greedy**.
*   Si se dispone de unos segundos/minutos para planificar el turno (lo cual es habitual), se recomienda **Simulated Annealing** o **Genetic Algorithm** por su capacidad para encontrar soluciones de mayor calidad, reduciendo el tiempo total de operación de la fábrica.

---
*Informe generado automáticamente por el sistema de Benchmarking de TecnoPlecision.*

# Informe Técnico: Optimización de Scheduling en TecnoPlecision Global LLC

## Fase 1: Formalización del Problema

### 1. Clasificación del Problema
El problema de programación de la producción en la planta se define formalmente como un **Problema de Programación de Tareas en Máquinas Paralelas Idénticas con Restricciones de Recursos**. Bajo la clasificación técnica de tres campos propuesta por **Graham et al. 1979**, este modelo se denota como:

$$P_m \mid res \mid C_{max}$$

Esta notación identifica que disponemos de $m$ máquinas idénticas ($P_m$), restricciones de recursos adicionales ($res$) y el objetivo de minimizar el tiempo de finalización de la última tarea o *makespan* ($C_{max}$). El problema es inherentemente no preventivo (*non-preemptive*), lo que añade una restricción de integridad temporal a cada tarea: una vez iniciada la fabricación de un componente, no puede ser interrumpida.



---

### 2. Definición de Estructuras de Datos

Para formalizar el modelo, se requieren las siguientes entradas:

* **Conjunto de Trabajos ($J$):** $\{j_1, j_2, \dots, j_n\}$, donde cada $j$ es un componente del pedido.
* **Conjunto de Máquinas ($M$):** $\{i_1, i_2, \dots, i_m\}$, representando las líneas de producción idénticas.
* **Conjunto de Recursos ($R$):** $\{k_1, k_2, \dots, k_r\}$, que agrupa los tipos de herramientas especializadas.
* **Vector de Tiempos ($P$):** Donde $p_j$ es la duración estimada de la tarea $j$.
* **Matriz de Recursos ($D$):** Donde $r_{jk}$ indica la cantidad del recurso $k$ que requiere el trabajo $j$.
* **Vector de Capacidades ($Q$):** Donde $Q_k$ es la cantidad máxima disponible del recurso $k$.

---

### 3. Modelo Matemático

#### Función Objetivo
Minimizar el tiempo de término del último trabajo del pedido (Makespan):
$$\min C_{max}$$

#### Restricciones Fundamentales

1. **Garantía de Procesamiento:**
   Cada trabajo $j$ debe ser asignado a una única máquina $i$:
   $$\sum_{i=1}^{m} x_{ij} = 1, \quad \forall j \in J$$

2. **No Solapamiento en Líneas (Disyunción):**
   Si dos trabajos $j$ y $l$ comparten la misma línea $i$, sus intervalos de ejecución no deben cruzarse:
   $$x_{ij} \cdot x_{il} = 1 \implies (S_j + p_j \le S_l) \cup (S_l + p_l \le S_j)$$

3. **Disponibilidad de Herramientas (Capacidad Acumulativa):**
   Para cada recurso $k$ y en todo instante $t$, la demanda agregada de los trabajos activos debe ser menor o igual a la oferta total:
   $$\sum_{j: S_j \le t < S_j + p_j} r_{jk} \le Q_k, \quad \forall k \in R$$

4. **Cota Superior del Tiempo:**
   $$C_{max} \ge S_j + p_j, \quad \forall j \in J$$

---

### 4. Propiedades de la Salida (Solución Óptima)

Una solución válida debe entregar:
1.  **Plan de Inicio ($S$):** Un valor de tiempo de comienzo preciso para cada componente.
2.  **Asignación ($X$):** El mapeo de cada componente a su línea de producción correspondiente.
3.  **Eficiencia de Red:** El valor de $C_{max}$ debe ser el mínimo global, garantizando que no existan retrasos por subutilización de máquinas mientras los recursos estén disponibles.

---

### Referencias Bibliográficas

Graham, R. L., Lawler, E. L., Lenstra, J. K., & Rinnooy Kan, A. H. G. (1979). Optimization and approximation in deterministic sequencing and scheduling: A survey. *Annals of Discrete Mathematics*, 5, 287-326. https://doi.org/10.1016/S0167-5060(08)70356-X
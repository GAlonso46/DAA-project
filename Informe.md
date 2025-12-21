# Informe Técnico: Optimización de Scheduling en TecnoPlecision Global LLC

## Fase 1: Formalización del Problema

### 1. Clasificación del Problema
El problema de programación de la producción en la planta se define como un **Problema de Programación de Tareas en Máquinas Paralelas Idénticas con Restricciones de Recursos** ($P_m | res | C_{max}$). 

El objetivo primordial es la minimización del *makespan* (tiempo total de finalización) bajo condiciones de recursos renovables limitados y procesos no preventivos.

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
Minimizar el tiempo de término del último trabajo del pedido:
$$\min C_{max}$$

#### Restricciones Fundamentales

1. **Garantía de Procesamiento:**
   Cada trabajo $j$ debe ser asignado a una única máquina $i$:
   $$\sum_{i=1}^{m} x_{ij} = 1, \quad \forall j \in J$$

2. **No Solapamiento en Líneas (Disyunción):**
   Si dos trabajos $j$ y $l$ comparten la misma línea $i$, sus intervalos de ejecución no deben cruzarse:
   $$x_{ij} \cdot x_{il} = 1 \implies (S_j + p_j \le S_l) \cup (S_l + p_l \le S_j)$$

3. **Disponibilidad de Herramientas (Capacidad Acumulativa):**
   Para cada recurso $k$ y en todo instante $t$, la demanda agregada debe ser menor o igual a la oferta:
   $$\sum_{j: S_j \le t < S_j + p_j} r_{jk} \le Q_k, \quad \forall k \in R$$

4. **Definición de Término:**
   $$C_{max} \ge S_j + p_j, \quad \forall j \in J$$

---

### 4. Propiedades de la Salida (Solución Óptima)

Una solución válida debe entregar:
1.  **Plan de Inicio ($S$):** Un valor de tiempo de comienzo para cada componente.
2.  **Asignación ($X$):** La línea de producción específica donde se fabricará cada pieza.
3.  **Eficiencia Máxima:** El valor de $C_{max}$ debe ser el mínimo posible que satisfaga todas las restricciones de recursos, eliminando tiempos muertos innecesarios provocados por cuellos de botella de herramientas.
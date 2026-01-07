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

## Fase 2: Análisis de Complejidad Computacional

### 1. Preliminares: Optimización vs. Decisión

Para establecer la complejidad computacional del problema de optimización planteado ($P_m \mid res \mid C_{max}$), primero debemos formular su versión de **Problema de Decisión** asociada. La teoría de la NP-completitud se aplica directamente a problemas de decisión. Si demostramos que la versión de decisión es **NP-completa**, entonces el problema de optimización correspondiente es **NP-duro**.

**Definición del Problema de Decisión $\Pi_{sched}$:**
* **Instancia:** Un conjunto de trabajos $J$, máquinas $M$, recursos $R$, tiempos $p_j$, capacidades $Q_k$, demandas $r_{jk}$ y un valor entero $K$ (el límite de tiempo o *deadline*).
* **Pregunta:** ¿Existe un cronograma factible $\mathcal{S}$ tal que el tiempo de finalización de todos los trabajos sea menor o igual a $K$ ($C_{max} \le K$), respetando todas las restricciones de recursos y máquinas?

### 2. Teorema de Complejidad

**Teorema 1:** El problema de decisión $\Pi_{sched}$ es **NP-completo**. En consecuencia, el problema de optimización asociado es **NP-duro**.

**Estrategia de Demostración:**
La demostración se realiza en dos pasos:
1.  **Restricción:** Mostramos que una instancia restringida de $\Pi_{sched}$ (sin recursos y con 2 máquinas) es isomorfa al problema de programación en multiprocesadores clásico ($P_2 \parallel C_{max}$).
2.  **Reducción:** Demostramos que el problema clásico **PARTITION** (conocido NP-completo) se reduce polinomialmente a $P_2 \parallel C_{max}$.

---

### 3. Definición del Problema Base: PARTITION

Utilizaremos el problema de la Partición como punto de partida, el cual es uno de los 21 problemas NP-completos originales de Karp (1972).

**Problema:** PARTITION
* **Entrada:** Un conjunto finito $A = \{a_1, a_2, \dots, a_n\}$ de enteros positivos. Sea $W = \sum_{i=1}^n a_i$ la suma total de los elementos.
* **Pregunta:** ¿Existe un subconjunto $A' \subseteq A$ tal que $\sum_{a \in A'} a = \sum_{a \in A \setminus A'} a = \frac{W}{2}$?

---

### 4. Demostración de la Reducción Polinomial (PARTITION $\propto P_2 \parallel C_{max}$)

Sea una instancia arbitraria de PARTITION definida por el conjunto $A$. Construiremos una instancia del problema de decisión de Scheduling con 2 máquinas ($P_2 \parallel C_{max}$) en tiempo polinomial.

**Construcción de la Instancia de Scheduling:**
1.  Definimos el conjunto de trabajos $J = \{1, 2, \dots, n\}$, donde cada trabajo $j$ corresponde al elemento $a_j \in A$.
2.  El tiempo de procesamiento de cada trabajo se define como $p_j = a_j$.
3.  Definimos el número de máquinas $m = 2$.
4.  No existen restricciones de recursos (o equivalentemente $Q_k = \infty$).
5.  Definimos el valor límite del *makespan* como $K = \frac{1}{2} \sum_{j=1}^n p_j = \frac{W}{2}$.

Esta transformación es lineal respecto a la entrada, es decir, $O(n)$, y por tanto polinomial.

**Prueba de Equivalencia:**
Debemos demostrar que la respuesta a la instancia de PARTITION es "SÍ" si y solo si la respuesta a la instancia construida de Scheduling es "SÍ".

**($\Rightarrow$) Implicación Directa:**
Supongamos que existe un subconjunto $A'$ tal que $\sum_{a \in A'} a = W/2$.
Construimos el cronograma asignando los trabajos correspondientes a $A'$ a la **Máquina 1** y los trabajos correspondientes a $A \setminus A'$ a la **Máquina 2**.
* El tiempo de finalización de la Máquina 1 es $\sum_{j \in A'} p_j = W/2 = K$.
* El tiempo de finalización de la Máquina 2 es $\sum_{j \notin A'} p_j = W/2 = K$.
* Por lo tanto, $C_{max} = \max(K, K) = K$. La respuesta al problema de scheduling es "SÍ".

**($\Leftarrow$) Implicación Inversa:**
Supongamos que existe un cronograma válido en 2 máquinas tal que $C_{max} \le K = W/2$.
Sea $J_1$ el conjunto de trabajos asignados a la Máquina 1 y $J_2$ el conjunto asignados a la Máquina 2.
Sabemos que la suma total de tiempos de procesamiento es $W$.
$$\sum_{j \in J_1} p_j + \sum_{j \in J_2} p_j = W = 2K$$
Si el cronograma es válido con $C_{max} \le K$, entonces necesariamente:
$$\sum_{j \in J_1} p_j \le K \quad \text{y} \quad \sum_{j \in J_2} p_j \le K$$
Dado que la suma de ambas cargas debe ser exactamente $2K$, la única solución matemática posible es que ambas desigualdades sean igualdades estrictas:
$$\sum_{j \in J_1} p_j = K \quad \text{y} \quad \sum_{j \in J_2} p_j = K$$
Por lo tanto, el conjunto de trabajos $J_1$ constituye un subconjunto cuyos valores suman exactamente $W/2$. Esto implica que $A' = \{a_j \mid j \in J_1\}$ es una solución válida para PARTITION. La respuesta es "SÍ".

---

### 5. Generalización y Transitividad de la Complejidad

Hasta este punto, hemos demostrado que $P_2 \parallel C_{max}$ es NP-completo. Ahora debemos formalizar por qué esto implica la dureza del problema general de TecnoPlecision Global LLC ($P_m \mid res \mid C_{max}$).

Utilizamos el argumento de **inclusión de instancias**.
Sea $\Psi_{Gen}$ el espacio de todas las instancias posibles del problema general con recursos, y $\Psi_{P2}$ el espacio de instancias del problema sin recursos con $m=2$.
Se cumple que $\Psi_{P2} \subset \Psi_{Gen}$.

Esto significa que el problema $P_2 \parallel C_{max}$ es un **caso particular** de $P_m \mid res \mid C_{max}$ donde:
1.  El parámetro $m$ se fija a 2.
2.  El vector de capacidades de recursos $Q$ tiende a infinito ($Q_k \to \infty$), relajando totalmente la restricción (3) del modelo matemático.

**Conclusión Lógica:**
Si existiera un algoritmo polinomial $\mathcal{A}$ capaz de resolver el problema general $\Psi_{Gen}$, este algoritmo también podría resolver cualquier instancia de $\Psi_{P2}$ (simplemente ignorando los recursos y fijando $m=2$).
Sin embargo, hemos demostrado que $\Psi_{P2}$ es NP-completo. Por lo tanto, tal algoritmo $\mathcal{A}$ no puede existir (a menos que P=NP).

Esto demuestra formalmente que el problema $P_m \mid res \mid C_{max}$ es **al menos tan difícil** como PARTITION, y por ende, es **NP-duro**.


## Fase 3: Diseño de Soluciones Algorítmicas

Solvers implementados:

- BruteForceSolver (bruteforce.py)
  - Enumeración exhaustiva de todas las asignaciones de n trabajos a m máquinas. Para cada asignación construye un schedule que preserva el orden relativo por máquina y verifica las restricciones de recursos mediante una simulación temporal discreta. Se incorpora un umbral de combinaciones para prevenir ejecuciones prohibitivas; usado como oráculo exacto en instancias pequeñas.

- EarliestStartSolver (earliest_start_solver.py)
  - Heurística voraz de tipo list‑scheduling: en cada iteración calcula para cada trabajo no asignado el par (inicio factible más temprano, máquina) evaluando candidatos basados en eventos (finalizaciones y tiempos libres) y un fallback hasta el último tiempo libre. Actualiza una línea temporal de uso de recursos para preservar factibilidad.

- GeneticSolver (metaheuristic.py)
  - Metaheurística sobre permutaciones (representación por secuencias de Job). Componentes: población inicial aleatoria, selección por torneo, cruza OX adaptada a objetos Job, mutación por intercambio, elitismo y mecanismo de reinicio ante estancamiento. Fitness = makespan obtenido por SolutionBuilder.

- GreedySolver (greedy.py)
  - Implementa List Scheduling con varias estrategias de ordenación (LPT, SPT, heurísticas sensibles a recursos como 'HeavyResource' y 'MostTotalResources'). Genera schedules a partir de la secuencia ordenada y selecciona la mejor estrategia por evaluación empírica.

- SimulatedAnnealingSolver (simulated_annealing.py)
  - Búsqueda local estocástica sobre permutaciones: vecinos por intercambio de dos posiciones, aceptación probabilística P = exp(−Δ/T) y enfriamiento multiplicativo. Mantiene la mejor solución observada y registra historial de mejora.

Comentarios de implementación y uso:

- Todas las implementaciones gestionan la restricción acumulativa de recursos mediante una estructura temporal discreta (mapa tiempo → uso por recurso).
- El protocolo de evaluación recomendado combina: (i) oráculo exacto (BruteForce) para instancias pequeñas; (ii) heurísticas deterministas (Greedy, EarliestStart) para soluciones rápidas y interpretables; (iii) metaheurísticas (Genetic, SA) para exploración intensiva cuando la dimensión lo requiere.

Análisis teórico adicional: cotas en el Augmented Model (Garey & Graham, 1975)

El artículo "Bounds for Multiprocessor Scheduling with Resource Constraints" de Garey y Graham (1975) proporciona cotas worst‑case para el rendimiento de heurísticas de tipo List Scheduling cuando se introducen restricciones acumulativas de recursos. Para el caso de interés de este proyecto —Augmented Model con orden parcial vacío (<=∅), es decir, tareas independientes— los resultados relevantes se resumen a continuación.

Definición del modelo considerado en el artículo

- Procesadores: n procesadores idénticos (líneas de producción).
- Tareas: conjunto finito de tareas con tiempos de ejecución τ_i.
- Recursos: s tipos de recursos R = {R1, ..., Rs} con capacidad normalizada (por ejemplo, 1).
- Restricción: en cualquier instante la suma de demandas activas sobre un recurso Ri no puede exceder su capacidad.
- Orden parcial vacío (<=∅): no hay precedencias entre tareas (caso de tareas independientes, como en este trabajo).

Resultados clave (razón ω/ω* entre makespan voraz ω y óptimo ω*):

- Teorema 2 (caso de máquinas abundantes):
  Si el número de máquinas permite procesar simultáneamente muchas tareas (n ≥ r en la notación del artículo) y el orden es vacío, entonces

  ω / ω* ≤ s + 1

  donde s es el número de tipos de recursos. Interpretación: en el peor caso una heurística voraz que no gestione adecuadamente la contención por recursos puede producir un makespan hasta (s+1) veces peor que el óptimo.

- Teorema 3 (cota general para máquinas limitadas):
  Para un número finito de procesadores (n ≥ 2) y múltiples recursos s, con orden vacío, el artículo da la cota

  ω / ω* ≤ min{2n + 1, s + 2 − n / (2s + 1)}

  que combina la contribución del cuello de botella por procesadores y la contribución por congestión de recursos. Esta expresión indica que la degradación worst‑case está acotada por términos que dependen simultáneamente de n y s.

---

### Referencias Bibliográficas

Graham, R. L., Lawler, E. L., Lenstra, J. K., & Rinnooy Kan, A. H. G. (1979). Optimization and approximation in deterministic sequencing and scheduling: A survey. *Annals of Discrete Mathematics*, 5, 287-326. https://doi.org/10.1016/S0167-5060(08)70356-X

Garey, M. R., & Johnson, D. S. (1979). *Computers and Intractability: A Guide to the Theory of NP-Completeness*. W. H. Freeman and Company.

Garey, M. R., & Graham, R. L. (1975). Bounds for Multiprocessor Scheduling with Resource Constraints. *SIAM Journal on Computing*, 4(2), June 1975.
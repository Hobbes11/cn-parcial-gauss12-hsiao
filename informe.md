# El pivote — Eliminación gaussiana 12×12: mínimo costo operacional y máxima exactitud de mantisa

## 1. Identificación

| Campo | Detalle |
|---|---|
| Nombre | Hong i Hsiao |
| Asignatura | Computación Numérica · INF-321 |
| Fecha | 19-11-2026 |
| Repositorio | https://github.com/Hobbes11/cn-parcial-gauss12-hsiao.git |

---

## 2. Planteamiento

Se resuelve A x = b con A densa de 12×12 (144 de 144 elementos no nulos, 9 cifras significativas por elemento) y b con 20 dígitos significativos. Los datos se ingresan completos, sin truncar: datos/matriz_a.csv y datos/vector_b.csv se leen como texto y se convierten a float para el algoritmo y a Fraction para la verificación.

Qué hace costoso este sistema:

| Característica | Valor | Consecuencia |
|---|---|---|
| Escalas de fila incompatibles | filas entre 10⁻⁵ y 10⁵ (elementos de A entre 10⁻⁸ y 10⁵) | restar un múltiplo de una fila grande a una pequeña empuja bits de esta fuera de los 53 de la mantisa |
| Pivote inicial minúsculo | a(1,1) = 1.3407×10⁻⁸, unos 12 órdenes bajo a(2,1) | sin pivoteo el multiplicador máximo es 2.75×10¹³ |
| Casi dependencia lineal | la fila F7 es casi combinación de F3 y F5 | κ₂(A) = 3.08×10¹³ sin que A sea singular |
| Matriz densa | sin ceros que saltar | el ahorro solo puede venir de no repetir trabajo |


---

## 3. Estrategia de eliminación

Orden de pasos. Para k = 1, …, 11: (i) si hay pivoteo, se elige la fila pivote entre las filas k..12 y se intercambia con la fila k; (ii) para cada fila i > k se calcula el multiplicador y se actualiza la fila; (iii) tras los 11 pasos se resuelve por sustitución regresiva. La implementación está en src/gauss.py y las dos corridas (sin pivoteo y con pivoteo parcial escalado) usan el mismo código; solo cambia el parámetro modo.

Pivoteo parcial escalado. Se calcula una vez s_i = máx_j |a_ij| (escala de cada fila original) y en el paso k se elige la fila con mayor |a_ik| / s_i. Se escala porque con filas entre 10⁻⁵ y 10⁵ el mayor valor absoluto elige mal: en la columna 1 elegiría F6 (3.69×10⁵), cuya razón a su escala es solo 0.38, mientras que el criterio escalado elige F8 (razón 1.00).

Por qué no excede el mínimo teórico:

1. Un multiplicador por fila y paso: m(i,k) = a(i,k) / a(k,k) se calcula una vez y se reutiliza en toda la fila y en b.
2. El barrido del paso k va desde la columna k+1. El elemento a(i,k) se fija en 0.0 sin operar (se anula por construcción).
3. Una sola factorización. Los multiplicadores se guardan en L y se tiene PA = LU; el refinamiento iterativo y el estimador de condición reutilizan L, U y P. Nunca se calcula la inversa ni se refactoriza.

Costo teórico. En el paso k se eliminan m = 12 − k filas; cada una cuesta m + 2 multiplicaciones/divisiones (1 división, m multiplicaciones, 1 multiplicación para b) y m + 1 sumas/restas. Entonces:

- mult/div de la eliminación = Σ m(m+2) = 506 + 132 = 638
- sumas/restas de la eliminación = Σ m(m+1) = 506 + 66 = 572
- sustitución regresiva = 66 mult + 66 sumas/restas + 12 divisiones = 144

Total 1354 = 2n³/3 (= 1152, término dominante) más los términos de orden n² propios de actualizar b y de la sustitución regresiva.

---

## 4. Conteo de operaciones

Convención. 1 flop = 1 operación aritmética elemental en coma flotante (multiplicación, división, suma o resta). Comparaciones, valor absoluto e intercambios de filas no son flops: se cuentan aparte como sobrecosto de estabilidad (también las divisiones |a_ik|/s_i del pivoteo escalado). El conteo incluye la actualización de b y la sustitución regresiva. Los números salen de un contador instrumentado en el código: cada operación incrementa su contador en gauss.py, justo donde se ejecuta, y conteo.py solo lo formatea (resultados/conteo_flops.md).

Las columnas de pivoteo corresponden a la corrida con pivoteo escalado; la corrida sin pivoteo tiene 0 en ellas y el mismo núcleo.

| Paso k | mult/div | sumas/restas | flops del paso | comparaciones (pivote) | divisiones de escalado | intercambios |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 143 | 132 | 275 | 11 | 12 | 1 |
| 2 | 120 | 110 | 230 | 10 | 11 | 0 |
| 3 | 99 | 90 | 189 | 9 | 10 | 1 |
| 4 | 80 | 72 | 152 | 8 | 9 | 1 |
| 5 | 63 | 56 | 119 | 7 | 8 | 1 |
| 6 | 48 | 42 | 90 | 6 | 7 | 1 |
| 7 | 35 | 30 | 65 | 5 | 6 | 1 |
| 8 | 24 | 20 | 44 | 4 | 5 | 1 |
| 9 | 15 | 12 | 27 | 3 | 4 | 1 |
| 10 | 8 | 6 | 14 | 2 | 3 | 0 |
| 11 | 3 | 2 | 5 | 1 | 2 | 0 |
| Eliminación | 638 | 572 | 1210 | 66 | 77 | 8 |
| Sustitución regresiva | 78 | 66 | 144 | 0 | 0 | 0 |
| Escalas s_i (una vez) | 0 | 0 | 0 | 132 | 0 | 0 |

- Núcleo (eliminación + b + sustitución): 1354 flops (mult/div = 716, sumas/restas = 638).
- Sobrecosto del pivoteo escalado: 275 operaciones = 198 comparaciones (66 de búsqueda de pivote + 132 para las escalas) + 77 divisiones de escalado; además, 8 intercambios de filas (movimiento de datos, no flops).

Comparación con las cotas del enunciado.

| Estrategia | Medido (contador) | Cota | Diferencia |
|---|---:|---:|---:|
| Sin pivoteo (núcleo) | 1354 | 1486 | −8.9 % |
| Pivoteo escalado (núcleo + sobrecosto) | 1629 | 1486 + 66 = 1552 | +5.0 % |
| Referencia teórica 2n³/3 | 1152 | — | solo el orden dominante |

Ambos conteos quedan dentro del ±10 % aceptado. Por qué el núcleo (1354) queda bajo la cota (1486): la diferencia es exactamente 132 = 2 × 66. La cota cuenta, para cada uno de los 66 elementos bajo la diagonal, la multiplicación y la resta que «actualizan» a(i,k), que por construcción vale 0; aquí ese elemento se fija en 0.0 sin operar. Es trabajo evitado, no omitido: el resultado es idéntico. Por qué el pivoteo escalado queda sobre la cota de +66 comparaciones: además de las 66 comparaciones de la búsqueda, el escalado agrega 132 comparaciones (calcular las s_i) y 77 divisiones; el total (+275) sigue dentro del margen.

---

## 5. Análisis de mantisa y pivoteo

Resultados de las dos corridas del mismo código (error relativo en norma infinito contra la solución exacta racional):

| | Sin pivoteo | Pivoteo parcial escalado |
|---|---:|---:|
| Multiplicador máximo | 2.75×10¹³ (paso 1) | 2.47×10⁹ (paso 3) |
| Factor de crecimiento | 2641.22 | 1.78 |
| Error relativo final | 2.08×10⁻¹⁰ | 2.36×10⁻¹³ |
| Bits perdidos (53 + log₂ error) | 20.8 | 11.1 |

Por qué el pivote a(1,1) es inaceptable. a(1,1) = 1.3407×10⁻⁸ es el elemento más pequeño de la columna 1; el mayor es 3.69×10⁵ (fila F6). Dividir por él genera multiplicadores de hasta m = 2.75×10¹³ ≈ 2^44.6. En el paso 1, cada elemento se actualiza como a_ij − m·a_1j, y el producto m·a_1j es enormemente mayor que a_ij: por ejemplo, a(2,2) pasa de 9.43×10⁴ a −2.54×10⁷, y en F3 el elemento a(3,2) pasa de 7.56×10⁻³ a −5.77. En una mantisa de 53 bits, al restar se alinean los exponentes: si el producto es 2^q veces mayor que a_ij, los q bits menos significativos de a_ij quedan bajo el último bit del resultado y se pierden de forma irrecuperable (el valor original ya no existe en la matriz). En la peor resta del proceso, q = 18.1 bits (≈ 5.4 dígitos decimales de ese elemento). Además, la matriz crece por un factor de 2641, y el error hacia atrás de la eliminación es proporcional al factor de crecimiento (Higham, 2002, cap. 9). El sistema sí se resuelve —ningún pivote se anula—, pero con el error de entrada ya sembrado.

Comparación en bits. Sin pivoteo se pierden 20.8 de los 53 bits; con pivoteo escalado, 11.1. La diferencia (9.7 bits) equivale a un factor ≈ 880 en el error, es decir, casi 3 dígitos decimales.

---

## 6. Condicionamiento

| Cantidad | Valor |
|---|---:|
| ‖A‖₁ | 1.1089×10⁶ |
| ‖A⁻¹‖₁ estimada (Hager/Higham con L y U, sin invertir) | 4.0289×10⁷ |
| κ₁(A) estimada | 4.4675×10¹³ (control numpy.linalg.cond(A,1): 4.4675×10¹³) |
| κ₂(A) | 3.0847×10¹³ (σ_máx = 2.258×10⁶, σ_mín = 7.320×10⁻⁸) |
| Cota κ₂·ε (ε = 2.22×10⁻¹⁶) | 6.85×10⁻³ → 2 dígitos garantizados |
| Cota κ₁·ε | 9.92×10⁻³ → 2 dígitos garantizados |
| κ₂ con filas equilibradas, κ₂(D⁻¹A), D = máximo de cada fila | 8.1323×10³ |
| Cota κ₂(D⁻¹A)·ε | 1.81×10⁻¹² → 11 dígitos |

Casi dependencia oculta. El vector singular izquierdo asociado a σ_mín de la matriz con filas equilibradas (σ_mín = 4.83×10⁻⁴) tiene su peso en tres filas: F3 (−0.456), F5 (−0.531) y F7 (+0.714); el resto vale |·| ≤ 0.003. Ajustando por mínimos cuadrados, F7/s7 ≈ 0.6356 · F3/s3 + 0.7412 · F5/s5 con un desajuste relativo de 2.3×10⁻³. Es coherente con la sección 5: F7 es el último pivote y el único con razón muy baja (2.48×10⁻³). La matriz no es singular, pero esa casi dependencia es lo que mantiene a κ₂ en 10¹³.

Por qué la cota resulta pesimista. La cota clásica ‖δx‖/‖x‖ ≲ κ·ε no garantiza ni 2 dígitos (6.9×10⁻³), pero se obtienen 10 a 13. Razones: (1) es un límite de peor caso sobre todas las perturbaciones posibles, y los errores de redondeo reales no se alinean con la dirección más sensible; (2) gran parte de κ ≈ 10¹³ viene de las escalas incompatibles entre filas, no de una sensibilidad intrínseca: al equilibrar las filas κ₂ baja a 8.1×10³ y la cota pasa a 1.8×10⁻¹² (≈ 11 dígitos), que es justo lo que el pivoteo escalado explota; (3) los datos de entrada no se truncaron, de modo que no hay error de entrada que amplificar: el único error es el de redondeo del algoritmo, y el residuo (sección 8) es muy pequeño.

Dígitos recuperables en doble precisión: 2 garantizados por la cota clásica; ≈ 11 según la cota con filas equilibradas; entre 10 y 13 medidos.

---

## 7. Resultados

Solución con pivoteo parcial escalado (resultados/solucion.csv). Dígitos «afirmados» = floor(−log₁₀(|d|/|x|)), donde d es la corrección del refinamiento (no usa la solución exacta); dígitos correctos = medidos contra la solución racional exacta. Cada valor se reporta con exactamente los dígitos afirmados.

| i | x (dígitos defendidos) | Afirmados | Correctos | x refinada (20 díg.) |
|---:|---:|---:|---:|---:|
| 1 | 7.384915626999e-01 | 13 | 13 | 7.3849156270000000000e-01 |
| 2 | −1.20593741680e+00 | 12 | 12 | −1.2059374168000000000e+00 |
| 3 | 4.387195200e-03 | 10 | 10 | 4.3871952000000000000e-03 |
| 4 | −9.1726453800e-02 | 11 | 11 | −9.1726453800000000000e-02 |
| 5 | 2.84610937250e+00 | 12 | 12 | 2.8461093725000000000e+00 |
| 6 | −6.281540899e-03 | 10 | 10 | −6.2815409000000000000e-03 |
| 7 | 1.47382059160e+00 | 12 | 12 | 1.4738205916000000000e+00 |
| 8 | −3.8492716400e-02 | 11 | 11 | −3.8492716400000000000e-02 |
| 9 | 9.15264803700e-01 | 12 | 12 | 9.1526480370000000000e-01 |
| 10 | −2.60713948520e+00 | 12 | 12 | −2.6071394852000000000e+00 |
| 11 | 5.1873629400e-02 | 11 | 11 | 5.1873629400000000000e-02 |
| 12 | −1.08493716250e+00 | 12 | 12 | −1.0849371625000000000e+00 |

Las 12 incógnitas tienen 10 o más dígitos correctos, y los dígitos afirmados coinciden con los efectivamente correctos en las 12. En la columna refinada, el afirmado está limitado a 20 por las cifras con que se entrega b; medido contra la solución exacta del sistema racional, resultan 35 a 38 dígitos correctos. Se observa además que la solución refinada coincide con números decimales de a lo más 10 cifras significativas (p. ej. 0.7384915627), coherente con que b se construyó a partir de una solución verdadera.

---

## 8. Verificación

Residuo en precisión extendida (r = b − A x con fractions, aritmética racional exacta, x del pivoteo escalado):

| | ‖r‖∞ |
|---|---:|
| Pivoteo escalado | 2.290876×10⁻¹⁰ |
| Sin pivoteo | 1.771752×10⁻⁷ |
| Residuo relativo ‖r‖∞ / (‖A‖∞‖x‖∞), pivoteo escalado | 1.117×10⁻¹⁷ |

El residuo relativo del pivoteo escalado es inferior a ε, o sea la solución es la exacta de un sistema muy próximo, y el residuo sin pivoteo es unas 770 veces mayor. Un residuo pequeño no garantiza un error pequeño (error ≲ κ · residuo relativo): aquí el residuo relativo es 1.1×10⁻¹⁷ y el error relativo es 2.4×10⁻¹³.

Refinamiento iterativo (residuo exacto; la corrección se resuelve con L y U ya calculadas, sin refactorizar).

a) x guardado en doble precisión:

| Paso | ‖r‖∞ | ‖x − x*‖/‖x*‖ |
|---:|---:|---:|
| 0 | 2.291×10⁻¹⁰ | 2.357×10⁻¹³ |
| 1 | 2.603×10⁻¹⁰ | 6.016×10⁻¹⁷ |
| 2 | 2.603×10⁻¹⁰ | 6.016×10⁻¹⁷ |
| 3 | 2.603×10⁻¹⁰ | 6.016×10⁻¹⁷ |

La primera pasada baja el error de 2.4×10⁻¹³ a 6.0×10⁻¹⁷ y luego se estanca: es el piso de guardar x en 53 bits (el residuo no mejora por la misma razón).

b) x guardado como racional exacto:

| Paso | ‖r‖∞ | ‖x − x*‖/‖x*‖ |
|---:|---:|---:|
| 0 | 2.291×10⁻¹⁰ | 2.357×10⁻¹³ |
| 1 | 1.366×10⁻²² | 6.174×10⁻²⁶ |
| 2 | 3.928×10⁻³⁵ | 1.614×10⁻³⁸ |
| 3 | 1.383×10⁻⁴⁸ | 4.224×10⁻⁵¹ |
| 4 | 5.374×10⁻⁶¹ | 1.103×10⁻⁶³ |

Cada pasada gana ≈ 12.6 dígitos: la factorización en doble precisión actúa como una buena aproximación de A⁻¹ y en cada pasada el error se reduce por un factor ≈ 2.6×10⁻¹³ (6.174×10⁻²⁶ / 2.357×10⁻¹³), es decir, la factorización en doble precisión sigue siendo una aproximación muy buena de A⁻¹ en la dirección que importa pese a κ ≈ 10¹³.

Control con biblioteca (numpy.linalg.solve, solo control; no sustituye la implementación propia). Dígitos correctos por incógnita:

| | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Implementación propia (pivoteo escalado) | 13 | 12 | 10 | 11 | 12 | 10 | 12 | 11 | 12 | 12 | 11 | 12 |
| numpy.linalg.solve | 12 | 11 | 9 | 11 | 12 | 9 | 12 | 11 | 12 | 12 | 11 | 12 |

La diferencia relativa máxima entre numpy y la solución propia es 1.04×10⁻¹⁰, del orden del error de la corrida sin pivoteo; la solución propia es igual o mejor en las 12 incógnitas.

---

## 9. Conclusiones

El compromiso elegido. Se eligió pivoteo parcial escalado. Sobre un núcleo de 1354 flops (que cumple el mínimo de eliminación densa: un multiplicador por fila, subdiagonal fijada, una sola factorización), el pivoteo agrega 275 operaciones de sobrecosto (≈ 20 %: 198 comparaciones y 77 divisiones, más 8 intercambios de filas). A cambio, el error baja de 2.1×10⁻¹⁰ a 2.4×10⁻¹³ (≈ 880 veces, 9.7 bits), el crecimiento pasa de 2641 a 1.78 y todas las incógnitas alcanzan 10 o más dígitos correctos. Ese costo se justifica porque el sobrecosto no son flops de la eliminación, y porque el pivoteo sin escalar elegiría mal con filas entre 10⁻⁵ y 10⁵. No se eligió pivoteo completo: su búsqueda de pivote cuesta O(n³) comparaciones y el pivoteo parcial escalado ya recupera casi todo lo posible aquí. Y el refinamiento iterativo, que reutiliza L y U, cuesta O(n²) por pasada y lleva el resultado más allá de lo que permite la cota clásica.

Qué haría distinto con n = 1000.

- El costo relativo del pivoteo se vuelve despreciable: el núcleo crece como 2n³/3 ≈ 6.7×10⁸ flops, y el sobrecosto como O(n²) (≈ 2×10⁶ operaciones: n²/2 comparaciones de búsqueda, n² para las escalas, n²/2 divisiones), es decir, ≈ 0.3 % en vez de 20 %. Con n grande el pivoteo escalado (o el parcial) es casi gratis.
- Implementación: una triple iteración en Python puro es demasiado lenta; usaría LU por bloques de una biblioteca optimizada (LAPACK vía numpy/scipy), que aprovecha la memoria caché. Cambia el objetivo de la prueba (aquí se prohíbe resolver con bibliotecas), pero en producción es lo correcto.
- Verificación: la solución exacta con fractions sería muy costosa; calcularía el residuo en mayor precisión (acumulación compensada o precisión extendida) y usaría refinamiento iterativo en precisión mixta.
- Condicionamiento: mantendría el estimador de Hager/Higham, que cuesta O(n²) una vez factorizada la matriz, y equilibraría filas y columnas antes de factorizar.
- Estructura: si la matriz tuviera estructura dispersa o simétrica definida positiva, usaría un método que la explote (almacenamiento disperso, Cholesky) en lugar de la eliminación densa.

---

## 10. Reproducibilidad

| Elemento | Versión |
|---|---|
| Python | 3.12.3 |
| numpy | 2.5.1 |
| Librería estándar | csv, math, fractions, decimal, pathlib, platform |

Comandos ejecutados desde la raíz del repositorio, en un entorno limpio:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```

python src/main.py regenera sin intervención manual resultados/solucion.csv, resultados/traza_eliminacion.txt, resultados/conteo_flops.md y resultados/residuo.txt.

---

## Fuentes

- Enunciado de la prueba parcial 3, El pivote, INF-321 Computación Numérica.
- N. J. Higham, Accuracy and Stability of Numerical Algorithms, 2.ª ed., SIAM, 2002 (cap. 9: factorización LU y factor de crecimiento; cap. 15: estimación del número de condición).
- W. W. Hager, «Condition estimates», SIAM J. Sci. Stat. Comput. 5(2), 1984, pp. 311–316 (estimador de ‖A⁻¹‖₁).
- G. H. Golub y C. F. Van Loan, Matrix Computations, 4.ª ed., Johns Hopkins University Press, 2013 (pivoteo parcial y refinamiento iterativo).

---

## Declaración de uso de inteligencia artificial

- Organizar el trabajo.
- Apoyo en las fórmulas de error, bits perdidos, cotas y condicionamiento.
- Borradores del informe y del readme.
- Revisión de la entrega frente a la pauta.

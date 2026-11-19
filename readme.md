# El pivote — Eliminación gaussiana 12×12

Resuelve un sistema lineal denso de 12 incógnitas con eliminación gaussiana en doble precisión, con y sin pivoteo parcial escalado, contando operaciones y verificando la solución con aritmética exacta.

## Autoría y asignatura

- Autor: Hong i Hsiao
- Asignatura: Computación Numérica · INF-321

## Requisitos

- Python 3.10 o superior.
- Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Ejecución

Desde la raíz del repositorio:

```bash
python src/main.py
```

Sin intervención manual, regenera todo el contenido de resultados/:

- solucion.csv — las 12 incógnitas con sus dígitos afirmados y correctos.
- traza_eliminacion.txt — resumen de las dos corridas y la matriz aumentada tras cada uno de los 11 pasos.
- conteo_flops.md — tabla de operaciones por paso y comparación con las cotas.
- residuo.txt — residuo exacto y su norma infinito, refinamiento iterativo, control con numpy y condicionamiento.

## Estructura de carpetas

```
cn-parcial-gauss12-<apellido>/
├─ readme.md
├─ informe.md
├─ requirements.txt
├─ datos/             # A (12x12) y b
├─ src/               # gauss.py, conteo.py, verificacion.py y main.py
└─ resultados/        # salidas generadas por python src/main.py
```

## Resultado resumido

Solución refinada (pivoteo parcial escalado + refinamiento iterativo), a 10 cifras significativas:

| i | x_i | i | x_i |
|---:|---:|---:|---:|
| 1 | 0.7384915627 | 7 | 1.473820592 |
| 2 | −1.205937417 | 8 | −0.03849271640 |
| 3 | 0.004387195200 | 9 | 0.9152648037 |
| 4 | −0.09172645380 | 10 | −2.607139485 |
| 5 | 2.846109373 | 11 | 0.05187362940 |
| 6 | −0.006281540900 | 12 | −1.084937163 |

- Total de flops: 1354 (núcleo: eliminación + b + sustitución regresiva); el pivoteo escalado agrega 275 operaciones de sobrecosto (1629 en total).
- Norma infinito del residuo: ‖r‖∞ = 2.29×10⁻¹⁰ (solución directa) y 3.9×10⁻³⁵ (solución refinada).

## Informe

El análisis completo está en [informe.md](informe.md).

## Licencia

Trabajo académico de la asignatura INF-321 (UCM).

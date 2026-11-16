# Conteo de operaciones

### Sin pivoteo

| Paso k | mult/div | sumas/restas | flops del paso | comparaciones (pivote) | divisiones de escalado | intercambios |
| 1 | 143 | 132 | 275 | 0 | 0 | 0 |
| 2 | 120 | 110 | 230 | 0 | 0 | 0 |
| 3 | 99 | 90 | 189 | 0 | 0 | 0 |
| 4 | 80 | 72 | 152 | 0 | 0 | 0 |
| 5 | 63 | 56 | 119 | 0 | 0 | 0 |
| 6 | 48 | 42 | 90 | 0 | 0 | 0 |
| 7 | 35 | 30 | 65 | 0 | 0 | 0 |
| 8 | 24 | 20 | 44 | 0 | 0 | 0 |
| 9 | 15 | 12 | 27 | 0 | 0 | 0 |
| 10 | 8 | 6 | 14 | 0 | 0 | 0 |
| 11 | 3 | 2 | 5 | 0 | 0 | 0 |
| Eliminación | 638 | 572 | 1210 | 0 | 0 | 0 |
| Sustitución regresiva | 78 | 66 | 144 | 0 | 0 | 0 |
| Cálculo de escalas s_i (una vez) | 0 | 0 | 0 | 0 | 0 | 0 |

- Flops del núcleo (eliminación + b + sustitución regresiva): 1354 (mult/div = 716, sumas/restas = 638)
- Sobrecosto de estabilidad (pivoteo): 0 comparaciones + 0 divisiones de escalado = 0 operaciones; 0 intercambios de filas (movimiento de datos, no flops)

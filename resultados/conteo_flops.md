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

### Pivoteo parcial escalado

| Paso k | mult/div | sumas/restas | flops del paso | comparaciones (pivote) | divisiones de escalado | intercambios |
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
| Cálculo de escalas s_i (una vez) | 0 | 0 | 0 | 132 | 0 | 0 |

- Flops del núcleo (eliminación + b + sustitución regresiva): 1354 (mult/div = 716, sumas/restas = 638)
- Sobrecosto de estabilidad (pivoteo): 198 comparaciones + 77 divisiones de escalado = 275 operaciones; 8 intercambios de filas (movimiento de datos, no flops)

## Comparación con las cotas del enunciado

| Estrategia | Medido (contador) | Cota enunciado | Diferencia |
| Sin pivoteo (núcleo) | 1354 | 1486 | -8.9 % |
| Pivoteo escalado (núcleo + sobrecosto) | 1629 | 1552 | +5.0 % |
| Referencia teórica 2n³/3 | 1152 | 2n³/3 | solo el orden dominante |

Por qué el núcleo medido (1354) queda bajo la cota (1486). La diferencia es exactamente 132 = 2 × 66: la cota cuenta, en cada fila y paso, la multiplicación y la resta que "actualizan" el elemento a(i,k), que por construcción vale 0. Aquí ese elemento se fija en 0.0 sin operar. Es trabajo evitado, no omitido: el resultado es idéntico y el conteo queda 8.9 % bajo la cota (dentro del ±10 % aceptado).

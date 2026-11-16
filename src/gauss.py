import csv
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

def leer_datos():
    with open(RAIZ / "datos" / "matriz_a.csv", newline="") as f:
        A_txt = [[v.strip() for v in fila] for fila in csv.reader(f) if fila]
    with open(RAIZ / "datos" / "vector_b.csv", newline="") as f:
        b_txt = [fila[0].strip() for fila in csv.reader(f) if fila]
    return [[float(v) for v in fila] for fila in A_txt], [float(v) for v in b_txt], A_txt, b_txt

def eliminar(A0, b0):
    n = len(A0)
    a, b = [fila[:] for fila in A0], b0[:]
    for k in range(n - 1):
        for i in range(k + 1, n):
            m = a[i][k] / a[k][k]
            for j in range(k + 1, n):
                prod = m * a[k][j]
                viejo = a[i][j]
                a[i][j] = viejo - prod
            b[i] = b[i] - m * b[k]
            a[i][k] = 0.0
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        acc = b[i]
        for j in range(i + 1, n):
            acc = acc - a[i][j] * x[j]
        x[i] = acc / a[i][i]
    return {"x": x, "U": a}

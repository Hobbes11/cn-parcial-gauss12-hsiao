import csv
from pathlib import Path
from conteo import nuevo_contador

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
    c = nuevo_contador(n)
    for k in range(n - 1):
        for i in range(k + 1, n):
            m = a[i][k] / a[k][k]
            c["md"][k] += 1
            for j in range(k + 1, n):
                prod = m * a[k][j]
                c["md"][k] += 1
                viejo = a[i][j]
                a[i][j] = viejo - prod
                c["sr"][k] += 1
            b[i] = b[i] - m * b[k]
            c["md"][k] += 1
            c["sr"][k] += 1
            a[i][k] = 0.0
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        acc = b[i]
        for j in range(i + 1, n):
            acc = acc - a[i][j] * x[j]
            c["md_reg"] += 1
            c["sr_reg"] += 1
        x[i] = acc / a[i][i]
        c["md_reg"] += 1
    return {"x": x, "U": a, "contador": c}

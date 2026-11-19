import csv
import math
from pathlib import Path
from conteo import nuevo_contador

RAIZ = Path(__file__).resolve().parent.parent

def leer_datos():
    with open(RAIZ / "datos" / "matriz_a.csv", newline="") as f:
        A_txt = [[v.strip() for v in fila] for fila in csv.reader(f) if fila]
    with open(RAIZ / "datos" / "vector_b.csv", newline="") as f:
        b_txt = [fila[0].strip() for fila in csv.reader(f) if fila]
    return [[float(v) for v in fila] for fila in A_txt], [float(v) for v in b_txt], A_txt, b_txt

def _formato(M, b, perm):
    return "\n".join(f"F{perm[i] + 1:<3}" + " ".join(f"{v:+.9e}" for v in M[i]) + f"  |  {b[i]:+.9e}"
                     for i in range(len(M)))

def eliminar(A0, b0, modo, traza=None):
    n = len(A0)
    a, b = [fila[:] for fila in A0], b0[:]
    L = [[0.0] * n for _ in range(n)]
    perm = list(range(n))
    c = nuevo_contador(n)
    esc = modo == "escalado"
    s = [1.0] * n
    if esc:
        for i in range(n):
            s[i] = abs(a[i][0])
            for j in range(1, n):
                c["cmp_escala"] += 1
                if abs(a[i][j]) > s[i]:
                    s[i] = abs(a[i][j])
    max_a0 = max(abs(v) for fila in a for v in fila)
    max_elem = max_a0
    max_mult, paso_mult = 0.0, 0
    bits_desp = 0.0
    pivotes = []
    if traza is not None:
        traza.append(f"Matriz aumentada inicial [A|b]\n{_formato(a, b, perm)}\n")
    for k in range(n - 1):
        if esc:
            p = k
            mejor = abs(a[k][k]) / s[k]
            c["div_escala"][k] += 1
            for i in range(k + 1, n):
                r = abs(a[i][k]) / s[i]
                c["div_escala"][k] += 1
                c["cmp"][k] += 1
                if r > mejor:
                    mejor, p = r, i
            if p != k:
                for M in (a, b, L, s, perm):
                    M[k], M[p] = M[p], M[k]
                c["swaps"][k] += 1
        pivotes.append(a[k][k])
        for i in range(k + 1, n):
            m = a[i][k] / a[k][k]
            c["md"][k] += 1
            L[i][k] = m
            if abs(m) > max_mult:
                max_mult, paso_mult = abs(m), k + 1
            for j in range(k + 1, n):
                prod = m * a[k][j]
                c["md"][k] += 1
                viejo = a[i][j]
                a[i][j] = viejo - prod
                c["sr"][k] += 1
                if viejo != 0.0 and prod != 0.0:
                    bits_desp = max(bits_desp, math.log2(abs(prod) / abs(viejo)))
            b[i] = b[i] - m * b[k]
            c["md"][k] += 1
            c["sr"][k] += 1
            a[i][k] = 0.0
        max_elem = max([max_elem] + [abs(a[i][j]) for i in range(k + 1, n) for j in range(k + 1, n)])
        if traza is not None:
            ceros = sum(1 for i in range(n) for j in range(i) if a[i][j] == 0.0)
            txt = f"Paso {k + 1} de {n - 1}: pivote a({k + 1},{k + 1}) = {a[k][k]:+.9e}"
            if esc:
                txt += f"  (fila original F{perm[k] + 1}, intercambio: {'sí' if c['swaps'][k] else 'no'})"
            traza.append(f"{txt}  | ceros bajo la diagonal: {ceros} de {n * (n - 1) // 2}\n {_formato(a, b, perm)}\n")
    pivotes.append(a[n - 1][n - 1])
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        acc = b[i]
        for j in range(i + 1, n):
            acc = acc - a[i][j] * x[j]
            c["md_reg"] += 1
            c["sr_reg"] += 1
        x[i] = acc / a[i][i]
        c["md_reg"] += 1
    return {"x": x, "U": a, "L": L, "perm": perm, "pivotes": pivotes, "escalas": s, "contador": c,
            "max_mult": max_mult, "paso_mult": paso_mult, "crecimiento": max_elem / max_a0, "bits_desp": bits_desp}

def resolver_con_LU(res, rhs):
    n = len(rhs)
    U, L, perm = res["U"], res["L"], res["perm"]
    y = [rhs[perm[i]] for i in range(n)]
    for i in range(n):
        for j in range(i):
            y[i] -= L[i][j] * y[j]
    z = [0.0] * n
    for i in range(n - 1, -1, -1):
        acc = y[i]
        for j in range(i + 1, n):
            acc -= U[i][j] * z[j]
        z[i] = acc / U[i][i]
    return z

def resolver_traspuesta_con_LU(res, rhs):
    n = len(rhs)
    U, L, perm = res["U"], res["L"], res["perm"]
    w = rhs[:]
    for i in range(n):
        for j in range(i):
            w[i] -= U[j][i] * w[j]
        w[i] /= U[i][i]
    for i in range(n - 1, -1, -1):
        for j in range(i + 1, n):
            w[i] -= L[j][i] * w[j]
    z = [0.0] * n
    for i in range(n):
        z[perm[i]] = w[i]
    return z

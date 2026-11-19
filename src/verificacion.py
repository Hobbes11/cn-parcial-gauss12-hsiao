import math
from decimal import Decimal, getcontext
from fractions import Fraction
import numpy as np
from gauss import resolver_con_LU, resolver_traspuesta_con_LU

getcontext().prec = 50
EPS = 2.22e-16

def cientifico(f, cifras):
    m, e = f"{Decimal(f.numerator) / Decimal(f.denominator):.{cifras - 1}e}".split("e")
    return f"{m}e{int(e):+03d}"

def formatear(x, d):
    return f"{x:.{max(min(d, 17), 1) - 1}e}"

def a_fracciones(A_txt, b_txt):
    return [[Fraction(v) for v in fila] for fila in A_txt], [Fraction(v) for v in b_txt]

def solucion_exacta(Af, bf):
    n = len(Af)
    M = [Af[i][:] + [bf[i]] for i in range(n)]
    for k in range(n):
        p = next(i for i in range(k, n) if M[i][k] != 0)
        M[k], M[p] = M[p], M[k]
        for i in range(k + 1, n):
            m = M[i][k] / M[k][k]
            M[i] = [M[i][j] - m * M[k][j] for j in range(n + 1)]
    x = [Fraction(0)] * n
    for i in range(n - 1, -1, -1):
        x[i] = (M[i][n] - sum(M[i][j] * x[j] for j in range(i + 1, n))) / M[i][i]
    return x

def residuo_exacto(Af, bf, x):
    xf = [Fraction(v) for v in x]
    return [bf[i] - sum(Af[i][j] * xf[j] for j in range(len(xf))) for i in range(len(Af))]

def norma_inf(v):
    return max(abs(Fraction(t)) for t in v)

def error_relativo(x, x_ref):
    return norma_inf([Fraction(a) - r for a, r in zip(x, x_ref)]) / norma_inf(x_ref)

def digitos_correctos(x, x_ref):
    out = []
    for xi, ri in zip(x, x_ref):
        err = abs(Fraction(xi) - ri) / abs(ri)
        out.append(99 if err == 0 else math.floor(-math.log10(float(err))))
    return out

def digitos_desde_correccion(d, x, tope=99):
    return [tope if di == 0 else min(tope, math.floor(-math.log10(abs(di) / abs(float(xi)))))
            for di, xi in zip(d, x)]

def refinar(res, Af, bf, x0, pasos, almacenamiento, x_ref):
    x = [Fraction(v) for v in x0]
    hist = []
    for p in range(pasos + 1):
        r = residuo_exacto(Af, bf, x)
        hist.append({"paso": p, "norma_r": norma_inf(r), "err_rel": error_relativo(x, x_ref),
                     "x": x[:], "d": None})
        if p == pasos:
            break
        d = resolver_con_LU(res, [float(t) for t in r])
        hist[-1]["d"] = d
        if almacenamiento == "doble":
            x = [Fraction(float(x[i]) + d[i]) for i in range(len(x))]
        else:
            x = [x[i] + Fraction(d[i]) for i in range(len(x))]
    return hist

def estimar_cond1(res, A):
    n = len(A)
    norma_A = max(sum(abs(A[i][j]) for i in range(n)) for j in range(n))
    x, est = [1.0 / n] * n, 0.0
    for _ in range(6):
        y = resolver_con_LU(res, x)
        est = max(est, sum(abs(v) for v in y))
        z = resolver_traspuesta_con_LU(res, [1.0 if v >= 0 else -1.0 for v in y])
        if max(abs(v) for v in z) <= sum(z[i] * x[i] for i in range(n)):
            break
        j = max(range(n), key=lambda i: abs(z[i]))
        x = [0.0] * n
        x[j] = 1.0
    return norma_A * est, norma_A, est

def diagnostico_condicion(A):
    M = np.array(A)
    E = M / np.abs(M).max(axis=1)[:, None]
    sv = np.linalg.svd(M, compute_uv=False)
    Ue, se, _ = np.linalg.svd(E)
    B = np.stack([E[2], E[4]], axis=1)
    coef = np.linalg.lstsq(B, E[6], rcond=None)[0]
    return {"k2": sv[0] / sv[-1], "sv_min": sv[-1], "sv_max": sv[0],
            "k2_equil": se[0] / se[-1], "se_min": se[-1], "vec_izq": Ue[:, -1],
            "coef_f7": coef, "rel_f7": np.linalg.norm(B @ coef - E[6]) / np.linalg.norm(E[6])}

def control_numpy(A, b):
    return [float(v) for v in np.linalg.solve(np.array(A), np.array(b))]

import math
from pathlib import Path
import numpy as np
import conteo
import gauss
import verificacion as ver

SALIDA = Path(__file__).resolve().parent.parent / "resultados"
NOMBRE = {"ninguno": "Sin pivoteo", "escalado": "Pivoteo parcial escalado"}
MODOS = list(NOMBRE)

def cient(f, d=6):
    return ver.cientifico(f, d + 1)

def escribir_traza(corridas, trazas, n):
    L = ["TRAZA DE LA ELIMINACIÓN GAUSSIANA (matriz aumentada [A|b] tras cada paso, 9 cifras mostradas)",
         "=" * 100, "",
         "RESUMEN DE LAS CORRIDAS (T2)", "",
         f"{'corrida':<28}{'mult. max':>11}{'paso':>5}{'crecim.':>10}{'bits desp.':>11}{'err. rel.':>11}{'dígitos':>9}{'bits perd.':>11}{'no nulos':>10}"
         ]
    for modo in MODOS:
        r = corridas[modo]
        L.append(f"{NOMBRE[modo]:<28}{r['max_mult']:>11.2e}{r['paso_mult']:>5d}{r['crecimiento']:>10.2f}{r['bits_desp']:>11.1f}{float(r['err']):>11.2e}"
                 f"{str(min(r['digitos'])) + '-' + str(max(r['digitos'])):>9}{r['bits_perdidos']:>11.1f}{r['no_nulos']:>6d}/{n * (n - 1) // 2}")
    e = corridas["escalado"]
    razones = [abs(e["pivotes"][k]) / e["escalas"][k] for k in range(n)]
    kmin = min(range(n), key=lambda k: razones[k])
    otras = min(v for k, v in enumerate(razones) if k != kmin)
    L += ["", "crecimiento = máx |a_ij^(k)| durante la eliminación / máx |a_ij| inicial",
          "bits desp.  = máx log2(|m*a_kj| / |a_ij|): bits de a_ij que quedan bajo el producto en la resta",
          "bits perd.  = 53 + log2(error relativo en norma infinito)", "",
          "Pivotes |u_kk| / s_fila en el pivoteo escalado, por posición de pivote:",
          "  " + "  ".join(f"{v:.2e}" for v in razones),
          "Orden de filas elegido (filas originales, en orden de pivote): " + " ".join(f"F{p + 1}" for p in e["perm"]),
          f"La fila F{e['perm'][kmin] + 1} llega a ser pivote con solo {razones[kmin]:.2e} de su escala "
          f"(las demás ≥ {otras:.2f}): casi dependencia lineal con otras filas.", ""]
    for modo in MODOS:
        L += ["=" * 100, f"CORRIDA: {NOMBRE[modo]}", "=" * 100, ""] + trazas[modo]
        L.append(f"Elementos bajo la diagonal distintos de cero: {corridas[modo]['no_nulos']} de {n * (n - 1) // 2}\n")
    (SALIDA / "traza_eliminacion.txt").write_text("\n".join(L), encoding="utf-8")

def escribir_conteo(corridas):
    md = ["# Conteo de operaciones", ""]
    for modo in MODOS:
        md.append(conteo.tabla_markdown(corridas[modo]["contador"], NOMBRE[modo]))
    md.append(conteo.comparar_con_cotas(corridas["ninguno"]["contador"], corridas["escalado"]["contador"]))
    (SALIDA / "conteo_flops.md").write_text("\n".join(md), encoding="utf-8")

def escribir_verificacion(corridas, A, b, Af, bf, x_ref):
    n, nx = len(A), ver.norma_inf(x_ref)
    res = corridas["escalado"]
    x = res["x"]
    hist_d = ver.refinar(res, Af, bf, x, 3, "doble", x_ref)
    hist_e = ver.refinar(res, Af, bf, x, 4, "extendido", x_ref)
    afirmados = ver.digitos_desde_correccion(hist_d[0]["d"], x)
    reales = res["digitos"]
    x_ext = hist_e[2]["x"]
    afirm_ext = ver.digitos_desde_correccion(hist_e[2]["d"], x_ext, tope=20)
    reales_ext = ver.digitos_correctos(x_ext, x_ref)
    f = ["i,x_directa_escalado,digitos_afirmados,digitos_correctos_reales,x_refinado_20dig,digitos_afirmados_refinado"]
    for i in range(n):
        f.append(f"{i + 1},{ver.formatear(x[i], afirmados[i])},{afirmados[i]},{reales[i]},"
                 f"{ver.cientifico(x_ext[i], 20)},{afirm_ext[i]}")
    (SALIDA / "solucion.csv").write_text("\n".join(f) + "\n", encoding="utf-8")

    r_ex = ver.residuo_exacto(Af, bf, x)
    nr = ver.norma_inf(r_ex)
    norma_A = max(sum(abs(v) for v in fila) for fila in Af)
    nr_sin = ver.norma_inf(ver.residuo_exacto(Af, bf, corridas["ninguno"]["x"]))
    k1, nA1, nAi1 = ver.estimar_cond1(res, A)
    dg = ver.diagnostico_condicion(A)
    x_np = ver.control_numpy(A, b)
    dig_np = ver.digitos_correctos(x_np, x_ref)
    cota2, cota1 = dg["k2"] * ver.EPS, k1 * ver.EPS
    e0, e1 = hist_d[0]["err_rel"], hist_d[1]["err_rel"]
    ganancia = [math.log10(hist_e[p]["err_rel"] / hist_e[p + 1]["err_rel"]) for p in range(len(hist_e) - 1)]
    R = ["VERIFICACIÓN INDEPENDIENTE",
         "=" * 100, "",
         "1) Residuo r = b - A x  (aritmética racional exacta; x = solución directa del pivoteo escalado)", ""]
    R += [f"  r[{i + 1:>2}] = {cient(r_ex[i])}" for i in range(n)]
    R += ["", f"  ||r||_inf (pivoteo escalado) = {cient(nr)}",
          f"  residuo relativo ||r||_inf / (||A||_inf ||x||_inf) = {cient(nr / (norma_A * nx))}",
          f"  ||r||_inf (sin pivoteo)      = {cient(nr_sin)}",
          "  (un residuo pequeño no garantiza un error pequeño: error ≲ κ · residuo relativo)", "",
          "2) Refinamiento iterativo (residuo exacto; corrección resuelta con L y U ya calculadas, sin refactorizar)",
          "", "  a) x guardado en doble precisión", f"  {'paso':>4} {'||r||_inf':>14} {'||x-x*||/||x*||':>18}"]
    R += [f"  {h['paso']:>4} {cient(h['norma_r'], 3):>14} {cient(h['err_rel'], 3):>18}" for h in hist_d]
    R += [f"  la pasada 1 baja el error de {float(e0):.1e} a {float(e1):.1e}; después se queda en el piso de almacenar x en 53 bits.", "",
          "  b) x guardado como racional exacto (precisión extendida)",
          f"  {'paso':>4} {'||r||_inf':>14} {'||x-x*||/||x*||':>18}"]
    R += [f"  {h['paso']:>4} {cient(h['norma_r'], 3):>14} {cient(h['err_rel'], 3):>18}" for h in hist_e]
    gan = f"{min(ganancia):.1f}" if max(ganancia) - min(ganancia) < 0.05 else f"{min(ganancia):.1f}-{max(ganancia):.1f}"
    R += [f"  cada pasada gana ~{gan} dígitos.", "",
          "3) Dígitos afirmados vs dígitos correctos",
          "  Convención: dígitos = floor(-log10(error relativo)). Los afirmados salen de la corrección del",
          "  refinamiento (no usan la solución exacta); los correctos se miden contra la solución racional exacta.", "",
          f"  {'i':>3} {'afirm. directa':>15} {'correctos':>10} {'afirm. refinada':>16} {'correctos':>10}"]
    R += [f"  {i + 1:>3} {afirmados[i]:>15} {reales[i]:>10} {afirm_ext[i]:>16} {reales_ext[i]:>10}" for i in range(n)]
    R += [f"  directa: coinciden en {sum(afirmados[i] == reales[i] for i in range(n))} de {n} incógnitas; "
          f"refinada (tope 20 = cifras de b): afirma {min(afirm_ext)}-{max(afirm_ext)}, correctos {min(reales_ext)}-{max(reales_ext)}", "",
          "4) Control con numpy.linalg.solve (solo control)", "",
          f"  dígitos correctos de numpy: {dig_np}",
          f"  máx diferencia relativa entre numpy y la solución propia: "
          f"{max(abs(x_np[i] - x[i]) / abs(x[i]) for i in range(n)):.2e}", "",
          "5) Condicionamiento", "",
          f"  ||A||_1 = {nA1:.4e};  ||A^-1||_1 estimada (Hager/Higham con L y U, sin invertir) = {nAi1:.4e}",
          f"  kappa_1(A) estimada = {k1:.4e}   (control numpy.linalg.cond(A,1): {np.linalg.cond(np.array(A), 1):.4e})",
          f"  kappa_2(A) = {dg['k2']:.4e}   (sigma_max = {dg['sv_max']:.3e}, sigma_min = {dg['sv_min']:.3e})",
          f"  cota kappa_2 · eps (eps = 2.22e-16) = {cota2:.2e}  -> dígitos garantizados: {math.floor(-math.log10(cota2))}",
          f"  cota kappa_1 · eps = {cota1:.2e}  -> dígitos garantizados: {math.floor(-math.log10(cota1))}",
          f"  kappa_2 con filas equilibradas (D^-1 A, D = máximo de cada fila) = {dg['k2_equil']:.4e}",
          f"  cota con filas equilibradas kappa_2(D^-1 A) · eps = {dg['k2_equil'] * ver.EPS:.2e}", "",
          f"  Casi dependencia (filas escaladas por su máximo; sigma_min de D^-1 A = {dg['se_min']:.3e}):",
          "  vector singular izquierdo asociado (peso por fila F1..F12): "
          + " ".join(f"{v:+.3f}" for v in dg["vec_izq"]),
          f"  F7/s7 ≈ {dg['coef_f7'][0]:.4f} · F3/s3 + {dg['coef_f7'][1]:.4f} · F5/s5, "
          f"desajuste relativo = {dg['rel_f7']:.2e}"]
    (SALIDA / "residuo.txt").write_text("\n".join(R) + "\n", encoding="utf-8")
    return nr, k1, dg["k2"]

def main():
    SALIDA.mkdir(exist_ok=True)
    A, b, A_txt, b_txt = gauss.leer_datos()
    Af, bf = ver.a_fracciones(A_txt, b_txt)
    x_ref = ver.solucion_exacta(Af, bf)
    n = len(A)
    corridas, trazas = {}, {}
    for modo in MODOS:
        trazas[modo] = []
        r = corridas[modo] = gauss.eliminar(A, b, modo, trazas[modo])
        r["err"] = ver.error_relativo(r["x"], x_ref)
        r["digitos"] = ver.digitos_correctos(r["x"], x_ref)
        r["bits_perdidos"] = 53 + math.log2(float(r["err"]))
        r["no_nulos"] = sum(1 for i in range(n) for j in range(i) if r["U"][i][j] != 0.0)
    escribir_traza(corridas, trazas, n)
    escribir_conteo(corridas)
    nr, k1, k2 = escribir_verificacion(corridas, A, b, Af, bf, x_ref)
    for modo in MODOS:
        r, t = corridas[modo], conteo.totales(corridas[modo]["contador"])
        print(f"{NOMBRE[modo]:<26} flops núcleo={t['nucleo']:>5} sobrecosto={t['sobrecosto']:>4} "
              f"mult máx={r['max_mult']:.2e} crec.={r['crecimiento']:.2f} err={float(r['err']):.2e} "
              f"dígitos {min(r['digitos'])}-{max(r['digitos'])}")
    print(f"||r||_inf = {cient(nr, 3)}   kappa_1 = {k1:.3e}   kappa_2 = {k2:.3e}")

if __name__ == "__main__":
    main()

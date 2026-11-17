from pathlib import Path
import conteo
import gauss

SALIDA = Path(__file__).resolve().parent.parent / "resultados"
NOMBRE = {"ninguno": "Sin pivoteo", "escalado": "Pivoteo parcial escalado"}
MODOS = list(NOMBRE)

def escribir_traza(corridas, trazas, n):
    L = ["TRAZA DE LA ELIMINACIÓN (matriz aumentada [A|b] tras cada paso, 9 cifras mostradas)", ""]
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

def main():
    SALIDA.mkdir(exist_ok=True)
    A, b, A_txt, b_txt = gauss.leer_datos()
    n = len(A)
    corridas, trazas = {}, {}
    for modo in MODOS:
        trazas[modo] = []
        r = corridas[modo] = gauss.eliminar(A, b, modo, trazas[modo])
        r["no_nulos"] = sum(1 for i in range(n) for j in range(i) if r["U"][i][j] != 0.0)
    escribir_traza(corridas, trazas, n)
    escribir_conteo(corridas)
    for modo in MODOS:
        r, t = corridas[modo], conteo.totales(corridas[modo]["contador"])
        print(f"{NOMBRE[modo]:<26} flops núcleo={t['nucleo']:>5} sobrecosto={t['sobrecosto']:>4} "
              f"mult máx={r['max_mult']:.2e} crec.={r['crecimiento']:.2f} bits desp.={r['bits_desp']:.1f} no nulos={r['no_nulos']}")

if __name__ == "__main__":
    main()

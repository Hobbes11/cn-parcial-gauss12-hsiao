from pathlib import Path
import conteo
import gauss

SALIDA = Path(__file__).resolve().parent.parent / "resultados"
NOMBRE = {"ninguno": "Sin pivoteo", "escalado": "Pivoteo parcial escalado"}

def escribir_conteo(res):
    md = ["# Conteo de operaciones", ""]
    md.append(conteo.tabla_markdown(res["contador"], NOMBRE["ninguno"]))
    (SALIDA / "conteo_flops.md").write_text("\n".join(md), encoding="utf-8")

def main():
    SALIDA.mkdir(exist_ok=True)
    A, b, A_txt, b_txt = gauss.leer_datos()
    n = len(A)
    res = gauss.eliminar(A, b)
    no_nulos = sum(1 for i in range(n) for j in range(i) if res["U"][i][j] != 0.0)
    print(f"Elementos no nulos bajo la diagonal: {no_nulos} de {n * (n - 1) // 2}")
    for i, xi in enumerate(res["x"]):
        print(f"x[{i + 1:>2}] = {xi:+.15e}")
    escribir_conteo(res)
    t = conteo.totales(res["contador"])
    print(f"Flops del núcleo (sin pivoteo): {t['nucleo']}")

if __name__ == "__main__":
    main()

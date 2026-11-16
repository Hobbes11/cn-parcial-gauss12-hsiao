import gauss

def main():
    A, b, A_txt, b_txt = gauss.leer_datos()
    n = len(A)
    res = gauss.eliminar(A, b)
    no_nulos = sum(1 for i in range(n) for j in range(i) if res["U"][i][j] != 0.0)
    print(f"Elementos no nulos bajo la diagonal: {no_nulos} de {n * (n - 1) // 2}")
    for i, xi in enumerate(res["x"]):
        print(f"x[{i + 1:>2}] = {xi:+.15e}")

if __name__ == "__main__":
    main()
    
def nuevo_contador(n):
    return {
        "n": n,
        "md": [0] * (n - 1),
        "sr": [0] * (n - 1),
        "cmp": [0] * (n - 1),
        "div_escala": [0] * (n - 1),
        "swaps": [0] * (n - 1),
        "cmp_escala": 0,
        "md_reg": 0,
        "sr_reg": 0,
    }

def totales(c):
    md, sr = sum(c["md"]), sum(c["sr"])
    comparaciones = sum(c["cmp"]) + c["cmp_escala"]
    div = sum(c["div_escala"])
    return {
        "md_elim": md,
        "sr_elim": sr,
        "nucleo": md + sr + c["md_reg"] + c["sr_reg"],
        "comparaciones": comparaciones,
        "div_escala": div,
        "intercambios": sum(c["swaps"]),
        "sobrecosto": comparaciones + div
    }

def tabla_markdown(c, titulo):
    t = totales(c)
    L = [f"### {titulo}", "",
         "| Paso k | mult/div | sumas/restas | flops del paso | comparaciones (pivote) | divisiones de escalado | intercambios |"
         ]
    for k in range(c["n"] - 1):
        L.append(f"| {k+1} | {c['md'][k]} | {c['sr'][k]} | {c['md'][k] + c['sr'][k]} | {c['cmp'][k]} | {c['div_escala'][k]} | {c['swaps'][k]} |")
    L.append(f"| Eliminación | {t['md_elim']} | {t['sr_elim']} | {t['md_elim'] + t['sr_elim']} | {sum(c['cmp'])} | {t['div_escala']} | {t['intercambios']} |")
    L.append(f"| Sustitución regresiva | {c['md_reg']} | {c['sr_reg']} | {c['md_reg'] + c['sr_reg']} | 0 | 0 | 0 |")
    L.append(f"| Cálculo de escalas s_i (una vez) | 0 | 0 | 0 | {c['cmp_escala']} | 0 | 0 |")
    L += ["",
          f"- Flops del núcleo (eliminación + b + sustitución regresiva): {t['nucleo']} (mult/div = {t['md_elim'] + c['md_reg']}, sumas/restas = {t['sr_elim'] + c['sr_reg']})",
          f"- Sobrecosto de estabilidad (pivoteo): {t['comparaciones']} comparaciones + {t['div_escala']} divisiones de escalado = {t['sobrecosto']} operaciones; "
          f"{t['intercambios']} intercambios de filas (movimiento de datos, no flops)", ""]
    return "\n".join(L)

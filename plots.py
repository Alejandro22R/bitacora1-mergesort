"""Genera las gráficas del informe a partir de results/summary.csv.

Uso:  python plots.py
Salidas: figures/*.png y results/derived.json (cifras derivadas que cita el informe).
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from mergesort import best_case_comparisons, worst_case_comparisons  # noqa: E402

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)

# Paleta categórica fija (azul, naranja, agua), en ese orden; tinta neutra para texto.
AZUL, NARANJA, AGUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#dcdad4"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "axes.titlecolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.axisbelow": True, "legend.frameon": False, "figure.dpi": 100,
})


def load():
    rows = list(csv.DictReader((ROOT / "results" / "summary.csv").open(encoding="utf-8")))
    data = {}
    for r in rows:
        key = (r["algoritmo"], r["entrada"])
        data.setdefault(key, []).append({
            "n": int(r["n"]), "t": float(r["tiempo_mediana_s"]),
            "c": float(r["comparaciones_mediana"]) if r["comparaciones_mediana"] else None,
            "rt": float(r["razon_tiempo_T2n_Tn"]) if r["razon_tiempo_T2n_Tn"] else None,
            "rc": float(r["razon_comparaciones_C2n_Cn"]) if r["razon_comparaciones_C2n_Cn"] else None,
        })
    return data


def col(series, k):
    return np.array([s[k] for s in series if s[k] is not None], dtype=float)


def ns_for(series, k):
    return np.array([s["n"] for s in series if s[k] is not None], dtype=float)


D = load()
M_ALE = D[("mergesort", "aleatoria")]
M_ORD = D[("mergesort", "ordenada")]
M_PEO = D[("mergesort", "peor_caso")]
INS = D[("insercion", "aleatoria")]
n_m = col(M_ALE, "n")
n_i = col(INS, "n")

# ---------------- Figura 1: tiempo en escala normal ----------------
fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.9))
a = ax[0]
a.plot(n_m, col(M_ALE, "t") * 1e3, "-o", color=AZUL, ms=4, lw=1.6, label="Aleatoria")
a.plot(n_m, col(M_PEO, "t") * 1e3, "-s", color=NARANJA, ms=4, lw=1.6, label="Peor caso")
a.plot(n_m, col(M_ORD, "t") * 1e3, "-^", color=AGUA, ms=4, lw=1.6, label="Ordenada")
a.set_xlabel("n (elementos)")
a.set_ylabel("Tiempo, mediana (ms)")
a.set_title("(a) Mergesort según el tipo de entrada", fontsize=9, loc="left")
a.legend(loc="upper left")
a.ticklabel_format(axis="x", style="plain")

b = ax[1]
sel = n_m <= n_i.max()
b.plot(n_m[sel], col(M_ALE, "t")[sel] * 1e3, "-o", color=AZUL, ms=4, lw=1.6, label="Mergesort")
b.plot(n_i, col(INS, "t") * 1e3, "-s", color=NARANJA, ms=4, lw=1.6, label="Inserción")
b.set_xlabel("n (elementos)")
b.set_ylabel("Tiempo, mediana (ms)")
b.set_title("(b) Contra un ordenamiento cuadrático", fontsize=9, loc="left")
b.legend(loc="upper left")
fig.tight_layout()
fig.savefig(FIG / "fig1_tiempo_escala_normal.png", dpi=200)
plt.close(fig)

# ---------------- Figura 2: log-log ----------------
fig, a = plt.subplots(figsize=(4.8, 3.4))
a.loglog(n_m, col(M_ALE, "t"), "-o", color=AZUL, ms=4, lw=1.6, label="Mergesort, aleatoria")
a.loglog(n_i, col(INS, "t"), "-s", color=NARANJA, ms=4, lw=1.6, label="Inserción, aleatoria")
# Referencias ancladas en n = 2^10 (sin etiquetas dentro de las curvas)
n0 = 1024.0
t_m0 = col(M_ALE, "t")[list(n_m).index(n0)]
t_i0 = col(INS, "t")[list(n_i).index(n0)]
ref_n = np.array([256.0, 131072.0])
a.loglog(ref_n, t_m0 * (ref_n * np.log2(ref_n)) / (n0 * math.log2(n0)), "--", color=MUTED, lw=1,
         label="Referencia $c\\,n\\lg n$")
ref_n2 = np.array([256.0, 8192.0])
a.loglog(ref_n2, t_i0 * (ref_n2 / n0) ** 2, ":", color=MUTED, lw=1.2, label="Referencia $c\\,n^2$")
a.set_xlabel("n (elementos, escala log)")
a.set_ylabel("Tiempo, mediana (s, escala log)")
a.legend(loc="upper left", fontsize=8)
fig.tight_layout()
fig.savefig(FIG / "fig2_tiempo_loglog.png", dpi=200)
plt.close(fig)

# ---------------- Figura 3: razón T(2n)/T(n) ----------------
fig, a = plt.subplots(figsize=(4.8, 3.2))
nt = ns_for(M_ALE, "rt")
a.semilogx(nt, col(M_ALE, "rt"), "o", color=AZUL, ms=5, label="Mergesort, tiempo")
a.semilogx(ns_for(M_ALE, "rc"), col(M_ALE, "rc"), "-", color=AGUA, lw=1.6, label="Mergesort, comparaciones")
a.semilogx(ns_for(INS, "rt"), col(INS, "rt"), "s", color=NARANJA, ms=5, label="Inserción, tiempo")
grid_n = np.array(sorted(set(list(n_m))))
a.semilogx(grid_n, 2 * np.log2(2 * grid_n) / np.log2(grid_n), "--", color=MUTED, lw=1,
           label="Teoría $2(1+1/\\lg n)$")
a.axhline(4, color=MUTED, lw=1, ls=":")
a.text(grid_n[-1], 4.05, "4 (cuadrático)", ha="right", va="bottom", fontsize=8, color=MUTED)
a.set_xlabel("n (escala log)")
a.set_ylabel("Razón T(2n)/T(n)")
a.set_ylim(1.5, 5.2)
a.legend(loc="center right", fontsize=8)
fig.tight_layout()
fig.savefig(FIG / "fig3_razon_T2n_Tn.png", dpi=200)
plt.close(fig)

# ---------------- Figura 4: comparaciones normalizadas por n lg n ----------------
fig, a = plt.subplots(figsize=(4.8, 3.2))
nn = n_m
norm = nn * np.log2(nn)
a.semilogx(nn, col(M_PEO, "c") / norm, "-s", color=NARANJA, ms=4, lw=1.6, label="Peor caso (medido)")
a.semilogx(nn, col(M_ALE, "c") / norm, "-o", color=AZUL, ms=4, lw=1.6, label="Aleatoria (medido)")
a.semilogx(nn, col(M_ORD, "c") / norm, "-^", color=AGUA, ms=4, lw=1.6, label="Ordenada (medido)")
a.semilogx(nn, [worst_case_comparisons(int(n)) / (n * math.log2(n)) for n in nn], "--", color=MUTED, lw=1,
           label="Fórmulas exactas")
a.semilogx(nn, [best_case_comparisons(int(n)) / (n * math.log2(n)) for n in nn], "--", color=MUTED, lw=1)
a.semilogx(nn, (nn * np.log2(nn) - 1.25 * nn) / norm, ":", color=MUTED, lw=1.2, label="$n\\lg n-1.25n$ (promedio)")
a.set_xlabel("n (escala log)")
a.set_ylabel("Comparaciones / (n lg n)")
a.set_ylim(0.4, 1.05)
a.legend(loc="center right", fontsize=8)
fig.tight_layout()
fig.savefig(FIG / "fig4_comparaciones.png", dpi=200)
plt.close(fig)

# ---------------- Cifras derivadas ----------------
def slope(ns, ys):
    return float(np.polyfit(np.log(ns), np.log(ys), 1)[0])

avg_theory = [(n * math.log2(n) - 1.25 * n) for n in n_m]
rel_err = [(c - t) / t * 100 for c, t in zip(col(M_ALE, "c"), avg_theory)]
exact_match_worst = all(int(c) == worst_case_comparisons(int(n)) for c, n in zip(col(M_PEO, "c"), n_m))
exact_match_best = all(int(c) == best_case_comparisons(int(n)) for c, n in zip(col(M_ORD, "c"), n_m))
rt_m = col(M_ALE, "rt")
rt_i = col(INS, "rt")
t_m = col(M_ALE, "t")
t_i = col(INS, "t")
common = [n for n in n_i]
speedup = {int(n): float(t_i[list(n_i).index(n)] / t_m[list(n_m).index(n)]) for n in common}

derived = {
    "pendiente_loglog_mergesort_aleatoria": slope(n_m, t_m),
    "pendiente_loglog_mergesort_n_ge_1024": slope(n_m[n_m >= 1024], t_m[n_m >= 1024]),
    "pendiente_loglog_insercion": slope(n_i, t_i),
    "razon_tiempo_mergesort": {"min": float(rt_m.min()), "max": float(rt_m.max()),
                                "mediana": float(np.median(rt_m))},
    "razon_tiempo_insercion": {"min": float(rt_i.min()), "max": float(rt_i.max()),
                                "mediana": float(np.median(rt_i))},
    "error_relativo_comparaciones_vs_nlgn_menos_1.25n_pct": {int(n): round(e, 3) for n, e in zip(n_m, rel_err)},
    "peor_caso_coincide_exacto_con_formula": exact_match_worst,
    "mejor_caso_coincide_exacto_con_formula": exact_match_best,
    "cociente_tiempo_insercion_sobre_mergesort": speedup,
    "tiempo_ordenada_sobre_aleatoria_mediana": float(np.median(col(M_ORD, "t") / t_m)),
    "razon_teorica_nlgn_rango": [float(2 * math.log2(2 * n_m[-2]) / math.log2(n_m[-2])),
                                 float(2 * math.log2(2 * n_m[0]) / math.log2(n_m[0]))],
}
(ROOT / "results" / "derived.json").write_text(json.dumps(derived, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(derived, indent=2, ensure_ascii=False))

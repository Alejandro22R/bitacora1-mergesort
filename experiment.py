"""Experimento reproducible: tiempo y comparaciones de mergesort.

Uso:  python experiment.py            (semilla por defecto 2026)
      python experiment.py --seed 7   (otra semilla)

Diseño
    * Tamaños que se duplican: mergesort 2^8 ... 2^17 (10 tamaños);
      inserción (referencia cuadrática) 2^8 ... 2^13 (6 tamaños).
    * 5 repeticiones por tamaño y por tipo de entrada; se reporta la mediana.
    * Entradas: permutación aleatoria (caso promedio), ya ordenada (mejor caso)
      y permutación de peor caso (construida por `worst_case_permutation`).
    * Semilla fija: random.Random(semilla * 1_000_003 + n) genera las permutaciones
      aleatorias de cada tamaño, de modo que no dependen del orden de ejecución.
    * Se hace una corrida de calentamiento por tamaño (no se registra), el
      recolector de basura se desactiva durante la medición y el reloj es
      time.perf_counter_ns().
    * Además del tiempo se cuentan las comparaciones entre elementos, que no
      dependen de la máquina.

Salidas (carpeta results/):
    raw_measurements.csv   una fila por repetición
    summary.csv            una fila por (algoritmo, entrada, n) con medianas y razones
    environment.json       datos del entorno y de la corrida
"""

from __future__ import annotations

import argparse
import csv
import gc
import json
import math
import platform
import random
import statistics
import sys
import time
from importlib import metadata
from pathlib import Path

from insertion_sort import insertion_sort
from mergesort import mergesort_counted, worst_case_permutation

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"

REPS = 5
SIZES_MERGE = [2**k for k in range(8, 18)]
SIZES_INSERTION = [2**k for k in range(8, 14)]


def make_input(kind: str, n: int, rng: random.Random) -> list:
    if kind == "aleatoria":
        a = list(range(n))
        rng.shuffle(a)
        return a
    if kind == "ordenada":
        return list(range(n))
    if kind == "peor_caso":
        return worst_case_permutation(n)
    raise ValueError(kind)


def timed(fn, data):
    """Devuelve (segundos, resultado). El GC se apaga solo durante la medición."""
    gc.collect()
    gc.disable()
    try:
        t0 = time.perf_counter_ns()
        out = fn(data)
        t1 = time.perf_counter_ns()
    finally:
        gc.enable()
    return (t1 - t0) / 1e9, out


def run(seed: int):
    rows = []
    plan = [("mergesort", "aleatoria", SIZES_MERGE),
            ("mergesort", "ordenada", SIZES_MERGE),
            ("mergesort", "peor_caso", SIZES_MERGE),
            ("insercion", "aleatoria", SIZES_INSERTION)]
    for algo, kind, sizes in plan:
        for n in sizes:
            rng = random.Random(seed * 1_000_003 + n)
            warm = make_input(kind, n, rng)
            if algo == "mergesort":
                mergesort_counted(warm)
            else:
                insertion_sort(warm)
            for rep in range(1, REPS + 1):
                data = make_input(kind, n, rng)
                expected = sorted(data)
                if algo == "mergesort":
                    secs, (out, comps) = timed(mergesort_counted, data)
                else:
                    secs, out = timed(insertion_sort, data)
                    comps = ""
                assert out == expected, f"resultado incorrecto: {algo} {kind} n={n}"
                rows.append({"algoritmo": algo, "entrada": kind, "n": n,
                             "rep": rep, "tiempo_s": secs, "comparaciones": comps})
            print(f"  {algo:9s} {kind:10s} n={n:>7d} listo", flush=True)
    return rows


def summarize(rows):
    groups = {}
    for r in rows:
        groups.setdefault((r["algoritmo"], r["entrada"], r["n"]), []).append(r)
    summary = []
    for (algo, kind, n), g in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2])):
        times = [x["tiempo_s"] for x in g]
        comps = [x["comparaciones"] for x in g if x["comparaciones"] != ""]
        summary.append({
            "algoritmo": algo, "entrada": kind, "n": n,
            "tiempo_mediana_s": statistics.median(times),
            "tiempo_min_s": min(times), "tiempo_max_s": max(times),
            "comparaciones_mediana": statistics.median(comps) if comps else "",
        })
    # razones T(2n)/T(n) y C(2n)/C(n)
    index = {(s["algoritmo"], s["entrada"], s["n"]): s for s in summary}
    for s in summary:
        nxt = index.get((s["algoritmo"], s["entrada"], 2 * s["n"]))
        s["razon_tiempo_T2n_Tn"] = nxt["tiempo_mediana_s"] / s["tiempo_mediana_s"] if nxt else ""
        if nxt and s["comparaciones_mediana"] != "":
            s["razon_comparaciones_C2n_Cn"] = nxt["comparaciones_mediana"] / s["comparaciones_mediana"]
        else:
            s["razon_comparaciones_C2n_Cn"] = ""
        n = s["n"]
        s["razon_teorica_nlgn"] = 2 * math.log2(2 * n) / math.log2(n)
    return summary


def write_csv(path: Path, rows, fields):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.9g}" if isinstance(v, float) else v) for k, v in r.items()})


def cpu_model() -> str:
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as f:
            for line in f:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "desconocido"


def versions():
    out = {}
    for pkg in ("hypothesis", "matplotlib", "numpy"):
        try:
            out[pkg] = metadata.version(pkg)
        except metadata.PackageNotFoundError:
            out[pkg] = "no instalado"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()
    RESULTS.mkdir(exist_ok=True)

    print(f"Semilla {args.seed}. Corriendo experimento...")
    t0 = time.time()
    rows = run(args.seed)
    summary = summarize(rows)

    write_csv(RESULTS / "raw_measurements.csv", rows,
              ["algoritmo", "entrada", "n", "rep", "tiempo_s", "comparaciones"])
    write_csv(RESULTS / "summary.csv", summary,
              ["algoritmo", "entrada", "n", "tiempo_mediana_s", "tiempo_min_s", "tiempo_max_s",
               "comparaciones_mediana", "razon_tiempo_T2n_Tn", "razon_comparaciones_C2n_Cn",
               "razon_teorica_nlgn"])

    env = {
        "semilla": args.seed,
        "repeticiones_por_tamano": REPS,
        "tamanos_mergesort": SIZES_MERGE,
        "tamanos_insercion": SIZES_INSERTION,
        "python": sys.version,
        "implementacion": platform.python_implementation(),
        "sistema": platform.platform(),
        "procesador": cpu_model(),
        "nucleos_logicos": __import__("os").cpu_count(),
        "reloj": "time.perf_counter_ns()",
        "gc_durante_medicion": "desactivado",
        "paquetes": versions(),
        "duracion_total_s": round(time.time() - t0, 1),
    }
    (RESULTS / "environment.json").write_text(json.dumps(env, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Listo en {env['duracion_total_s']} s. Resultados en {RESULTS}")


if __name__ == "__main__":
    main()

# Bitácora 1: Mergesort (Equipo 4)

Maestría en Tecnologías de la Información, Cohorte X, 2026-III. Análisis y Diseño de Algoritmos, Profa. Msc. Sosa.

Integrantes: Dulce Pérez, Ramón Maita, Ingrid Martínez y Rafael Berroterán.

Este repositorio contiene la implementación de Mergesort descendente con conteo exacto de comparaciones, sus pruebas, el experimento de tiempos y comparaciones, y las gráficas del informe `Equipo_4_Bitacora1.pdf`.

## Requisitos y versiones

| Componente | Versión usada en la corrida original |
|---|---|
| Python (CPython) | 3.13.18 |
| hypothesis | 6.170.14 |
| matplotlib | 3.11.2 |
| numpy | 2.5.3 |
| Sistema | Linux 6.18.44 x86_64, Intel Xeon 2,10 GHz, 2 núcleos lógicos |

El algoritmo y las pruebas unitarias usan solo la biblioteca estándar. Hypothesis se necesita para las 4 pruebas basadas en propiedades (si no está instalada, esas pruebas se omiten y el resto corre igual), y matplotlib y numpy solo se usan para las gráficas.

## Comandos exactos

Desde la carpeta raíz del proyecto:

```bash
python -m venv .venv
source .venv/bin/activate          # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
python experiment.py --seed 2026
python plots.py
```

* `python -m unittest discover -s tests -v` ejecuta 19 pruebas; deben pasar todas.
* `python experiment.py --seed 2026` tarda unos 15 segundos en el equipo original y escribe `results/raw_measurements.csv`, `results/summary.csv` y `results/environment.json`.
* `python plots.py` lee `results/summary.csv` y escribe las cuatro figuras en `figures/` y las cifras derivadas en `results/derived.json`.

## Semillas

* Experimento: semilla 2026. Cada tamaño n usa `random.Random(2026 * 1_000_003 + n)`, de modo que las permutaciones no dependen del orden de ejecución.
* Pruebas con aleatoriedad: `random.Random(2026)` (diferencial y conteo) y `random.Random(4)` (estabilidad).
* Hypothesis: `derandomize=True`, con 300 ejemplos por propiedad.

## Qué debería reproducir otra máquina

Con la misma versión de Python, las permutaciones y por tanto las comparaciones son idénticas: la lista ordenada y la permutación de peor caso dan exactamente B(n) y W(n), y la entrada aleatoria queda muy cerca de n lg n − 1,25n. Los tiempos en segundos cambian con la máquina; lo que debe mantenerse es la forma de las curvas (pendiente log-log cercana a 1,1 para Mergesort y a 2 para inserción) y que la razón T(2n)/T(n) de Mergesort ronde 2,1 con algo de ruido (entre 1,9 y 2,5 en la corrida original).

## Estructura

```
mergesort.py          merge, mergesort_counted, mergesort y fórmulas teóricas B(n), W(n)
insertion_sort.py     ordenamiento por inserción (referencia cuadrática)
tests/test_mergesort.py   19 pruebas: unitarias, diferenciales y por propiedades
experiment.py         experimento (10 tamaños de 2^8 a 2^17, 5 repeticiones, mediana)
plots.py              figuras y cifras derivadas
results/              datos crudos, resumen, entorno y cifras derivadas
figures/              gráficas en escala normal, log-log, razón T(2n)/T(n) y comparaciones
```

Correspondencia con el informe: la Figura 1 es `fig1`, la Figura 2 junta `fig2` (log-log) y `fig3` (razón T(2n)/T(n)), y la Figura 3 es `fig4` (comparaciones).

## Nota sobre el entorno de la corrida original

Los datos incluidos se generaron en el entorno de ejecución en la nube del asistente de IA usado por el equipo (ver el registro de uso de IA del informe), no en un computador personal. Quien quiera medir su propio equipo puede volver a correr `experiment.py` y `plots.py`; `results/environment.json` guardará los datos de esa máquina.

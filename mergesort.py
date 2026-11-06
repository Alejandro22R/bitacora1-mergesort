"""Mergesort descendente (top-down) con conteo exacto de comparaciones.

Bitácora 1 · Análisis y Diseño de Algoritmos · Equipo 4.

Especificación
    Entrada : lista `a` de n elementos con un orden total (operador `<`).
    Salida  : lista nueva `b`, permutación de `a`, tal que b[0] <= b[1] <= ... <= b[n-1].
    Pre     : los elementos de `a` son comparables entre sí con `<`.
    Post    : `b` es permutación de `a`, está ordenada y el orden es estable
              (los elementos equivalentes conservan su orden relativo de entrada).

La entrada nunca se modifica. El costo auxiliar de memoria es Θ(n).
"""

from __future__ import annotations

from typing import Any, List, Sequence, Tuple


def merge(left: Sequence[Any], right: Sequence[Any]) -> Tuple[List[Any], int]:
    """Mezcla dos secuencias ordenadas y devuelve (resultado, comparaciones).

    Invariante del ciclo principal (con k = i + j):
        out[0:k] contiene los k menores elementos de left[0:i] + right[0:j],
        ordenados, y cada elemento de out[0:k] es <= left[i] y <= right[j]
        (cuando esos índices existen).

    Cada iteración hace exactamente una comparación y avanza i o j, por lo que
    al salir del ciclo el número de comparaciones es i + j.
    """
    i = j = 0
    n_left, n_right = len(left), len(right)
    out: List[Any] = []
    while i < n_left and j < n_right:
        if right[j] < left[i]:
            out.append(right[j])
            j += 1
        else:
            out.append(left[i])
            i += 1
    comparisons = i + j
    out.extend(left[i:])
    out.extend(right[j:])
    return out, comparisons


def mergesort_counted(a: Sequence[Any]) -> Tuple[List[Any], int]:
    """Ordena `a` y devuelve (lista_ordenada, comparaciones_entre_elementos)."""
    n = len(a)
    if n <= 1:
        return list(a), 0
    mid = n // 2
    left, c_left = mergesort_counted(a[:mid])
    right, c_right = mergesort_counted(a[mid:])
    merged, c_merge = merge(left, right)
    return merged, c_left + c_right + c_merge


def mergesort(a: Sequence[Any]) -> List[Any]:
    """Ordena `a` y devuelve una lista nueva."""
    return mergesort_counted(a)[0]


# Fórmulas teóricas de comparaciones

def worst_case_comparisons(n: int) -> int:
    """W(n) = n*ceil(lg n) - 2**ceil(lg n) + 1, con W(0) = W(1) = 0."""
    if n <= 1:
        return 0
    k = (n - 1).bit_length()
    return n * k - (1 << k) + 1


def best_case_comparisons(n: int) -> int:
    """B(n) = floor(n/2) + B(floor(n/2)) + B(ceil(n/2)), con B(0) = B(1) = 0."""
    if n <= 1:
        return 0
    h = n // 2
    return h + best_case_comparisons(h) + best_case_comparisons(n - h)


def worst_case_permutation(n: int) -> List[int]:
    """Permutación de range(n) que obliga a hacer W(n) comparaciones.

    Se construye al revés de la mezcla: la mitad izquierda recibe los rangos
    impares y la derecha los pares, de modo que cada mezcla alterna los
    elementos de ambos lados y agota un lado solo al final.
    """
    if n <= 1:
        return list(range(n))
    n_left = n // 2
    left = worst_case_permutation(n_left)
    right = worst_case_permutation(n - n_left)
    return [2 * x + 1 for x in left] + [2 * x for x in right]

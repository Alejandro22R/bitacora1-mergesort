"""Ordenamiento por inserción: referencia cuadrática para el contraste.

Se usa solo como comparación del experimento y como oráculo adicional en las
pruebas. Es el algoritmo que ya resuelve la Guía de lectura; aquí no se analiza.
"""

from __future__ import annotations

from typing import Any, List, Sequence


def insertion_sort(a: Sequence[Any]) -> List[Any]:
    """Devuelve una lista nueva ordenada (estable)."""
    out = list(a)
    for k in range(1, len(out)):
        key = out[k]
        j = k - 1
        while j >= 0 and key < out[j]:
            out[j + 1] = out[j]
            j -= 1
        out[j + 1] = key
    return out

"""Pruebas unitarias, diferenciales y basadas en propiedades de mergesort.

Ejecutar desde la raíz del proyecto:  python -m unittest discover -s tests -v
"""

import math
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from insertion_sort import insertion_sort
from mergesort import (
    best_case_comparisons,
    merge,
    mergesort,
    mergesort_counted,
    worst_case_comparisons,
    worst_case_permutation,
)

try:
    from hypothesis import given, settings, strategies as st

    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False


class Item:
    """Elemento cuyo orden depende solo de `key`; `tag` sirve para verificar estabilidad."""

    def __init__(self, key, tag):
        self.key, self.tag = key, tag

    def __lt__(self, other):
        return self.key < other.key


class CasosBase(unittest.TestCase):
    def test_vacio_y_un_elemento(self):
        self.assertEqual(mergesort([]), [])
        self.assertEqual(mergesort([7]), [7])

    def test_dos_elementos(self):
        self.assertEqual(mergesort([2, 1]), [1, 2])
        self.assertEqual(mergesort([1, 2]), [1, 2])

    def test_ejemplo_pequeno(self):
        self.assertEqual(mergesort([5, 2, 4, 7, 1, 3, 2, 6]), [1, 2, 2, 3, 4, 5, 6, 7])

    def test_ordenado_inverso_e_iguales(self):
        self.assertEqual(mergesort(list(range(50))), list(range(50)))
        self.assertEqual(mergesort(list(range(50, 0, -1))), list(range(1, 51)))
        self.assertEqual(mergesort([3] * 20), [3] * 20)

    def test_negativos_y_cadenas(self):
        self.assertEqual(mergesort([0, -5, 3, -1]), [-5, -1, 0, 3])
        self.assertEqual(mergesort(["b", "a", "c", "a"]), ["a", "a", "b", "c"])

    def test_no_modifica_la_entrada(self):
        original = [4, 3, 2, 1]
        copia = list(original)
        mergesort(original)
        self.assertEqual(original, copia)

    def test_merge_directo(self):
        self.assertEqual(merge([1, 4, 9], [2, 3, 10, 11])[0], [1, 2, 3, 4, 9, 10, 11])
        self.assertEqual(merge([], [1, 2]), ([1, 2], 0))
        self.assertEqual(merge([1, 2], []), ([1, 2], 0))

    def test_estabilidad(self):
        rng = random.Random(4)
        items = [Item(rng.randint(0, 5), idx) for idx in range(200)]
        resultado = mergesort(items)
        for a, b in zip(resultado, resultado[1:]):
            self.assertLessEqual(a.key, b.key)
            if a.key == b.key:
                self.assertLess(a.tag, b.tag)


class ConteoDeComparaciones(unittest.TestCase):
    def test_peor_caso_coincide_con_la_formula(self):
        for n in range(0, 301):
            _, c = mergesort_counted(worst_case_permutation(n))
            self.assertEqual(c, worst_case_comparisons(n), msg=f"n={n}")

    def test_mejor_caso_en_entrada_ordenada(self):
        for n in range(0, 301):
            _, c = mergesort_counted(list(range(n)))
            self.assertEqual(c, best_case_comparisons(n), msg=f"n={n}")

    def test_potencia_de_dos_tiene_forma_cerrada(self):
        for k in range(1, 15):
            n = 2**k
            self.assertEqual(worst_case_comparisons(n), n * k - n + 1)
            self.assertEqual(best_case_comparisons(n), (n // 2) * k)

    def test_cota_superior_con_constantes_explicitas(self):
        for n in range(1, 20001):
            self.assertLessEqual(worst_case_comparisons(n), n * math.log2(n) + 1e-9, msg=f"n={n}")

    def test_cota_inferior_con_constantes_explicitas(self):
        for n in range(4, 20001):
            self.assertGreaterEqual(worst_case_comparisons(n), 0.5 * n * math.log2(n), msg=f"n={n}")

    def test_toda_entrada_queda_entre_mejor_y_peor_caso(self):
        rng = random.Random(2026)
        for n in (1, 2, 3, 10, 33, 100, 257):
            for _ in range(30):
                datos = [rng.randrange(0, 3 * n) for _ in range(n)]
                _, c = mergesort_counted(datos)
                self.assertGreaterEqual(c, best_case_comparisons(n))
                self.assertLessEqual(c, worst_case_comparisons(n))


class Diferencial(unittest.TestCase):
    """Prueba diferencial con semilla fija contra sorted() y contra inserción."""

    def test_contra_sorted_y_contra_insercion(self):
        rng = random.Random(2026)
        for _ in range(500):
            n = rng.randint(0, 120)
            datos = [rng.randint(-50, 50) for _ in range(n)]
            esperado = sorted(datos)
            self.assertEqual(mergesort(datos), esperado)
            self.assertEqual(insertion_sort(datos), esperado)


@unittest.skipUnless(HAS_HYPOTHESIS, "hypothesis no está instalado")
class Propiedades(unittest.TestCase):
    """Pruebas basadas en propiedades (derandomize=True, por lo que son reproducibles)."""

    @settings(max_examples=300, derandomize=True, deadline=None)
    @given(st.lists(st.integers(min_value=-1000, max_value=1000), max_size=200))
    def test_igual_a_sorted(self, xs):
        self.assertEqual(mergesort(xs), sorted(xs))

    @settings(max_examples=300, derandomize=True, deadline=None)
    @given(st.lists(st.integers(min_value=-1000, max_value=1000), max_size=200))
    def test_es_permutacion_y_esta_ordenada(self, xs):
        ys = mergesort(xs)
        self.assertEqual(sorted(ys), sorted(xs))
        self.assertTrue(all(a <= b for a, b in zip(ys, ys[1:])))

    @settings(max_examples=300, derandomize=True, deadline=None)
    @given(st.lists(st.integers(min_value=0, max_value=5), max_size=150))
    def test_estable_por_propiedad(self, claves):
        items = [Item(k, idx) for idx, k in enumerate(claves)]
        esperado = sorted(items, key=lambda it: it.key)
        resultado = mergesort(items)
        self.assertEqual([(i.key, i.tag) for i in resultado], [(i.key, i.tag) for i in esperado])

    @settings(max_examples=300, derandomize=True, deadline=None)
    @given(st.lists(st.integers(), max_size=200))
    def test_idempotente_y_conteo_acotado(self, xs):
        ys, c = mergesort_counted(xs)
        self.assertEqual(mergesort(ys), ys)
        self.assertGreaterEqual(c, best_case_comparisons(len(xs)))
        self.assertLessEqual(c, worst_case_comparisons(len(xs)))


if __name__ == "__main__":
    unittest.main(verbosity=2)

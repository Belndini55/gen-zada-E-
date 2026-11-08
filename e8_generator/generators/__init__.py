"""Inicjalizacja wszystkich 12 działów generatorów zadań CKE E8 oraz pakietów proceduralnych."""

from __future__ import annotations

from . import (
    g01_liczby,
    g02_procenty,
    g03_potegi,
    g04_pierwiastki,
    g05_wyrazenia,
    g06_rownania,
    g07_predkosc,
    g08_wspolrzedne,
    g09_planimetria,
    g10_stereometria,
    g11_statystyka,
    g12_prawdop,
    g13_cke_archiwum,
    g14_procedural_algebra,
    g15_procedural_geometria_dane,
)
from .base import REGISTRY

__all__ = ["REGISTRY"]

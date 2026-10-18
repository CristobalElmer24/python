from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AFND:
    """Autómata finito no determinista (con transiciones ε).
    Una transición es (origen, simbolos, destino); simbolos=None significa ε."""
    estados: list
    alfabeto: list
    transiciones: list
    inicial: str
    finales: frozenset


@dataclass
class AFD:
    estados: list
    alfabeto: list
    delta: dict            # (estado, símbolo) -> estado
    inicial: str
    finales: frozenset
    composicion: dict = field(default_factory=dict)  # estado AFD -> estados del AFND
    trampa: Optional[str] = None

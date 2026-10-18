from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Token:
    tipo: str
    lexema: str
    posicion: int

    def a_dict(self):
        return asdict(self)

from __future__ import annotations
from math import log2, pow
from typing import Any, Callable, Dict, Optional
import json


class Halstead:
    def __init__(self, u_operators: float = 0., operators: float = 0., u_operands: float = 0., operands: float = 0.):
        self.n: int = int(u_operators or operators or u_operands or operands)

        self.u_operators: float = u_operators
        self.operators: float = operators

        self.u_operands: float = u_operands
        self.operands: float = operands

    def try_calc(func: Callable[..., float]) -> Callable[..., Optional[float]]:  # type: ignore
        def wrap(*args: Any, **kwargs: Any) -> Optional[float]:
            try:
                result: Optional[float] = func(*args, **kwargs)
            except:
                result = None
            return result
        return wrap

    @try_calc
    def length(self) -> float:
        return self.operators + self.operands

    @try_calc
    def estimated_program_length(self) -> float:
        return self.u_operators * log2(self.u_operators) + self.u_operands * log2(self.u_operands)

    @try_calc
    def purity_ratio(self) -> float:
        estimated_program_length: Optional[float] = self.estimated_program_length()
        length: Optional[float] = self.length()

        if estimated_program_length is None or length is None:
            raise TypeError

        return estimated_program_length / length

    @try_calc
    def vocabulary(self) -> float:
        return self.u_operators + self.u_operands

    @try_calc
    def volume(self) -> float:
        length: Optional[float] = self.length()
        vocabulary: Optional[float] = self.vocabulary()

        if length is None or vocabulary is None:
            raise TypeError

        return length * log2(vocabulary)

    @try_calc
    def difficulty(self) -> float:
        return (self.u_operators / 2.) * (self.operands / self.u_operands)

    @try_calc
    def level(self) -> float:
        difficulty: Optional[float] = self.difficulty()

        if difficulty is None:
            raise TypeError

        return 1. / difficulty

    @try_calc
    def effort(self) -> float:
        difficulty: Optional[float] = self.difficulty()
        volume: Optional[float] = self.volume()

        if difficulty is None or volume is None:
            raise TypeError

        return difficulty * volume

    @try_calc
    def time(self) -> float:
        effort: Optional[float] = self.effort()

        if effort is None:
            raise TypeError

        return effort / 18.

    @try_calc
    def bugs(self) -> float:
        effort: Optional[float] = self.effort()

        if effort is None:
            raise TypeError

        return pow(effort, 2. / 3.) / 3000.

    @classmethod
    def from_data(cls, data: Dict[str, float]) -> Halstead:
        return cls(
            u_operators=data["n1"],
            operators=data["N1"],
            u_operands=data["n2"],
            operands=data["N2"]
        )

    def __str__(self) -> str:
        return json.dumps(self.as_dict(), indent=4)

    def __repr__(self) -> str:
        return json.dumps(self.as_dict(), indent=4)

    def as_dict(self) -> Dict[str, Optional[float]]:
        return {
            "n1": self.u_operators,
            "N1": self.operators,
            "n2": self.u_operands,
            "N2": self.operands,
            "length": self.length(),
            "estimated_program_length": self.estimated_program_length(),
            "purity_ratio": self.purity_ratio(),
            "vocabulary": self.vocabulary(),
            "volume": self.volume(),
            "difficulty": self.difficulty(),
            "level": self.level(),
            "effort": self.effort(),
            "time": self.time(),
            "bugs": self.bugs()
        }

    def avg(self) -> Dict[str, Optional[float]]:
        return {k: (v / self.n if self.n and v else None) for k, v in self.as_dict().items()}

    def merge(self, other: Halstead) -> None:
        self.n += 1

        self.u_operators += other.u_operators
        self.operators += other.operators

        self.u_operands += other.u_operands
        self.operands += other.operands

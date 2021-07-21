from __future__ import annotations
from math import log2, pow
from typing import Any, Callable, Dict, Optional
import json


class Halstead:
    def __init__(
        self,
        u_operators: float = 0.,
        operators: float = 0.,
        u_operands: float = 0.,
        operands: float = 0.
    ):
        self.n: int = int(sum([u_operators, operators, u_operands, operands]) > 0.)

        self.u_operators = u_operators
        self.operators: float = operators

        self.u_operands: float = u_operands
        self.operands: float = operands

    def try_calc(  # type: ignore
        func: Callable[..., Optional[float]]
    ) -> Callable[..., Optional[float]]:
        def wrap(*args: Any, **kwargs: Any) -> Optional[float]:
            try:
                result = func(*args, **kwargs)
            except:
                result = None
            return result
        return wrap

    @try_calc
    def length(self) -> Optional[float]:
        return self.operators + self.operands

    @try_calc
    def estimated_program_length(self) -> Optional[float]:
        return self.u_operators * log2(self.u_operators) + self.u_operands * log2(self.u_operands)

    @try_calc
    def purity_ratio(self) -> Optional[float]:
        estimated_program_length = self.estimated_program_length()
        length = self.length()

        if estimated_program_length is None or length is None:
            raise TypeError

        return estimated_program_length / length

    @try_calc
    def vocabulary(self) -> Optional[float]:
        return self.u_operators + self.u_operands

    @try_calc
    def volume(self) -> Optional[float]:
        length = self.length()
        vocabulary = self.vocabulary()

        if length is None or vocabulary is None:
            raise TypeError

        return length * log2(vocabulary)

    @try_calc
    def difficulty(self) -> Optional[float]:
        return (self.u_operators / 2.) * (self.operands / self.u_operands)

    @try_calc
    def level(self) -> Optional[float]:
        difficulty = self.difficulty()

        if difficulty is None:
            raise TypeError

        return 1. / difficulty

    @try_calc
    def effort(self) -> Optional[float]:
        difficulty = self.difficulty()
        volume = self.volume()

        if difficulty is None or volume is None:
            raise TypeError

        return difficulty * volume

    @try_calc
    def time(self) -> Optional[float]:
        effort = self.effort()

        if effort is None:
            raise TypeError

        return effort / 18.

    @try_calc
    def bugs(self) -> Optional[float]:
        effort = self.effort()

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
            "n": self.n,
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

    @try_calc
    def avg_value(self, value: float) -> Optional[float]:
        return value / self.n

    def avg(self) -> Dict[str, Optional[float]]:
        avg = Halstead(
            self.avg_value(self.u_operators) or 0.,
            self.avg_value(self.operators) or 0.,
            self.avg_value(self.u_operands) or 0.,
            self.avg_value(self.operands) or 0.
        )
        avg.n = self.n

        return avg.as_dict()

    def merge(self, other: Halstead) -> None:
        self.n += other.n

        self.u_operators += other.u_operators
        self.operators += other.operators

        self.u_operands += other.u_operands
        self.operands += other.operands

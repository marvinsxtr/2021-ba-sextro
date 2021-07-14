from math import log2, pow
from typing import Dict
import json


class Halstead:
  def __init__(self, u_operators=0., operators=0., u_operands=0., operands=0.):
    self.n: int = int(u_operators or operators or u_operands or operands)

    self.u_operators: float = u_operators
    self.operators: float = operators

    self.u_operands: float = u_operands
    self.operands: float = operands

  def try_calc(func):
    def wrap(*args, **kwargs):
        try:
          result = func(*args, **kwargs)
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
    return self.estimated_program_length() / self.length()

  @try_calc
  def vocabulary(self) -> float:
    return self.u_operators + self.u_operands

  @try_calc
  def volume(self) -> float:
    return self.length() * log2(self.vocabulary())

  @try_calc
  def difficulty(self) -> float:
    return (self.u_operators / 2.) * (self.operands / self.u_operands)

  @try_calc
  def level(self) -> float:
    return 1. / self.difficulty()

  @try_calc
  def effort(self) -> float:
    return self.difficulty() * self.volume()

  @try_calc
  def time(self) -> float:
    return self.effort() / 18.

  @try_calc
  def bugs(self) -> float:
    return pow(self.effort(), 2. / 3.) / 3000.

  @classmethod
  def from_data(cls, data: dict):
    return cls(
      u_operators=data["n1"],
      operators=data["N1"],
      u_operands=data["n2"],
      operands=data["N2"]
    )

  def __str__(self):
    return json.dumps(self.as_dict(), indent=4)

  def __repr__(self):
    return json.dumps(self.as_dict(), indent=4)

  def as_dict(self) -> Dict:
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

  def avg(self) -> Dict:
    return {k: (v / self.n if self.n else None) for k, v in self.as_dict().items()}

  def merge(self, other):
    self.n += 1

    self.u_operators += other.u_operators
    self.operators += other.operators

    self.u_operands += other.u_operands
    self.operands += other.operands

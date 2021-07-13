from math import log2, pow


class Halstead:
  def __init__(self):
    self.n: int = 1

    self.u_operators: float = 0.
    self.operators: float = 0.

    self.u_operands: float = 0.
    self.operands: float = 0.

  def length(self) -> float:
    return self.operators + self.operands

  def estimated_program_length(self) -> float:
    return self.u_operators * log2(self.u_operators) \
      + self.u_operands * log2(self.u_operands)

  def purity_ratio(self) -> float:
    return self.estimated_program_length() / self.length()

  def vocabulary(self) -> float:
    return self.u_operators + self.u_operands

  def volume(self) -> float:
    return self.length() * log2(self.vocabulary())

  def difficulty(self) -> float:
    return self.u_operators / 2. * self.operands / self.u_operands

  def level(self) -> float:
    return 1. / self.difficulty()

  def effort(self) -> float:
    return self.difficulty() * self.volume()

  def time(self) -> float:
    return self.effort() / 18.

  def bugs(self) -> float:
    return pow(self.effort(), 2. / 3.) / 3000.

  def as_dict(self) -> dict:
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

  def avg(self) -> dict:
    return {k: v / self.n for k, v in self.as_dict().items()}

  def merge(self, other):
    self.n += 1

    self.u_operators += other.u_operators
    self.operators += other.operators

    self.u_operands += other.u_operands
    self.operands += other.operands

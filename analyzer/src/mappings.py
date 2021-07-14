from typing import Dict
import json

from analyzer.src.halstead import Halstead
from analyzer.src.features import Features


class Mappings:
  def __init__(self):
    self.mappings = {k: Halstead() for k, _ in Features.as_dict().items()}

  def avg(self) -> str:
    return {k: v.avg() for k, v in self.mappings.items()}

  def get(self, feature: str) -> Halstead:
    return self.mappings[feature]

  def merge(self, feature: str, new: Halstead):
    current: Halstead = self.get(feature)
    current.merge(new)

    self.mappings[feature] = current

  def as_dict(self) -> Dict:
    return {k: v.as_dict() for k, v in self.mappings.items()}

  def __str__(self) -> str:
    return json.dumps(self.as_dict(), indent=4)

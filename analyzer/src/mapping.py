from typing import Any, Dict
import json

from analyzer.src.halstead import Halstead


class Mapping:
    def __init__(self, mapping: Dict[str, Halstead]) -> None:
        self.mapping = mapping

    def avg(self) -> Dict[str, Any]:
        return {k: v.avg() for k, v in self.mapping.items()}

    def get(self, feature: str) -> Halstead:
        return self.mapping[feature]

    def merge(self, feature: str, new: Halstead) -> None:
        current: Halstead = self.get(feature)
        current.merge(new)

        self.mapping[feature] = current

    def as_dict(self) -> Dict[str, Any]:
        return {k: v.as_dict() for k, v in self.mapping.items()}

    def __str__(self) -> str:
        return json.dumps(self.as_dict(), indent=4)

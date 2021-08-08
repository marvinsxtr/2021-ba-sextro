from analyzer.src.metrics import Metrics
from typing import Any, Dict
import json


class Mapping:
    """This class maps features to metric suites."""

    def __init__(self, mapping: Dict[str, Metrics]) -> None:
        self.mapping = mapping

    def get(self, feature: str) -> Metrics:
        """
        Returns the metrics for a feature key.

        :param feature: Feature key
        :return: The metric suite identified by the feature key
        """
        return self.mapping[feature]

    def merge(self, feature: str, new: Metrics) -> None:
        """
        Merges two metric suites for a given feature.

        :param feature: Feature key
        :param new: Metric suite to merge
        """
        current: Metrics = self.get(feature)
        current.merge(new)

        self.mapping[feature] = current

    def as_dict(self) -> Dict[str, Any]:
        """
        Returns a dict representation of the mapping.

        :return: Dict representation of the mapping
        """
        return {k: v.as_dict() for k, v in self.mapping.items()}

    def __str__(self) -> str:
        """
        Prints the mapping.

        :return: Pretty printed JSON string
        """
        return json.dumps(self.as_dict(), indent=4)

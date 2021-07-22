from typing import Any, Dict, Optional
import json

from analyzer.src.halstead import Halstead


class Mapping:
    """This class maps features to Halstead suites."""

    def __init__(self, mapping: Dict[str, Halstead]) -> None:
        self.mapping = mapping

    def avg(self) -> Dict[str, Dict[str, Optional[float]]]:
        """
        Calculate the averages of all mapped Halstead suites.

        :return: The mapping containing the average Halstead suites
        """
        return {k: v.avg() for k, v in self.mapping.items()}

    def get(self, feature: str) -> Halstead:
        """
        Returns the Halstead value for a feature key.

        :param feature: Feature key
        :return: The Halstead suite identified by the feature key
        """
        return self.mapping[feature]

    def merge(self, feature: str, new: Halstead) -> None:
        """
        Merges two Halstead suites for a given feature.

        :param feature: Feature key
        :param new: Halstead suite to merge
        """
        current: Halstead = self.get(feature)
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

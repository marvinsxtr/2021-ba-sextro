from __future__ import annotations
from typing import Any, Dict, List, Optional
import json


class Values:
    """This class contains a list of values and offers utility functions on it."""

    def __init__(self, values: List[float]) -> None:
        self._values = values

    def values(self) -> List[float]:
        """
        Returns the raw array of values.

        :return: Saved values
        """
        return self._values

    def filtered_values(self) -> List[float]:
        """
        Filters out any `None` values.

        :return: Filtered list of values
        """
        return list(filter(lambda x: x is not None, self.values()))

    def sum(self) -> float:
        """
        Returns the sum of the filtered values.

        :return: The sum of the filtered values
        """
        return sum(self.filtered_values())

    def count(self) -> float:
        """
        Returns the number of values that are not `None`.

        :return: Number of values
        """
        return len(self.filtered_values())

    def avg(self) -> Optional[float]:
        """
        Returns the average value or `None` if the list contains zero items.

        :return: The average value
        """
        if self.count():
            return self.sum() / self.count()
        else:
            return None

    def merge(self, other: Values) -> None:
        """
        Merges two values.

        :param other: The other values
        """
        self._values.extend(other.values())

    def as_dict(self) -> Dict[str, Any]:
        """
        Returns the values with their count and average value.

        :return: Dictionary containing the values, the average and the count
        """
        return {
            "values": self.filtered_values(),
            "average": self.avg(),
            "count": self.count()
        }

    def __repr__(self) -> str:
        """
        Returns a string representation.

        :return: Pretty printed JSON string
        """
        return json.dumps(self.as_dict(), indent=4)

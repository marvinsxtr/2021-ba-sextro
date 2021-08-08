from __future__ import annotations
from analyzer.src.values import Values
from typing import Any, Dict, List, Optional
import json
from enum import Enum


class Metric(Enum):
    """Enum containing the path to each value in the data dictionary."""
    NARGS = ("nargs", "sum")
    NEXITS = ("nexits", "sum")
    COGNITIVE = ("cognitive", "sum")
    CYCLOMATIC = ("cyclomatic", "sum")
    U_OPERATORS = ("halstead", "n1")
    OPERATORS = ("halstead", "N1")
    U_OPERANDS = ("halstead", "n2")
    OPERANDS = ("halstead", "N2")
    FUNCTIONS = ("nom", "functions")
    CLOSURES = ("nom", "closures")
    SLOC = ("loc", "sloc")
    PLOC = ("loc", "ploc")
    LLOC = ("loc", "lloc")
    CLOC = ("loc", "cloc")
    BLANK = ("loc", "blank")
    MI_ORIGINAL = ("mi", "mi_original")
    MI_SEI = ("mi", "mi_sei")
    MI_VISUAL_STUDIO = ("mi", "mi_visual_studio")

    @staticmethod
    def as_dict() -> Dict[str, List[str]]:
        """
        Returns a dict representation of all metrics.

        :return: Dict mapping the metrics to a list of tokens
        """
        return dict(map(lambda x: (x.name.lower(), list(x.value)), Metric))


class Metrics:
    """
    This class represents the whole metric suite and offers a range of utility methods for
    performing calculations on it.
    """

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        # Set attributes for metrics
        for name, path in Metric.as_dict().items():
            if data:
                values = Values([data[path[0]][path[1]]])
            else:
                values = Values([])
            setattr(self, name, values)

    def __str__(self) -> str:
        """
        Prints the metrics.

        :return: Pretty printed JSON string
        """
        return json.dumps(self.as_dict(), indent=4)

    def __repr__(self) -> str:
        """Returns a string representation.

        :return: Pretty printed JSON string
        """
        return json.dumps(self.as_dict(), indent=4)

    def as_dict(self) -> Dict[str, Any]:
        """
        Returns a dict representation.

        :returns: Dict containing all metrics
        """
        return {k: getattr(self, k).as_dict() for k in Metric.as_dict().keys()}

    def merge(self, other: Metrics) -> None:
        """
        Merges two metric suites.

        :param other: The other metrics
        """
        for name in Metric.as_dict().keys():
            self_metric: Values = getattr(self, name)
            other_metric: Values = getattr(other, name)

            self_metric.merge(other_metric)

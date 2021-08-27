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
    LENGTH = ("halstead", "length")
    ESTIMATED_PROGRAM_LENGTH = ("halstead", "estimated_program_length")
    PURITY_RATIO = ("halstead", "purity_ratio")
    VOCABULARY = ("halstead", "vocabulary")
    VOLUME = ("halstead", "volume")
    DIFFICULTY = ("halstead", "difficulty")
    LEVEL = ("halstead", "level")
    EFFORT = ("halstead", "effort")
    TIME = ("halstead", "time")
    BUGS = ("halstead", "bugs")
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
    def as_list() -> List[str]:
        """
        Returns a list of all metrics.

        :return: List of all metrics
        """
        return list(map(lambda x: x.name.lower(), Metric))

    @staticmethod
    def usability_metrics() -> List[str]:
        """
        Returns a list of metrics which are linked to usability.

        :return: Usability metrics
        """
        usability_metrics = [Metric.COGNITIVE, Metric.CYCLOMATIC, Metric.LENGTH, Metric.ESTIMATED_PROGRAM_LENGTH, Metric.PURITY_RATIO, Metric.VOCABULARY,
                             Metric.VOLUME, Metric.DIFFICULTY, Metric.LEVEL, Metric.EFFORT, Metric.TIME, Metric.BUGS, Metric.MI_ORIGINAL, Metric.MI_SEI, Metric.MI_VISUAL_STUDIO]
        return list(map(lambda x: x.name.lower(), usability_metrics))

    @staticmethod
    def as_dict() -> Dict[str, List[str]]:
        """
        Returns a dict representation of all metrics.

        :return: Dict mapping the metrics to a list of tokens
        """
        return dict(map(lambda x: (x.name.lower(), list(x.value)), Metric))


class Metrics:
    """This class represents the whole metric suite and offers a range of utility methods."""

    def __init__(self, data: Optional[Dict[str, Any]] = None):
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

        :return: Dict containing all metrics
        """
        return {k: getattr(self, k).as_dict() for k in Metric.as_list()}

    def merge(self, other: Metrics) -> None:
        """
        Merges two metric suites.

        :param other: The other metrics
        """
        for name in Metric.as_list():
            self_metric: Values = getattr(self, name)
            other_metric: Values = getattr(other, name)

            self_metric.merge(other_metric)

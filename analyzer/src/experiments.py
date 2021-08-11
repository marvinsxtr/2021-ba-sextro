from __future__ import annotations
from typing import Any, Dict

from analyzer.src.mapping import Mapping
from analyzer.src.features import Features
from analyzer.src.metrics import Metrics


class Experiments():
    def __init__(self, experiments: Dict[str, Mapping]) -> None:
        self.experiments = experiments

    @classmethod
    def initialized(cls) -> Experiments:
        return cls(Experiments.get_experiments())

    @staticmethod
    def get_experiments() -> Dict[str, Mapping]:
        """
        Returns the initialized values for different experiments.

        :return: The initialized experiment values.
        """
        node_experiment = Mapping({k: Metrics(None) for k in Features.as_dict().keys()})

        double_features = [val for val in Features.as_dict().keys() for _ in (0, 1)]
        space_experiment = Mapping({k if i % 2 else "no_" + k: Metrics(None)
                                    for i, k in enumerate(double_features)})

        return {
            "nodes": node_experiment,
            "spaces": space_experiment
        }

    def get(self, name: str) -> Mapping:
        """
        Returns an experiment with a specific name.

        :return: The requested Mapping
        """
        return self.experiments[name]

    def merge(self, other: Experiments) -> None:
        """
        Merges two experiments.

        :param other: The other experiment
        """
        for experiment, mapping in self.experiments.items():
            mapping.merge(other.experiments[experiment])

    def as_dict(self) -> Dict[str, Any]:
        """
        Returns a dict representation of the mapping.

        :return: Dict representation of the mapping
        """
        return {k: v.as_dict() for k, v in self.experiments.items()}

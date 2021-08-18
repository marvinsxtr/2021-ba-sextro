from __future__ import annotations
from typing import Any, Dict, List, Optional
from enum import Enum

from analyzer.src.mapping import Mapping
from analyzer.src.features import Features
from analyzer.src.metrics import Metrics


class Experiment(str, Enum):
    NODES = "nodes"
    SPACES = "spaces"
    FILES = "files"

    def __str__(self) -> str:
        """
        Returns the experiment key as a string.

        :return: Experiment key
        """
        return self.value

    @staticmethod
    def as_dict() -> Dict[str, List[str]]:
        """
        Returns a dict representation of all Experiments.

        :return: Dict mapping the experiments to their keys
        """
        return dict(map(lambda x: (x.name.lower(), list(x.value)), Experiment))


class Experiments():
    def __init__(self, experiments: Dict[str, Mapping]) -> None:
        self.experiments = experiments

    @classmethod
    def initialized(cls, experiment_names: List[str]) -> Experiments:
        """
        Returns the initialized experiments.

        :param experiment_names: The list of experiments to conduct
        :return: The initialized experiments 
        """
        return cls(Experiments.get_experiments(experiment_names))

    @staticmethod
    def get_experiments(experiment_names: List[str]) -> Dict[str, Mapping]:
        """
        Returns the initialized values for different experiments.

        :return: The initialized experiment values.
        """
        experiments = dict()

        if Experiment.NODES in experiment_names:
            experiments[str(Experiment.NODES)] = Mapping(
                {k: Metrics(None) for k in Features.as_dict().keys()})

        if Experiment.SPACES in experiment_names:
            double_features = [val for val in Features.as_dict().keys() for _ in (0, 1)]
            experiments[str(Experiment.SPACES)] = Mapping({k if i % 2 else "no_" + k: Metrics(None)
                                                           for i, k in enumerate(double_features)})

        if Experiment.FILES in experiment_names:
            experiments[str(Experiment.FILES)] = Mapping(
                {k: Metrics(None) for k in Features.as_dict().keys()})

        return experiments

    def get(self, name: str) -> Optional[Mapping]:
        """
        Returns an experiment with a specific name.

        :return: The requested Mapping
        """
        return self.experiments.get(name)

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

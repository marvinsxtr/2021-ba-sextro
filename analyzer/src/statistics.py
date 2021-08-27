from typing import Any, Dict, List, Optional
from enum import Enum

from analyzer.src.experiments import Experiment
from analyzer.src.values import Values
from analyzer.src.metrics import Metric
from analyzer.src.features import Features
from analyzer.src.utils import get_analyzer_res_path, load_json_file, save_json_file

import scipy.stats as st


class Tests(str, Enum):
    MANN_WHITNEY_U = "mann_whitney_u"

    def __str__(self) -> str:
        """
        Returns the test name as a string.

        :return: Test name
        """
        return self.value

    @staticmethod
    def as_list() -> List[str]:
        """
        Returns a lsit of all statistic tests.

        :return: List of statistic tests
        """
        return list(map(lambda x: x.value, Tests))

    @staticmethod
    def proportion(u: float, m: float, n: float) -> Optional[float]:
        """
        Specific to the Mann-Whitney U test.
        Proportion of cases in which a value from one sample exceeds a value from the other, 
        which takes values between 0 and 1. The null case corresponds to an expected proportion of 1/2.

        :param u: The statistic of the Mann-Whitney U test
        :param m: First sample size
        :param n: Second sample size
        :return: The proportion
        """
        product = m * n

        if not product:
            return None
        else:
            return u / product


class Statistics:
    """This class handles statistic significance tests."""

    @staticmethod
    def analyze_results() -> None:
        """Runs statistic tests on the result data."""
        result = load_json_file(get_analyzer_res_path(), name="results_with_raw_values.json")

        if not result:
            return

        statistics = dict()

        spaces = result.get(Experiment.SPACES)
        if spaces:
            spaces_statistics: Dict[str, Any] = dict()

            for feature in Features.as_list():
                spaces_statistics[feature] = dict()

                for metric in Metric.as_list():
                    spaces_statistics[feature][metric] = dict()

                    values_used = Values(spaces[feature][metric]["values"]).filtered_values()
                    values_not_used = Values(spaces["no_" + feature]
                                             [metric]["values"]).filtered_values()

                    min_len = min([len(values_used), len(values_not_used)])

                    if min_len == 0:
                        continue

                    test_result = st.mannwhitneyu(
                        values_used, values_not_used, use_continuity=False)

                    spaces_statistics[feature][metric][str(Tests.MANN_WHITNEY_U)] = {
                        "statistic": test_result[0],
                        "p_value": test_result[1],
                        "proportion": Tests.proportion(test_result[0], len(values_used), len(values_not_used))
                    }

            statistics[str(Experiment.SPACES)] = spaces_statistics
        save_json_file(statistics, get_analyzer_res_path(), name="statistic_tests.json")

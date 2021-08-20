from typing import Any, Dict, List
import random
from enum import Enum

from analyzer.src.experiments import Experiment
from analyzer.src.values import Values
from analyzer.src.metrics import Metric
from analyzer.src.features import Features
from analyzer.src.utils import get_res_path, load_json_file, save_json_file

import scipy.stats as st


class Tests(str, Enum):
    MANN_WHITNEY_U = "mann_whitney_u"
    WILCOXON_RANK_SUM = "wilcoxon_rank_sum"
    WILCOXON_SIGNED_RANK = "wilcoxon_signed_rank"

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


class Statistics:
    """This class handles statistic significance tests."""

    @staticmethod
    def analyze_results() -> None:
        """Runs statistic tests on the result data."""
        result = load_json_file(get_res_path(tool="analyzer"), name="res_with_raw_values.json")

        if not result:
            return

        statistics = dict()

        spaces = result.get(Experiment.SPACES)
        if spaces:
            spaces_statistics: Dict[str, Any] = dict()

            for feature in Features.as_dict().keys():
                spaces_statistics[feature] = dict()

                for metric in Metric.as_dict().keys():
                    spaces_statistics[feature][metric] = dict()

                    values_used = Values(spaces[feature][metric]["values"]).filtered_values()
                    values_not_used = Values(spaces["no_" + feature]
                                             [metric]["values"]).filtered_values()

                    min_len = min([len(values_used), len(values_not_used)])

                    if min_len == 0:
                        continue

                    sample_used = random.sample(values_used, min_len)
                    sample_not_used = random.sample(values_not_used, min_len)

                    statistic_tests = [
                        (str(Tests.MANN_WHITNEY_U) + "_same_sample_size",
                         st.mannwhitneyu(sample_used, sample_not_used)),
                        (str(Tests.WILCOXON_RANK_SUM) + "_same_sample_size",
                         st.ranksums(sample_used, sample_not_used)),
                        (str(Tests.WILCOXON_SIGNED_RANK) + "_same_sample_size",
                         st.wilcoxon(sample_used, sample_not_used, zero_method="zsplit")),
                        (str(Tests.MANN_WHITNEY_U) + "_different_sample_size",
                         st.mannwhitneyu(values_used, values_not_used)),
                        (str(Tests.WILCOXON_RANK_SUM) + "_different_sample_size",
                         st.ranksums(values_used, values_not_used))
                    ]

                    for test_name, test_result in statistic_tests:
                        spaces_statistics[feature][metric][test_name] = {
                            "statistic": test_result[0],
                            "p_value": test_result[1]
                        }

            statistics[str(Experiment.SPACES)] = spaces_statistics
        save_json_file(statistics, get_res_path(tool="analyzer"), name="tst.json")

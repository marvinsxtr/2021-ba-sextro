from typing import Any, Dict

from analyzer.src.values import Values
from analyzer.src.metrics import Metric
from analyzer.src.features import Features
from analyzer.src.utils import get_res_path, save_json_file

import scipy.stats as st


class Statistics:
    """This class handles statistic significance tests."""

    @staticmethod
    def analyze(result: Dict[str, Any]) -> None:
        """Runs statistic tests on the result data."""
        spaces = result["spaces"]
        statistics: Dict[str, Any] = dict()

        for feature in Features.as_dict().keys():
            statistics[feature] = dict()

            for metric in Metric.as_dict().keys():
                statistics[feature][metric] = dict()

                sample_used = Values(spaces[feature][metric]["values"]).filtered_values()
                sample_not_used = Values(spaces["no_" + feature]
                                         [metric]["values"]).filtered_values()

                if len(sample_used) == 0 or len(sample_not_used) == 0:
                    continue

                res = st.mannwhitneyu(sample_used, sample_not_used)
                statistics[feature][metric]["mannwhitneyu"] = {
                    "statistic": res[0],
                    "pvalue": res[1]
                }

        save_json_file(statistics, get_res_path(tool="analyzer"), name="tst.json")

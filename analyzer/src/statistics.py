from typing import Any, Dict
import random

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

                values_used = Values(spaces[feature][metric]["values"]).filtered_values()
                values_not_used = Values(spaces["no_" + feature]
                                         [metric]["values"]).filtered_values()

                min_len = min([len(values_used), len(values_not_used)])

                if min_len == 0:
                    continue

                sample_used = random.sample(values_used, min_len)
                sample_not_used = random.sample(values_not_used, min_len)

                res = st.mannwhitneyu(sample_used, sample_not_used)
                statistics[feature][metric]["mannwhitneyu"] = {
                    "statistic": res[0],
                    "pvalue": res[1]
                }

        save_json_file(statistics, get_res_path(tool="analyzer"), name="tst.json")

from analyzer.src.experiments import Experiment
from typing import Any, Dict
import random

from analyzer.src.values import Values
from analyzer.src.metrics import Metric
from analyzer.src.features import Features
from analyzer.src.utils import get_res_path, load_json_file, save_json_file

import scipy.stats as st


class Statistics:
    """This class handles statistic significance tests."""

    @staticmethod
    def analyze_results() -> None:
        """Runs statistic tests on the result data."""
        result = load_json_file(get_res_path(tool="analyzer"), name="res.json")

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

                    res = st.mannwhitneyu(sample_used, sample_not_used)
                    spaces_statistics[feature][metric]["mannwhitneyu"] = {
                        "statistic": res[0],
                        "pvalue": res[1]
                    }
            statistics[str(Experiment.SPACES)] = spaces_statistics
        save_json_file(statistics, get_res_path(tool="analyzer"), name="tst.json")

from typing import Any, Dict
import random

from analyzer.src.metrics import Metric
from analyzer.src.features import Features

import scipy.stats as st


class Statistics:
    """This class handles statistic significance tests."""

    @staticmethod
    def analyze(result: Dict[str, Any]) -> None:
        """Runs statistic tests on the result data."""
        spaces = result["spaces"]

        for feature in Features.as_dict().keys():
            for metric in Metric.as_dict().keys():
                values_feature_used = spaces[feature][metric]["values"]
                values_feature_not_used = spaces["no_" + feature][metric]["values"]

                min_len = min([len(values_feature_used), len(values_feature_not_used)])

                sample_used = random.sample(values_feature_used, min_len)
                sample_not_used = random.sample(values_feature_not_used, min_len)

                print(feature, metric, st.wilcoxon(sample_used, sample_not_used, zero_method="zsplit"))

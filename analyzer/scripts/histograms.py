import pandas as pd
import matplotlib.pyplot as plt

import os
import json
from os.path import join

from analyzer.src.utils import get_analyzer_res_path
from analyzer.src.metrics import Metric
from analyzer.src.features import Features


def generate_histograms() -> None:
    """Generate histograms from the raw values."""
    features = Features.as_list()
    metrics = Metric.as_list()

    with open(join(get_analyzer_res_path(), "results_with_raw_values.json"), "r", encoding="utf-8") as res:
        data = json.load(res)

    spaces = data["spaces"]

    for feature in features:
        metrics_feature = spaces[feature]
        metrics_no_feature = spaces["no_" + feature]

        for metric in metrics:
            no_series = pd.Series(metrics_no_feature[metric]["values"])
            filtered_no_series = no_series[no_series.between(
                no_series.quantile(.05), no_series.quantile(.95))]

            df_no = pd.DataFrame({
                "no_" + feature: filtered_no_series,
            })

            series = pd.Series(metrics_feature[metric]["values"])
            filtered_series = series[series.between(
                series.quantile(.05), series.quantile(.95))]

            df = pd.DataFrame({
                feature: filtered_series
            })

            path = join(get_analyzer_res_path(), "histograms", feature, metric)

            os.makedirs(path, exist_ok=True)

            df.hist(bins=100)
            plt.savefig(f'{path}/{feature}_{metric}.png')

            df_no.hist(bins=100)
            plt.savefig(f'{path}/no_{feature}_{metric}.png')


generate_histograms()

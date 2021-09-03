import os
from os.path import join
from typing import Any, Dict, List

from analyzer.src.metrics import Metric
from analyzer.src.features import Features
from analyzer.src.utils import get_analyzer_res_path, load_json_file, to_camel_case

import pandas as pd
from matplotlib.cbook import boxplot_stats


def generate_boxplots() -> None:
    """Generates boxplots from the raw result data."""
    metrics = Metric.usability_metrics()
    features = Features.as_list()

    results = load_json_file(get_analyzer_res_path(), "results_with_raw_values.json")
    if results is None:
        print("Make sure to run the analyzer first.")
        return

    spaces = results["spaces"]

    path = join(get_analyzer_res_path(), "boxplots")
    os.makedirs(path, exist_ok=True)

    with open(join(path, f"boxplots.txt"), "w+", encoding="utf-8") as boxplots:
        for metric in metrics:
            series_data: List[List[float]] = list()

            for feature in features:
                metrics_feature = spaces[feature]
                metrics_no_feature = spaces["no_" + feature]

                no_series = pd.Series(metrics_no_feature[metric]["values"])
                series = pd.Series(metrics_feature[metric]["values"])

                series_data.extend([no_series, series])

            boxplot_data: List[Dict[str, Any]] = [
                boxplot_stats(series)[0] for series in series_data]

            escaped_metric = metric.replace("_", "\_")

            plots = ["""\\addplot+ [
boxplot prepared={{
lower whisker={0}, lower quartile={1},
median={2},
upper quartile={3}, upper whisker={4},
}},
] coordinates {{}};
""".format(
                boxplot["whislo"],
                boxplot["q1"],
                boxplot["med"],
                boxplot["q3"],
                boxplot["whishi"]
            ) for boxplot in boxplot_data]

            boxplots.write("""\\begin{{figure}}
\\begin{{tikzpicture}}
\\begin{{axis}}[
boxplot/draw direction=y,
width=\\textwidth, height=8cm, enlarge x limits=0.05,
x axis line style={{opacity=0}},
axis x line*=bottom,
axis y line=left,
cycle list={{{{dashed}},{{black}}}},
enlarge y limits,
ylabel={{{0}}},
xtick={{{1}}},
xticklabels={{{2}}},
x tick label style={{
    text height=1.0cm,
    align=center,
    anchor=center
}},
x=2cm,
x tick label as interval,
boxplot={{
    draw position={{1/3 + Floor(\plotnumofactualtype/2) + 1/3*mod(\plotnumofactualtype,2)}},
    box extend=0.3,
}},
]
{3}
\\end{{axis}}
\\end{{tikzpicture}}
\\caption[Comparison of the "{0}" metric depending on the use of each feature]{{Comparison between the distributions of the "{0}" metric in code spaces with and without usage of each Rust feature.}}
\\label{{fig:comparison_boxplots_{4}}}
\\end{{figure}}
""".format(
                escaped_metric,
                ",".join(map(str, list(range(len(features) + 1)))),
                ",".join([f"{{{val}\\\\\\tiny{{not used/used}}}}" for val in list(
                    map(lambda x: to_camel_case("bounds" if x == "trait_bounds" else x), features))]),
                "".join(plots),
                metric
            ))


generate_boxplots()

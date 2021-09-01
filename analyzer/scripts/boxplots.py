import os
from os.path import join

from analyzer.src.metrics import Metric
from analyzer.src.features import Features
from analyzer.src.utils import get_analyzer_res_path, load_json_file

import pandas as pd


def generate_boxplots() -> None:
    """Generates boxplots from the raw result data."""
    metrics = Metric.as_list()
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
            data = list()

            for feature in features:
                metrics_feature = spaces[feature]
                metrics_no_feature = spaces["no_" + feature]

                no_series = pd.Series(metrics_no_feature[metric]["values"])
                series = pd.Series(metrics_feature[metric]["values"])

                data.extend([no_series, series])

            plots = ["""\\addplot+ [
boxplot prepared={{
lower whisker={0}, lower quartile={1},
median={2},
upper quartile={3}, upper whisker={4},
}},
] coordinates {{}};
""".format(
                series.quantile(.025),
                series.quantile(.25),
                series.quantile(.5),
                series.quantile(.75),
                series.quantile(.975)
            ) for series in data]

            boxplots.write("""\\begin{{tikzpicture}}
\\begin{{axis}}[
boxplot/draw direction=y,
width=14cm, height=8cm, enlarge x limits=0.05,
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
\\\\
""".format(
                metric.replace("_", "\_"),
                ",".join(map(str, list(range(len(features) + 1)))),
                ",".join([f"{{{val}\\\\\\tiny{{not used/used}}}}" for val in list(
                    map(lambda x: "bounds" if x == "trait_bounds" else x, features))]),
                "".join(plots))
            )


generate_boxplots()

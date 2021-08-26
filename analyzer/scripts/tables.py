from typing import Any, Dict
from os.path import join
import os

from analyzer.src.statistics import Tests
from analyzer.src.experiments import Experiment
from analyzer.src.utils import get_analyzer_res_path, load_json_file
from analyzer.src.features import Features
from analyzer.src.metrics import Metric


def generate_tables() -> None:
    """Generates LaTeX tables from the results."""
    statistics = load_json_file(get_analyzer_res_path(), name="corrected_statistic_tests.json")
    if not statistics:
        return

    for experiment in Experiment.as_dict().keys():
        if not statistics.get(experiment):
            continue

        for test in Tests.as_list():
            generate_table(statistics, experiment, test,)


def generate_table(statistics: Dict[str, Any], experiment: str, test: str) -> None:
    """
    Generate a table file for one feature.

    :param statistics: The content of the staticstics file
    :param experiment: Experiment name
    :param test: Name of the statistic test
    """
    path = join(get_analyzer_res_path(), "tables")
    os.makedirs(path, exist_ok=True)

    with open(join(path, f"tables_{experiment}_{test}.txt"), "w+", encoding="utf-8") as tables:
        for feature in Features.as_dict().keys():
            rows = list()
            for metric in Metric.as_dict().keys():
                test_results = statistics[experiment][feature][metric].get(test)
                if not test_results:
                    continue

                proportion = round(test_results["proportion"], 3)

                p_value = test_results["corrected_p_value"]
                rejected = "Rejected" if p_value < 0.05 else "Not rejected"

                significance = "-"
                if p_value < 0.1:
                    significance = "."
                if p_value < 0.05:
                    significance = "*"
                if p_value < 0.01:
                    significance = "**"
                if p_value < 0.001:
                    significance = "***"

                metric = "estimated_length" if metric == "estimated_program_length" else metric
                metric = metric.replace("_", "\_")

                if p_value < 0.0001:
                    p_value = "{:0.3e}".format(p_value)
                    number, exponent = p_value.split("e")
                    p_value = f"{number}*10^{{{exponent}}}"
                else:
                    p_value = round(p_value, 3)

                rows.append(
                    f"{metric} & ${p_value}$ & ${proportion}$ & {rejected} & ${significance}$ \\\\")

            feature = feature.replace("_", "\_")
            tables.write("""
\\begin{{table}}
\\begin{{center}}
\\caption*{{{0}}}
\\begin{{tabular}}{{ l c c c c }}
\\toprule
\\textbf{{Metric}} & \\textbf{{p-value}} & \\textbf{{Proportion}} & \\textbf{{Decision}} & \\textbf{{Significance}} \\\\ 
\\midrule
{1}
\\bottomrule
\\end{{tabular}}
\\caption[Significance and p-values for the feature "{2}" in code spaces]{{$H0$: No significant difference in each metric between code spaces with feature usage and without. Significance and p-value for the feature "{3}" obtained by applying the Mann-Whitney U test with Bonferroni correction.  (Significance codes: 0 "***" 0.001 "**" 0.01 "*" 0.05 "." 0.1 "–" 1)}}
\\label{{tab:{4}_{5}}}
\\end{{center}}
\\end{{table}}
                """.format(feature, "\n".join(rows), feature, feature, feature, metric.replace("\\", "")))


generate_tables()

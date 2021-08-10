from analyzer.src.utils import get_res_path, load_json_file
from analyzer.src.features import Features
from analyzer.src.metrics import Metric


def generate_latex_tables() -> None:
    """Generates LaTex tables from the results."""
    statistics = load_json_file(get_res_path(tool="analyzer"), name="tst.json")
    table_number = 1

    if not statistics:
        return

    with open("./data/analyzer/res/tab.txt", "w+", encoding="utf-8") as tables:

        for feature in Features.as_dict().keys():
            rows = list()

            for metric in Metric.as_dict().keys():
                test_results = statistics[feature][metric].get("mannwhitneyu")
                if not test_results:
                    continue

                pvalue = test_results["pvalue"]
                rejected = "Rejected" if pvalue < 0.05 else "Not rejected"

                significance = "-"
                if pvalue < 0.1:
                    significance = "."
                if pvalue < 0.05:
                    significance = "*"
                if pvalue < 0.01:
                    significance = "**"
                if pvalue < 0.001:
                    significance = "***"

                metric = metric.replace("_", "\_")

                if pvalue < 0.0001:
                    pvalue = "{:0.5e}".format(pvalue)
                else:
                    pvalue = round(pvalue, 5)

                rows.append(
                    f"$H0_{{\\textrm{{{feature}, {metric}}}}}$ & ${pvalue}$ & {rejected} & ${significance}$ \\\\")

            tables.write("""
\\begin{{table}}
\\begin{{center}}
\\begin{{tabular}}{{ l l l l l }}
\\toprule
\\textbf{{Name}} & \\textbf{{p-value}} & \\textbf{{Decision}} & \\textbf{{Significance}} \\\\ 
\\midrule
{0}
\\end{{tabular}}
\\caption[Significance and p-values for the feature "{1}" in code spaces]{{$H0$: No significant difference in each metric between code spaces with feature usage and without. Significance and p-value for the feature "{2}" obtained by applying a Mann-Whitney U test.  (Significance codes: 0 "***" 0.001 "**" 0.01 "*" 0.05 "." 0.1 "–" 1)}}
\\label{{table{3}}}
\\end{{center}}
\\end{{table}}
            """.format("\n".join(rows), feature, feature, table_number))

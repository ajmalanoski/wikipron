#!/usr/bin/env python
"""Error analysis tool for G2P.

Two input files are required:

1.  Covering grammar: a two-column TSV file in which the left column contains
    zero or more graphemes, and the right contains zero or more phones it can
    correspond to.
2.  Test output: a three-column TSV file in which the columns are the graphemic
    form, the gold pronunciation, and the hypothesized pronunciation.

Example:

espresso    ɛ s p ɹ ɛ s ə ʊ ɛ k s p ɹ ɛ s ə ʊ
"""

__author__ = "Arundhati Sengupta"


import argparse

import prettytable
import pynini
from pynini.lib import rewrite


def main(args: argparse.Namespace) -> None:
    with pynini.default_token_type("utf8"):
        cg_fst = pynini.string_file(args.cg_path).closure().optimize()
        rulematch_predmatch = 0
        rulematch_pred_notmatch = 0
        not_rulematch_predmatch = 0
        not_rulematch_pred_notmatch = 0
        total_records = 0
        with open(args.test_path, "r") as source:
            for line in source:
                total_records += 1
                ortho, gold_p, hypo_p = line.rstrip().split("\t", 2)
                hypo_p = hypo_p.replace(" ", "")
                gold_p = gold_p.replace(" ", "")
                # print(ortho, gold_p, hypo_p)
                try:
                    if rewrite.matches(ortho, hypo_p, cg_fst):
                        if gold_p == hypo_p:
                            rulematch_predmatch += 1
                        else:
                            # print("Line ", total_records)
                            # print("The prediction is wrong")
                            # print("Word is", ortho)
                            # print("Pronunciation is", gold_p)
                            # print("Predicted:", hypo_p)
                            # print("=====")
                            # print()
                            rulematch_pred_notmatch += 1
                    elif gold_p == hypo_p:
                        not_rulematch_predmatch += 1
                        print("Line ", total_records)
                        print("The CG messed up")
                        print("Word is", ortho)
                        print("Pronunciation is", gold_p)
                        print("Possible rewrites include:")
                        print(rewrite.rewrites(ortho, cg_fst, input_token_type="utf8", output_token_type="utf8"))
                        print("=====")
                        print()
                    else:
                        not_rulematch_pred_notmatch += 1
                except pynini.lib.rewrite.Error as e:
                    print("Line ", total_records)
                    print(e)
                    print("Word is", ortho)
                    print("Predicted pronunciation is", hypo_p)
                    print("Actual pronunciation is", gold_p)
                    print()
                    print("=====")
                    print()
                    continue
        # Collects percentages.
        rule_m_pred_nm = 100 * rulematch_pred_notmatch / total_records
        rule_m_pred_m = 100 * rulematch_predmatch / total_records
        rule_nm_pred_m = 100 * not_rulematch_predmatch / total_records
        rule_nm_pred_nm = 100 * not_rulematch_pred_notmatch / total_records
        # Builds and prints the table.
        print_table = prettytable.PrettyTable()
        print_table.field_names = ["", "CG match", "CG non-match"]
        print_table.add_row(
            ["Pron match", f"{rule_m_pred_m:.2f}", f"{rule_nm_pred_m:.2f}"]
        )
        print_table.add_row(
            [
                "Pron non-match",
                f"{rule_m_pred_nm:.2f}",
                f"{rule_nm_pred_nm:.2f}",
            ]
        )
        print(print_table)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cg_path", required=True, help="path to TSV covering grammar file"
    )
    parser.add_argument(
        "--test_path", required=True, help="path to test TSV file"
    )
    main(parser.parse_args())
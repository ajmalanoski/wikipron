#!/usr/bin/env python
"""Error analysis tool for G2P.

Two input files are required:

1.  Covering grammar: a two-column TSV file in which the left column contains
    zero or more graphemes, and the right contains zero or more phones it can
    correspond to.
2.  Test output: a three-column TSV file in which the columns are the graphemic
    form, the hypothesized pronunciation, and the gold pronunciation.

Example:

espresso	ɛ s p ɹ ɛ s ə ʊ	ɛ k s p ɹ ɛ s ə ʊ
"""

__author__ = "Arundhati Sengupta"


import argparse

import prettytable  # type: ignore
import pynini
from pynini.lib import rewrite


def main(args: argparse.Namespace) -> None:
    cg_fst = pynini.string_file(args.cg_path, input_token_type = 'utf8', output_token_type = 'utf8' ).closure().optimize()
    rulematch_predmatch = 0
    rulematch_pred_notmatch = 0
    not_rulematch_predmatch = 0
    not_rulematch_pred_notmatch = 0
    total_records = 0
    with open(args.test_path, "r") as source:
        for line in source:
            
            (ortho_str, hypo_p_str, gold_p_str) = line.rstrip().split("\t", 2)
            ortho = pynini.accep(ortho_str, token_type="utf8")

           # There are spaces in the pronunciations which we don't need for this.
            hypo_p_str = hypo_p_str.replace(" ", "")
            hypo_p = pynini.accep(hypo_p_str, token_type="utf8")
            gold_p_str = gold_p_str.replace(" ", "")
            gold_p = pynini.accep(gold_p_str, token_type="utf8")
            try:
                total_records += 1
                if rewrite.matches(ortho, hypo_p, cg_fst):       
                   if gold_p == hypo_p:
                    rulematch_predmatch += 1
                   else:
                    rulematch_pred_notmatch += 1 
                else:
                    if gold_p == hypo_p:
                        not_rulematch_predmatch += 1
                        print("Line ", total_records)
                        print("The CG messed up")
                        print("Word is", ortho_str)
                        print("Pronunciation is", gold_p_str)
                        print("Possible rewrites include:")
                        print(rewrite.rewrites(ortho, cg_fst, input_token_type="utf8", output_token_type="utf8"))
                        print("=====")
                        print()
                    else:
                        not_rulematch_pred_notmatch += 1
            except pynini.lib.rewrite.Error as e:
                # print("Something's not right...")
                print(e)
                print("Word is", ortho_str)
                print("Predicted pronunciation is", hypo_p_str)
                print("Actual pronunciation is", gold_p_str)
                print("Line ", total_records)
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
    print_table.field_names = ["", "CG match", "CG not-match"]
    print_table.add_row(
        ["Pron match", f"{rule_m_pred_m:.2f}", f"{rule_nm_pred_m:.2f}"]
    )
    print_table.add_row(
        ["Pron not-match", f"{rule_m_pred_nm:.2f}", f"{rule_nm_pred_nm:.2f}"]
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

#!/usr/bin/env python
"""Makes test file.

Takes the gold data and the model output, and creates a three-column TSV where
each line has a word, its gold pronunciation, and the predicted pronunciation.
Assumes that the input files have the same words in the same order.
"""

import argparse
import logging


def main(args: argparse.Namespace) -> None:
    with open(args.gold, "r") as gf, open(args.pred, "r") as pf:
        with open(args.out, "w") as wf:
            for lineno, (g_line, p_line) in enumerate(zip(gf, pf), 1):
                g_word, g_pron = g_line.split("\t")
                p_word, p_pron = p_line.split("\t")
                # Make sure that gold data and predictions have the
                # same words.
                if not g_word == p_word:
                    logging.warning(
                        "%s != %s (line %d)", g_word, p_word, lineno
                    )
                    continue
                # Note that we use `strip` to remove the newline.
                g_pron = g_pron.strip()
                p_pron = p_pron.strip()
                line = f"{g_word}\t{g_pron}\t{p_pron}"
                print(line, file=wf)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "gold", help="TSV with words and correct pronunciations"
    )
    parser.add_argument(
        "pred", help="TSV with words and predicted pronunciations"
    )
    parser.add_argument("out", help="file to write to")
    main(parser.parse_args())

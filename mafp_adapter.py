"""Adapter: MAFP --format json output -> the-sword mafp-pairs input file.

MAFP (mergers-and-acquisitions-for-peace/analyze.py) already emits the
exact document shape that the-sword (defense.py
import_acquisition_pairs and sword_cli.py defense import-pairs)
consumes. Verified 2026-11-20 against the shipped sample
the-sword/demo/mafp-pairs.json: identical top level keys and identical
per pair keys. This adapter is therefore a validating normalizer, not
a reshaper. It:

1. Validates the required top level and per pair fields, and fails
   loudly on any drift instead of letting the importer skip silently.
2. Attaches the screening caveat as a top level field so the limit
   travels with the file: portfolios are capped at --limit patents
   per company (default 10). This is a screening sample, not a full
   portfolio audit. Scores are screening scores, not valuations.
3. Passes every pair through unchanged.

Usage: python3 mafp_to_sword.py mafp-output.json mafp-pairs.json
"""
import json
import sys

CAVEAT = ("Screening sample only: patent portfolios are capped per run "
          "(--limit, default 10 recent patents per company). Scores are "
          "screening scores from 0 to 100, not valuations and not "
          "advice. Candidates imported from this file are screening "
          "input, not fielded inventory.")

TOP_REQUIRED = {"tool", "version", "sector", "pairs_scored",
                "score_note", "pairs"}
PAIR_REQUIRED = {"acquirer", "target", "screening_score",
                 "gap_concepts_top"}


def convert(src_path, dst_path):
    with open(src_path) as f:
        doc = json.load(f)
    missing = TOP_REQUIRED - set(doc)
    if missing:
        raise SystemExit("MAFP document missing top level fields: %s"
                         % sorted(missing))
    if doc["tool"] != "Mergers and Acquisitions For Peace":
        raise SystemExit("unexpected tool field: %r" % doc["tool"])
    for i, pair in enumerate(doc["pairs"]):
        pmissing = PAIR_REQUIRED - set(pair)
        if pmissing:
            raise SystemExit("pair %d missing fields: %s"
                             % (i, sorted(pmissing)))
    out = dict(doc)
    out["screening_caveat"] = CAVEAT
    out["pairs_scored"] = len(out["pairs"])
    with open(dst_path, "w") as f:
        json.dump(out, f, indent=1)
    return out


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    result = convert(sys.argv[1], sys.argv[2])
    print("wrote %s: %d pairs, caveat attached"
          % (sys.argv[2], len(result["pairs"])))

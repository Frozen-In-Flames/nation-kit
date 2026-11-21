# nation-kit

The umbrella for the Nation Kit: a thin, process level runner that
executes the six core command line interfaces against one shared
data directory, in build order, with the-ledger as the settlement
layer and the only cash book.

The six cores are the-ledger (treasury), the-registry (records),
the-shield (safety), the-sword (security), the-commons
(infrastructure), and the-safety-net (welfare). Each core remains a
separate repository with its own tests and its own stated limits.
This repository adds no shared library and changes no core code. It
invokes each core CLI as a subprocess with an absolute `--data-dir`
path under one data root, one subdirectory per core, and owns only
the cross core rules: run order, settlement, and the Mergers and
Acquisitions For Peace feed into the-sword.

## Run

```bash
python3 nation_kit_runner.py CORES_DIR DATA_ROOT
```

CORES_DIR holds checkouts of the six cores. The demo scenario seeds
ledger revenue of 100,000 NCU, records one registry filing, one
shield product, the MAFP candidate import into the-sword, one
commons post point, and one safety net enrollment of 500 NCU, then
books the matching settlement expense in the-ledger in the same run.
The closing oracle, reproduced by the test suite, is revenue
$100,000.00 NCU, expenditure $500.00 NCU, cash $99,500.00 NCU.

The MAFP feed is prepared by `mafp_adapter.py`, a validating
normalizer over Mergers and Acquisitions For Peace JSON output. It
checks the required fields, fails loudly on drift, and attaches the
screening caveat to the file itself.

## Decisions applied

The Priority 3 design note left four questions open. Two were
resolved by the mandate of November 21, 2026 and are recorded here
for later reversal. Settlement is booked at enrollment time, in the
same run that creates the obligation, keeping the umbrella write
only and never reading core files. The runner lives in its own thin
repository, this one, rather than inside the-ledger. The remaining
questions, demo dataset content beyond the prototype records and
any deeper integration, remain open by design.

## Honest limits

This runner is a local demonstration harness over local files. It
is not a server, not a deployment, and not an operating government.
The cores record and track; they do not operate the functions they
record, and this umbrella inherits that limit unchanged. The MAFP
import carries a screening caveat: patent portfolios are capped per
run (default 10 recent patents per company), so imported records
are screening candidates, not capability audits and not fielded
inventory. The end to end test reproduces the prototype closing
figure against real core checkouts; it is skipped, never faked,
when the six checkouts are not present.

## License

Apache-2.0.

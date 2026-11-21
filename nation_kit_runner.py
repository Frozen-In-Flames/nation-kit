"""Nation Kit umbrella runner.

Design premise, verified against the six repos: every core CLI takes
the same global flag, --data-dir DIR (default data/), and every core
stores plainly named JSON files inside that directory. No core imports
another core. The umbrella is therefore a process level runner, not a
shared library: it points each CLI at one shared data root, with one
subdirectory per core so file ownership stays obvious.

Settlement rule demonstrated here: when a core creates an obligation
(the safety net enrolling a beneficiary), the umbrella records the
matching money movement in the-ledger (treasury expense) in the same
run, so the-ledger stays the single cash book. Cores never write to
each other's files.

Usage: python3 nation_kit_runner.py CORES_DIR DATA_ROOT
  CORES_DIR holds the six checkouts (the-ledger, the-registry,
  the-shield, the-sword, the-commons, the-safety-net).

Placement and timing decisions, applied under the November 21, 2026
mandate from the Priority 3 design note (UMBRELLA.md section 7), and
recorded here for later reversal: the runner lives in its own thin
repo (this repo), and settlement is booked at enrollment time in the
same run, keeping the umbrella write only and never reading core
files. The alternative, booking at the safety net payment run, is
documented in the design note.
"""
import os
import subprocess
import sys

CORES = [
    ("the-ledger", "ledger_cli.py"),
    ("the-registry", "registry_cli.py"),
    ("the-shield", "shield_cli.py"),
    ("the-sword", "sword_cli.py"),
    ("the-commons", "commons_cli.py"),
    ("the-safety-net", "safety_net_cli.py"),
]


def run(cores_dir, data_root, core, cli, args):
    core_dir = os.path.join(cores_dir, core)
    data_dir = os.path.join(data_root, core)
    os.makedirs(data_dir, exist_ok=True)
    cmd = [sys.executable, cli, "--data-dir", data_dir] + args
    proc = subprocess.run(cmd, cwd=core_dir, capture_output=True,
                          text=True)
    status = "ok" if proc.returncode == 0 else "FAIL"
    print("[%s] %s %s" % (status, core, " ".join(args)))
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
        raise SystemExit(1)
    return proc.stdout.strip()


def main():
    # Absolute paths are required: each CLI resolves --data-dir
    # relative to its own working directory, and the runner sets the
    # working directory to the core checkout. A relative data root
    # would scatter data inside the checkouts (observed in testing).
    cores_dir = os.path.abspath(sys.argv[1])
    data_root = os.path.abspath(sys.argv[2])
    pairs = os.environ.get(
        "MAFP_PAIRS",
        os.path.join(cores_dir, "the-sword", "demo", "mafp-pairs.json"))

    for core, _cli in CORES:
        os.makedirs(os.path.join(data_root, core), exist_ok=True)

    # Build order 1 to 6, matching the Nation Kit sequence.
    run(cores_dir, data_root, "the-ledger", "ledger_cli.py",
        ["treasury", "revenue", "--source", "demo appropriation",
         "--amount", "100000", "--note", "umbrella demo seed"])
    run(cores_dir, data_root, "the-registry", "registry_cli.py",
        ["patent", "record", "--title", "Demo capability filing",
         "--inventor", "Demo Inventor",
         "--description", "Umbrella prototype filing"])
    run(cores_dir, data_root, "the-shield", "shield_cli.py",
        ["food", "register", "--id", "DEMO-1", "--name", "Demo ration",
         "--category", "food", "--maker", "Demo Maker"])
    if os.path.exists(pairs):
        run(cores_dir, data_root, "the-sword", "sword_cli.py",
            ["defense", "import-pairs", "--json", pairs,
             "--domain", "air"])
    run(cores_dir, data_root, "the-commons", "commons_cli.py",
        ["post", "register", "--id", "PO-1", "--locality", "Demo Town",
         "--type", "residential"])
    run(cores_dir, data_root, "the-safety-net", "safety_net_cli.py",
        ["benefits", "enroll", "--id", "BEN-1", "--program", "other",
         "--amount", "500", "--schedule", "monthly"])

    # Settlement: the enrollment obligation above is booked in
    # the-ledger in the same run. the-ledger is the only cash book.
    run(cores_dir, data_root, "the-ledger", "ledger_cli.py",
        ["treasury", "expense", "--recipient", "BEN-1",
         "--amount", "500", "--purpose", "benefit payment",
         "--note",
         "settlement for safety-net enrollment BEN-1"])
    balance = run(cores_dir, data_root, "the-ledger", "ledger_cli.py",
                  ["treasury", "balance"])
    print("ledger balance after settlement:", balance)
    print("data root:", data_root)


if __name__ == "__main__":
    main()

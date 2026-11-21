"""End to end umbrella test: the six cores, one shared data root.

Oracle: the Priority 3 prototype run closed at revenue $100,000.00
NCU, expenditure $500.00 NCU, cash $99,500.00 NCU. This test
reproduces that closing figure against real checkouts of the six
cores. Cores are located from NATION_KIT_CORES_DIR, a sibling
cores/ directory, or sibling checkouts of this repo. In CI the
workflow checks the six cores out into cores/. The test skips,
rather than fakes, when no checkouts exist.
"""
import os, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
RUNNER = os.path.join(ROOT, "nation_kit_runner.py")
CORES_REQUIRED = ("the-ledger", "the-registry", "the-shield",
                  "the-sword", "the-commons", "the-safety-net")

def find_cores_dir():
    candidates = []
    env = os.environ.get("NATION_KIT_CORES_DIR")
    if env: candidates.append(env)
    candidates.append(os.path.join(ROOT, "cores"))
    candidates.append(os.path.join(ROOT, ".."))
    for path in candidates:
        path = os.path.normpath(path)
        if all(os.path.isdir(os.path.join(path, c)) for c in CORES_REQUIRED):
            return path
    return None

CORES = find_cores_dir()

@unittest.skipIf(CORES is None, "six core checkouts not available")
class TestUmbrella(unittest.TestCase):
    def test_demo_run_closes_at_oracle_figure(self):
        with tempfile.TemporaryDirectory() as td:
            data_root = os.path.join(td, "nation-data")
            proc = subprocess.run(
                [sys.executable, RUNNER, CORES, data_root],
                capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("$99,500.00 NCU", proc.stdout)
            for core in CORES_REQUIRED:
                self.assertTrue(os.path.isdir(os.path.join(data_root, core)),
                                "missing data dir for %s" % core)
if __name__ == "__main__": unittest.main()

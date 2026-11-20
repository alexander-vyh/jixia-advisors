"""The committed plugin must match the shared core and run without the source checkout."""
import json
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_committed_plugin_copies_match_the_shared_core():
    result = subprocess.run([sys.executable, ROOT / "bin/build-plugin", "--check"], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_catalog_plugin_installs_as_real_files_and_runs_standalone(tmp_path):
    entry, = json.loads((ROOT / ".claude-plugin/marketplace.json").read_bytes())["plugins"]
    plugin = ROOT / entry["source"]
    for manifest in ("plugin.json", ".claude-plugin/plugin.json"):
        assert json.loads((plugin / manifest).read_bytes())["name"] == entry["name"]
    # Codex silently drops symlinks on install; claude.ai rejects a top-level bin/.
    assert not [path for path in plugin.rglob("*") if path.is_symlink()]
    assert not (plugin / "bin").exists()

    core = shutil.copytree(plugin, tmp_path / entry["name"]) / "skills/advise/jixia"
    plan = json.loads(subprocess.check_output(
        [sys.executable, "-B", core / "counsel.py", "run"], cwd=tmp_path,
        input=b"Audit this rollout for failure modes and root cause."))
    assert plan["model"] == "yushitai" and plan["mandatory"]
    assert (core / "reps/yushitai" / (plan["dissenter"] + ".md")).is_file()

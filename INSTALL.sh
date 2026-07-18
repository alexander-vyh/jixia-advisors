#!/usr/bin/env bash
# Install jixia-advisors agents + advisor-routing skeleton for Claude Code.
#
# Usage:
#   ./INSTALL.sh             # backup any existing real file, symlink the new
#   ./INSTALL.sh --uninstall # remove symlinks (backups are left alone)
#
# Backup-then-symlink: nothing is silently clobbered. If a file at the
# destination is already a symlink, it's replaced. If it's a real file,
# it's backed up to <name>.backup-YYYYMMDD-HHMMSS before being symlinked.
#
# Installs:
#   - claude/agents/*.md            -> ~/.claude/agents/        (the advisor pool)
#   - claude/skills/advise          -> ~/.claude/skills/advise  (the /advise front door)
#   - claude/hooks/jixia_send_bounce.py -> ~/.claude/hooks/     (send-bounce hook pair)
#   - bin/jixia-counsel-report      -> ~/.claude/bin/           (the keep/kill tally)
#   - jixia/{routing_classifier,dissent,advise_autopick}.py + registry.json + reps/
#                                   -> ~/.claude/jixia/          (the /advise auto-pick imports)
#   - ~/.claude/jixia/                                          (counsel-log + bounce-state dir)
#   - merges claude/settings-hooks.json into ~/.claude/settings.json (Slack staging matchers)

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="${CLAUDE_DIR:-$HOME/.claude}"
AGENTS_SRC="$REPO_DIR/claude/agents"
AGENTS_DST="$CLAUDE_DIR/agents"
SETTINGS="$CLAUDE_DIR/settings.json"
HOOKS_BLOCK="$REPO_DIR/claude/settings-hooks.json"

UNINSTALL=0
[ "${1:-}" = "--uninstall" ] && UNINSTALL=1

ts="$(date +%Y%m%d-%H%M%S)"
n=0

# link_path SRC DST — backup-then-symlink (or remove on uninstall). Increments n.
link_path() {
  local src="$1" dst="$2"
  [ -e "$src" ] || return 0

  if [ "$UNINSTALL" = "1" ]; then
    if [ -L "$dst" ] && [ "$(readlink "$dst")" = "$src" ]; then
      rm "$dst"
      echo "    removed: $dst"
      n=$((n+1))
    fi
    return 0
  fi

  mkdir -p "$(dirname "$dst")"
  if [ -L "$dst" ]; then
    rm "$dst"
  elif [ -e "$dst" ]; then
    local backup="$dst.backup-$ts"
    mv "$dst" "$backup"
    echo "    backup:  $dst -> $backup"
  fi
  ln -s "$src" "$dst"
  echo "    link:    $dst -> ${src#$HOME/}"
  n=$((n+1))
}

# --- 1. advisor pool (agents) ---
mkdir -p "$AGENTS_DST"
for src in "$AGENTS_SRC"/*.md; do
  [ -f "$src" ] || continue
  link_path "$src" "$AGENTS_DST/$(basename "$src")"
done

# --- 2. /advise skill (directory symlink) ---
link_path "$REPO_DIR/claude/skills/advise" "$CLAUDE_DIR/skills/advise"

# --- 3. send-bounce hook ---
link_path "$REPO_DIR/claude/hooks/jixia_send_bounce.py" "$CLAUDE_DIR/hooks/jixia_send_bounce.py"

# --- 4. counsel report (bin) ---
link_path "$REPO_DIR/bin/jixia-counsel-report" "$CLAUDE_DIR/bin/jixia-counsel-report"

# --- 5. routing classifier + its runtime deps (the /advise auto-pick imports these) ---
# The advise skill's snippet adds ~/.claude/jixia to sys.path and imports
# advise_autopick, which imports routing_classifier + dissent; each resolves
# registry.json relative to its own file, so the module + the registry must sit
# together. reps/ is symlinked so a historical dissent occupant resolves to its real
# source-backed rep file. (backup-then-symlink + uninstall handled by link_path.)
for f in routing_classifier.py dissent.py advise_autopick.py registry.json; do
  link_path "$REPO_DIR/jixia/$f" "$CLAUDE_DIR/jixia/$f"
done
link_path "$REPO_DIR/jixia/reps" "$CLAUDE_DIR/jixia/reps"

# --- 6. runtime state dir (counsel-log + bounce-state live here) ---
if [ "$UNINSTALL" != "1" ]; then
  mkdir -p "$CLAUDE_DIR/jixia"
  echo "    dir:     $CLAUDE_DIR/jixia (counsel-log.jsonl + bounce-state.jsonl)"
fi

# --- 7. settings.json hook merge (idempotent: remove-our-entries-then-append) ---
# Our entries are identified by the command containing 'jixia_send_bounce.py', so
# re-install never duplicates and --uninstall cleanly removes them.
SETTINGS="$SETTINGS" HOOKS_BLOCK="$HOOKS_BLOCK" MODE="$([ "$UNINSTALL" = "1" ] && echo uninstall || echo install)" \
python3 <<'PY'
import json, os, sys

settings_path = os.environ["SETTINGS"]
block_path = os.environ["HOOKS_BLOCK"]
mode = os.environ["MODE"]
MARK = "jixia_send_bounce.py"

def load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        print(f"    WARN: {path} is not valid JSON; leaving it untouched.")
        sys.exit(0)

settings = load(settings_path, {})
if not isinstance(settings, dict):
    print("    WARN: settings.json is not an object; leaving it untouched.")
    sys.exit(0)
hooks = settings.setdefault("hooks", {})

def strip_ours(event):
    """Drop any matcher-entry whose command references our hook (idempotent + uninstall)."""
    entries = hooks.get(event, [])
    kept = []
    for entry in entries:
        cmds = " ".join(h.get("command", "") for h in entry.get("hooks", []))
        if MARK in cmds:
            continue
        kept.append(entry)
    if kept:
        hooks[event] = kept
    elif event in hooks:
        del hooks[event]

for event in ("PreToolUse", "PostToolUse"):
    strip_ours(event)

if mode == "install":
    block = load(block_path, {}).get("hooks", {})
    for event, entries in block.items():
        hooks.setdefault(event, [])
        hooks[event].extend(entries)
    # Tidy: drop an empty hooks dict rather than leave {}
    if not hooks:
        settings.pop("hooks", None)
    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")
    print(f"    merge:   Slack staging matchers -> {settings_path}")
    print("    NOTE: the send-bounce hook only fires in sessions where the Slack MCP")
    print("          tools are present (mcp__*__slack_send_message[_draft]). If you do")
    print("          not use a Slack integration, the hook is inert (and fail-open).")
else:
    if not hooks:
        settings.pop("hooks", None)
    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")
    print(f"    unmerge: removed Slack staging matchers from {settings_path}")
PY

if [ "$UNINSTALL" = "1" ]; then
  echo "==> removed $n symlinks (settings entries unmerged; backups left alone)"
else
  echo "==> installed $n symlinks + runtime dir + settings merge"
fi

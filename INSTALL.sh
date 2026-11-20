#!/usr/bin/env bash
# Install Jixia Advisors for Claude Code: the advisor agents, the shared advise skill, and the send-bounce hook.
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
#   - jixia/advisors/*.md                       -> ~/.claude/agents/            (named Claude Code agents)
#   - plugins/jixia-advisors/skills/advise      -> ~/.claude/skills/advise      (the shared advise skill)
#   - plugins/jixia-advisors/skills/advise-full -> ~/.claude/skills/advise-full (its menu-first alias)
#   - claude/hooks/jixia_send_bounce.py         -> ~/.claude/hooks/             (send-bounce hook pair)
#   - bin/jixia-counsel-report                  -> ~/.claude/bin/               (the keep/kill tally)
#   - ~/.claude/jixia/                          (counsel-log + bounce-state dir)
#   - merges into ~/.claude/settings.json: the Slack staging matchers from
#     claude/settings-hooks.json and env JIXIA_COUNSEL_LOG, which turns on the skill's counsel log

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="${CLAUDE_DIR:-$HOME/.claude}"
AGENTS_SRC="$REPO_DIR/jixia/advisors"
AGENTS_DST="$CLAUDE_DIR/agents"
SETTINGS="$CLAUDE_DIR/settings.json"
HOOKS_BLOCK="$REPO_DIR/claude/settings-hooks.json"

UNINSTALL=0
[ "${1:-}" = "--uninstall" ] && UNINSTALL=1

ts="$(date +%Y%m%d-%H%M%S)"
n=0

# link_path SRC DST [OLD_SRC] — back up and link, or remove our link on uninstall.
link_path() {
  local src="$1" dst="$2" old_src="${3:-$1}"

  if [ "$UNINSTALL" = "1" ]; then
    local target
    if [ -L "$dst" ] && target="$(readlink "$dst")" && { [ "$target" = "$src" ] || [ "$target" = "$old_src" ]; }; then
      rm "$dst"
      echo "    removed: $dst"
      n=$((n+1))
    fi
    return 0
  fi
  [ -e "$src" ] || return 0

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
  name="$(basename "$src")"
  # Also recognize our previous source path when uninstalling before a reinstall.
  link_path "$src" "$AGENTS_DST/$name" "$REPO_DIR/claude/agents/$name"
done

# --- 2. the shared advise skill + its menu-first alias (directory symlinks) ---
for skill in advise advise-full; do
  link_path "$REPO_DIR/plugins/jixia-advisors/skills/$skill" "$CLAUDE_DIR/skills/$skill" "$REPO_DIR/claude/skills/$skill"
done

# --- 3. send-bounce hook ---
link_path "$REPO_DIR/claude/hooks/jixia_send_bounce.py" "$CLAUDE_DIR/hooks/jixia_send_bounce.py"

# --- 4. counsel report (bin) ---
link_path "$REPO_DIR/bin/jixia-counsel-report" "$CLAUDE_DIR/bin/jixia-counsel-report"

# --- 5. retire the module links older installs made; the skill now bundles its core ---
for f in routing_classifier.py dissent.py advise_autopick.py advise_full.py registry.json reps advisors; do
  dst="$CLAUDE_DIR/jixia/$f"
  if [ -L "$dst" ] && [[ "$(readlink "$dst")" == "$REPO_DIR"/* ]]; then
    rm "$dst"
    echo "    retired: $dst"
  fi
done

# --- 6. runtime state dir (counsel-log + bounce-state live here) ---
if [ "$UNINSTALL" != "1" ]; then
  mkdir -p "$CLAUDE_DIR/jixia"
  echo "    dir:     $CLAUDE_DIR/jixia (counsel-log.jsonl + bounce-state.jsonl)"
fi

# --- 7. settings.json merge (idempotent: remove-our-entries-then-append) ---
# Our hook entries are identified by the command containing 'jixia_send_bounce.py', so
# re-install never duplicates and --uninstall cleanly removes them. JIXIA_COUNSEL_LOG
# tells the skill's counsel.py where to append routed/counseled records.
SETTINGS="$SETTINGS" HOOKS_BLOCK="$HOOKS_BLOCK" COUNSEL_LOG="$CLAUDE_DIR/jixia/counsel-log.jsonl" \
MODE="$([ "$UNINSTALL" = "1" ] && echo uninstall || echo install)" \
python3 <<'PY'
import json, os, sys

settings_path = os.environ["SETTINGS"]
block_path = os.environ["HOOKS_BLOCK"]
mode = os.environ["MODE"]
log_path = os.environ["COUNSEL_LOG"]
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
    settings.setdefault("env", {})["JIXIA_COUNSEL_LOG"] = log_path
elif isinstance(settings.get("env"), dict):
    settings["env"].pop("JIXIA_COUNSEL_LOG", None)
    if not settings["env"]:
        del settings["env"]
# Tidy: drop an empty hooks dict rather than leave {}
if not hooks:
    settings.pop("hooks", None)
with open(settings_path, "w", encoding="utf-8") as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)
    f.write("\n")
if mode == "install":
    print(f"    merge:   Slack staging matchers + JIXIA_COUNSEL_LOG -> {settings_path}")
    print("    NOTE: the send-bounce hook only fires in sessions where the Slack MCP")
    print("          tools are present (mcp__*__slack_send_message[_draft]). If you do")
    print("          not use a Slack integration, the hook is inert (and fail-open).")
else:
    print(f"    unmerge: removed Slack staging matchers + JIXIA_COUNSEL_LOG from {settings_path}")
PY

if [ "$UNINSTALL" = "1" ]; then
  echo "==> removed $n symlinks (settings entries unmerged; backups left alone)"
else
  echo "==> installed $n symlinks + runtime dir + settings merge"
fi

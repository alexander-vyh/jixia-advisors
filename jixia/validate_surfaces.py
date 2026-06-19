#!/usr/bin/env python3
"""Install/sync validator for the method CALL SURFACES (advisor-convening-methods-v2, T3).

Oracle: openspec/changes/advisor-convening-methods-v2/specs/method-call-surfaces.md

Companion to validate_registry.py. That validator proves the registry's CONTRACTS are
distinct (M1-M8). THIS validator proves the callable SURFACES that expose those methods
in Claude and Codex stay in sync with the registry, resolve against REPO paths (so a
fresh checkout / CI validates with no install step), and do not drift from the
historical-source provenance README. Stdlib-only, offline, and independent of any v1
Slack hooks (no-v1-trigger-coupling): it reads files, nothing else.

Checks (each error string NAMES the offending method or source so callers can locate it):
  S1 - every registry method has a Claude command wrapper claude/commands/<method>.md
  S2 - every registry method has a Codex skill .agents/skills/<method>/SKILL.md
  S3 - each Claude wrapper DELEGATES to the registry (references registry.json) and does
       NOT embed a hand-maintained roster (no copied list of claude/agents advisor names)
  S4 - each Codex skill DELEGATES to the registry (references registry.json)
  S5 - each Codex skill's frontmatter `name:` equals the method id it serves
  S6 - every advisor / rep a surface references resolves in the REPO:
       claude/agents/<name>.md must exist; any jixia/reps/<...>.md path must exist
  S7 - drift guard: every registry historical-rep cites a source present in
       docs/historical-council-sources/README.md (matched on source_url, the exact
       provenance anchor both artifacts share)

Usage:
  python3 jixia/validate_surfaces.py     # validates the real repo surfaces, exit 0/1
"""

import json
import os
import re
import sys

REQUIRED_METHODS = {
    "jixia", "seven-sages", "areopagus", "junto", "parishad", "yushitai",
}

# Advisor names referenced explicitly as claude/agents/<name>.md inside a surface file.
_ADVISOR_REF = re.compile(r"claude/agents/([A-Za-z0-9_-]+)\.md")
# Rep module paths referenced explicitly as jixia/reps/<...>.md inside a surface file.
_REP_REF = re.compile(r"jixia/reps/[A-Za-z0-9_./-]+\.md")
# A bare advisor-directory mention (jixia/reps/<method>/) is a roster *pointer*, not a
# hardcoded roster; it is allowed. We only validate explicit *.md references for S6.


def _here():
    return os.path.dirname(os.path.abspath(__file__))


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _frontmatter_name(text):
    """Return the value of a top-of-file YAML `name:` key, or None.

    The Codex skill exemplar (.agents/skills/beads/SKILL.md) opens with a `---`
    frontmatter block carrying `name:` and `description:`. We parse `name:` without a
    yaml dependency (stdlib-only env).
    """
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    block = m.group(1) if m else text
    nm = re.search(r"^name:\s*(.+?)\s*$", block, re.MULTILINE)
    return nm.group(1).strip() if nm else None


def validate(registry, repo_root):
    """Return a list of human-readable error strings (empty list == surfaces valid).

    Each error names the offending method or source. repo_root contains claude/,
    .agents/, jixia/, and docs/.
    """
    errors = []
    methods = registry.get("methods", {})

    agents_dir = os.path.join(repo_root, "claude", "agents")
    # Set of advisor ids that actually resolve in the repo, for the embedded-roster guard.
    repo_advisors = set()
    if os.path.isdir(agents_dir):
        repo_advisors = {
            fn[:-3] for fn in os.listdir(agents_dir) if fn.endswith(".md")
        }

    readme_path = os.path.join(
        repo_root, "docs", "historical-council-sources", "README.md"
    )
    readme_text = _read(readme_path) if os.path.isfile(readme_path) else ""
    readme_lower = readme_text.lower()

    for name in sorted(methods.keys()):
        # --- S1: Claude command wrapper ------------------------------------
        cmd_path = os.path.join(repo_root, "claude", "commands", name + ".md")
        cmd_text = None
        if not os.path.isfile(cmd_path):
            errors.append(
                "S1: method %r has no Claude command wrapper "
                "(expected claude/commands/%s.md)" % (name, name)
            )
        else:
            cmd_text = _read(cmd_path)

        # --- S2: Codex skill ------------------------------------------------
        skill_path = os.path.join(repo_root, ".agents", "skills", name, "SKILL.md")
        skill_text = None
        if not os.path.isfile(skill_path):
            errors.append(
                "S2: method %r has no Codex skill "
                "(expected .agents/skills/%s/SKILL.md)" % (name, name)
            )
        else:
            skill_text = _read(skill_path)

        # --- S3: Claude wrapper delegates, does not embed a roster ----------
        if cmd_text is not None:
            if "registry.json" not in cmd_text:
                errors.append(
                    "S3: Claude wrapper for method %r does not delegate to the "
                    "registry (no reference to registry.json)" % name
                )
            # Embedded-roster guard: a wrapper that hand-maintains a roster lists
            # multiple real advisor ids verbatim. A delegating wrapper points at the
            # registry / a reps directory and names at most incidental examples.
            named = set(_ADVISOR_REF.findall(cmd_text))
            embedded = named & repo_advisors
            if len(embedded) >= 3:
                errors.append(
                    "S3: Claude wrapper for method %r appears to embed a "
                    "hand-maintained roster (names %d repo advisors: %s); it must "
                    "delegate to the registry instead"
                    % (name, len(embedded), ", ".join(sorted(embedded)))
                )

        # --- S4: Codex skill delegates -------------------------------------
        if skill_text is not None and "registry.json" not in skill_text:
            errors.append(
                "S4: Codex skill for method %r does not delegate to the registry "
                "(no reference to registry.json)" % name
            )

        # --- S5: Codex skill name matches the method -----------------------
        if skill_text is not None:
            declared = _frontmatter_name(skill_text)
            if declared != name:
                errors.append(
                    "S5: Codex skill for method %r declares frontmatter name %r "
                    "(must equal the method id)" % (name, declared)
                )

        # --- S6: advisor / rep references resolve in the repo --------------
        for surf_name, surf_text in (("claude", cmd_text), ("codex", skill_text)):
            if surf_text is None:
                continue
            for advisor in sorted(set(_ADVISOR_REF.findall(surf_text))):
                advisor_path = os.path.join(agents_dir, advisor + ".md")
                if not os.path.isfile(advisor_path):
                    errors.append(
                        "S6: %s surface for method %r references advisor %r which "
                        "does not resolve to claude/agents/%s.md"
                        % (surf_name, name, advisor, advisor)
                    )
            for rep_path in sorted(set(_REP_REF.findall(surf_text))):
                abs_rep = os.path.join(repo_root, rep_path)
                if not os.path.isfile(abs_rep):
                    errors.append(
                        "S6: %s surface for method %r references rep module %r "
                        "which does not exist in the repo" % (surf_name, name, rep_path)
                    )

    # --- S7: registry historical-rep provenance present in the README ------
    if not readme_text:
        errors.append(
            "S7: historical-council-sources README is missing at %s (cannot verify "
            "registry-rep provenance)" % readme_path
        )
    for name in sorted(methods.keys()):
        for rep in methods[name].get("historical_roster", []):
            rep_id = rep.get("id", "<no-id>")
            url = (rep.get("source_url") or "").strip().lower()
            if not url:
                # M3 in validate_registry.py already covers missing source metadata;
                # without a url we cannot run the provenance drift check.
                continue
            if url not in readme_lower:
                errors.append(
                    "S7: method %r historical rep %r cites a source (%s) not present "
                    "in docs/historical-council-sources/README.md "
                    "(registry<->README provenance drift)"
                    % (name, rep_id, rep.get("source_url"))
                )

    return errors


def main(argv=None):
    here = _here()
    repo_root = os.path.dirname(here)
    registry_path = os.path.join(here, "registry.json")

    with open(registry_path, encoding="utf-8") as f:
        registry = json.load(f)

    errors = validate(registry, repo_root=repo_root)
    if errors:
        print("SURFACES INVALID (%d violation(s)):" % len(errors), file=sys.stderr)
        for e in errors:
            print("  - " + e, file=sys.stderr)
        return 1
    print("OK: surfaces valid (6 methods, Claude + Codex, registry-delegating, "
          "repo-resolved, README provenance in sync).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

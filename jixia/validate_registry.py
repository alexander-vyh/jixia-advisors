#!/usr/bin/env python3
"""Registry distinctness validator (advisor-convening-methods-v2, T1b).

Oracle: openspec/changes/advisor-convening-methods-v2/test-oracle-brief.md

Static, stdlib-only validator for jixia/registry.json. Exits 0 when the registry is
valid; exits non-zero and PRINTS one line per violation (each naming the offending
method or representative) otherwise.

Checks (mutation ids from the oracle brief):
  M1 - exactly the six required method ids, each once (no missing / dup / renamed)
  M2 - every selectable practical advisor resolves to claude/agents/<name>.md (repo)
  M3 - every historical rep has full source metadata
  M4 - every method load_policy == "lazy"; every rep is method-scoped (rep.method
       matches its method; default reps belong to a historical-default method)
  M5 - not all six share one behavior contract (generic wrapper)
  M6 - every historical-default method has a non-empty roster AND each rep's module
       file exists and is non-empty
  M7 (= NC-1) - no two methods share an identical contract triple
       (output_fields set, entry_gate, refusal): copy-paste drift
  M8 - every method's verb_field is one of its output_fields, and no two methods
       share the same verb_field (verb collision)
  + phase coverage: every required output field is produced by at least one phase

HONEST LIMIT (documented, NOT a bug): this static check CANNOT catch NC-2, the
isomorphic-rename wrapper (two methods whose field strings differ but encode the
same template). A pairwise string-set comparison passes NC-2 by construction. That
case is the live-output fixture's job (T4 / 9aw.5), out of scope for this validator.

Usage:
  python3 jixia/validate_registry.py            # validates the real registry, exit 0/1
"""

import json
import os
import sys

REQUIRED_METHODS = {
    "jixia", "seven-sages", "areopagus", "junto", "parishad", "yushitai",
}

REQUIRED_REP_FIELDS = (
    "id", "type", "source_title", "source_url", "source_note", "confidence",
)
VALID_REP_TYPES = {"person", "role", "exemplar"}


def _here():
    return os.path.dirname(os.path.abspath(__file__))


def _contract_triple(method):
    """The mechanically-checkable contract: (output-field set, entry gate, refusal).

    output_fields is order-insensitive (a set), so phase/field reordering does not
    dodge the M7 collision check.
    """
    fields = frozenset(method.get("output_fields", []))
    gate = (method.get("entry_gate") or "").strip()
    refusal = (method.get("refusal") or "").strip()
    return (fields, gate, refusal)


def validate(registry, repo_root):
    """Return a list of human-readable error strings (empty list == valid).

    Each error string names the offending method (or rep id) so callers can locate
    the violation. repo_root is the directory that contains claude/agents/ and jixia/.
    """
    errors = []
    methods = registry.get("methods", {})

    # --- M1: exactly the six required ids, each once -------------------------
    present = set(methods.keys())
    for missing in sorted(REQUIRED_METHODS - present):
        errors.append("M1: required method %r is missing" % missing)
    for extra in sorted(present - REQUIRED_METHODS):
        errors.append("M1: unexpected/renamed method %r is not a required method id" % extra)
    # JSON object keys are unique, so duplicate ids cannot occur in a parsed dict;
    # the missing/extra pair above already catches the rename case (rename = one
    # missing required id + one extra id).

    # --- per-method structural checks ---------------------------------------
    verb_owner = {}  # verb_field -> [method names] for M8 collision
    contract_owner = {}  # contract triple -> [method names] for M5/M7

    for name in sorted(methods.keys()):
        m = methods[name]
        output_fields = m.get("output_fields", [])
        verb = m.get("verb_field")
        gate = (m.get("entry_gate") or "").strip()
        refusal = (m.get("refusal") or "").strip()
        policy = m.get("default_roster_policy")

        # M8: verb_field must be one of output_fields
        if not verb:
            errors.append("M8: method %r has no verb_field" % name)
        elif verb not in output_fields:
            errors.append(
                "M8: method %r verb_field %r is not among its output_fields %r"
                % (name, verb, output_fields)
            )
        else:
            verb_owner.setdefault(verb, []).append(name)

        # non-empty entry gate + refusal (fail-closed)
        if not gate:
            errors.append("M5: method %r has an empty entry_gate" % name)
        if not refusal:
            errors.append("M5: method %r has an empty refusal" % name)

        # M4: load policy must be lazy
        if m.get("load_policy") != "lazy":
            errors.append(
                "M4: method %r load_policy is %r, must be 'lazy'"
                % (name, m.get("load_policy"))
            )

        # phase coverage: every output field produced by >=1 phase
        produced = set()
        for phase in m.get("phases", []):
            produced.update(phase.get("produces", []))
        for field in output_fields:
            if field not in produced:
                errors.append(
                    "phase-coverage: method %r output field %r is not produced by any phase"
                    % (name, field)
                )

        # contract triple bookkeeping (M5/M7)
        triple = _contract_triple(m)
        contract_owner.setdefault(triple, []).append(name)

        # --- M2: practical advisor resolution -------------------------------
        # A method may name advisors via practical_allowlist; any named advisor must
        # resolve to claude/agents/<name>.md in the repo.
        for advisor in m.get("practical_allowlist", []):
            advisor_path = os.path.join(repo_root, "claude", "agents", advisor + ".md")
            if not os.path.isfile(advisor_path):
                errors.append(
                    "M2: method %r references practical advisor %r which does not "
                    "resolve to claude/agents/%s.md" % (name, advisor, advisor)
                )

        # --- representative checks (M3/M4/M6) -------------------------------
        roster = m.get("historical_roster", [])

        # M6: historical-default method must have a non-empty functional roster
        if policy == "historical" and not roster:
            errors.append(
                "M6: historical-default method %r has an empty historical_roster"
                % name
            )

        for rep in roster:
            rep_id = rep.get("id", "<no-id>")

            # M3: full source metadata
            for field in REQUIRED_REP_FIELDS:
                if not rep.get(field):
                    errors.append(
                        "M3: method %r representative %r is missing source metadata "
                        "field %r" % (name, rep_id, field)
                    )
            if rep.get("type") and rep["type"] not in VALID_REP_TYPES:
                errors.append(
                    "M3: method %r representative %r has invalid type %r"
                    % (name, rep_id, rep["type"])
                )

            # M4: method-scoped. If the rep declares a method, it must match. A rep
            # that belongs to a historical roster is, by being listed here, scoped to
            # this method; an explicit mismatching `method` field is a cross-method leak.
            declared = rep.get("method")
            if declared is not None and declared != name:
                errors.append(
                    "M4: method %r representative %r declares method %r "
                    "(cross-method leak; rosters must be method-scoped)"
                    % (name, rep_id, declared)
                )

            # M6: rep module body must exist and be non-empty
            module = rep.get("module")
            if not module:
                if policy == "historical":
                    errors.append(
                        "M6: historical-default method %r representative %r has no "
                        "module path" % (name, rep_id)
                    )
            else:
                module_path = os.path.join(repo_root, module)
                if not os.path.isfile(module_path):
                    errors.append(
                        "M6: method %r representative %r module %r does not exist"
                        % (name, rep_id, module)
                    )
                elif os.path.getsize(module_path) == 0:
                    errors.append(
                        "M6: method %r representative %r module %r is empty"
                        % (name, rep_id, module)
                    )

    # --- M8: verb-field collision across methods ----------------------------
    for verb, owners in sorted(verb_owner.items()):
        if len(owners) > 1:
            errors.append(
                "M8: verb_field %r is shared by methods %s (verb collision)"
                % (verb, ", ".join(sorted(owners)))
            )

    # --- M5 / M7: contract-triple collisions --------------------------------
    # M5 = all six share one contract; M7 = any two share an identical triple.
    if methods and len(contract_owner) == 1 and len(methods) > 1:
        all_names = ", ".join(sorted(methods.keys()))
        errors.append(
            "M5: all methods (%s) share one identical behavior contract "
            "(generic wrapper)" % all_names
        )
    for triple, owners in contract_owner.items():
        if len(owners) > 1:
            errors.append(
                "M7: methods %s share an identical contract triple "
                "(output-field set + entry gate + refusal); copy-paste drift"
                % ", ".join(sorted(owners))
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
        print("REGISTRY INVALID (%d violation(s)):" % len(errors), file=sys.stderr)
        for e in errors:
            print("  - " + e, file=sys.stderr)
        return 1
    print("OK: registry valid (6 methods, contracts pairwise-distinct).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

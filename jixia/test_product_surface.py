"""Behavioral contract for Jixia's public product front door."""

from __future__ import annotations

import importlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
TOUR = ROOT / "docs" / "PRODUCT_TOUR.md"
EVIDENCE = ROOT / "docs" / "EVIDENCE.md"
ROSTER = ROOT / "docs" / "ADVISOR_ROSTER.md"
REGISTRY = ROOT / "jixia" / "registry.json"
INSTALLER = ROOT / "INSTALL.sh"
PRODUCT_VERIFIER = ROOT / "bin" / "verify-product-front-door"

CATEGORY = "The advisory layer for agentic work."
PROMISE = "Convene the right perspectives. Leave with a practical next action."

EVIDENCE_PRS = (5, 6, 7, 11, 15, 16)


def _position(text: str, needle: str) -> int:
    position = text.find(needle)
    assert position >= 0, f"public surface is missing {needle!r}"
    return position


def _record(text: str, number: int, next_number: int | None) -> str:
    start = _position(text, f"### PR #{number} ")
    if next_number is None:
        next_section = text.find("\n## ", start)
        return text[start:] if next_section < 0 else text[start:next_section]
    return text[start : _position(text, f"### PR #{next_number} ")]


def _normalize_pr_text(text: str) -> str:
    without_markdown = re.sub(r"[`*_#]", "", text)
    return " ".join(without_markdown.lower().split())


def _unsupported_source_quotes(record: str, source_body: str) -> list[str]:
    source = _normalize_pr_text(source_body)
    return [
        quote
        for quote in re.findall(r"<q>(.*?)</q>", record, re.DOTALL)
        if not _normalize_pr_text(quote) or _normalize_pr_text(quote) not in source
    ]


def _false_product_claim(text: str) -> bool:
    normalized = " ".join(text.lower().split())
    universal_council = bool(
        re.search(
            r"\b(?:every|all|each)\s+(?:question|prompt|request)s?\b", normalized
        )
    ) and any(
        term in normalized
        for term in ("seven agents", "seven perspectives", "full council", "many agents")
    )
    codex_limitation = any(
        limitation in normalized
        for limitation in ("does not", "not install", "only the claude", "claude-only")
    )
    codex_install = (
        "codex" in normalized
        and not codex_limitation
        and (
            "install.sh" in normalized
            or "global codex installer" in normalized
        )
        and any(
            effect in normalized
            for effect in ("install", "globally", "available", "deploy")
        )
    )
    quality_proof = (
        bool(re.search(r"\b(?:proves|guarantees)\b", normalized))
        or any(
            term in normalized
            for term in (
                "has proven",
                "measured results show",
                "benchmark demonstrates",
            )
        )
    ) and any(
        outcome in normalized
        for outcome in (
            "better decisions",
            "improves every decision",
            "decision quality",
            "advice improves",
        )
    )
    slack_guarantee = "slack" in normalized and (
        any(
            phrase in normalized
            for phrase in ("blocks every", "always blocks", "cannot send")
        )
        or bool(
            re.search(
                r"\b(?:sensitive|every|all)\b.{0,40}\b(?:blocked|stopped|held)\b"
                r".{0,30}\b(?:until|before)\b",
                normalized,
            )
        )
    )
    strongest_model_guarantee = (
        any(term in normalized for term in ("unpinned", "omit a model pin", "no model pin"))
        and "strongest" in normalized
        and any(term in normalized for term in ("always", "guarantee", "inherits", "runs"))
    )
    return (
        universal_council
        or codex_install
        or quality_proof
        or slack_guarantee
        or strongest_model_guarantee
    )


def test_readme_leads_with_category_promise_companion_and_audience():
    readme = README.read_text(encoding="utf-8")
    first_section = readme[: _position(readme, "\n## ")]

    assert CATEGORY in first_section
    assert PROMISE in first_section
    assert "companion to [Escapement]" in first_section
    assert "operators" in first_section.lower()


def test_readme_puts_decision_material_and_limits_before_install():
    readme = README.read_text(encoding="utf-8")

    loop = _position(readme, "## The advisory loop in two minutes")
    evidence = _position(readme, "## Evidence, including the unfinished proof")
    entrypoints = _position(readme, "## Start with the question you have")
    limits = _position(readme, "## Current surfaces and truthful limits")
    install = _position(readme, "## Install the Claude surface")
    architecture = _position(readme, "## Advisory model and roster")

    assert loop < evidence < entrypoints < limits < install < architecture
    assert "[Open the representative product tour](docs/PRODUCT_TOUR.md)" in readme
    assert "[Inspect the evidence](docs/EVIDENCE.md)" in readme


def test_tour_is_labeled_and_exercises_the_real_advise_surface():
    tour = TOUR.read_text(encoding="utf-8")
    disclosure = _position(tour.lower(), "representative walkthrough")
    first_step = _position(tour, "## 1. Frame the work")

    assert disclosure < first_step
    assert "not a captured consultation" in tour.lower()
    assert "## Try it after installation" in tour
    assert "/advise-full " in tour
    assert "verbatim" in tour.lower()
    assert "dissent seat" in tour.lower()
    for heading in (
        "## 1. Frame the work",
        "## 2. Route to the method",
        "## 3. Resolve an installed roster",
        "## 4. Keep dissent structural",
        "## 5. Synthesize into action",
        "## 6. Learn without pretending",
    ):
        assert heading in tour


def test_tour_example_matches_the_executable_route_and_registry():
    tour = TOUR.read_text(encoding="utf-8")
    quoted_prompt = re.search(r"^> /advise-full (.+(?:\n> .+)*)", tour, re.MULTILINE)
    assert quoted_prompt, "tour must contain one executable /advise-full example"
    prompt = quoted_prompt.group(1).replace("\n> ", " ")

    jixia_dir = str(ROOT / "jixia")
    if jixia_dir not in sys.path:
        sys.path.insert(0, jixia_dir)
    advise_full = importlib.import_module("advise_full")
    menu = advise_full.build_menu(
        prompt, session_id="tour-verification", channel_id="adhoc"
    )
    plan = advise_full.resolve_selection(
        prompt,
        model="jixia",
        roster="practical",
        agents=["behavioral-psychologist", "management-philosophizer"],
        session_id="tour-verification",
        channel_id="adhoc",
    )
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))["methods"]
    method = registry[plan["model"]]

    assert f"method: {menu['recommended_model']}" in tour
    assert f"roster: {menu['roster']}" in tour
    assert f"confidence margin: {menu['confidence']}" in tour
    assert f"dissent seat: {menu['dissenter']}" in tour
    assert f"method: {plan['model']}" in tour
    assert f"agents: {', '.join(plan['agents'])}" in tour
    assert f"dissent seat: {plan['dissenter']}" in tour
    assert "override: true" in tour
    assert plan["dissenter"] in plan["agents"]
    for field in method["output_fields"]:
        display_field = field.replace("_", " ")
        assert re.search(rf"^{re.escape(display_field)}$", tour, re.MULTILINE)


def test_evidence_records_bind_observed_results_to_counterevidence():
    evidence = EVIDENCE.read_text(encoding="utf-8")

    for index, number in enumerate(EVIDENCE_PRS):
        next_number = EVIDENCE_PRS[index + 1] if index + 1 < len(EVIDENCE_PRS) else None
        record = _record(evidence, number, next_number)
        nonempty = [line for line in record.splitlines() if line.strip()]
        assert len(nonempty) == 4, f"PR #{number} must have exactly three evidence fields"
        assert nonempty[1] == (
            f"- **Record:** [Merged pull request #{number}]"
            f"(https://github.com/alexander-vyh/jixia-advisors/pull/{number})"
        )
        assert nonempty[2].startswith("- **Observed PR-body facts:** ")
        assert nonempty[3].startswith("- **PR-body limit:** ")
        for claim_line in nonempty[2:]:
            quotes = re.findall(r"<q>(.*?)</q>", claim_line)
            assert quotes
            assert all(_normalize_pr_text(quote) for quote in quotes)
            residue = re.sub(r"<q>.*?</q>", "", claim_line)
            residue = residue.split(":**", 1)[1]
            assert not re.search(r"[a-z0-9]", residue, re.IGNORECASE)

    assert "not testimonials" in evidence.lower()
    assert "no automated github check runs" in evidence.lower()


@pytest.mark.skipif(
    os.environ.get("JIXIA_VERIFY_LIVE_EVIDENCE") != "1",
    reason="set JIXIA_VERIFY_LIVE_EVIDENCE=1 for the fail-closed GitHub oracle",
)
def test_live_evidence_records_match_github():
    """Resolve the public evidence against GitHub, not a copied local fixture."""
    evidence = EVIDENCE.read_text(encoding="utf-8")
    for index, number in enumerate(EVIDENCE_PRS):
        result = subprocess.run(
            [
                "gh",
                "pr",
                "view",
                str(number),
                "--repo",
                "alexander-vyh/jixia-advisors",
                "--json",
                "number,state,mergedAt,mergeCommit,body,statusCheckRollup",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        pull = json.loads(result.stdout)
        assert pull["number"] == number
        assert pull["state"] == "MERGED"
        assert pull["mergedAt"]
        assert pull["mergeCommit"]["oid"]
        assert pull["statusCheckRollup"] == []

        next_number = EVIDENCE_PRS[index + 1] if index + 1 < len(EVIDENCE_PRS) else None
        public_record = _record(evidence, number, next_number)
        assert _unsupported_source_quotes(public_record, pull["body"]) == []

    workflows = subprocess.run(
        [
            "gh",
            "workflow",
            "list",
            "--all",
            "--repo",
            "alexander-vyh/jixia-advisors",
            "--json",
            "name",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert workflows.returncode == 0, workflows.stderr
    workflow_output = workflows.stdout.strip()
    assert workflow_output == "" or json.loads(workflow_output) == []


def test_source_quote_oracle_rejects_an_unsupported_capability_mutation():
    source_body = "The six convening methods are now callable and registry-validated."
    mutated_record = (
        "<q>The six convening methods are now callable and registry-validated.</q> "
        "<q>Jixia shipped a hosted dashboard.</q>"
    )
    assert _unsupported_source_quotes(mutated_record, source_body) == [
        "Jixia shipped a hosted dashboard."
    ]


def test_source_quote_oracle_rejects_empty_evidence():
    assert _unsupported_source_quotes("<q></q>", "Any source body") == [""]


def test_canonical_product_verifier_enables_the_live_fail_closed_oracle():
    verifier = PRODUCT_VERIFIER.read_text(encoding="utf-8")
    assert os.access(PRODUCT_VERIFIER, os.X_OK)
    assert "JIXIA_VERIFY_LIVE_EVIDENCE=1" in verifier
    assert "jixia/test_product_surface.py" in verifier


def test_product_surfaces_match_the_executable_contract():
    readme = README.read_text(encoding="utf-8")
    tour = TOUR.read_text(encoding="utf-8")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    installer = INSTALLER.read_text(encoding="utf-8")

    assert len(registry["methods"]) == 6
    assert len(list((ROOT / "claude" / "agents").glob("*.md"))) == 20
    assert "CLAUDE_DIR" in installer
    assert "CODEX" not in installer
    assert "20 advisor lenses" in readme
    assert "six convening methods" in readme
    assert "repo-local method skills" in readme
    assert "globally installs only the Claude Code surface" in readme
    assert "not proven" in f"{readme}\n{tour}".lower()


def test_public_roster_matches_the_advisor_files_and_model_policy():
    roster = ROSTER.read_text(encoding="utf-8")
    documented = set(re.findall(r"^- `([^`]+)` —", roster, re.MULTILINE))
    agent_files = list((ROOT / "claude" / "agents").glob("*.md"))
    actual = {path.stem for path in agent_files}
    assert documented == actual

    unpinned = {
        path.stem
        for path in agent_files
        if not re.search(r"^model:\s*\S+", path.read_text(encoding="utf-8"), re.MULTILINE)
    }
    policy_paragraph = roster.split("The other 12 definitions", 1)[0].rsplit(
        "Eight definitions", 1
    )[1]
    documented_unpinned = set(re.findall(r"`([^`]+)`", policy_paragraph))
    assert documented_unpinned == unpinned


def test_relative_markdown_links_on_product_surfaces_resolve():
    markdown_link = re.compile(r"\[[^]]+\]\(([^)]+)\)")
    for surface in (README, TOUR, EVIDENCE, ROSTER):
        for target in markdown_link.findall(surface.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            relative, _, fragment = target.partition("#")
            resolved = (surface.parent / relative).resolve()
            assert resolved.exists(), f"{surface.relative_to(ROOT)} has dead link {target}"
            if fragment:
                anchors = {
                    re.sub(
                        r"-+",
                        "-",
                        re.sub(r"[^a-z0-9 -]", "", line.lstrip("# ").lower()).replace(
                            " ", "-"
                        ),
                    ).strip("-")
                    for line in resolved.read_text(encoding="utf-8").splitlines()
                    if line.startswith("#") and " " in line
                }
                assert fragment in anchors, f"dead anchor {target}"


@pytest.mark.parametrize(
    "false_claim",
    (
        "Every question runs a full council of seven agents.",
        "All prompts convene many agents before answering.",
        "Jixia runs seven perspectives on each question.",
        "Codex is globally installed by INSTALL.sh.",
        "INSTALL.sh installs Jixia for Codex everywhere.",
        "Run INSTALL.sh to make Jixia available in Claude and Codex.",
        "Jixia has proven that its advice improves decision quality.",
        "The routing log guarantees better decisions.",
        "Measured results show that Jixia produces better decisions.",
        "The Slack hook blocks every sensitive message.",
        "A staged Slack message cannot send without counsel.",
        "Sensitive Slack drafts are stopped until an advisor reviews them.",
        "Unpinned advisors always run the strongest available model.",
    ),
)
def test_false_product_claim_detector_rejects_semantic_mutations(false_claim: str):
    assert _false_product_claim(false_claim)


def test_public_product_surfaces_contain_no_false_capability_claims():
    for surface in (README, TOUR, EVIDENCE, ROSTER):
        text = " ".join(surface.read_text(encoding="utf-8").splitlines())
        offenders = [
            sentence
            for sentence in re.split(r"(?<=[.!?])\s+", text)
            if _false_product_claim(sentence)
        ]
        assert offenders == [], f"{surface}: {offenders}"

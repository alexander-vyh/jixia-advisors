"""CLI for the advise skill. The UTF-8 question or draft comes from stdin.

Read-only unless $JIXIA_COUNSEL_LOG names a counsel log (the Claude Code installer sets
it): then `run` appends the `routed` record and `record` appends the `counseled` one.
"""

import argparse
import json
import os
import sys

# Running the skill from a read-only mount must not require cache files.
sys.dont_write_bytecode = True

import advise_autopick
import advise_full

LOG_ENV = "JIXIA_COUNSEL_LOG"
SESSION_ENV = "CLAUDE_CODE_SESSION_ID"  # the session id the send-bounce hook also records


def route(args, draft):
    """Return (the printed result, the counsel-log record or None)."""
    session_id = os.environ.get(SESSION_ENV, "")
    if args.command == "record":
        if not os.environ.get(LOG_ENV):
            raise ValueError(f"${LOG_ENV} is not set; there is no counsel log to record to.")
        if not session_id:
            raise ValueError(f"${SESSION_ENV} is empty; the record could not join a bounce.")
        record = advise_autopick.build_counseled_record(session_id, args.channel,
                                                        dict.fromkeys(args.lens), draft)
        return record, record

    if args.command == "menu":
        menu = advise_full.build_menu(draft)
        if menu["fell_back"] or menu["dissent_degraded"]:
            raise ValueError("Routing or seating unavailable; use the file-based route.")
        # Don't echo the draft, session metadata, or the in-memory routing record.
        return {key: menu[key] for key in ("selected_model", "models", "roster",
                                           "dissenter", "confidence", "mandatory")}, None

    plan = advise_full.resolve_selection(draft, model=args.model, roster=args.roster,
                                         dissent_occupant=args.dissenter,
                                         remove_dissent=args.remove_dissent,
                                         session_id=session_id, channel_id=args.channel)
    if plan["fell_back"] or plan["dissent_degraded"]:
        raise ValueError("Routing or seating unavailable; use the file-based route.")
    if plan["model_override_unresolved"]:
        raise ValueError(f"Unknown method {args.model!r}. Use menu to see available methods.")

    model, roster = plan["model"], plan["roster"]
    options = advise_full.agent_options(model, roster)
    if args.command == "options":
        return {"model": model, "roster": roster, "roster_options": advise_full.roster_options(model),
                **options}, None

    advisors = list(dict.fromkeys(args.advisor))
    unknown = [advisor for advisor in advisors if advisor not in options["practical_pool"]]
    if unknown:
        raise ValueError(f"Not a bundled practical advisor: {', '.join(unknown)}. Use options.")

    result = {"model": model, "roster": roster, "advisors": advisors,
              "historical_reps": options["historical_reps"],
              **{key: plan[key] for key in ("dissenter", "dissent_prompt", "mandatory", "reinstated", "confidence")}}
    return result, {**plan["record"], "entry": "advise-full" if args.from_menu else "advise"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("menu", help="Show the preselected method and collapsed roster")
    for name in ("options", "run"):
        sub = commands.add_parser(name, help=("Expand available rosters and lenses" if name == "options"
                                               else "Resolve a counsel plan"))
        sub.add_argument("--model", help="Method id or alias from registry.json")
        sub.add_argument("--roster", choices=("practical", "historical"))
        if name == "run":
            sub.add_argument("--advisor", action="append", default=[], help="Practical advisor id (repeatable)")
            sub.add_argument("--dissenter", help="Swap the mandatory dissent lens")
            sub.add_argument("--remove-dissent", action="store_true", help="Demonstrate reinstatement of the seat")
            sub.add_argument("--from-menu", action="store_true", help="The user chose from the menu")
            sub.add_argument("--channel", default="adhoc", help="Channel id named by a send-bounce notice")
        else:
            sub.set_defaults(dissenter=None, remove_dissent=False, channel="adhoc")
    record = commands.add_parser("record", help="Log a finished consultation for a send-bounce notice")
    record.add_argument("--channel", required=True, help="Channel id exactly as the notice shows it")
    record.add_argument("--lens", action="append", required=True, help="Lens consulted (repeatable)")
    args = parser.parse_args()
    try:
        draft = sys.stdin.buffer.read().decode("utf-8")
        if not draft.strip():
            raise ValueError("Supply the question or verbatim draft on standard input.")
        result, entry = route(args, draft)
    except ValueError as exc:
        parser.exit(2, f"{exc}\n")
    if entry and (log_path := os.environ.get(LOG_ENV)):
        try:
            advise_autopick.append_record(entry, log_path)
        except OSError as exc:
            if args.command == "record":
                parser.exit(1, f"Counsel log not written: {exc}\n")
            print(f"Counsel log not written: {exc}", file=sys.stderr)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

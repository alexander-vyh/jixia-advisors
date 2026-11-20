"""Read-only CLI for the packaged advise skill. The UTF-8 draft comes from stdin."""

import argparse
import json
import sys

# Running the skill from a read-only mount must not require cache or log files.
sys.dont_write_bytecode = True

import advise_full


def route(args, draft):
    if args.command == "menu":
        menu = advise_full.build_menu(draft)
        if menu["fell_back"] or menu["dissent_degraded"]:
            raise ValueError("Routing or seating unavailable; use the file-based route.")
        # Don't echo the draft, session metadata, or the in-memory routing record.
        return {key: menu[key] for key in ("selected_model", "models", "roster",
                                          "dissenter", "confidence", "mandatory")}

    plan = advise_full.resolve_selection(draft, model=args.model, roster=args.roster,
                                         dissent_occupant=args.dissenter,
                                         remove_dissent=args.remove_dissent)
    if plan["fell_back"] or plan["dissent_degraded"]:
        raise ValueError("Routing or seating unavailable; use the file-based route.")
    if plan["model_override_unresolved"]:
        raise ValueError(f"Unknown method {args.model!r}. Use menu to see available methods.")

    model, roster = plan["model"], plan["roster"]
    options = advise_full.agent_options(model, roster)
    if args.command == "options":
        return {"model": model, "roster": roster, "roster_options": advise_full.roster_options(model), **options}

    advisors = list(dict.fromkeys(args.advisor))
    unknown = [advisor for advisor in advisors if advisor not in options["practical_pool"]]
    if unknown:
        raise ValueError(f"Not a bundled practical advisor: {', '.join(unknown)}. Use options.")

    return {"model": model, "roster": roster, "advisors": advisors,
            "historical_reps": options["historical_reps"],
            **{key: plan[key] for key in ("dissenter", "dissent_prompt", "mandatory", "reinstated", "confidence")}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("menu", help="Show the preselected method and collapsed roster")
    for name in ("options", "run"):
        sub = commands.add_parser(name, help=("Expand available rosters and lenses" if name == "options"
                                               else "Resolve a read-only counsel plan"))
        sub.add_argument("--model", help="Method id or alias from registry.json")
        sub.add_argument("--roster", choices=("practical", "historical"))
        if name == "run":
            sub.add_argument("--advisor", action="append", default=[], help="Practical advisor id (repeatable)")
            sub.add_argument("--dissenter", help="Swap the mandatory dissent lens")
            sub.add_argument("--remove-dissent", action="store_true", help="Demonstrate reinstatement of the seat")
        else:
            sub.set_defaults(dissenter=None, remove_dissent=False)
    args = parser.parse_args()
    try:
        draft = sys.stdin.buffer.read().decode("utf-8")
        if not draft.strip():
            raise ValueError("Supply the question or verbatim draft on standard input.")
        result = route(args, draft)
    except ValueError as exc:
        parser.exit(2, f"{exc}\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

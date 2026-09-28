"""CLI: python -m etsy_agents <command> ..."""

import argparse

from .agents import CEO, SPECIALISTS
from .runtime import run_agent

PLAYBOOKS = {
    "launch": "Plan the launch of my Etsy store: find the best niche and 3 products, vet suppliers and margins, "
    "write the first listings, build a 30-day marketing plan, and a starting budget/P&L.",
    "weekly": "Run the weekly routine: refresh trending product ideas for my niche, draft this week's content "
    "calendar, and review any sales/ad numbers in outputs/finance or the task notes for what to scale or cut.",
}


def main() -> None:
    p = argparse.ArgumentParser(prog="etsy_agents", description="AI team that runs your Etsy store")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("agents", help="list the team")
    sub.add_parser("launch", help="CEO plans a full store launch")
    sub.add_parser("weekly", help="CEO runs the weekly routine")
    ceo = sub.add_parser("ask", help="give the CEO any goal")
    ceo.add_argument("goal")
    one = sub.add_parser("run", help="talk to one specialist directly")
    one.add_argument("agent", choices=[s.name for s in SPECIALISTS])
    one.add_argument("task")
    a = p.parse_args()

    if a.cmd == "agents":
        for s in [CEO, *SPECIALISTS]:
            print(f"{s.name:20} {s.description}")
        return
    if a.cmd == "run":
        spec, task = next(s for s in SPECIALISTS if s.name == a.agent), a.task
    else:
        spec, task = CEO, PLAYBOOKS.get(a.cmd) or a.goal
    print("\n" + run_agent(spec, task))
    print("\nDeliverables are in ./outputs/ (drafts only, nothing was published).")


main()

"""Adversarial niche research: discover -> advocates argue -> cross-examination -> judge.

Each advocate champions one niche, then reads every other advocate's case and attacks it. A judge who
argues for nothing picks the winner. This is how the agents challenge each other's conclusions.
"""

import json
from concurrent.futures import ThreadPoolExecutor

import anthropic

from .agents import SPECIALISTS, AgentSpec
from .runtime import MODEL, OUTPUT_DIR, run_agent

RESEARCHER = next(s for s in SPECIALISTS if s.name == "product_researcher")

CASE_TASK = """Build the strongest evidence-based case that '{niche}' is the best niche + POD product for this
store. Cover: winnable long-tail keywords, page-one competition, the ONE best product and price, unit economics
after Etsy/POD fees, Q4 and post-holiday timing, design workload, IP/policy risk. Then list the 3 strongest
arguments AGAINST your niche and the number that would change your mind. Mark unverified figures. Save the case
to debate/round2_{slug}.md and return it."""

REBUT_TASK = """You advocate for '{niche}'. Here are the cases for the rival niches:

{rivals}

Attack each rival case: find weak evidence, unverified numbers, bad unit economics, timing or IP problems.
Then defend your own niche against the attacks you expect, and say honestly if a rival now looks better than
yours (you may concede). Save to debate/round3_{slug}.md and return it."""

JUDGE_TASK = """You are the neutral Judge. Below are the round-2 cases and round-3 rebuttals for each niche.

{everything}

Choose the winning niche + single best POD product to launch first, a runner-up, and a fallback. Weigh
evidence quality, expected profit per sale, realistic sales for a zero-review shop, timing, design workload
and IP risk. Reject claims that are unverified or refuted. Give a scorecard table, the decision, the first
5 designs to make, target price, and the numbers to verify before spending money. Save to debate/verdict.md."""


def _advocate(niche: str) -> AgentSpec:
    return AgentSpec(
        f"advocate_{niche[:20]}",
        f"Advocate for {niche}",
        f"You are an advocate agent who argues for the niche '{niche}', but you stay honest: never invent "
        "numbers, and concede when a rival is stronger. Use web_search.",
    )


def _slug(niche: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in niche.lower())[:30].strip("_")


def _top_niches(client: anthropic.Anthropic, report: str, n: int) -> list[str]:
    msg = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": f"From this report list the top {n} candidate niches as a JSON array of short strings. "
            f"Output only the JSON.\n\n{report}",
        }],
    )
    text = "".join(b.text for b in msg.content if b.type == "text")
    return json.loads(text[text.index("["): text.rindex("]") + 1])[:n]


def run_debate(top_n: int = 5, focus: str = "") -> str:
    client = anthropic.Anthropic()
    print("== Round 1: discovery ==")
    report = run_agent(
        RESEARCHER,
        f"Research the best POD niches for a new Etsy store. {focus} Rank the top candidates with evidence.",
        client,
    )
    niches = _top_niches(client, report, top_n)
    print("Contenders:", niches)

    print("== Round 2: advocates make their case ==")
    with ThreadPoolExecutor(len(niches)) as pool:
        cases = list(pool.map(
            lambda n: run_agent(_advocate(n), CASE_TASK.format(niche=n, slug=_slug(n)), client), niches))

    print("== Round 3: cross-examination ==")

    def rebut(i: int) -> str:
        rivals = "\n\n".join(f"### {niches[j]}\n{cases[j]}" for j in range(len(niches)) if j != i)
        task = REBUT_TASK.format(niche=niches[i], rivals=rivals, slug=_slug(niches[i]))
        return run_agent(_advocate(niches[i]), task, client)

    with ThreadPoolExecutor(len(niches)) as pool:
        rebuttals = list(pool.map(rebut, range(len(niches))))

    print("== Verdict ==")
    everything = "\n\n".join(
        f"## {n}\n### Case\n{c}\n### Rebuttal\n{r}" for n, c, r in zip(niches, cases, rebuttals))
    judge = AgentSpec("judge", "Neutral judge", "You are a rigorous, skeptical judge. Use web_search to spot-check claims.")
    verdict = run_agent(judge, JUDGE_TASK.format(everything=everything), client)
    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / "debate").mkdir(exist_ok=True)
    (OUTPUT_DIR / "debate" / "verdict_final.md").write_text(verdict)
    return verdict

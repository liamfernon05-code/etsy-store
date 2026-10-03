"""Statistics for AI-visibility sampling. Stdlib only.

Why this exists: assistants are non-deterministic (SparkToro: <1 in 100 chance of the same brand list twice),
so a single run says nothing and 5-10 runs per prompt give uselessly wide intervals. We report a
*mention rate with an interval*, never a rank, and refuse to call a change real unless intervals separate.
"""

from __future__ import annotations

import math
import random

MIN_RUNS_HEADLINE = 200  # valid runs per platform per period before a headline claim is allowed


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def clustered_bootstrap(per_prompt: dict[str, tuple[int, int]], iters: int = 2000, seed: int = 7,
                        alpha: float = 0.05) -> tuple[float, float]:
    """CI for the pooled rate, resampling prompts first (prompts differ in difficulty), then runs within them."""
    items = [(k, n) for k, n in per_prompt.values() if n > 0]
    if not items:
        return (0.0, 1.0)
    rng = random.Random(seed)
    rates = []
    for _ in range(iters):
        tk = tn = 0
        for _ in items:
            k, n = items[rng.randrange(len(items))]
            p = k / n
            tk += sum(1 for _ in range(n) if rng.random() < p)
            tn += n
        rates.append(tk / tn)
    rates.sort()
    return (rates[int(alpha / 2 * iters)], rates[min(iters - 1, int((1 - alpha / 2) * iters))])


def min_detectable_diff(n_per_wave: int, p: float = 0.3) -> float:
    """Approx. minimum detectable difference in proportions at 80% power, alpha=0.05, equal waves."""
    if n_per_wave <= 0:
        return 1.0
    return 2.8 * math.sqrt(2 * p * (1 - p) / n_per_wave)


def compare_waves(a: dict[str, tuple[int, int]], b: dict[str, tuple[int, int]], iters: int = 2000, seed: int = 11) -> dict:
    """Difference in pooled rate (b - a) with a clustered-bootstrap interval; verdict only if it excludes 0."""
    def pooled(d):
        n = sum(x[1] for x in d.values())
        return (sum(x[0] for x in d.values()) / n) if n else 0.0

    rng = random.Random(seed)

    def draw(d):
        items = [(k, n) for k, n in d.values() if n > 0]
        if not items:
            return 0.0
        tk = tn = 0
        for _ in items:
            k, n = items[rng.randrange(len(items))]
            p = k / n
            tk += sum(1 for _ in range(n) if rng.random() < p)
            tn += n
        return tk / tn

    diffs = sorted(draw(b) - draw(a) for _ in range(iters))
    lo, hi = diffs[int(0.025 * iters)], diffs[int(0.975 * iters)]
    delta = pooled(b) - pooled(a)
    verdict = "no detectable change"
    if lo > 0:
        verdict = "increase (interval excludes 0)"
    elif hi < 0:
        verdict = "decrease (interval excludes 0)"
    return {"delta": delta, "ci": (lo, hi), "verdict": verdict}


def validity_label(valid_runs: int) -> str:
    if valid_runs >= MIN_RUNS_HEADLINE:
        return "headline-grade sample"
    return f"diagnostic only (<{MIN_RUNS_HEADLINE} valid runs): do not make trend claims"

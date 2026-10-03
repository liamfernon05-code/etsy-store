import json

import pytest

from local_seo_agent.probe import Budget, compare, estimate, run_probe, summarise
from local_seo_agent.probe import stats
from local_seo_agent.probe.entities import extract_listed_entities, is_distinctive, match_client
from local_seo_agent.probe.prompts import build_prompts
from local_seo_agent.probe.providers import (FakeProvider, OpenAICompatProvider, OpenAIResponsesProvider,
                                              ProbeResponse)
from local_seo_agent.probe.store import Store


def test_wilson_known_values():
    lo, hi = stats.wilson(1, 10)
    assert round(lo, 2) == 0.02 and round(hi, 2) == 0.40       # the "useless interval" the critique warned about
    lo, hi = stats.wilson(60, 200)
    assert 0.23 < lo < 0.25 and 0.36 < hi < 0.38
    assert stats.wilson(0, 0) == (0.0, 1.0)


def test_clustered_bootstrap_is_wider_than_naive_when_prompts_differ():
    per = {f"a{i}": (8, 8) for i in range(5)} | {f"b{i}": (0, 8) for i in range(5)}   # half easy, half impossible
    lo, hi = stats.clustered_bootstrap(per, iters=800)
    nlo, nhi = stats.wilson(40, 80)
    assert (hi - lo) > (nhi - nlo)
    assert stats.clustered_bootstrap(per, iters=300, seed=1) == stats.clustered_bootstrap(per, iters=300, seed=1)


def test_compare_waves_refuses_noise_and_detects_real_change():
    same = {f"p{i}": (3, 10) for i in range(10)}
    assert stats.compare_waves(same, same)["verdict"] == "no detectable change"
    up = {f"p{i}": (8, 10) for i in range(10)}
    assert stats.compare_waves(same, up)["verdict"].startswith("increase")


def test_min_detectable_diff_matches_critique():
    assert 0.12 < stats.min_detectable_diff(200, 0.3) < 0.14       # ~13 points at 200 runs vs 200


def test_validity_label():
    assert "diagnostic" in stats.validity_label(50) and "headline" in stats.validity_label(200)


def test_prompts_need_city_and_terms(profile):
    ps = build_prompts(profile)
    assert ps and all("Austin" in p.text for p in ps) and len({p.id for p in ps}) == len(ps)
    profile.primary_city, profile.address.city = "", ""
    with pytest.raises(ValueError):
        build_prompts(profile)


def test_entity_match_levels(profile):
    profile.website = "https://www.riversidedental.example"
    assert match_client("Call (512) 555-0147", [], profile)["verified"]
    assert match_client("see more", ["https://riversidedental.example/x"], profile)["cited"]
    m = match_client("1. Riverside Family Dental in Austin is great", [], profile)
    assert m["name_match"] and not m["verified"]                      # distinctive name, not hard-verified
    assert not match_client("1. Other Dental", [], profile)["name_match"]


def test_generic_name_needs_city_context(profile):
    profile.name, profile.brand_aliases = "Smith Plumbing", []
    assert not is_distinctive("Smith Plumbing")
    assert not match_client("Smith Plumbing is a chain in Dallas far from here." + " x" * 150 + " Austin", [], profile)["name_match"]
    assert match_client("Smith Plumbing in Austin is highly rated", [], profile)["name_match"]


def test_extract_listed_entities():
    text = "1. **Maple Grove Care** - great\n2) Downtown Experts: ok\n- City Pros Group (best)\nNot a list line"
    assert extract_listed_entities(text) == ["Maple Grove Care", "Downtown Experts", "City Pros Group"]


def test_run_probe_end_to_end_with_budget(tmp_path, profile):
    store = Store(tmp_path / "p.sqlite")
    prov = FakeProvider(cost_per_call=0.01, p_mention=0.5)
    res = run_probe(profile, [prov], store, "w1", runs=4, budget=Budget(0.10))
    assert res["halted"] and res["completed"] == 10                  # stops at the hard cap, in code
    store2 = Store(tmp_path / "q.sqlite")
    res = run_probe(profile, [FakeProvider(p_mention=0.5)], store2, "w1", runs=5, budget=Budget(10))
    assert not res["halted"]
    s = summarise(store2, "w1", profile)["providers"]["fake"]
    assert s["valid_runs"] == res["completed"] and "diagnostic" in s["validity"]
    assert s["mention_rate_ci_clustered"][0] < s["mention_rate"] < s["mention_rate_ci_clustered"][1]
    assert s["top_named_entities"] and s["top_cited_domains"]
    assert summarise(store2, "w1", profile)["not_measured"]          # honest about Google AI Overviews etc.


def test_runs_record_errors_and_exclude_them(tmp_path, profile):
    class Flaky(FakeProvider):
        def ask(self, prompt, profile):
            raise RuntimeError("boom")

    store = Store(tmp_path / "p.sqlite")
    res = run_probe(profile, [Flaky()], store, "w1", runs=1, budget=Budget(5))
    assert res["failed"] > 0 and res["completed"] == 0
    assert summarise(store, "w1", profile)["providers"] == {}


def test_compare_refuses_across_model_versions(tmp_path, profile):
    store = Store(tmp_path / "p.sqlite")
    run_probe(profile, [FakeProvider(model="m1")], store, "a", runs=2, budget=Budget(5))
    run_probe(profile, [FakeProvider(model="m2")], store, "b", runs=2, budget=Budget(5))
    assert "not comparable" in compare(store, "a", "b", "fake")["verdict"]


def test_estimate(profile):
    e = estimate(profile, [FakeProvider(cost_per_call=0.1)], runs=10)
    assert e["calls"] == e["prompts"] * 10 and e["estimated_cost_usd"] == round(e["calls"] * 0.1, 2)


class _Obj:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def test_openai_provider_parses_citations_and_sets_location(profile):
    seen = {}

    class R:
        def create(self, **kw):
            seen.update(kw)
            ann = _Obj(type="url_citation", url="https://www.yelp.com/biz/x")
            return _Obj(output_text="1. A", model="gpt-x-2026", output=[_Obj(type="message", content=[_Obj(annotations=[ann])])])

    r = OpenAIResponsesProvider(model="gpt-x", client=_Obj(responses=R())).ask("best dentist in Austin", profile)
    assert r.cited_urls == ["https://www.yelp.com/biz/x"] and r.model_version == "gpt-x-2026"
    assert seen["tools"][0]["user_location"]["city"] == "Austin"      # geo-targeting is mandatory for local


def test_perplexity_provider_location_and_citations(profile):
    seen = {}

    class C:
        def create(self, **kw):
            seen.update(kw)
            msg = _Obj(content="text")
            return _Obj(choices=[_Obj(message=msg)], model="sonar-x", model_extra={"citations": ["https://a.test/x"],
                        "search_results": [{"url": "https://b.test/y"}]})

    p = OpenAICompatProvider("perplexity", model="sonar", client=_Obj(chat=_Obj(completions=C())))
    r = p.ask("q", profile)
    assert r.cited_urls == ["https://b.test/y", "https://a.test/x"]            # search_results first, then citations
    assert seen["extra_body"]["web_search_options"]["user_location"]["city"] == "Austin"


def test_model_is_never_hardcoded(monkeypatch):
    monkeypatch.delenv("LSA_OPENAI_MODEL", raising=False)
    with pytest.raises(SystemExit):
        OpenAIResponsesProvider(model="", client=object())

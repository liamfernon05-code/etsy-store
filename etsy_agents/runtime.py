"""Agent loop, tools, and CEO delegation, built on the Anthropic SDK."""

import os
from pathlib import Path

import anthropic

from .agents import CEO, COMMON_RULES, SPECIALISTS, AgentSpec

MODEL = os.environ.get("ETSY_AGENTS_MODEL", "claude-sonnet-5-5")
ROOT = Path(os.environ.get("ETSY_AGENTS_HOME", Path.cwd())).resolve()
OUTPUT_DIR = ROOT / "outputs"
MAX_TURNS = 30

WEB_SEARCH = {"type": "web_search_20250305", "name": "web_search", "max_uses": 8}

FILE_TOOLS = [
    {
        "name": "read_file",
        "description": "Read a text file. Paths are relative to the project root (e.g. store_profile.md or outputs/...).",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
    {
        "name": "save_file",
        "description": "Save a deliverable (markdown) under outputs/. Path is relative to outputs/.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
            "required": ["path", "content"],
        },
    },
]

DELEGATE_TOOL = {
    "name": "delegate",
    "description": "Give a task to a specialist agent and get back their report. Available: "
    + "; ".join(f"{s.name} ({s.description})" for s in SPECIALISTS),
    "input_schema": {
        "type": "object",
        "properties": {
            "agent": {"type": "string", "enum": [s.name for s in SPECIALISTS]},
            "task": {"type": "string", "description": "Specific, self-contained instructions with any needed context."},
        },
        "required": ["agent", "task"],
    },
}


def _safe(base: Path, rel: str) -> Path:
    path = (base / rel).resolve()
    if base.resolve() not in path.parents and path != base.resolve():
        raise ValueError(f"path escapes {base}: {rel}")
    return path


def _run_file_tool(name: str, args: dict) -> str:
    try:
        if name == "read_file":
            return _safe(ROOT, args["path"]).read_text()[:50_000]
        path = _safe(OUTPUT_DIR, args["path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(args["content"])
        return f"saved {path.relative_to(ROOT)}"
    except Exception as e:  # report to the model so it can recover
        return f"error: {e}"


def run_agent(spec: AgentSpec, task: str, client: anthropic.Anthropic | None = None, verbose: bool = True) -> str:
    client = client or anthropic.Anthropic()
    is_ceo = spec is CEO
    tools = [WEB_SEARCH, *FILE_TOOLS] + ([DELEGATE_TOOL] if is_ceo else [])
    system = f"{spec.prompt}\n{COMMON_RULES}"
    messages = [{"role": "user", "content": task}]
    if verbose:
        print(f"\n[{spec.name}] working: {task[:100]}...")

    for _ in range(MAX_TURNS):
        resp = client.messages.create(
            model=MODEL, max_tokens=8000, system=system, tools=tools, messages=messages
        )
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason == "pause_turn":  # server-side search still running
            continue
        if resp.stop_reason != "tool_use":
            break
        results = []
        for block in resp.content:
            if block.type != "tool_use":
                continue
            if block.name == "delegate":
                by_name = {s.name: s for s in SPECIALISTS}
                out = run_agent(by_name[block.input["agent"]], block.input["task"], client, verbose)
            else:
                out = _run_file_tool(block.name, block.input)
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": out})
        messages.append({"role": "user", "content": results})

    text = "".join(b.text for b in resp.content if b.type == "text")
    if verbose:
        print(f"[{spec.name}] done")
    return text

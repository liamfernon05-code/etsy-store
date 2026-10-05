// End-to-end: real Worker runtime (wrangler dev, local KV) + mock Fish and GHL servers.
// Run: node test/e2e.mjs
import http from "node:http";
import { spawn } from "node:child_process";
import assert from "node:assert/strict";

const seen = [];
const mock = http.createServer((req, res) => {
  let b = ""; req.on("data", (c) => (b += c));
  req.on("end", () => {
    seen.push({ method: req.method, url: req.url, headers: req.headers, body: b ? JSON.parse(b) : null });
    res.setHeader("Content-Type", "application/json");
    res.end(JSON.stringify(req.url.includes("phone-calls") ? { id: "call_e2e_1" } : { ok: true }));
  });
});
await new Promise((r) => mock.listen(8799, r));

const W = 8788, base = `http://127.0.0.1:${W}`;
const vars = {
  FISH_API_KEY: "test-key", GHL_TOKEN: "test-ghl", LEAD_WEBHOOK_SECRET: "lead-s", FISH_WEBHOOK_SECRET: "fish-s",
  FISH_BASE_URL: "http://127.0.0.1:8799", GHL_BASE_URL: "http://127.0.0.1:8799",
  FISH_AGENT_ID: "agent_x", FISH_PHONE_NUMBER_ID: "num_x", DEFAULT_COUNTRY_CODE: "+61",
};
const args = ["wrangler", "dev", "--port", String(W), "--ip", "127.0.0.1", ...Object.entries(vars).flatMap(([k, v]) => ["--var", `${k}:${v}`])];
const proc = spawn("npx", args, { stdio: ["ignore", "pipe", "pipe"] });
let log = ""; proc.stdout.on("data", (d) => (log += d)); proc.stderr.on("data", (d) => (log += d));

try {
  for (let i = 0; i < 90; i++) {
    try { if ((await fetch(base + "/health")).ok) break; } catch {}
    if (i === 89) throw new Error("worker did not start:\n" + log.slice(-2000));
    await new Promise((r) => setTimeout(r, 1000));
  }
  const post = (path, body, secret) =>
    fetch(base + path, { method: "POST", headers: { "x-webhook-secret": secret, "content-type": "application/json" }, body: JSON.stringify(body) }).then(async (r) => [r.status, await r.json()]);

  const lead = { contact_id: "ghl_c1", first_name: "Liam", phone: "0412 345 678", customData: { enquiry: "SEO for my clinic", consent: "I agree to receive an AI phone call about my enquiry." } };

  let [s, j] = await post("/webhook/lead", lead, "wrong"); assert.equal(s, 401);
  [s, j] = await post("/webhook/lead", { ...lead, customData: { enquiry: "x" } }, "lead-s"); assert.equal(j.reason, "no consent");
  assert.equal(seen.length, 0, "no call without consent");

  [s, j] = await post("/webhook/lead", lead, "lead-s"); assert.deepEqual([s, j.status, j.callId], [200, "called", "call_e2e_1"]);
  const call = seen[0];
  assert.equal(call.url, "/v1/agent/phone-calls");
  assert.equal(call.headers.authorization, "Bearer test-key");
  assert.equal(call.headers["idempotency-key"], "lead-ghl_c1");
  assert.equal(call.body.to_number, "+61412345678");
  assert.deepEqual(call.body.dynamic_variables, { first_name: "Liam", enquiry: "SEO for my clinic" });

  [s, j] = await post("/webhook/lead", lead, "lead-s"); assert.equal(j.reason, "already called");
  assert.equal(seen.length, 1, "no second call");

  const evt = { type: "call.analyzed", data: { call_id: "call_e2e_1", summary: "Wants SEO, budget 2k, start next month", analysis: { extraction: { qualified: true } } } };
  [s, j] = await post("/webhook/fish", evt, "fish-s"); assert.deepEqual([s, j.status, j.contactId], [200, "written", "ghl_c1"]);
  assert.equal(seen[1].url, "/contacts/ghl_c1/notes");
  assert.equal(seen[1].headers.authorization, "Bearer test-ghl");
  assert.match(seen[1].body.body, /QUALIFIED[\s\S]*budget 2k/);
  assert.equal(seen[2].url, "/contacts/ghl_c1/tags");
  assert.deepEqual(seen[2].body, { tags: ["ai-qualified"] });

  [s, j] = await post("/webhook/fish", evt, "fish-s"); assert.equal(j.status, "duplicate");
  console.log("E2E PASS: consent gate, call placed once, write-back once, dedupe, auth");
} catch (e) {
  console.error("E2E FAIL:", e.message); process.exitCode = 1;
} finally {
  proc.kill("SIGTERM"); mock.close(); setTimeout(() => process.exit(process.exitCode ?? 0), 500);
}

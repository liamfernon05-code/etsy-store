import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.js";

function kv() {
  const m = new Map();
  return { get: async (k) => m.get(k) ?? null, put: async (k, v) => void m.set(k, v), m };
}
const env = () => ({
  FISH_API_KEY: "k", FISH_AGENT_ID: "agent1", FISH_PHONE_NUMBER_ID: "num1", DEFAULT_COUNTRY_CODE: "+61",
  GHL_TOKEN: "t", LEAD_WEBHOOK_SECRET: "s1", FISH_WEBHOOK_SECRET: "s2", LEADS: kv(),
});
const post = (path, body, secret) =>
  new Request("https://w.test" + path, { method: "POST", headers: { "x-webhook-secret": secret }, body: JSON.stringify(body) });
const lead = { contact_id: "c1", first_name: "Sam", phone: "0412 345 678", enquiry: "kitchen", consent: "yes" };

function stubFetch(handler) {
  const calls = [];
  globalThis.fetch = async (url, init) => { calls.push({ url, init }); return handler(url, init); };
  return calls;
}

test("rejects wrong secret", async () => {
  const res = await worker.fetch(post("/webhook/lead", lead, "bad"), env());
  assert.equal(res.status, 401);
});

test("no consent -> no call", async () => {
  const calls = stubFetch(() => new Response("{}"));
  const res = await worker.fetch(post("/webhook/lead", { ...lead, consent: "" }, "s1"), env());
  assert.equal((await res.json()).reason, "no consent");
  assert.equal(calls.length, 0);
});

test("places call with E.164, vars and idempotency key; dedupes", async () => {
  const e = env();
  const calls = stubFetch(() => new Response(JSON.stringify({ id: "call9" })));
  const res = await worker.fetch(post("/webhook/lead", lead, "s1"), e);
  assert.equal((await res.json()).status, "called");
  const body = JSON.parse(calls[0].init.body);
  assert.equal(body.to_number, "+61412345678");
  assert.deepEqual(body.dynamic_variables, { first_name: "Sam", enquiry: "kitchen" });
  assert.equal(calls[0].init.headers["Idempotency-Key"], "lead-c1");
  assert.equal(e.LEADS.m.get("call:call9"), "c1");
  const again = await worker.fetch(post("/webhook/lead", lead, "s1"), e);
  assert.equal((await again.json()).reason, "already called");
  assert.equal(calls.length, 1);
});

test("fish failure returns 502 and does not mark as called", async () => {
  const e = env();
  stubFetch(() => new Response("nope", { status: 409 }));
  const res = await worker.fetch(post("/webhook/lead", lead, "s1"), e);
  assert.equal(res.status, 502);
  assert.equal(e.LEADS.m.has("lead:c1"), false);
});

test("call.analyzed writes note + tag back, once", async () => {
  const e = env();
  await e.LEADS.put("call:call9", "c1");
  const calls = stubFetch(() => new Response("{}"));
  const evt = { type: "call.analyzed", data: { call_id: "call9", summary: "Wants kitchen reno", analysis: { extraction: { qualified: true } } } };
  const res = await worker.fetch(post("/webhook/fish", evt, "s2"), e);
  assert.equal((await res.json()).contactId, "c1");
  assert.ok(calls[0].url.endsWith("/contacts/c1/notes"));
  assert.match(JSON.parse(calls[0].init.body).body, /QUALIFIED[\s\S]*kitchen reno/);
  assert.deepEqual(JSON.parse(calls[1].init.body), { tags: ["ai-qualified"] });
  const dup = await worker.fetch(post("/webhook/fish", evt, "s2"), e);
  assert.equal((await dup.json()).status, "duplicate");
  assert.equal(calls.length, 2);
});

test("other fish events ignored", async () => {
  const res = await worker.fetch(post("/webhook/fish", { type: "call.started" }, "s2"), env());
  assert.equal((await res.json()).status, "ignored");
});

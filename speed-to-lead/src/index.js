import { hasConsent, parseLead, safeEqual, toE164 } from "./lib.js";
import { buildCallRequest, parseAnalyzedEvent, parseCallResponse } from "./fish.js";
import { writeBack } from "./ghl.js";

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), { status, headers: { "Content-Type": "application/json" } });

function authorised(request, secret) {
  if (!secret) return false; // refuse to run unauthenticated
  const given = request.headers.get("x-webhook-secret") ?? new URL(request.url).searchParams.get("secret");
  return safeEqual(given ?? "", secret);
}

async function handleLead(request, env) {
  if (!authorised(request, env.LEAD_WEBHOOK_SECRET)) return json({ error: "unauthorised" }, 401);

  let lead;
  try {
    lead = parseLead(await request.json(), env);
  } catch (e) {
    return json({ error: String(e.message ?? e) }, 400);
  }

  // Consent first: no tick box, no call, and no further processing.
  if (!hasConsent(lead.consent, env.CONSENT_VALUE)) return json({ status: "skipped", reason: "no consent" });

  const phone = toE164(lead.phone, env.DEFAULT_COUNTRY_CODE);
  if (!phone) return json({ status: "skipped", reason: "invalid phone" });

  if (await env.LEADS.get(`lead:${lead.contactId}`)) return json({ status: "skipped", reason: "already called" });

  const { url, init } = buildCallRequest(env, lead, phone);
  const res = await fetch(url, init);
  if (!res.ok) {
    // 502 so GoHighLevel retries; the Idempotency-Key makes a retry safe.
    console.error("fish call failed", res.status, (await res.text()).slice(0, 300));
    return json({ error: "call failed", status: res.status }, 502);
  }
  const { callId } = parseCallResponse(await res.json().catch(() => ({})));
  await env.LEADS.put(`lead:${lead.contactId}`, callId ?? "placed", { expirationTtl: 60 * 60 * 24 * 30 });
  if (callId) await env.LEADS.put(`call:${callId}`, lead.contactId, { expirationTtl: 60 * 60 * 24 * 30 });
  return json({ status: "called", callId });
}

async function handleFish(request, env) {
  if (!authorised(request, env.FISH_WEBHOOK_SECRET)) return json({ error: "unauthorised" }, 401);

  const event = parseAnalyzedEvent(await request.json().catch(() => null));
  if (!event) return json({ status: "ignored" });

  if (event.callId && (await env.LEADS.get(`done:${event.callId}`))) return json({ status: "duplicate" });
  const contactId = event.contactId ?? (event.callId ? await env.LEADS.get(`call:${event.callId}`) : null);
  if (!contactId) return json({ error: "cannot match call to a contact" }, 422);

  try {
    await writeBack(env, contactId, event);
  } catch (e) {
    console.error(String(e));
    return json({ error: "crm write failed" }, 502);
  }
  if (event.callId) await env.LEADS.put(`done:${event.callId}`, "1", { expirationTtl: 60 * 60 * 24 * 30 });
  return json({ status: "written", contactId });
}

export default {
  async fetch(request, env) {
    const { pathname } = new URL(request.url);
    if (request.method === "POST" && pathname === "/webhook/lead") return handleLead(request, env);
    if (request.method === "POST" && pathname === "/webhook/fish") return handleFish(request, env);
    if (pathname === "/health") return json({ ok: true });
    return json({ error: "not found" }, 404);
  },
};

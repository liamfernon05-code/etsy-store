// ALL Fish Audio request/response shapes live in this file.
//
// UNVERIFIED: this was written without access to docs.fish.audio. The endpoint
// (POST /v1/agent/phone-calls), the Idempotency-Key header and the call.analyzed
// event name come from the guide; the JSON field names below are best guesses.
// Check them against
//   https://docs.fish.audio/agents/telephony/outbound-calls
//   https://docs.fish.audio/agents/monitor/webhooks
//   https://docs.fish.audio/agents/monitor/post-call-analysis
// and edit ONLY this file if any differ. Tests in test/ pin the current shapes.

import { findKey, toBool } from "./lib.js";

const BASE = "https://api.fish.audio";

export function buildCallRequest(env, lead, phoneE164) {
  return {
    url: `${BASE}/v1/agent/phone-calls`,
    init: {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.FISH_API_KEY}`,
        "Content-Type": "application/json",
        "Idempotency-Key": `lead-${lead.contactId}`,
      },
      body: JSON.stringify({
        agent_id: env.FISH_AGENT_ID,
        phone_number_id: env.FISH_PHONE_NUMBER_ID,
        to_number: phoneE164,
        dynamic_variables: { first_name: lead.firstName, enquiry: lead.enquiry },
        metadata: { contact_id: lead.contactId },
      }),
    },
  };
}

export function parseCallResponse(json) {
  return { callId: json?.id ?? json?.call_id ?? json?.phone_call_id ?? null };
}

/** Returns null for events we don't act on. */
export function parseAnalyzedEvent(body) {
  const type = body?.type ?? body?.event;
  if (type !== "call.analyzed") return null;
  const data = body?.data ?? body;
  const q = findKey(data, "qualified");
  return {
    callId: data?.call_id ?? data?.id ?? findKey(data, "call_id") ?? null,
    contactId: findKey(data?.metadata ?? {}, "contact_id") ?? null,
    summary: findKey(data, "summary") ?? null,
    qualified: q === undefined ? null : toBool(q),
  };
}

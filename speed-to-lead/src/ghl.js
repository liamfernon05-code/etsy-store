// GoHighLevel (LeadConnector API v2) write-back. Auth is a Private Integration token.
const BASE = "https://services.leadconnectorhq.com";

function headers(env) {
  return {
    Authorization: `Bearer ${env.GHL_TOKEN}`,
    Version: "2021-07-28",
    Accept: "application/json",
    "Content-Type": "application/json",
  };
}

async function call(env, method, path, body) {
  const res = await fetch(BASE + path, { method, headers: headers(env), body: JSON.stringify(body) });
  if (!res.ok) throw new Error(`GHL ${method} ${path} -> ${res.status} ${(await res.text()).slice(0, 200)}`);
}

/** Add the call summary as a note, tag the outcome, and optionally set a custom field. */
export async function writeBack(env, contactId, { summary, qualified }) {
  const verdict = qualified === null ? "not determined" : qualified ? "QUALIFIED" : "not qualified";
  const note = `AI call summary (${verdict})\n\n${summary ?? "No summary returned."}`;
  await call(env, "POST", `/contacts/${contactId}/notes`, { body: note });
  const tag = qualified === null ? "ai-call-unscored" : qualified ? "ai-qualified" : "ai-not-qualified";
  await call(env, "POST", `/contacts/${contactId}/tags`, { tags: [tag] });
  if (env.GHL_QUALIFIED_FIELD_ID && qualified !== null) {
    await call(env, "PUT", `/contacts/${contactId}`, {
      customFields: [{ id: env.GHL_QUALIFIED_FIELD_ID, field_value: qualified ? "Yes" : "No" }],
    });
  }
}

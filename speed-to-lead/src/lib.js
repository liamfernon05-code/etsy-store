// Pure helpers: no network, no Worker APIs, so they can be unit tested directly.

const E164 = /^\+[1-9]\d{7,14}$/;

/** Convert a phone number to E.164, or return null if it can't be made valid. */
export function toE164(raw, defaultCountryCode = "") {
  if (raw == null) return null;
  const text = String(raw).trim();
  const digits = text.replace(/\D/g, "");
  if (!digits) return null;
  const cc = String(defaultCountryCode).replace(/\D/g, "");

  let out;
  if (text.startsWith("+")) out = "+" + digits;
  else if (digits.startsWith("00")) out = "+" + digits.slice(2);
  else if (cc && digits.startsWith("0")) out = "+" + cc + digits.slice(1);
  else if (cc && digits.startsWith(cc) && digits.length >= 11) out = "+" + digits;
  else if (cc) out = "+" + cc + digits;
  else return null;

  if (!E164.test(out)) return null;
  // US/Canada (+1) numbers are exactly 10 digits after the country code and the
  // area code can't start with 0 or 1; anything else would be a dud dial.
  if (out.startsWith("+1") && !/^\+1[2-9]\d{9}$/.test(out)) return null;
  return out;
}

const YES = new Set(["true", "yes", "y", "on", "1", "checked", "agree", "agreed", "consent", "i agree"]);

/** True only for an explicit, positive consent value. Missing or unknown means no. */
export function hasConsent(value, customLabel = "") {
  if (value === true) return true;
  if (Array.isArray(value)) return value.some((v) => hasConsent(v, customLabel));
  if (typeof value !== "string") return false;
  const v = value.trim().toLowerCase();
  if (!v) return false;
  if (YES.has(v) || v.startsWith("i agree")) return true;
  return Boolean(customLabel) && v === customLabel.trim().toLowerCase();
}

// GoHighLevel custom-webhook bodies carry contact fields at the top level and
// workflow "custom data" under customData. Look in both.
function pick(body, keys) {
  for (const scope of [body, body?.customData, body?.contact]) {
    if (!scope || typeof scope !== "object") continue;
    for (const k of keys) {
      const v = scope[k];
      if (v !== undefined && v !== null && v !== "") return v;
    }
  }
  return undefined;
}

/** Normalise a GHL new-lead webhook body. Throws on a body we cannot use. */
export function parseLead(body, env = {}) {
  const contactId = pick(body, ["contact_id", "contactId", "id"]);
  const full = pick(body, ["full_name", "fullName", "name"]);
  const firstName = pick(body, ["first_name", "firstName"]) ?? (full ? String(full).trim().split(/\s+/)[0] : undefined);
  const phone = pick(body, ["phone", "phone_number", "phoneNumber"]);
  const enquiry = pick(body, [env.ENQUIRY_FIELD || "enquiry", "enquiry", "message"]);
  const consent = pick(body, [env.CONSENT_FIELD || "consent", "consent"]);

  if (!contactId) throw new Error("missing contact id (contact_id)");
  return {
    contactId: String(contactId),
    firstName: firstName ? String(firstName) : "there",
    phone,
    enquiry: enquiry ? String(enquiry) : "your enquiry",
    consent,
  };
}

/** Constant-time-ish string comparison for shared secrets. */
export function safeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

// Depth-limited search so we tolerate Fish Audio nesting extraction results
// a level or two deeper than expected.
export function findKey(obj, key, depth = 4) {
  if (!obj || typeof obj !== "object" || depth < 0) return undefined;
  if (key in obj && obj[key] !== undefined && obj[key] !== null) return obj[key];
  for (const v of Object.values(obj)) {
    const hit = findKey(v, key, depth - 1);
    if (hit !== undefined) return hit;
  }
  return undefined;
}

export function toBool(v) {
  if (typeof v === "boolean") return v;
  if (typeof v === "string") return ["true", "yes", "y", "1"].includes(v.trim().toLowerCase());
  return false;
}

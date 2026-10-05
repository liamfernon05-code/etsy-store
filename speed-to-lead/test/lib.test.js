import test from "node:test";
import assert from "node:assert/strict";
import { toE164, hasConsent, parseLead } from "../src/lib.js";

test("toE164 handles AU formats", () => {
  assert.equal(toE164("0412 345 678", "+61"), "+61412345678");
  assert.equal(toE164("+61 412 345 678", "+61"), "+61412345678");
  assert.equal(toE164("61412345678", "+61"), "+61412345678");
  assert.equal(toE164("0061412345678", "+61"), "+61412345678");
  assert.equal(toE164("412345678", "+61"), "+61412345678");
});
test("toE164 handles US formats", () => {
  assert.equal(toE164("(734) 212-2691", "+1"), "+17342122691");
  assert.equal(toE164("734.212.2691", "+1"), "+17342122691");
  assert.equal(toE164("1 734 212 2691", "+1"), "+17342122691");
  assert.equal(toE164("+1 734 212 2691", "+1"), "+17342122691");
  assert.equal(toE164("212 2691", "+1"), null); // 7 digits is too short
});
test("toE164 rejects junk", () => {
  assert.equal(toE164("", "+61"), null);
  assert.equal(toE164("abc", "+61"), null);
  assert.equal(toE164("123", "+61"), null);
  assert.equal(toE164("0412345678", ""), null);
});
test("consent is opt-in only", () => {
  for (const v of [true, "true", "Yes", "I agree to receive an AI phone call about my enquiry.", ["I agree"]]) assert.equal(hasConsent(v), true, String(v));
  for (const v of [undefined, null, "", "false", "no", false, [], "maybe"]) assert.equal(hasConsent(v), false, String(v));
  assert.equal(hasConsent("Call me please", "call me please"), true);
});
test("parseLead reads top level and customData", () => {
  const l = parseLead({ contact_id: "c1", full_name: "Sam Lee", phone: "0412", customData: { enquiry: "kitchen", consent: "yes" } });
  assert.deepEqual([l.contactId, l.firstName, l.enquiry, l.consent], ["c1", "Sam", "kitchen", "yes"]);
  assert.throws(() => parseLead({ phone: "1" }));
});

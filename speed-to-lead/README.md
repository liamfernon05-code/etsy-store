# speed-to-lead

GoHighLevel new lead -> Fish Audio AI call within a minute -> summary and qualified flag written back to the GHL contact. A Cloudflare Worker (free plan is enough).

```
GHL form -> workflow "Custom Webhook" -> POST /webhook/lead -> Fish Audio call
Fish Audio call.analyzed -> POST /webhook/fish -> GHL note + tag (+ optional custom field)
```

## Status

- Offline tests pass (`npm test`): phone formatting, consent gate, idempotency, dedupe, write-back.
- **Fish Audio JSON field names are unverified** (docs were not reachable when this was written). Check `src/fish.js` against the three Fish docs pages linked in that file's header before going live. It is the only file that knows Fish's shapes.
- Not yet deployed or tested against a real call.

## Phone number

Leads are in the US, so `DEFAULT_COUNTRY_CODE` is `+1`. A number bought inside GHL (LC Phone) may not expose SIP credentials for importing into Fish (unverified): to start, buy a US number in Fish ($1.20 a month) and use its `phone_number_id`. Importing your own GHL/Twilio number later changes only that id in `wrangler.toml`.

## Before you deploy (from the guide)

1. Outbound calling enabled for your Fish workspace (ask support; do this first).
2. Agent built and **published**; Hang up call tool on; Analysis page has a yes/no `qualified` field. Agent instructions are in the guide, with `{{owner_name}}` and `{{offer}}` defaults set on the agent.
3. A phone number bought or imported. Note the **agent id** and **phone number id**.
4. Consent checkbox on your GHL form, e.g. "I agree to receive an AI phone call about my enquiry."

## Deploy

```bash
cd speed-to-lead && npm install
npx wrangler login
npx wrangler kv namespace create LEADS      # paste the printed id into wrangler.toml
# edit wrangler.toml: FISH_AGENT_ID, FISH_PHONE_NUMBER_ID, DEFAULT_COUNTRY_CODE, field names

npx wrangler secret put FISH_API_KEY         # paste when prompted, never in code or chat
npx wrangler secret put GHL_TOKEN            # GHL Private Integration token (below)
npx wrangler secret put LEAD_WEBHOOK_SECRET  # any long random string
npx wrangler secret put FISH_WEBHOOK_SECRET  # another long random string
npx wrangler deploy                          # prints https://speed-to-lead.<you>.workers.dev
```

## GoHighLevel setup

**Private Integration token** (Settings > Private Integrations > Create): scopes `contacts.write` (and `contacts.readonly`). Copy the token into `GHL_TOKEN`.

**Workflow** (Automation > Workflows), trigger "Form Submitted" for your form, then:
1. Optional If/Else: continue only if the consent field is not empty.
2. Action **Custom Webhook**, method POST, URL `https://speed-to-lead.<you>.workers.dev/webhook/lead`, header `x-webhook-secret: <LEAD_WEBHOOK_SECRET>`.
3. Custom data (key -> value): `enquiry` -> your enquiry/message field, `consent` -> your consent checkbox field. Keys must match `ENQUIRY_FIELD` / `CONSENT_FIELD` in `wrangler.toml`. GHL already sends `contact_id`, `first_name` and `phone`.

The connector re-checks consent itself: a missing, empty or unrecognised value means no call. If your checkbox label does not start with "I agree", set `CONSENT_VALUE` to the exact label.

**Fish Audio webhook**: in the Fish Audio webhooks settings add `https://speed-to-lead.<you>.workers.dev/webhook/fish?secret=<FISH_WEBHOOK_SECRET>` for `call.analyzed`. (Fish's own signature scheme is not implemented because it was not documented where I could read it; the shared secret in the URL is the guard.)

Results appear on the contact as a note, plus tag `ai-qualified` / `ai-not-qualified` / `ai-call-unscored`. Set `GHL_QUALIFIED_FIELD_ID` to also fill a custom field.

## Verify (guide step 4)

Submit a real test lead with your own mobile and the box ticked, then check: phone rings in ~1 minute; it says your name (not `first_name` or `{{...}}`); it hangs up on its own; transcript has a `qualified` value; the note lands on the contact; and **close your laptop and test again**.

Logs while testing: `npx wrangler tail`.

## Compliance

US leads: prior express written consent kept (the form record, per the FCC's 2024 ruling on AI voices under the TCPA), AI disclosed in the first sentence, recording disclosed (some states need all-party consent), National Do Not Call Registry and state calling-hour rules checked (federal: 8am to 9pm in the lead's local time). Read the first few dozen transcripts before trusting `qualified`.

# Etsy Print-on-Demand AI Team

A team of AI agents (built on the Claude API) that runs a **print-on-demand Etsy store** for you. A **CEO agent**
takes a goal, delegates to specialists, and hands you finished drafts to approve.

| Agent | Job |
|---|---|
| `ceo` | Plans, delegates, reviews, reports |
| `product_researcher` | Finds winning POD niches/products (demand, competition, pricing, seasonality) |
| `pod_specialist` | Picks Printful/Printify/Gelato + blanks, unit economics, print-file specs |
| `designer` | Original design collections, slogans (IP-checked), AI image prompts, mockup plans |
| `listing_writer` | SEO titles, 13 tags, descriptions, photo plans |
| `marketing_manager` | Brand, Pinterest/Instagram/TikTok/email/Etsy Ads plans and content |
| `customer_service` | Drafts replies to messages, reviews, defects, returns |
| `finance_analyst` | Margins, fees, ad break-even, P&L, what to scale/retire |

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
# edit store_profile.md with your niche, budget and policies
```

## Use

```bash
python -m etsy_agents agents                     # list the team
python -m etsy_agents launch                     # CEO plans a full store launch
python -m etsy_agents weekly                     # weekly routine
python -m etsy_agents ask "Design a 6-shirt collection for nurses"
python -m etsy_agents run designer "Create 5 designs for the dog-mom niche"
python -m etsy_agents run customer_service "Buyer says her mug arrived chipped. Draft a reply."
```

All deliverables are written to `outputs/` (git-ignored). Set `ETSY_AGENTS_MODEL` to change the model.

## Print-on-demand rules that matter

- **IP is the top cause of suspensions.** No brands, characters, celebrities, lyrics, or teams. Agents check
  slogans against the USPTO trademark database and flag risk, but you make the final call.
- **Disclose your production partner** on Etsy, and disclose AI-generated design work where Etsy requires it.
- **Order samples** of your top products before launching to check print quality.
- Plan seasonal products early (Q4 gift shopping starts in late summer).
- Agents only produce **drafts**. They never publish listings, post to social, spend on ads, or message
  customers. You review and approve everything.

## Roadmap (Phase 2)

1. Etsy Open API v3 integration (create draft listings, read orders/stats) after you register an Etsy app.
2. Printful/Printify API tools to upload designs, create products and fetch live costs.
3. Image generation tools for designs and mockups.
4. Scheduled runs (cron/GitHub Actions) for the weekly routine.

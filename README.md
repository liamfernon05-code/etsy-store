# Etsy Store AI Team

A team of AI agents (built on the Claude API) that runs an Etsy store for you. A **CEO agent** takes a goal,
delegates to specialists, and hands you finished drafts to approve.

| Agent | Job |
|---|---|
| `ceo` | Plans, delegates, reviews, reports |
| `product_researcher` | Finds winning niches/products (demand, competition, pricing, trends) |
| `sourcing_specialist` | Finds POD / dropship / production partners, computes unit economics |
| `listing_writer` | SEO titles, 13 tags, descriptions, photo/mockup plans |
| `marketing_manager` | Brand, Pinterest/Instagram/TikTok/email/Etsy Ads plans and content |
| `customer_service` | Drafts replies to messages, reviews, returns |
| `finance_analyst` | Margins, fees, ad break-even, P&L, what to scale/kill |

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
python -m etsy_agents ask "Find 5 wedding-gift products under $40"
python -m etsy_agents run customer_service "Buyer says her mug arrived chipped. Draft a reply."
```

All deliverables are written to `outputs/` (git-ignored). Set `ETSY_AGENTS_MODEL` to change the model.

## Important: Etsy rules and safety

- Etsy does **not** allow reselling generic mass-produced goods. The team is built around print-on-demand,
  production partners you disclose, and digital downloads. Always verify current Etsy policy.
- Agents only produce **drafts**. They never publish listings, post to social, spend on ads, or message
  customers. You review and click go. That's deliberate: you're on the hook for the shop.

## Roadmap (Phase 2)

1. Etsy Open API v3 integration (create draft listings, read orders/stats) after you register an Etsy app.
2. Printful/Printify API tools to push designs and fetch live costs.
3. Scheduled runs (cron/GitHub Actions) for the weekly routine.
4. Image generation for mockups and designs.

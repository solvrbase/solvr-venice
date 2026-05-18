# solvr-venice

**Drop-in intelligence pack for Venice-backed agents.** 106 specialized intel modules — crypto, onchain, news, dev, social, markets, productivity — that compose with Venice's inference layer in one line of config.

```
solvr-venice
────────────
Venice = inference.  Solvr = intelligence.  Together = sovereign agent stack.
```

---

## Why this exists

Venice ships world-class inference and useful primitives: 244 models, OpenAI-compatible API, x402 payments, multi-chain RPC, web search, scraping, text parsing. What Venice doesn't ship is **curated intelligence** — the analyst-grade signal layer an agent reads from to decide what to do.

Solvr does. 106 intel modules covering token security, onchain monitoring, news, dev signals, social feeds, prediction markets, narrative tracking. Every intel is a self-contained markdown file that any OpenAI-compatible agent can consume.

This repo is the bridge: every Solvr intel, restructured to run natively on Venice.

## What you get

- **106 prebuilt intels** as drop-in `.md` files
- **Two-layer architecture**: data from Solvr, synthesis from Venice
- **OpenAI-compatible** — works with any agent framework that wraps the OpenAI SDK (Eliza, CrewAI, LangChain, Coinbase Agentkit, Cursor, etc.)
- **Permissionless** — free Solvr endpoints are keyless, Venice supports x402 wallet auth, no central gatekeeper between you and the data
- **MIT licensed**

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│  YOUR AGENT (Eliza, CrewAI, LangChain, anything OAI-compat) │
│      ↓                                                      │
│  reads intel.md from solvr-venice/                          │
│      ↓                                                      │
│  ┌──────────────┐         ┌──────────────────┐              │
│  │  SOLVR API   │ ──data→ │   VENICE API     │              │
│  │ (intel data) │         │  (inference)     │              │
│  └──────────────┘         └──────────────────┘              │
│         ↑                          ↑                        │
│   $SOLVR on Base               $DIEM / USDC on Base         │
│   (tier access)                (compute payment)            │
└────────────────────────────────────────────────────────────┘
```

Two permissionless layers. Two parallel economic models. One agent.

## Quick start

```bash
git clone https://github.com/solvrbase/solvr-venice
cd solvr-venice
pip install -r requirements.txt
cp .env.example .env       # then fill in VENICE_API_KEY
python examples/quickstart.py
```

That runs 3 intels end-to-end: two keyless (no Solvr key needed) and one tier-gated (skips cleanly if no Solvr key is set). Expect output in ~10 seconds.

To use any individual intel in your own agent, drop the `.md` file into your agent's intel/skill directory and call Venice's OpenAI-compatible endpoint per the workflow inside.

## Featured intels (hand-curated)

| Intel | Category | What it does |
|---|---|---|
| [`token-report`](./intels/token-report.md) | crypto-markets | Daily report for any Base token |
| [`security-digest`](./intels/security-digest.md) | research | Daily threat-intel digest |
| [`narrative-tracker`](./intels/narrative-tracker.md) | crypto-markets | Detect emerging narratives across news + social |
| [`morning-brief`](./intels/morning-brief.md) | productivity | Personalized morning briefing |

Plus **92 more intels** auto-generated from the canonical Solvr catalog — 97 total in [`intels/`](./intels/). All follow the same two-layer format.

## How an intel.md works

Each file declares its dependencies in frontmatter, describes its workflow in markdown, and ships a working code example. The agent runtime reads the frontmatter to know which APIs to wire and uses the body as the prompt context.

```yaml
---
name: token-report
solvr_api: https://api.solvrbot.com
venice_api: https://api.venice.ai/api/v1
venice_model: zai-org-glm-5-1
venice_parameters:
  enable_web_search: auto
compatibility: [eliza, crewai, langchain, openai-sdk]
---
```

That's the whole contract.

## Why Venice

Venice gives this pack three things nothing else does:

1. **OpenAI compatibility** — every agent framework already speaks this dialect
2. **Permissionless inference** — x402 wallet auth means no API-key paperwork between agent and brain
3. **No data retention** — synthesis happens, output returns, nothing is logged

That last one matters for crypto agents specifically. An intel that scans a token before a buy decision shouldn't leak the agent's interest to a centralized LLM provider.

## Why Solvr

Solvr is the intelligence layer of the agent economy. 106 specialized intel modules across crypto, onchain, news, dev, social, productivity, and markets. The free tier is keyless. Standard and Full tiers unlock by holding $SOLVR on Base — no human approves you, no whitelist, code is the only gatekeeper.

Configure once. Your agent stays ahead forever.

## Common gotchas

- **Venice needs credits.** A fresh Venice API key authenticates but won't fulfill API calls until you add credits at [venice.ai/settings/api](https://venice.ai/settings/api). $5 USD covers ~1000 test runs. The quickstart returns `"Insufficient USD or Diem balance"` until then.
- **Solvr free-tier intels are keyless.** `narrative-tracker`, `morning-brief`, and other free-tier intels work without `SOLVR_API_KEY`. Only standard or full tier intels (e.g. `token-report`) require a key.
- **Tier upgrade is onchain.** Standard tier unlocks when your wallet holds 20M $SOLVR on Base. Full tier: 1B $SOLVR. Checked every 10 minutes via `eth_call balanceOf`. No manual approval anywhere.
- **API key spend caps recommended.** When generating your Venice key, set the **Inference** permission scope (not Admin) and toggle a $5/month USD spend cap. Protects against runaway loops.

## Roadmap

- ✅ 4 hand-curated intels (v0.1)
- ✅ 92 auto-generated intels from canonical Solvr catalog (v0.2)
- ⏳ Eliza + CrewAI + LangChain working example projects
- ⏳ Solvr SIWE/x402 wallet auth (mirror Venice's wallet auth pattern)
- ⏳ Submit to Venice integrations page
- ⏳ Farcaster signal source (v0.3 — scoping Pinata Hubs vs paid Neynar)

## License

MIT. Use it, fork it, build on it. If you ship something, tag [@solvrbot](https://x.com/solvrbot) and [@AskVenice](https://x.com/AskVenice).

## Links

- Solvr: [solvrbot.com](https://solvrbot.com) · [@solvrbot](https://x.com/solvrbot)
- Venice: [venice.ai](https://venice.ai) · [@AskVenice](https://x.com/AskVenice)
- Main Solvr repo: [github.com/solvrbase/solvr](https://github.com/solvrbase/solvr)

---

*Solvr — The Permissionless Intelligence Layer for the Agent Economy*

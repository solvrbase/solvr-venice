---
name: narrative-tracker
description: Detect emerging crypto narratives by aggregating news + trending tokens + social signal. Solvr collects the signal, Venice extracts the narrative.
category: crypto-markets
tier: free
source: https://github.com/solvrbase/solvr-venice
solvr_api: https://api.solvrbot.com
venice_api: https://api.venice.ai/api/v1
venice_model: zai-org-glm-5-1
venice_alt_models: [venice-uncensored, kimi-k2-5]
venice_parameters:
  enable_web_search: auto
compatibility: [eliza, crewai, langchain, openai-sdk, coinbase-agentkit, any-openai-compatible]
---

# Narrative Tracker

Detect what's actually being talked about in crypto right now, before it's an obvious trade. Solvr aggregates news, trending tokens, and Farcaster signal. Venice extracts the underlying narrative threads and ranks them by emergence strength. Fully keyless on Solvr's free tier — Venice charges for inference only.

## Two layers, one workflow

| Layer | Provider | What it does |
|---|---|---|
| Data | Solvr (free tier, keyless) | `/news` + `/dex/trending` + `/farcaster` — raw narrative signal |
| Inference | Venice | `/chat/completions` with `zai-org-glm-5-1` — narrative extraction + ranking |

## Endpoints

- `GET https://api.solvrbot.com/api/v1/news?limit=20` — news headlines across categories (keyless)
- `GET https://api.solvrbot.com/api/v1/dex/trending` — trending tokens on Base (keyless)
- `GET https://api.solvrbot.com/api/v1/farcaster?limit=20` — trending Farcaster casts (keyless)
- `POST https://api.venice.ai/api/v1/chat/completions` — narrative extraction (Venice)

## Workflow

1. Fetch news, trending tokens, and Farcaster casts from Solvr (all keyless — no API key needed).
2. Pass the combined corpus to Venice with narrative-detection instructions.
3. Venice clusters mentions, extracts narrative threads, and ranks by emergence strength (how fresh + how cross-source).
4. Output: top 5 narratives with one-line description, supporting tickers/projects, and a freshness score (0-100).

## Output format

```
Top 5 emerging narratives — <date>

1. <NARRATIVE NAME>                         freshness: 87/100
   <one-line description>
   tickers: $X $Y $Z
   sources: <count> news, <count> casts, <count> trending tokens

2. <NARRATIVE NAME>                         freshness: 72/100
   ...

(etc)

Watch: <narratives at freshness 40-60 — earlier signal>
```

## Python (OpenAI SDK pointed at Venice)

```python
import os, requests
from openai import OpenAI

# No Solvr API key needed — these are keyless free-tier endpoints
SOLVR = "https://api.solvrbot.com"
venice = OpenAI(
    api_key=os.environ["VENICE_API_KEY"],
    base_url="https://api.venice.ai/api/v1",
)

def narrative_tracker() -> str:
    news     = requests.get(f"{SOLVR}/api/v1/news", params={"limit": 20}).json()
    trending = requests.get(f"{SOLVR}/api/v1/dex/trending").json()
    casts    = requests.get(f"{SOLVR}/api/v1/farcaster", params={"limit": 20}).json()

    r = venice.chat.completions.create(
        model="zai-org-glm-5-1",
        messages=[
            {"role": "system", "content": (
                "You are a crypto narrative analyst. Cluster the inputs into narrative threads. "
                "Rank by emergence strength: how fresh (last 24h weighted higher) and how "
                "cross-source (mentions in news + Farcaster + trending tokens weighted higher than "
                "single-source). Output top 5 with freshness score 0-100."
            )},
            {"role": "user", "content": (
                f"news: {news}\n\ntrending tokens: {trending}\n\nfarcaster casts: {casts}"
            )},
        ],
        extra_body={"venice_parameters": {"enable_web_search": "auto"}},
    )
    return r.choices[0].message.content
```

## Auth modes

| Solvr | Venice |
|---|---|
| **Keyless** — no auth needed for news/dex/farcaster | Bearer API key OR `X-Sign-In-With-X` + USDC on Base (x402) |

**Fully permissionless variant**: This entire intel runs without a Solvr API key. Pair with Venice's x402 wallet auth and the whole stack runs on wallet signatures + USDC. No accounts. No keys. Just hold a wallet.

## Customize

- Increase `limit` on news/farcaster to expand the corpus (up to 50 each).
- Add `topic` filter to `/news` to scope to a vertical: `"DeFi"`, `"AI agents"`, `"prediction markets"`, etc.
- Swap `venice_model` to `venice-uncensored` for unfiltered narrative analysis (useful for sensitive or controversial threads).
- Schedule every 4-6 hours for live narrative tracking, or daily for the morning digest version.

## Why this is the cheapest intel in the pack

Solvr's free tier is keyless — no payment of any kind for the data layer. Venice charges per LLM call (typically < $0.001 with `kimi-k2-5`). Total cost per run: cents. Run this every hour for narrative drift detection.

---
name: morning-brief
description: Personalized morning briefing — news, markets, macro, priorities. Solvr supplies the world data, Venice writes the brief.
category: productivity
tier: free
source: https://github.com/solvrbase/solvr-venice
solvr_api: https://api.solvrbot.com
venice_api: https://api.venice.ai/api/v1
venice_model: zai-org-glm-5-1
venice_alt_models: [kimi-k2-5, venice-uncensored]
venice_parameters:
  enable_web_search: auto
compatibility: [eliza, crewai, langchain, openai-sdk, coinbase-agentkit, any-openai-compatible]
---

# Morning Brief

Wake-up briefing your agent generates daily. Pulls overnight news, macro indicators, crypto market snapshot, and renders a one-page brief calibrated to your domain. Fully keyless on Solvr (free tier) — works without any API key on the data side.

## Two layers, one workflow

| Layer | Provider | What it does |
|---|---|---|
| Data | Solvr (free tier, keyless) | `/news` + `/worlddata` + `/dex/trending` — overnight signal |
| Inference | Venice | `/chat/completions` — write the brief |

## Endpoints

- `GET https://api.solvrbot.com/api/v1/news?limit=15&category={category}` — top news (keyless)
- `GET https://api.solvrbot.com/api/v1/worlddata?query={macro_indicator}` — macro/economic data (keyless, 180+ countries via FRED + World Bank)
- `GET https://api.solvrbot.com/api/v1/dex/trending` — trending tokens snapshot (keyless)
- `POST https://api.venice.ai/api/v1/chat/completions` — brief synthesis (Venice)

## Workflow

1. Fetch overnight news (default: `general` + `business` + `tech`).
2. Fetch 2-3 macro indicators (default: `fed rate`, `s&p 500`, `vix`).
3. Fetch DEX trending snapshot.
4. Pass everything to Venice with the brief prompt + your personalization (focus areas, role, time horizon).
5. Venice writes the brief in the requested format.

## Output format

```
☕ Morning Brief — <date>

OVERNIGHT
- <headline>: <one-line context>
- <headline>: <context>
- <headline>: <context>

MACRO
- Fed rate: <value> (<change>)
- S&P 500: <value> (<change>)
- VIX: <value> (<change>)
- <user's watched indicators>

CRYPTO
- BTC: <price> (<24h>%)
- Top mover: $<symbol> (<change>%)
- Trending narrative: <one-line>

YOUR PRIORITIES
- <inferred from context + user focus areas>
```

## Python (OpenAI SDK pointed at Venice)

```python
import os, requests
from openai import OpenAI

# Keyless on Solvr free tier
SOLVR = "https://api.solvrbot.com"
venice = OpenAI(
    api_key=os.environ["VENICE_API_KEY"],
    base_url="https://api.venice.ai/api/v1",
)

USER_PROFILE = {
    "role": "founder of a permissionless intelligence project on Base",
    "focus": ["onchain narratives", "AI agent infra", "Base ecosystem"],
    "watch_macro": ["fed rate", "vix", "s&p 500"],
}

def morning_brief() -> str:
    news = []
    for cat in ["general", "business", "tech"]:
        news.append(requests.get(f"{SOLVR}/api/v1/news",
                                  params={"category": cat, "limit": 5}).json())

    macro = {ind: requests.get(f"{SOLVR}/api/v1/worlddata",
                                params={"query": ind}).json()
             for ind in USER_PROFILE["watch_macro"]}

    trending = requests.get(f"{SOLVR}/api/v1/dex/trending").json()

    r = venice.chat.completions.create(
        model="zai-org-glm-5-1",
        messages=[
            {"role": "system", "content": (
                "You are an executive analyst writing a morning brief. "
                "Calibrate every item to the user's role and focus areas. "
                "Be punchy. No filler. Three bullets per section max."
            )},
            {"role": "user", "content": (
                f"user_profile: {USER_PROFILE}\n\n"
                f"news: {news}\n\nmacro: {macro}\n\ntrending: {trending}"
            )},
        ],
        extra_body={"venice_parameters": {"enable_web_search": "auto"}},
    )
    return r.choices[0].message.content
```

## Auth modes

| Solvr | Venice |
|---|---|
| **Keyless** — all endpoints used here are free tier | Bearer API key OR `X-Sign-In-With-X` + USDC on Base (x402) |

**Fully permissionless variant**: Same as `narrative-tracker` — this runs without any Solvr key. Combine with Venice's wallet auth for a fully wallet-only agent stack.

## Customize

- **Focus areas**: edit `USER_PROFILE.focus` — the brief will skew toward those topics
- **Macro indicators**: add anything from FRED + World Bank — `population`, `inflation`, `unemployment`, `10y treasury yield`, `oil price`, etc.
- **News categories**: `general` | `world` | `tech` | `business` | `science` | `health` | `politics`
- **Frequency**: schedule at 6am local time via your agent runtime's cron primitive
- **Format**: change the system prompt to output JSON, markdown, or a custom template for downstream piping

## Why this intel matters

A morning brief is the highest-frequency intel an agent ships to its operator. It's the daily proof the agent is doing its job. Make it useful and the operator trusts the agent. Make it generic and they tune it out. The two-layer architecture lets you keep cost trivial (Solvr keyless + cheap Venice model) while quality stays high.

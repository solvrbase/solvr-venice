---
name: token-pick
description: Find low-risk tokens with positive momentum using security + TA filters.
category: crypto-markets
tier: standard
source: https://github.com/solvrbase/solvr-venice
solvr_api: https://api.solvrbot.com
venice_api: https://api.venice.ai/api/v1
venice_model: zai-org-glm-5-1
venice_alt_models: [venice-uncensored, kimi-k2-5, qwen3-vl-235b-a22b]
venice_parameters:
  enable_web_search: auto
compatibility: [eliza, crewai, langchain, openai-sdk, coinbase-agentkit, any-openai-compatible]
---

# Token Pick

Find low-risk tokens with positive momentum using security + TA filters. Solvr supplies the data; Venice synthesizes the output.

## Two layers, one workflow

| Layer | Provider | What it does |
|---|---|---|
| Data | Solvr | endpoints listed below (tier: `standard`) |
| Inference | Venice | `/chat/completions` with `zai-org-glm-5-1` — synthesis + formatting |

## Endpoints
- `GET https://api.solvrbot.com/api/v1/dex/trending` — trending tokens
- `POST https://api.solvrbot.com/api/v1/security/scan` — token security scan
- `POST https://api.solvrbot.com/api/v1/ta/quick` — quick TA

## Instructions
1. Fetch trending tokens: `GET https://api.solvrbot.com/api/v1/dex/trending`
2. For top 10 trending, run security scan: `POST https://api.solvrbot.com/api/v1/security/scan`
3. Filter: only keep tokens with `risk_score` <= 35 (safe)
4. For safe tokens, fetch quick TA: `POST https://api.solvrbot.com/api/v1/ta/quick`
5. Score each: +1 RSI < 65, +1 MACD bullish, +1 price > 0%, +1 volume > avg
6. Output top 3 picks with score and rationale.

```
🎯 TODAY'S PICKS (low-risk + momentum)
1. $TOKEN — Risk: 12/100 | RSI: 58 | MACD: ↑ | Score: 4/4
   Why: Clean contract, accumulation pattern, rising volume
```

## Venice synthesis

After fetching data per the instructions above, pipe through Venice for natural-language synthesis:

```python
import os, requests
from openai import OpenAI

venice = OpenAI(
    api_key=os.environ["VENICE_API_KEY"],
    base_url="https://api.venice.ai/api/v1",
)
SOLVR = "https://api.solvrbot.com"
HEADERS = {"Authorization": f"Bearer {os.environ['SOLVR_API_KEY']}"}  # omit for free-tier intels

# 1. Fetch Solvr data per the instructions above
# data = requests.get(...).json()  or requests.post(...).json()

# 2. Pass to Venice for synthesis
r = venice.chat.completions.create(
    model="zai-org-glm-5-1",
    messages=[
        {"role": "system", "content": "Follow the token-pick intel instructions to produce the output."},
        {"role": "user", "content": str(data)},
    ],
    extra_body={"venice_parameters": {"enable_web_search": "auto"}},
)
print(r.choices[0].message.content)
```

## Auth modes

| Solvr | Venice |
|---|---|
| Bearer API key (`SOLVR_API_KEY`) | Bearer API key OR `X-Sign-In-With-X` + USDC on Base (x402) |

Standard tier unlocks by holding 20M $SOLVR on Base.

## Customize

- Swap `venice_model` to `venice-uncensored` for unfiltered analysis, or `kimi-k2-5` for fastest/cheapest synthesis.
- Set `enable_web_search` to `"off"` if you only want the Solvr data, no augmentation.
- Plug into any agent framework that wraps the OpenAI SDK — Eliza, CrewAI, LangChain, Coinbase Agentkit, or anything OpenAI-compatible.

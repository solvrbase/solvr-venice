---
name: weekly-review
description: Weekly review — what happened, what changed, and what to prioritize next week.
category: productivity
tier: free
source: https://github.com/solvrbase/solvr-venice
solvr_api: https://api.solvrbot.com
venice_api: https://api.venice.ai/api/v1
venice_model: zai-org-glm-5-1
venice_alt_models: [venice-uncensored, kimi-k2-5, qwen3-vl-235b-a22b]
venice_parameters:
  enable_web_search: auto
compatibility: [eliza, crewai, langchain, openai-sdk, coinbase-agentkit, any-openai-compatible]
---

# Weekly Review

Weekly review — what happened, what changed, and what to prioritize next week. Solvr supplies the data; Venice synthesizes the output.

## Two layers, one workflow

| Layer | Provider | What it does |
|---|---|---|
| Data | Solvr | endpoints listed below (tier: `free`) |
| Inference | Venice | `/chat/completions` with `zai-org-glm-5-1` — synthesis + formatting |

## Endpoints
- `GET https://api.solvrbot.com/api/v1/news?category=general&limit=10` — week's news
- `GET https://api.solvrbot.com/api/v1/dex/trending` — crypto performance
- `GET https://api.solvrbot.com/api/v1/worlddata?query=s%26p+500` — market performance

## Instructions
1. Fetch week's top news
2. Fetch key market metrics for the week
3. Review structure:
   - Key events this week (top 5)
   - Market performance summary
   - Wins and misses (if tracking positions)
   - Top 3 priorities for next week
4. Output in weekly review template format.

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
        {"role": "system", "content": "Follow the weekly-review intel instructions to produce the output."},
        {"role": "user", "content": str(data)},
    ],
    extra_body={"venice_parameters": {"enable_web_search": "auto"}},
)
print(r.choices[0].message.content)
```

## Auth modes

| Solvr | Venice |
|---|---|
| Keyless (free tier — no Solvr key needed) | Bearer API key OR `X-Sign-In-With-X` + USDC on Base (x402) |

_This is a free-tier intel — no Solvr API key required._

## Customize

- Swap `venice_model` to `venice-uncensored` for unfiltered analysis, or `kimi-k2-5` for fastest/cheapest synthesis.
- Set `enable_web_search` to `"off"` if you only want the Solvr data, no augmentation.
- Plug into any agent framework that wraps the OpenAI SDK — Eliza, CrewAI, LangChain, Coinbase Agentkit, or anything OpenAI-compatible.

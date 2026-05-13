---
name: startup-idea
description: Generate startup ideas by finding gaps in current trends and macro data.
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

# Startup Idea

Generate startup ideas by finding gaps in current trends and macro data. Solvr supplies the data; Venice synthesizes the output.

## Two layers, one workflow

| Layer | Provider | What it does |
|---|---|---|
| Data | Solvr | endpoints listed below (tier: `free`) |
| Inference | Venice | `/chat/completions` with `zai-org-glm-5-1` — synthesis + formatting |

## Endpoints
- `GET https://api.solvrbot.com/api/v1/news?topic=problem+pain+frustrated+need&limit=10` — pain points
- `GET https://api.solvrbot.com/api/v1/worlddata?query={market_stat}` — market size data
- `GET https://api.solvrbot.com/api/v1/github/trending?since=weekly` — tech enabling new solutions

## Instructions
1. Fetch news about unsolved problems and pain points
2. Fetch trending tech repos for solution primitives
3. Fetch market size data for promising spaces
4. Generate ideas using the formula:
   [Trending tech] + [Underserved problem] = [Startup idea]
5. Score each idea: market size × tech readiness × founder fit
6. Output: 5 startup ideas with one-liner, market estimate, and tech stack.

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
        {"role": "system", "content": "Follow the startup-idea intel instructions to produce the output."},
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

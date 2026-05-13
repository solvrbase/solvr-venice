---
name: security-digest
description: Daily threat-intel digest covering vulnerabilities, exploits, and active attacks. Solvr aggregates the signals, Venice synthesizes the brief.
category: research
tier: standard
source: https://github.com/solvrbase/solvr-venice
solvr_api: https://api.solvrbot.com
venice_api: https://api.venice.ai/api/v1
venice_model: zai-org-glm-5-1
venice_alt_models: [venice-uncensored, kimi-k2-5]
venice_parameters:
  enable_web_search: auto
compatibility: [eliza, crewai, langchain, openai-sdk, coinbase-agentkit, any-openai-compatible]
---

# Security Digest

Daily threat-intel briefing for agents that need to know what's getting attacked. Surfaces fresh vulnerabilities, exploits, and ongoing attacks across crypto and tech ecosystems. Solvr feeds the raw threat signal; Venice produces the synthesized brief with severity grading.

## Two layers, one workflow

| Layer | Provider | What it does |
|---|---|---|
| Data | Solvr | `/threat-intel` + `/news?topic=security` — aggregated threat signal |
| Inference | Venice | `/chat/completions` with `zai-org-glm-5-1` — severity grading + synthesis |

## Endpoints

- `POST https://api.solvrbot.com/api/v1/threat-intel` — daily threat-intel report (Solvr standard tier)
- `GET https://api.solvrbot.com/api/v1/news?topic=security+exploit+vulnerability&limit=10` — fresh news context (Solvr free, keyless)
- `POST https://api.venice.ai/api/v1/chat/completions` — synthesis (Venice)

## Workflow

1. Fetch threat-intel report from Solvr.
2. Fetch security-tagged news from Solvr (no key needed).
3. Pass both to Venice with grading instructions.
4. Venice returns the digest with severity ratings (Critical / High / Medium / Low) per incident.
5. Optional: post to your alert channel if any Critical-severity item is fresh (<24h).

## Output format

```
Security Digest — <date>

CRITICAL (action required)
- <incident>: <one-line summary>  [<source>]

HIGH (track closely)
- <incident>: <summary>  [<source>]

MEDIUM (awareness)
- <incident>: <summary>  [<source>]

LOW (background)
- <incident>: <summary>  [<source>]

Themes: <emerging patterns Venice identified across the day>
```

## Python (OpenAI SDK pointed at Venice)

```python
import os, requests
from openai import OpenAI

venice = OpenAI(
    api_key=os.environ["VENICE_API_KEY"],
    base_url="https://api.venice.ai/api/v1",
)
SOLVR = "https://api.solvrbot.com"
S_HEADERS = {"Authorization": f"Bearer {os.environ['SOLVR_API_KEY']}"}

def security_digest() -> str:
    threats = requests.post(f"{SOLVR}/api/v1/threat-intel", headers=S_HEADERS).json()
    news    = requests.get(f"{SOLVR}/api/v1/news",
                           params={"topic": "security exploit vulnerability", "limit": 10}).json()

    r = venice.chat.completions.create(
        model="zai-org-glm-5-1",
        messages=[
            {"role": "system", "content": (
                "You are a security analyst. Produce a daily threat-intel digest. "
                "Grade each incident Critical / High / Medium / Low. Be conservative — "
                "Critical means active exploitation with confirmed impact."
            )},
            {"role": "user", "content": f"threats: {threats}\n\nnews: {news}"},
        ],
        extra_body={"venice_parameters": {"enable_web_search": "auto"}},
    )
    return r.choices[0].message.content
```

## Auth modes

| Solvr | Venice |
|---|---|
| Bearer API key (today) for `/threat-intel`; `/news` is keyless | Bearer API key OR `X-Sign-In-With-X` + USDC on Base (x402) |

**Permissionless variant**: If you only want the news-driven version (no Solvr threat-intel), drop the first endpoint and run keyless against `/news` + Venice. Quality drops without the curated threat feed, but it works.

## Customize

- Set the `news` topic to your domain: `"smart contract exploit"`, `"DeFi hack"`, `"key compromise"`, `"supply chain attack"`.
- Swap `venice_model` to `venice-uncensored` if you want unredacted analysis of disclosure-restricted incidents.
- Schedule daily via your agent runtime's cron primitive.

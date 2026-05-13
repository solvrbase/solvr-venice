---
name: token-report
description: Daily performance report for any Base token. Solvr supplies the data, Venice synthesizes the report.
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

# Token Report

Drop-in daily report for any Base token. Solvr returns the onchain intelligence (price, security, holders, TA). Venice synthesizes it into a structured analyst report.

## Two layers, one workflow

| Layer | Provider | What it does |
|---|---|---|
| Data | Solvr | `/intel/{address}` + `/ta/quick` — onchain truth |
| Inference | Venice | `/chat/completions` with `zai-org-glm-5-1` — natural-language synthesis |

## Endpoints

- `GET https://api.solvrbot.com/api/v1/intel/{address}` — unified intel (Solvr standard tier)
- `POST https://api.solvrbot.com/api/v1/ta/quick` — quick TA (Solvr standard tier)
- `GET https://api.solvrbot.com/api/v1/news?topic={symbol}` — narrative context (Solvr free, keyless)
- `POST https://api.venice.ai/api/v1/chat/completions` — synthesis (Venice)

## Workflow

1. Fetch intel + TA from Solvr (parallel).
2. Pass both as JSON context to Venice `/chat/completions`.
3. Venice returns the formatted report. With `enable_web_search: auto`, it also adds live narrative context.
4. Alert if `risk_score > 50` or `|price_change_24h| > 20%`.

## Output format

```
$SYMBOL daily report — <date>

Price     $<price_usd> (<change_24h>% 24h)
MCap      $<market_cap>
Volume    $<volume_24h>
Holders   <holder_count>

Security  <risk_score>/100 — <verdict>
RSI       <rsi>   MACD: <macd_signal>
Verdict   BREAKOUT / BREAKDOWN / ACCUMULATION / QUIET

Narrative <one paragraph from Venice web search>
Alert     <triggered or none>
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

def token_report(address: str, symbol: str) -> str:
    intel = requests.get(f"{SOLVR}/api/v1/intel/{address}", headers=S_HEADERS).json()
    ta    = requests.post(f"{SOLVR}/api/v1/ta/quick", headers=S_HEADERS,
                          json={"symbol": symbol}).json()

    r = venice.chat.completions.create(
        model="zai-org-glm-5-1",
        messages=[
            {"role": "system", "content": "You are a crypto analyst. Output the daily report in the exact format requested."},
            {"role": "user",   "content": f"intel: {intel}\n\nta: {ta}\n\nProduce the report."},
        ],
        extra_body={"venice_parameters": {"enable_web_search": "auto"}},
    )
    return r.choices[0].message.content
```

## Auth modes

| Solvr | Venice |
|---|---|
| Bearer API key (today) — or wallet sign for free tier (keyless) | Bearer API key OR `X-Sign-In-With-X` + USDC on Base (x402) |

**Permissionless path**: Free Solvr endpoints (news, dex, worlddata) are keyless today. Standard/Full tier endpoints unlock by holding $SOLVR on Base. Venice charges per-call from your wallet's USDC balance via x402.

## Customize

- Swap `venice_model` to `venice-uncensored` for raw analysis, `kimi-k2-5` for fastest/cheapest synthesis.
- Set `enable_web_search` to `"off"` if you want pure onchain data.
- Replace `/ta/quick` with `/ta/analysis` (Full tier) for multi-timeframe analysis.

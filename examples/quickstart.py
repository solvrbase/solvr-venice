"""
solvr-venice quickstart
=======================

Runs three intels end-to-end against Solvr + Venice. Two of them are fully keyless
on the Solvr side (no API key needed), one uses the Solvr Bearer token for premium
intel.

Setup:
    pip install openai requests
    export VENICE_API_KEY="vk-..."          # from venice.ai/settings/api
    export SOLVR_API_KEY="solvr_..."        # only for token-report (premium intel)
    python quickstart.py
"""
from __future__ import annotations

import os
import requests
from openai import OpenAI

# ─── Clients ──────────────────────────────────────────────────────────────────

SOLVR = "https://api.solvrbot.com"
SOLVR_AUTH = {"Authorization": f"Bearer {os.environ.get('SOLVR_API_KEY', '')}"}

venice = OpenAI(
    api_key=os.environ["VENICE_API_KEY"],
    base_url="https://api.venice.ai/api/v1",
)

DEFAULT_MODEL = "zai-org-glm-5-1"


def _synthesize(system: str, user: str, *, model: str = DEFAULT_MODEL, web_search: bool = True) -> str:
    """Call Venice for synthesis. OpenAI SDK pointed at Venice's compat endpoint."""
    r = venice.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        extra_body={
            "venice_parameters": {
                "enable_web_search": "auto" if web_search else "off",
            },
        },
    )
    return r.choices[0].message.content


# ─── Intel 1: narrative-tracker (Solvr keyless + Venice) ─────────────────────

def narrative_tracker() -> str:
    """Detect emerging crypto narratives. No Solvr API key required."""
    news = requests.get(f"{SOLVR}/api/v1/news", params={"limit": 20}).json()
    trending = requests.get(f"{SOLVR}/api/v1/dex/trending").json()
    casts = requests.get(f"{SOLVR}/api/v1/farcaster", params={"limit": 20}).json()

    return _synthesize(
        system=(
            "You are a crypto narrative analyst. Cluster the inputs into narrative "
            "threads. Rank by emergence strength: how fresh (last 24h weighted higher) "
            "and how cross-source. Output top 5 with freshness score 0-100."
        ),
        user=f"news: {news}\n\ntrending: {trending}\n\ncasts: {casts}",
    )


# ─── Intel 2: morning-brief (Solvr keyless + Venice) ─────────────────────────

USER_PROFILE = {
    "role": "agent operator building on Base",
    "focus": ["AI agent infra", "onchain narratives", "Base ecosystem"],
    "watch_macro": ["fed rate", "vix", "s&p 500"],
}


def morning_brief() -> str:
    """Daily executive brief calibrated to USER_PROFILE. No Solvr API key required."""
    news = []
    for cat in ["general", "business", "tech"]:
        news.append(requests.get(f"{SOLVR}/api/v1/news",
                                  params={"category": cat, "limit": 5}).json())
    macro = {
        ind: requests.get(f"{SOLVR}/api/v1/worlddata", params={"query": ind}).json()
        for ind in USER_PROFILE["watch_macro"]
    }
    trending = requests.get(f"{SOLVR}/api/v1/dex/trending").json()

    return _synthesize(
        system=(
            "You are an executive analyst writing a morning brief. Calibrate every "
            "item to the user's role and focus areas. Be punchy. No filler. "
            "Three bullets per section max."
        ),
        user=(
            f"user_profile: {USER_PROFILE}\n\n"
            f"news: {news}\n\nmacro: {macro}\n\ntrending: {trending}"
        ),
    )


# ─── Intel 3: token-report (Solvr standard tier + Venice) ─────────────────────

def token_report(address: str, symbol: str) -> str:
    """Daily report for a specific Base token. Requires SOLVR_API_KEY."""
    if not os.environ.get("SOLVR_API_KEY"):
        return "SKIPPED: token-report requires SOLVR_API_KEY (standard tier).\n" \
               "Get one at solvrbot.com/api-docs#agent-register or skip this intel."

    intel = requests.get(f"{SOLVR}/api/v1/intel/{address}", headers=SOLVR_AUTH).json()
    ta = requests.post(f"{SOLVR}/api/v1/ta/quick", headers=SOLVR_AUTH,
                       json={"symbol": symbol}).json()

    return _synthesize(
        system=(
            "You are a crypto analyst. Output a structured daily report. "
            "Sections: PRICE, MCAP, VOLUME, HOLDERS, SECURITY, RSI, MACD, VERDICT, NARRATIVE, ALERT."
        ),
        user=f"intel: {intel}\n\nta: {ta}",
    )


# ─── Run all three ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("solvr-venice quickstart — 3 intels via Solvr + Venice")
    print("=" * 60)

    print("\n[1/3] narrative-tracker (keyless Solvr + Venice)")
    print("-" * 60)
    print(narrative_tracker())

    print("\n[2/3] morning-brief (keyless Solvr + Venice)")
    print("-" * 60)
    print(morning_brief())

    print("\n[3/3] token-report (premium Solvr + Venice)")
    print("-" * 60)
    # Replace with any Base token address you want to analyze
    SOLVR_TOKEN = "0x6DfB7BFA06e7c2B6c20C22c0afb44852C201eB07"
    print(token_report(SOLVR_TOKEN, "SOLVR"))

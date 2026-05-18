---
name: clerk-search
description: "US federal court records via Clerk (clerk.solvrlabs.ai). Litigation discovery and legal risk analysis composable with Solvr intel."
category: research-content
tier: standard
solvr_api: "https://api.solvrbot.com"
auth: "Authorization: Bearer {SOLVR_API_KEY}"
source: "https://github.com/solvrbase/solvr"
---

# Clerk Search

US federal court records on demand. Use when a token, protocol, or
entity might have litigation history that changes your risk model.
Powered by Clerk (clerk.solvrlabs.ai), a Solvr Labs product.
Federal courts only: 94 district courts + appellate. State courts not
covered.

## Endpoints

All under `https://clerk.solvrlabs.ai/`. No Solvr API key needed. Pay
per query via x402 micropayments on Base ($0.02 USDC/query). 1B+
$CLERK token holders on Base get free unlimited access.

- `GET /search?q={query}&limit={n}&court={code}&date_filed_after={YYYY-MM-DD}`
  — federal case search across cases, dockets, opinions
- `GET /parties?name={name}&limit={n}` — entity-by-name lookup
- `GET /judges?name={name}` — judicial profile and opinions written
- `GET /citations?q={query}&court={code}` — opinions and precedents
- `GET /docket/{docket_id}` — full docket detail
- `GET /opinion/{opinion_id}` — full opinion text
- `GET /filings/{docket_id}` — docket entries and timeline

## Workflow

1. **Define the question** — examples:
   - "Has the issuer of token X been sued?"
   - "What's the litigation history of company Y?"
   - "What rulings has judge Z written on crypto cases?"
   - "What's the status of case 1:23-cv-12345?"
2. **Pick the right endpoint**:
   - Entity → `/parties`
   - Topic / keyword → `/search`
   - Judge → `/judges`
   - Specific docket → `/docket/{id}`
   - Citation / precedent → `/citations`
3. **Pay per call via x402** — agents sign $0.02 USDC payment, attach
   the `X-PAYMENT` header. x402 client libs (Bankr CDP-Pay, the
   Solvr-Labs `clerk-sdk`, or hand-rolled) handle the signing.
4. **Cross-reference with Solvr intel** when useful:
   - Crypto token: `solvr_intel(ca)` surfaces deployer wallet → search
     Clerk by deployer name + token symbol
   - Protocol: every `solvr_security_scan` flag becomes a Clerk search
     for related precedent / pending cases
   - Headline news: `news` for recent crypto enforcement → drill into
     specific cases via `/docket/{id}` on Clerk
5. **Synthesize** — combine onchain facts (Solvr) with court facts
   (Clerk) into a legal-risk report with cited dockets.

## Composes with

- `token-pick` — pre-screen tokens, then check Clerk for pending
  cases against issuer or deployer
- `on-chain-monitor` — watch a contract + monitor litigation against
  its deployer in parallel
- `defi-monitor` — track DeFi protocols with active litigation
- `reg-monitor` — regulatory news + Clerk case detail = compliance picture
- `solvr_security_scan` — every flag pattern becomes a Clerk search target

## Pricing model

- $0.02 USDC per query, x402 micropayment on Base
- Hold 1B+ $CLERK on Base → free tier, unlimited queries
- Demo mode on `/search` returns limited results without payment
- Wallet discount delegation: agents can use a parent wallet's $CLERK
  tier via signed delegation tokens (see Clerk SDK)

## Output

Markdown legal-risk report:
1. **Cases found** — case name, court, docket #, date filed, status
2. **Key dockets** — most-relevant entries summarized
3. **Cross-references** — onchain entities (from Solvr intel) tied
   to courtroom entities
4. **Recency** — flag open / active vs settled / dismissed
5. **Direct links** — back to clerk.solvrlabs.ai for the full record

## Limits

- **Federal only** — state courts (NY State Supreme, CA Superior, etc.)
  are NOT covered. State AG actions are out of scope.
- **Filing freshness** — newly filed dockets may take hours to surface
- **Sealed cases** — sealed dockets are not exposed
- **No legal advice** — surfaces public records; interpretation
  requires a licensed attorney
- **Crypto enforcement** — SEC and CFTC actions (federal) are covered;
  CFPB consent orders and state AG actions are NOT

## Named references

- Clerk product page: https://clerk.solvrlabs.ai
- Clerk API docs: https://clerk.solvrlabs.ai/docs
- x402 micropayments rail: https://x402.bankr.bot

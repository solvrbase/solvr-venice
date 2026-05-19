---
name: gitlawb-discovery
description: "Discover gitlawb-network projects via the GitHub Search API. Trending, new, and topic-filtered repo discovery with ranking and noise filtering."
category: dev-code
tier: free
solvr_api: "https://api.solvrbot.com"
auth: "Authorization: Bearer {SOLVR_API_KEY}"
source: "https://github.com/solvrbase/solvr"
---

# Gitlawb Discovery

Discover projects in the gitlawb network (decentralized git for AI agents)
without a public listing API. Gitlawb.com itself doesn't expose a JSON
endpoint for repo discovery — the web frontend uses React Server
Components against peer nodes via internal protocols. To surface
gitlawb-related projects programmatically, proxy through GitHub Search,
which catalogs every repo mentioning gitlawb in its README, topic tags,
or remote config.

No auth required for low-rate-limit use (60 requests / hour / IP
unauthenticated, 5000 with a GitHub PAT).

## Endpoints

GitHub REST API v3 — public, keyless at the free rate limit, CORS open
(works from any frontend).

- `GET https://api.github.com/search/repositories?q={query}&sort={field}&order={dir}&per_page={n}`

Useful queries:

- `topic:gitlawb` — repos that opted into the `gitlawb` topic tag.
  High signal, low recall (~3 repos at time of writing). Best for
  curated discovery.
- `gitlawb in:readme` — any repo mentioning gitlawb in its README.
  Broader (~250 repos), includes some "awesome list" noise but
  surfaces the real ecosystem.
- `user:Gitlawb` — repos under the official Gitlawb org.
- `git-remote-gitlawb` — repos with the gitlawb remote helper in
  config (currently 0; useful as the ecosystem matures).

Sort fields: `stars` (most popular), `updated` (recently active),
`forks`, `help-wanted-issues`. Order: `asc` or `desc`.

## Workflow

1. **Pick the discovery mode**:
   - Trending → `sort=stars&order=desc` on the broad `gitlawb in:readme` query
   - New / Recent → `sort=updated&order=desc` on the same query
   - High signal only → `q=topic:gitlawb` (small but real)
2. **Fetch the page** — usually `per_page=30` is enough for one screen
3. **Filter noise** — exclude repos whose name contains `awesome-`
   (curated lists that just mention gitlawb) unless that's what the
   user wants. Optional: deprioritize repos with stars=0 and no
   description.
4. **Rank** — for trending, the API's `stars` sort is usually right.
   For more nuanced ranking, blend stars + recency:
   `score = stars + (days_since_2026_01_01 - days_since_updated_at) * 0.5`
5. **Enrich** — for each repo of interest, hit
   `GET https://api.github.com/repos/{owner}/{repo}/topics` if you
   want richer topic data (the search endpoint truncates topics).
6. **Output** — markdown table or card list with name, description,
   stars, last_updated, language, homepage.

## Composes with

- `dev-digest` — blend gitlawb-network activity into a general
  dev/AI ecosystem digest
- `code-health` — once a repo is discovered, audit it for
  dependency risks and quality signals
- `dependency-audit` — check the deps of a discovered repo for CVEs
- `repo-pulse` — measure activity/momentum on a specific gitlawb repo
- `search-intel` — use the Solvr intel catalog to find a related
  Solvr intel that fits the discovered repo's stack

## Rate limit handling

- Unauthenticated: 60 / hour / IP. Cache aggressively client-side
  (e.g. 5-minute TTL per query).
- With a GitHub PAT (optional, env var GITHUB_TOKEN): 5000 / hour.
  Add header `Authorization: Bearer {GITHUB_TOKEN}`.
- On 403 with `X-RateLimit-Remaining: 0`, the response includes
  `X-RateLimit-Reset` (unix timestamp). Use it to message the user
  when capacity returns.

## Limits

- **Gitlawb is decentralized** — the canonical source of truth is the
  peer-node network, not GitHub. This recipe surfaces the
  GITHUB-MIRRORED slice. Projects without GitHub presence are
  invisible here.
- **README-keyword false positives** — repos that mention gitlawb
  in passing (changelogs, awesome lists) show up. Lead with
  `topic:gitlawb` for highest precision; broaden to `in:readme` for
  recall.
- **Search index lag** — GitHub indexes new content within minutes
  to hours; brand-new repos may not appear immediately.
- **No private repos** — search only covers public.

## Output

Markdown report or JSON array, depending on caller:

1. **Discovery summary** — query used, total matches, top-N shown
2. **Repo cards** — name, description, stars, forks, language,
   updated_at (relative), homepage link, html_url
3. **Topic tags** for each repo when present
4. **Rate-limit status** — remaining / reset time so the agent
   self-throttles on subsequent calls

## Named references

- GitHub Search REST API:
  https://docs.github.com/en/rest/search/search#search-repositories
- gitlawb project home: https://gitlawb.com
- gitlawb organization on GitHub: https://github.com/Gitlawb

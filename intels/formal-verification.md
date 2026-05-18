---
name: formal-verification
description: AI-assisted formal verification for smart contracts and cryptographic protocols. Lean / K Framework / Coq workflow grounded in live Solvr intel.
category: dev-code
tier: standard
solvr_api: https://api.solvrbot.com
auth: Authorization: Bearer {SOLVR_API_KEY}
source: https://github.com/solvrbase/solvr
---

# Formal Verification

AI-assisted formal verification: prove mathematical correctness of a
smart contract or cryptographic primitive against a written
specification. Use when "passes tests" is not enough — adversarial
environment, immutable deployment, custody at stake. Inspired by
Vitalik Buterin's 2026-05-18 essay framing FV as "the final form of
software development."

## Stack choices

- **Lean 4** — best AI-tooling ecosystem (Leanstral, miniF2F). Use
  for protocol-level proofs, cryptographic reductions (e.g. Signal
  X3DH → DDH), arithmetic invariants. `omega` tactic handles
  integer arithmetic, `decide` for finite cases, `induction` for loops.
- **K Framework / KEVM** — for EVM bytecode-level execution semantics.
  Use when you need "the compiled bytecode behaves as proven," not
  just "the source intent is proven."
- **Coq / Isabelle** — alternatives. Lean has the strongest AI
  ecosystem now; pick these only if a target library already exists.
- **SMT solvers** (Z3, CVC5) — back-end automation for the proof
  assistants above. Usually invoked via tactics, not directly.

## Endpoints (ground the spec in live data)

- `GET https://api.solvrbot.com/api/v1/intel/{ca}` — actual holders,
  liquidity, deployer history. Use to write realistic adversary
  assumptions.
- `POST https://api.solvrbot.com/api/v1/security/scan` — flags
  known-pattern vulnerabilities. Each flag becomes a theorem to prove
  is NOT exploitable in this contract.
- `POST https://api.solvrbot.com/api/v1/security/bundles` — buyer
  concentration data. Backs theorems about MEV / sandwich resistance.
- `GET https://api.solvrbot.com/api/v1/news?topic={primitive}+formal+verification`
  — prior art on verifying this contract type.

## Workflow

1. **Identify the target**: contract CA, cryptographic primitive name,
   or protocol document.
2. **Pull intel**: `solvr_intel(ca)` + `solvr_security_scan(ca)` to
   ground the spec. Adversary assumptions should match real holder
   distribution + known attack surface.
3. **State theorems**: write what "correct" means as machine-checkable
   propositions. Examples:
   - `totalSupply` is conserved across every state transition
   - No `transfer` path lets an admin move non-admin balances
     without consent
   - Adversary with chain history but no private keys cannot
     distinguish session key from random (cryptographic reduction)
4. **Generate proof skeleton in Lean** — theorem statements with
   `sorry` placeholders. State the theorem precisely; the proof body
   can iterate.
5. **Hand to a proof-trained model** (Leanstral, DeepSeek-Math, or
   Lean Copilot) via the openai-compat shim to fill in proof steps.
6. **Compile in `lean` / `lake build`** — failure is the agent's
   feedback signal. Loop until clean.
7. **For end-to-end** (Project Everest pattern): also prove the
   compiled bytecode matches the Lean version. KEVM is the
   crypto-native path; symbolic execution is the fallback.
8. **Output**: the THEOREM STATEMENTS (human audits these), the
   PROOFS (compiler audits these), the ASSUMPTIONS section
   (everything that's *not* proven and must be trusted).

## Composes with

- `token-pick` — pre-screen which contracts are worth the FV cost
- `on-chain-monitor` — watch the verified contract for
  spec-violating transactions post-deploy
- `solvr_security_scan` — every flag in the scan response becomes a
  theorem-to-disprove in the FV pass

## Limits (per Vitalik)

- **Hidden assumptions in specs** — "the adversary cannot read this
  memory region" might not hold against side-channel attacks.
  Surface every assumption explicitly in the output.
- **Compilation gap** — proving Lean source ≠ proving compiled
  bytecode. Bridge with KEVM or compiler-verified toolchains
  (e.g. CompCert-style).
- **Spec incompleteness** — a proven contract can still be exploited
  if the spec didn't cover the attack vector. FV reduces risk,
  doesn't eliminate it.
- **Trusted base** — the proof checker itself (Lean kernel) is the
  last line of trust. Small + audited but non-zero.

## Output

Markdown report with sections:
1. **Verified theorems** — what was proven, in human-readable terms
2. **Lean / K artifacts** — links to the proof files
3. **Assumptions** — everything trusted-not-proven (kernel,
   bytecode-compile correctness, etc.)
4. **Residual risk** — known attack vectors NOT covered by the proofs
5. **Audit checklist for the human** — what to read before signing
   off

## Named references

- Project Everest (TLS verification, Microsoft Research)
- KEVM — K Framework + EVM semantics
- Signal protocol formal proofs (X3DH → DDH reduction)
- Cryptol (browser crypto verification)
- Leanstral (proof-assistant-trained LLM)
- Vitalik Buterin, "A shallow dive into formal verification"
  (2026-05-18) — origin essay:
  https://vitalik.eth.limo/general/2026/05/18/fv.html

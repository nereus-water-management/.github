# Nereus — Product Requirements & Roadmap (PRD)

> New to Nereus? See the **[organization README](profile/README.md)** for what the platform is and how the repos fit together. This document is the plan.

The single master document for the Nereus program — Sentry analytics, the secure platform, the cost-out engine, the customer workflow, and Proteus. It carries both the **near-term conference plan** (the next quarter, month by month) and the **full program** behind it.

**Team:** two full-stack developers — **Will** (lead; foundation, calc, analysis, cost-out, Proteus) and **Parker** (contractor; the graph library + DevOps/deploy). Each owns whole features end to end.

**The deliverable set (five files):**
- **`NEREUS_PRD.md`** — this document (spec + timeline + rollups).
- **`nereus_backlog.csv`** — the leaf backlog, one row per card, import-ready for the git Project.
- **`pontus/IMPLEMENTATION.md`** — backend repo, code-level trace.
- **`sentry/IMPLEMENTATION.md`** — Sentry frontend repo, code-level trace.
- **`proteus/IMPLEMENTATION.md`** — Proteus frontend repo, code-level trace.

**Item IDs are the join key** across all five and the git cards: card `G16` ↔ CSV row `G16` ↔ `pontus §G16` ↔ `sentry §G16`.

---

## 1. Timeline — the conference (late September) and beyond

**The deadline shapes everything.** Target: a live, reliable product demo at the **late-September conference** — a *capability demo on curated data*, not a production launch. Working backward, the demo must be **feature-complete by end of August**, leaving September for integration, demo data, and dry runs. **September is a hardening month, not a build month** — no risky net-new work in the weeks before a live demo.

**Capacity.** Both devs work **35 h/week** ≈ **154 h/month** (Jul, Aug) and ~95 h in a short hardening September. Estimates are **Claude-Code-adjusted**: code and test hours compress (~0.5× dev, ~0.6× test-dev); review, deploy, and contingency don't.

**The product spine is a credibility chain**, and the order you *build* it is the inverse of the order you *pitch* it:

> **Build:** clean data → analysis → graphs → cost-out → CTA
> **Pitch:** the cost number (the hook) → "and here's exactly why" (the graphs + calc beneath it)

The hinge is a hard rule: **no dollar figure appears without a one-click drill-down to the graph that shows it and the calc that derives it.** Cost-out without explanation reads as a guess to the engineer in the audience whose first question is "how do you know?" The drill-down answers it by construction (the RFQ requires `graph_support` + `calc_support` on every ranked opportunity). That's why cost-out is built **last** — it earns credibility from the layers beneath — even though it's pitched **first**.

### Capability by month (the headline you can demo)

| Month | What you show on stage | The line |
|---|---|---|
| **End July** | A live system reads a real operator log and surfaces its gaps, errors, and a few cooling graphs | *"We read your messy log and made sense of it."* |
| **End August** | The ranked cost-out — top money leaks, each drilling into the graph + calc that prove it | *"Here's where you're losing money — and exactly why."* |
| **Late September** | The whole chain, polished and rehearsed, with a book-a-review CTA | *"The complete story, live and reliable."* |

### July — Foundation & the opener  *(Will 152 h · Parker 142 h)*
**Capability:** a deployed single-tenant instance ingests Grant's new log format and produces the data-quality report plus the first three cooling graphs.

| | Work | Items |
|---|---|---|
| **Will** | Rework the parser for Grant's new format; finish the pipeline (missing-data refactor + orchestration); finish the calc the opener needs (validation + cost/water-balance — chemistry & cost already done/landing); the report analysis (status rollup + water-balance capability). | B1, B5, B6, C1, C5, D2, D4 |
| **Parker** | Stand up CI/CD + deploy in week 1 (single-tenant demo instance); the reusable graph framework; the three opener graphs — trend-with-limits (#4), water-balance waterfall (#25), cycles-vs-bleed (#26). | J5, E0, E4, F25, F26 |

**Demo proof:** open the app → load a customer log → see the data-quality findings in *their* data + three graphs of *their* operation.
**Gate / risk:** the parser depends on **Grant finalizing the new input format** — the one external dependency that gates the start; lock it before July 1.
**Stretch:** Parker has ~218 h spare across the window — fill it with more graphs whose backend calc is **already done** (cooling/chemical/water-balance), not SPC charts that need Will's deferred stats work.

### August — The payoff: explained cost-out  *(Will 158 h · Parker 75 h)*
**Capability:** the ranked savings list — the top money leaks — each wired to the graph and calc that justify it. The part no incumbent can show.

| | Work | Items |
|---|---|---|
| **Will** | Cooling math; double-counting guards; chemical-feed analyzer (feeds overfeed); cost-out framework + ranking; the **top-3 core opportunities** — cycles (#1), water-balance leak (#4), **chemical overfeed (#16)** — each with graph + calc drill-down. | C4, C7, D5, G0, G1, G4, G16 |
| **Parker** | The cooling/cost graphs the cost-out drills into — approach-to-wet-bulb (#30), condenser approach (#33), water-cost stacked bar (#37), chemical use (#38) — then keep pulling calc-ready graphs from the deferred pile. | F30, F33, F37, F38, +extras |

**Demo proof:** the full chain works end to end — click any dollar figure, it drills to the proof. Feature-complete.
**Why chemical overfeed (#16) is in the demo even though it isn't the biggest line:** it's the one card a Nalco/Veolia/Kurita rep *structurally cannot* show — telling a customer to buy less chemical cannibalizes the incumbent's revenue. Vendor-neutrality becomes a dollar figure the incumbent can never produce; the log-native angle ("no new sensors") is the second wedge.
**Stretch:** add best-cycle-by-limiting-ion (#2) and wastewater/sewer (#31) to go top-3 → top-5.

### September — Integration, polish, hardening, rehearsal  *(no net-new build)*
**Capability:** the same chain, *reliable and rehearsed*, plus the book-a-review CTA that converts the demo into a meeting.

| | Work | Items |
|---|---|---|
| **Will** | Lightweight book-a-review CTA (email to Grant/Troy); curate the demo dataset; edge cases, error/empty states; dry runs. | I2 (lite) |
| **Parker** | Deploy hardening, demo-environment reliability, performance, graph polish. | (deploy) |
| **Shared** | Cross-cutting test/QA pass; demo script / talking points. | J6, J7 |

**Demo proof:** a clean dry-run of the full pitch on curated data, on the real demo environment, end to end without a hiccup — twice.
**Hard rule:** anything not feature-complete by end of August is cut from the demo, not crammed into September. If July slips, the release valve is graph *count* (drop to the 3 openers) and cost-out depth (top-3 is the floor) — never September build.

### After the conference — Post-MVP (the real-customer phase)
Tagged `Post-MVP` in the backlog — real work, not lost, just off the conference path. Resumes in roughly this order once the demo lands:
1. **Full platform (Theme A):** multi-tenant auth, RBAC, OIDC/MFA, retention, controlled deletion, audit, compliance — what turns the single-tenant demo into a product real customers can use.
2. **The rest of the graph library** (the other ~42 of 47, incl. the SPC family) and **the rest of the cost-out engine** (the other ~28 of 33).
3. **Second-wave analyzers:** regression, DOE, statistical forecasting.
4. **Full customer workflow** (beyond the lite CTA), appointment setting, self-serve onboarding, integrations (Ask Nereus, analytics/anomaly layer).
5. **Proteus** — our modeling tool (out of the RFQ; not needed to win the conference).

### The honest read
- **It fits 35 h/week — but Will is at the line every month** (Jul 152/154, Aug 158/154, Sep light). Almost no slack on Will's track; a surprise eats the demo. It only fits because most of July is *finishing* nearly-done calc, not greenfield.
- **Parker has ~218 h spare** and can't take Will's domain work — so he buffers his zero-context ramp and enriches the demo with extra calc-ready graphs. The bottleneck is Will, not Parker.
- **What made it fit:** deferring SPC (stats + charts — not core to a cooling pitch) and moving cooling math to August. Adding anything back means taking something out; the months are full.
- **Biggest risk is external:** Grant's parser format gates July. Lock it before July 1 or the chain shifts right.
- **Claude Code helps most exactly where this scope lives** — graphs, calc finish, cost-out logic (the compressible columns); the judgment-bound platform work is deferred. That alignment is why the MVP fits and the full program doesn't in this window.

---

## 2. How the backlog is organized

**One row per leaf item (129 total)** in `nereus_backlog.csv`. Columns:

### Hour model (per item)
| Column | Meaning |
|---|---|
| **Dev_hrs** | Building it — core implementation only. |
| **TestDev_hrs** | Writing the automated tests (Jest) — part of building, separated so test rigor is visible. |
| **QA_hrs** | Verifying it behaves — checking against the acceptance criterion. |
| **Deploy_hrs** | Integration, migration, release for the item. |
| **Buffer_hrs** | 12% of the other four — scales with item size. |
| **Total_hrs** | Sum of the five. |
| **Remaining_hrs** | Total adjusted for `Status` (Done = 0, In-progress = 50%, Rework/To-do = 100%). |

### Classification columns
| Column | Values | Use |
|---|---|---|
| **Product** | Sentry · Proteus | `Sentry` = contracted RFQ scope; `Proteus` = our addition (out of RFQ). Filter `Sentry` for the contractor quote. |
| **Repo** | pontus · sentry-fe · proteus-fe · combos | Where the code lives; full-stack items show two repos and appear in both repo docs. |
| **Assignee** | Will · Parker · Shared | Who owns it. |
| **Skill** | PE/DE/AE/FE/IE | Skill center of gravity (informational; both are full-stack). |
| **Milestone** | Jul · Aug · Sep · Post-MVP | The conference plan above; `Post-MVP` = after the conference. |
| **Status** | Done · In-progress · Rework · To-do | Current build state (Will's Jun-30 update). |

### The two-person split
Cut along the dependency graph, not frontend/backend:
- **Will** — foundation & high-context core: platform (A), pipeline (B), calc library (C), analysis (D), cost-out (G), Proteus (H), platform-side integration (J2–J4). The critical path and everything domain-bound.
- **Parker** — well-specified, parallelizable slices behind the calc-library dependency: the 47 graphs (E + F) and **DevOps/deploy (J5)**. Clean vertical slices a developer with zero codebase context can build from the spec + contract.
- **Shared** — the cross-cutting test/QA package (J6) and docs/handoff (J7).

Both are full-stack, so `Assignee` is the owner, not a layer boundary.

---

## 3. Rollups

### Conference MVP (Jul–Sep), Claude-Code-effective vs 35 h/wk capacity
| Month | Will | Parker | Capacity/person |
|---|---|---|---|
| July | 152 h | 142 h | 154 h |
| August | 158 h | 75 h | 154 h |
| September | ~47 h | polish | ~95 h |
| **MVP scope** | 26 items across Jul/Aug/Sep | | |

### Full program (all 129 items, total hours)
| Cut | Items | Total h | Remaining h* |
|---|---|---|---|
| **Will** | 41 | ~2,127 | ~2,000 |
| **Parker** | 86 | ~2,065 | ~2,065 |
| **Shared** | 2 | ~105 | ~105 |
| **Product = Sentry** (RFQ scope) | 125 | ~4,009 | — |
| **Product = Proteus** | 4 | ~289 | — |
| **Total** | **129** | **~4,298** | **~3,975** |

\* Remaining reflects what's already built (chemistry, augmenters, cadence/correct, data-quality analyzers; cost + dynamics landing). Activity split program-wide: Dev 55% · Test-dev 19% · QA 12% · Deploy 4% · Buffer 11%.

### By theme
| Theme | Name | Items | Total h |
|---|---|---|---|
| A | Platform & Security | 12 | 742 |
| B | Data Pipeline | 6 | 256 |
| C | Calculation Library | 7 | 297 |
| D | Analysis Engine | 8 | 369 |
| E | Graphs §1 (framework + 24) | 25 | 625 |
| F | Graphs §2 (23) | 23 | 431 |
| G | Cost-Out (framework + 33) | 34 | 772 |
| H | Proteus | 4 | 289 |
| I | Customer Workflow | 3 | 166 |
| J | Onboarding/Integration/DevOps/QA | 7 | 352 |

---

## 4. Themes (workstream intros)

Leaf items — with per-item hours, owner, repo, milestone, dependencies, acceptance — are in the CSV (filter by `Theme`). The repo docs carry the code-level detail.

- **A — Platform & Security.** The secure multi-tenant backbone: tenant data model, auth, RBAC, retention/deletion, audit. Deferred past the conference (the demo is single-tenant); the first real-customer push after.
- **B — Data Pipeline.** Parse → cadence → correct → augment → validate. Cadence/correct/augment built; parser reworks for Grant's new format; missing-data refactor + orchestration remain.
- **C — Calculation Library.** The tested source of truth for every formula. Chemistry done; cost + dynamics landing; validation/cooling remain (SPC deferred).
- **D — Analysis Engine.** The Sentry report: data-quality findings (built) + the 13 capability analyzers (water-balance/heat-transfer/chemical-feed for the MVP; the rest Post-MVP).
- **E / F — Graph Library (47).** A reusable framework then the graphs. ~9 in the conference demo; the rest Post-MVP. Parker's, both repo halves.
- **G — Cost-Out (33).** Ranked dollar savings, never fabricated. Framework + top-3 for the demo; the rest Post-MVP. Drill-down to graph + calc is mandatory.
- **H — Proteus.** The mechanistic what-if tool (Pontus `/model` + Proteus frontend). Out of RFQ, deferred.
- **I — Customer Workflow.** Accept/decline/defer/discuss + appointment to Grant/Troy. Lite CTA for the demo; full workflow Post-MVP.
- **J — Onboarding / Integration / DevOps / QA.** DevOps/deploy (Parker, week 1) is on the MVP path; onboarding and integrations are Post-MVP.

---

## 5. Risks & open questions (for PO/SME)
- **Parser format (gating):** Grant must finalize the new input format before July 1 — it gates the whole chain.
- **House style:** confirm against the real `server/index.js`, an existing endpoint, and `authenticate.js` before writing new backend code.
- **Appointment method:** the RFQ leaves it open; PO to choose (calendar API vs scheduling link vs email request) — lite email for the demo.
- **Savings data:** none in the source workbook by design; the engine computes from each customer's real rates — confirm the rate-entry path.
- **Total-analytical chemistry:** runs without activity-coefficient correction (documented limitation); SME to accept or scope the correction separately.
- **Confirm Will's done-list:** marked Done — cadence, correct, augment, chemistry, data-quality analyzers; In-progress — cost, dynamics, missing-data refactor, status rollup. Unconfirmed (assumed To-do): validation rules (C1), SPC stats (C2), cooling (C4), biological (C6).

## 6. Out of scope
- Activity-coefficient / ion-pairing chemistry (deferred).
- Energy cost-out beyond the documented kW/ton formulas; biocide speciation in the Proteus UI.
- The Ask Nereus product and the analytics/anomaly internals (integration only).
- SOC 2 / ISO 27001 certification — readiness/evidence only.

---

## 7. The files
| File | What it is |
|---|---|
| `NEREUS_PRD.md` | This master — spec, conference timeline, rollups, risks. |
| `nereus_backlog.csv` | 129-item leaf backlog with hours, Product/Repo/Assignee/Milestone/Status, dependencies, acceptance. Import to the git Project (one card per row; `Milestone` → iteration). |
| `pontus/IMPLEMENTATION.md` | Backend code-level trace (data model, auth, pipeline, calc, analysis, cost-out logic, graph transforms, Proteus `/model`). |
| `sentry/IMPLEMENTATION.md` | Sentry frontend trace (graph components, cost-out list, workflow UI). |
| `proteus/IMPLEMENTATION.md` | Proteus frontend trace (the four-tab tool, caching). |

Item IDs join all five and the git cards.

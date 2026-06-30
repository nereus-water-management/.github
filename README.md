# .github

Organization-wide configuration and program documentation for the **Nereus** org.

This repository does two jobs:

1. **Organization profile** — `profile/README.md` is what GitHub renders on
   `github.com/<org>` (the public front door).
2. **Program home** — the cross-cutting docs that don't belong to any single
   code repo: the PRD, the backlog, and the Project-import tooling.

> This file (the repo-root `README.md`) is what shows when you open the
> `.github` repo itself. For the platform overview, see
> **[`profile/README.md`](profile/README.md)**; for the plan, see
> **[`NEREUS_PRD.md`](NEREUS_PRD.md)**.

## Contents

| Path | What |
|---|---|
| `profile/README.md` | The organization profile (renders on the org page) |
| `NEREUS_PRD.md` | Program PRD & roadmap — what we're building and when |
| `nereus_backlog.csv` | The 129-item development backlog (import into the Project) |
| `scripts/import_to_github_project.py` | Populate the GitHub Project from the backlog |
| `scripts/IMPORT.md` | Importer setup & usage |

## The code repositories

| Repo | What | Docs |
|---|---|---|
| `pontus` | Backend — log parser, augmentation/calculation library, API | `README.md` + `IMPLEMENTATION.md` |
| `sentry` | Operator-log analytics frontend | `README.md` + `IMPLEMENTATION.md` |
| `proteus` | Single-water modeling frontend | `README.md` + `IMPLEMENTATION.md` |

## Start here

- **New to Nereus?** → [`profile/README.md`](profile/README.md)
- **Building?** → [`NEREUS_PRD.md`](NEREUS_PRD.md), then the relevant repo's `IMPLEMENTATION.md`
- **Populating the board?** → [`scripts/IMPORT.md`](scripts/IMPORT.md)

Item IDs (e.g. `G16`) are the join key across the backlog, the repo docs, and the Project cards.

---

*Org-wide issue/PR templates and community-health files can also live in this repo if you add them later.*

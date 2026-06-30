# Importing the backlog into a GitHub Project

`import_to_github_project.py` reads `nereus_backlog.csv` and:
1. creates one **issue** per row (`[ID] Title` + body with description, acceptance, hours),
2. adds each issue to your **Projects V2** board,
3. sets the board's **custom fields** (hours, Assignee, Milestone, Status, Theme, …).

Stdlib only — no `pip install`. Idempotent — safe to re-run.

## 1. Prerequisites

| Need | Detail |
|---|---|
| **Token** | `export GITHUB_TOKEN=…` — classic PAT with `repo` + `project`, or fine-grained with **Issues: R/W** + **Projects: R/W**. Never pass it on the command line. |
| **Project** | owner login + number, from the URL `…/<owner>/projects/<NUMBER>`. Org-owned or user-owned. |
| **Repo** | `owner/repo` to hold the issues (Project items that are issues must live in a repo). |
| **(optional)** | a JSON map for native assignees: `{"Will":"willgh","Parker":"parkergh"}`. |

## 2. Run it

```sh
export GITHUB_TOKEN=ghp_xxx

# Always dry-run first — builds every payload, hits no API, writes nothing:
python import_to_github_project.py --csv nereus_backlog.csv \
    --owner my-org --owner-type org --project-number 7 \
    --repo my-org/nereus --dry-run

# Real run — creates missing fields, issues, and sets field values:
python import_to_github_project.py --csv nereus_backlog.csv \
    --owner my-org --owner-type org --project-number 7 \
    --repo my-org/nereus --create-fields

# Optional native assignees + issue labels:
python import_to_github_project.py … --create-fields --labels --assignee-map team.json
```

| Flag | Effect |
|---|---|
| `--dry-run` | print planned actions; no API, no writes |
| `--create-fields` | create missing Project fields (single-select / number / text) |
| `--labels` | also add `theme:` / `assignee:` / `milestone:` / `product:` issue labels |
| `--assignee-map FILE` | map Assignee → GitHub username for native assignees |
| `--only A1,G16` | limit to specific IDs (good for a first real test) |
| `--owner-type user` | if the Project is user-owned rather than org-owned |

**Suggested first real run:** `--create-fields --only A1,E0,G16` to verify three issues land with fields set, then run the full set.

## 3. Field mapping

- **Single-select** (options auto-derived from the CSV): Product, Repo, Assignee, Skill, Theme, Phase, Milestone, Status.
- **Number:** Dev_hrs, TestDev_hrs, QA_hrs, Deploy_hrs, Buffer_hrs, Total_hrs, Remaining_hrs.
- **Text:** Dependencies.
- **Issue body:** Title, Description, Acceptance, a metadata table, and a hidden `nereus-id:<ID>` marker.

## 4. Idempotency & re-runs

The script writes `.import_state.json` (CSV `ID` → issue + project item). Re-running **updates** fields rather than duplicating issues. If that file is lost, it falls back to finding the issue by its `nereus-id:` marker before creating a new one. To refresh the board after editing the CSV (e.g., new estimates or a status change), just re-run.

## 5. Notes & gotchas

- **Make the Status field map cleanly:** Projects ship a default *Status* field (Todo/In Progress/Done). The script will try to use a field literally named `Status`; our values are `Done / In-progress / Rework / To-do`. Either let `--create-fields` add the missing options is **not** automatic for the built-in Status field — if you hit an option mismatch, add our four options to the Project's Status field in the UI once, or rename the CSV column. The script prints any missing options it can't set.
- **Iterations:** Milestone is created as a single-select (Jul/Aug/Sep/Post-MVP). If you'd rather drive a real **Iteration** field (with dates), create it in the UI and I can add iteration-mapping to the script.
- **Rate limits:** the script paces itself and backs off on secondary limits; ~129 rows take a few minutes.
- **Labels** are created on first use by GitHub if missing (default color).

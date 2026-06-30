#!/usr/bin/env python3
"""
import_to_github_project.py
===========================

Populate a GitHub **Projects V2** board from `nereus_backlog.csv`:
  1. create one issue per CSV row (title `[ID] Title`, body from Description/Acceptance/hours),
  2. add each issue to the Project,
  3. set the Project's custom fields (hours, Assignee, Milestone, Status, Theme, …).

Off-the-shelf CSV→issue tools create issues but usually don't set Projects-V2
custom fields. This does, via the GraphQL API. Stdlib only — no pip install.

------------------------------------------------------------------------------
PREREQUISITES (what you provide)
------------------------------------------------------------------------------
1. A token in the environment — never pass it on the command line:
       export GITHUB_TOKEN=ghp_xxx
   Scopes: classic PAT -> `repo` + `project`
           fine-grained -> Issues: Read & write, Projects: Read & write
2. The Project owner + number (from the URL .../<owner>/projects/<NUMBER>).
3. A repo to hold the issues (owner/repo).

------------------------------------------------------------------------------
USAGE
------------------------------------------------------------------------------
  # 1) Always dry-run first — builds every payload, hits no API, writes nothing:
  python import_to_github_project.py --csv nereus_backlog.csv \
      --owner my-org --owner-type org --project-number 7 \
      --repo my-org/nereus --dry-run

  # 2) Real run (creates fields if missing, creates issues, sets fields):
  python import_to_github_project.py --csv nereus_backlog.csv \
      --owner my-org --owner-type org --project-number 7 \
      --repo my-org/nereus --create-fields

  # Re-run any time — idempotent via .import_state.json (updates, never duplicates).

Flags:
  --owner-type {org,user}   project owner kind (default org)
  --create-fields           create missing Project fields (single-select/number/text)
  --labels                  also add issue labels (theme/assignee/milestone/product)
  --assignee-map FILE       JSON {"Will":"willgh","Parker":"parkergh"} -> native assignees
  --only ID1,ID2            limit to specific CSV IDs (testing)
  --dry-run                 print planned actions, touch nothing

The script is conservative about rate limits (small pauses, retry on secondary
limits). For ~129 rows expect a few minutes.
"""
import argparse, csv, json, os, sys, time, urllib.request, urllib.error, urllib.parse

API = "https://api.github.com"
GQL = "https://api.github.com/graphql"
STATE_FILE = ".import_state.json"

# ---- CSV column -> Project field mapping -----------------------------------
SINGLE_SELECT = ["Product", "Repo", "Assignee", "Skill", "Theme", "Phase", "Milestone", "Status"]
NUMBER        = ["Dev_hrs", "TestDev_hrs", "QA_hrs", "Deploy_hrs", "Buffer_hrs", "Total_hrs", "Remaining_hrs"]
TEXT          = ["Dependencies"]
# Title/Description/Acceptance go into the issue body, not project fields.

# ---------------------------------------------------------------------------
def die(msg): print(f"ERROR: {msg}", file=sys.stderr); sys.exit(1)

def http(url, method="GET", token=None, body=None, gql=False, retries=4):
    data = json.dumps(body).encode() if body is not None else None
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "nereus-backlog-importer",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req) as r:
                return json.loads(r.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            payload = e.read().decode()
            # secondary rate limit / abuse detection -> back off and retry
            if e.code in (403, 429) and ("secondary rate" in payload.lower() or "rate limit" in payload.lower()):
                wait = 2 ** (attempt + 3)
                print(f"  rate-limited; sleeping {wait}s…"); time.sleep(wait); continue
            die(f"{method} {url} -> {e.code}\n{payload}")
        except urllib.error.URLError as e:
            die(f"network error reaching {url}: {e}")
    die("exhausted retries (rate limit)")

def gql(query, variables, token):
    out = http(GQL, "POST", token=token, body={"query": query, "variables": variables}, gql=True)
    if "errors" in out:
        die("GraphQL: " + json.dumps(out["errors"], indent=2))
    return out["data"]

# ---------------------------------------------------------------------------
def load_state():
    return json.load(open(STATE_FILE)) if os.path.exists(STATE_FILE) else {}
def save_state(s):
    json.dump(s, open(STATE_FILE, "w"), indent=2)

def get_project(owner, owner_type, number, token):
    root = "organization" if owner_type == "org" else "user"
    q = f"""
    query($login:String!,$number:Int!){{
      {root}(login:$login){{ projectV2(number:$number){{
        id title
        fields(first:60){{ nodes{{
          ... on ProjectV2FieldCommon {{ id name dataType }}
          ... on ProjectV2SingleSelectField {{ id name options {{ id name }} }}
        }} }}
      }} }}
    }}"""
    d = gql(q, {"login": owner, "number": int(number)}, token)
    proj = (d.get(root) or {}).get("projectV2")
    if not proj: die(f"Project #{number} not found for {owner_type} '{owner}' (check token scopes).")
    fields = {}
    for f in proj["fields"]["nodes"]:
        if not f: continue
        fields[f["name"]] = {"id": f["id"], "dataType": f.get("dataType"),
                             "options": {o["name"]: o["id"] for o in f.get("options", [])}}
    return proj["id"], fields

def create_field(project_id, name, data_type, options, token):
    # data_type: SINGLE_SELECT | NUMBER | TEXT
    if data_type == "SINGLE_SELECT":
        opts = [{"name": (o or "—")[:100], "color": "GRAY", "description": ""} for o in options]
        q = """mutation($p:ID!,$n:String!,$o:[ProjectV2SingleSelectFieldOptionInput!]!){
          createProjectV2Field(input:{projectId:$p,dataType:SINGLE_SELECT,name:$n,singleSelectOptions:$o}){
            projectV2Field{ ... on ProjectV2SingleSelectField{ id name options{ id name } } } } }"""
        d = gql(q, {"p": project_id, "n": name, "o": opts}, token)
        f = d["createProjectV2Field"]["projectV2Field"]
        return {"id": f["id"], "dataType": "SINGLE_SELECT", "options": {o["name"]: o["id"] for o in f["options"]}}
    else:
        q = """mutation($p:ID!,$n:String!,$t:ProjectV2CustomFieldType!){
          createProjectV2Field(input:{projectId:$p,dataType:$t,name:$n}){
            projectV2Field{ ... on ProjectV2FieldCommon{ id name dataType } } } }"""
        d = gql(q, {"p": project_id, "n": name, "t": data_type}, token)
        f = d["createProjectV2Field"]["projectV2Field"]
        return {"id": f["id"], "dataType": data_type, "options": {}}

def ensure_fields(project_id, fields, rows, token, create, dry):
    """Make sure every mapped field exists; create if --create-fields."""
    needed = []
    for col in SINGLE_SELECT:
        opts = sorted({(r.get(col) or "").strip() for r in rows if (r.get(col) or "").strip()})
        needed.append((col, "SINGLE_SELECT", opts))
    for col in NUMBER: needed.append((col, "NUMBER", None))
    for col in TEXT:   needed.append((col, "TEXT", None))

    for name, dtype, opts in needed:
        if name in fields:
            # for single-selects, create any missing options
            if dtype == "SINGLE_SELECT":
                missing = [o for o in opts if o not in fields[name]["options"]]
                if missing:
                    print(f"  field '{name}' missing options: {missing} "
                          f"(add them in the Project UI, or recreate the field)")
            continue
        if not create:
            die(f"Project field '{name}' missing. Re-run with --create-fields, or add it in the UI.")
        print(f"  creating field '{name}' ({dtype})" + (f" with {len(opts)} options" if opts else ""))
        if dry:
            fields[name] = {"id": f"DRY-{name}", "dataType": dtype,
                            "options": {o: f"DRY-{o}" for o in (opts or [])}}
        else:
            fields[name] = create_field(project_id, name, dtype, opts or [], token)
            time.sleep(0.3)
    return fields

def issue_body(r):
    L = []
    if r.get("Description"): L += [r["Description"], ""]
    if r.get("Acceptance"):  L += [f"**Acceptance:** {r['Acceptance']}", ""]
    meta = [("Theme", r.get("Theme")), ("Product", r.get("Product")), ("Repo", r.get("Repo")),
            ("Assignee", r.get("Assignee")), ("Milestone", r.get("Milestone")),
            ("Status", r.get("Status")), ("Phase", r.get("Phase")),
            ("Dependencies", r.get("Dependencies"))]
    L.append("| field | value |"); L.append("|---|---|")
    for k, v in meta:
        if v: L.append(f"| {k} | {v} |")
    hrs = [c for c in NUMBER if r.get(c)]
    if hrs:
        L.append(f"| Hours (Dev/TestDev/QA/Deploy/Buffer = Total · Remaining) | "
                 f"{r.get('Dev_hrs','-')}/{r.get('TestDev_hrs','-')}/{r.get('QA_hrs','-')}/"
                 f"{r.get('Deploy_hrs','-')}/{r.get('Buffer_hrs','-')} = "
                 f"{r.get('Total_hrs','-')} · {r.get('Remaining_hrs','-')} |")
    L += ["", f"<!-- nereus-id:{r['ID']} -->"]   # marker for idempotency / search
    return "\n".join(L)

def find_issue_by_marker(repo, item_id, token):
    owner, name = repo.split("/")
    q = f'repo:{owner}/{name} in:body "nereus-id:{item_id}"'
    url = f"{API}/search/issues?q=" + urllib.parse.quote(q)
    res = http(url, token=token)
    for it in res.get("items", []):
        if f"nereus-id:{item_id}" in (it.get("body") or ""):
            return it
    return None

def create_issue(repo, r, labels, assignee_map, token):
    owner, name = repo.split("/")
    body = {"title": f"[{r['ID']}] {r['Title']}", "body": issue_body(r)}
    if labels:
        th = (r.get("Theme") or "").split(" ")[0]
        body["labels"] = [f"theme:{th}", f"assignee:{r.get('Assignee','')}",
                          f"milestone:{r.get('Milestone','')}", f"product:{r.get('Product','')}"]
        body["labels"] = [l for l in body["labels"] if l.split(":")[1]]
    if assignee_map and r.get("Assignee") in assignee_map:
        body["assignees"] = [assignee_map[r["Assignee"]]]
    return http(f"{API}/repos/{owner}/{name}/issues", "POST", token=token, body=body)

def add_to_project(project_id, content_node_id, token):
    q = """mutation($p:ID!,$c:ID!){ addProjectV2ItemById(input:{projectId:$p,contentId:$c}){ item{ id } } }"""
    return gql(q, {"p": project_id, "c": content_node_id}, token)["addProjectV2ItemById"]["item"]["id"]

def set_field(project_id, item_id, field, raw, token):
    dt = field["dataType"]
    if dt == "SINGLE_SELECT":
        oid = field["options"].get((raw or "").strip())
        if not oid: return
        value = {"singleSelectOptionId": oid}
    elif dt == "NUMBER":
        try: value = {"number": float(raw)}
        except (TypeError, ValueError): return
    else:
        if not (raw or "").strip(): return
        value = {"text": str(raw)}
    q = """mutation($p:ID!,$i:ID!,$f:ID!,$v:ProjectV2FieldValue!){
      updateProjectV2ItemFieldValue(input:{projectId:$p,itemId:$i,fieldId:$f,value:$v}){ projectV2Item{ id } } }"""
    gql(q, {"p": project_id, "i": item_id, "f": field["id"], "v": value}, token)

# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Import backlog CSV into a GitHub Projects V2 board.")
    ap.add_argument("--csv", default="nereus_backlog.csv")
    ap.add_argument("--owner", required=True, help="org or user login that owns the Project")
    ap.add_argument("--owner-type", choices=["org", "user"], default="org")
    ap.add_argument("--project-number", required=True, type=int)
    ap.add_argument("--repo", required=True, help="owner/repo to create issues in")
    ap.add_argument("--create-fields", action="store_true")
    ap.add_argument("--labels", action="store_true")
    ap.add_argument("--assignee-map", help="JSON file mapping Assignee -> github username")
    ap.add_argument("--only", help="comma-separated CSV IDs to limit to")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token and not a.dry_run:
        die("set GITHUB_TOKEN in the environment (never on the command line).")
    token = token or "DRY"

    rows = list(csv.DictReader(open(a.csv)))
    if a.only:
        keep = set(a.only.split(",")); rows = [r for r in rows if r["ID"] in keep]
    if not rows: die("no rows to import.")
    assignee_map = json.load(open(a.assignee_map)) if a.assignee_map else None
    print(f"{len(rows)} rows from {a.csv}" + ("  [DRY-RUN]" if a.dry_run else ""))

    if a.dry_run:
        # Offline: validate parsing + payload construction, no API calls.
        fields = {}
        fields = ensure_fields("DRY-PROJECT", fields, rows, token, create=True, dry=True)
        print(f"\nWould ensure {len(fields)} project fields: {', '.join(fields)}")
        print("\nSample issue (first row):")
        print(f"  title: [{rows[0]['ID']}] {rows[0]['Title']}")
        print("  body:\n" + "\n".join("    " + l for l in issue_body(rows[0]).splitlines()))
        print(f"\nWould create/sync {len(rows)} issues, add each to project #{a.project_number}, "
              f"and set {len(SINGLE_SELECT+NUMBER+TEXT)} fields per item.")
        # quick integrity check: distinct option counts
        for col in SINGLE_SELECT:
            vals = sorted({(r.get(col) or '').strip() for r in rows if (r.get(col) or '').strip()})
            print(f"  {col}: {len(vals)} options -> {vals}")
        return

    project_id, fields = get_project(a.owner, a.owner_type, a.project_number, token)
    print(f"project: {project_id}")
    fields = ensure_fields(project_id, fields, rows, token, a.create_fields, dry=False)

    state = load_state()
    for i, r in enumerate(rows, 1):
        rid = r["ID"]; st = state.get(rid, {})
        print(f"[{i}/{len(rows)}] {rid} — {r['Title'][:48]}")
        # 1) issue (idempotent: state file, else search by marker)
        if "issue_node_id" not in st:
            found = find_issue_by_marker(a.repo, rid, token)
            if found:
                st = {"number": found["number"], "issue_node_id": found["node_id"], "url": found["html_url"]}
                print(f"    found existing issue #{found['number']}")
            else:
                iss = create_issue(a.repo, r, a.labels, assignee_map, token)
                st = {"number": iss["number"], "issue_node_id": iss["node_id"], "url": iss["html_url"]}
                print(f"    created issue #{iss['number']}")
                time.sleep(0.6)
        # 2) add to project
        if "item_id" not in st:
            st["item_id"] = add_to_project(project_id, st["issue_node_id"], token)
            time.sleep(0.3)
        # 3) set fields
        for col in SINGLE_SELECT + NUMBER + TEXT:
            if col in fields and r.get(col) not in (None, ""):
                set_field(project_id, st["item_id"], fields[col], r[col], token)
        state[rid] = st; save_state(state)
    print(f"\nDone. State in {STATE_FILE} (re-run to update without duplicating).")

if __name__ == "__main__":
    import urllib.parse
    main()

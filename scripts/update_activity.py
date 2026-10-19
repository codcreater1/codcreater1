import json, re, subprocess

USER = "codcreater1"
raw = subprocess.run(["gh", "api", f"users/{USER}/events/public?per_page=100"],
                     capture_output=True, text=True, check=True).stdout
events = json.loads(raw)

rows, seen = [], set()
SKIP = (f"{USER}/{USER}", f"{USER}/Murat-Can-Nergiz")
for e in events:
    repo = e["repo"]["name"]
    if repo in SKIP:
        continue
    link = f"[`{repo.split('/')[1]}`](https://github.com/{repo})"
    date = e["created_at"][:10]
    if e["type"] == "PushEvent":
        for c in reversed(e["payload"].get("commits", [])):
            if c["sha"] in seen:
                continue
            seen.add(c["sha"])
            rows.append(f"| {link} | {c['message'].splitlines()[0][:70].replace('|', '/')} | {date} |")
    elif e["type"] == "PullRequestEvent":
        pr = e["payload"]["pull_request"]
        if pr["number"] in seen or e["payload"]["action"] not in ("opened", "closed"):
            continue
        seen.add(pr["number"])
        state = "merged" if pr.get("merged") else e["payload"]["action"]
        rows.append(f"| {link} | PR {state}: {pr['title'][:60].replace('|', '/')} | {date} |")
    if len(rows) >= 5:
        break

body = ("| Repo | Commit | Date |\n|---|---|---|\n" + "\n".join(rows[:5])) if rows else "_No recent public activity._"
s = open("README.md", encoding="utf-8").read()
s = re.sub(r"(<!--ACTIVITY:START-->).*?(<!--ACTIVITY:END-->)",
           lambda m: f"{m.group(1)}\n{body}\n{m.group(2)}", s, flags=re.S)
open("README.md", "w", encoding="utf-8").write(s)

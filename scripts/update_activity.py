import json, re, subprocess

USER = "codcreater1"
raw = subprocess.run(["gh", "api", f"users/{USER}/events/public?per_page=100"],
                     capture_output=True, text=True, check=True).stdout
events = json.loads(raw)

rows, seen = [], set()
for e in events:
    if e["type"] != "PushEvent":
        continue
    repo = e["repo"]["name"]
    if repo in (f"{USER}/{USER}", f"{USER}/Murat-Can-Nergiz"):
        continue
    for c in reversed(e["payload"].get("commits", [])):
        if c["sha"] in seen:
            continue
        seen.add(c["sha"])
        msg = c["message"].splitlines()[0][:70].replace("|", "/")
        rows.append(f"| [`{repo.split('/')[1]}`](https://github.com/{repo}) | {msg} | {e['created_at'][:10]} |")
    if len(rows) >= 5:
        break

body = ("| Repo | Commit | Date |\n|---|---|---|\n" + "\n".join(rows[:5])) if rows else "_No recent public activity._"
s = open("README.md", encoding="utf-8").read()
s = re.sub(r"(<!--ACTIVITY:START-->).*?(<!--ACTIVITY:END-->)",
           lambda m: f"{m.group(1)}\n{body}\n{m.group(2)}", s, flags=re.S)
open("README.md", "w", encoding="utf-8").write(s)

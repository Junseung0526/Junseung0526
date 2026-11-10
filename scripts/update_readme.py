"""Refresh the 'Recent Projects' block of README.md from the GitHub API."""
import json, os, re, urllib.request

USER = os.environ.get("GH_USER", "Junseung0526")
LIMIT = 5
START, END = "<!-- RECENT:START -->", "<!-- RECENT:END -->"


def fetch():
    req = urllib.request.Request(
        f"https://api.github.com/users/{USER}/repos?type=owner&sort=pushed&per_page=30",
        headers={"Accept": "application/vnd.github+json",
                 "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def render(repos):
    rows = ["| Repository | Description | Language | Last push |", "|---|---|---|---|"]
    for r in repos:
        desc = (r["description"] or "-").replace("|", "/")
        rows.append(f"| [{r['name']}]({r['html_url']}) | {desc} | {r['language'] or '-'} | {r['pushed_at'][:10]} |")
    return "\n".join(rows)


def main():
    repos = [r for r in fetch() if not r["fork"] and not r["archived"] and r["name"] != USER][:LIMIT]
    if not repos:  # never blank the section on an empty/failed listing
        return
    s = open("README.md", encoding="utf-8").read()
    new = re.sub(re.escape(START) + r".*?" + re.escape(END),
                 lambda _: f"{START}\n{render(repos)}\n{END}", s, flags=re.S)
    assert new != s or START in s, "markers missing"
    open("README.md", "w", encoding="utf-8").write(new)


if __name__ == "__main__":
    main()

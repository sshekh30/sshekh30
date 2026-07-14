#!/usr/bin/env python3
"""
Fetches GitHub stats (repos, all-time commits, lines of code added/deleted)
and writes them into dark_mode.svg / light_mode.svg by element id.

Env vars:
  GH_TOKEN  - a classic Personal Access Token with scopes: repo, read:user
  LOGIN     - your GitHub username (e.g. sshekh30)

Idempotent: replaces the text inside <tspan id="..."> each run.
Caches per-repo additions/deletions in cache/loc_cache.json to stay fast
and within rate limits.
"""
import os
import re
import sys
import json
import time
import datetime
import urllib.request
import urllib.error

TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
LOGIN = os.environ.get("LOGIN", "sshekh30")
API = "https://api.github.com/graphql"
SVGS = ["dark_mode.svg", "light_mode.svg"]
CACHE_DIR = "cache"
CACHE_FILE = os.path.join(CACHE_DIR, "loc_cache.json")

if not TOKEN:
    sys.exit("ERROR: set GH_TOKEN (classic PAT with repo + read:user scopes).")


def gql(query, variables, retries=3):
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(API, data=body, method="POST")
    req.add_header("Authorization", f"bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode())
            if "errors" in data:
                raise RuntimeError(data["errors"])
            return data["data"]
        except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as e:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))


def get_user():
    q = """query($login:String!){ user(login:$login){ id createdAt
             repositories(ownerAffiliations:OWNER, isFork:false){ totalCount } } }"""
    u = gql(q, {"login": LOGIN})["user"]
    return u["id"], u["createdAt"], u["repositories"]["totalCount"]


def all_time_commits(created_at):
    """Sum totalCommitContributions year-by-year since account creation."""
    start = datetime.datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    now = datetime.datetime.now(datetime.timezone.utc)
    total = 0
    q = """query($login:String!,$from:DateTime!,$to:DateTime!){
             user(login:$login){ contributionsCollection(from:$from,to:$to){
               totalCommitContributions restrictedContributionsCount } } }"""
    year_start = start
    while year_start < now:
        year_end = min(year_start + datetime.timedelta(days=365), now)
        c = gql(q, {"login": LOGIN,
                    "from": year_start.isoformat(),
                    "to": year_end.isoformat()})["user"]["contributionsCollection"]
        total += c["totalCommitContributions"] + c["restrictedContributionsCount"]
        year_start = year_end
    return total


def list_repos():
    q = """query($login:String!,$cursor:String){
             user(login:$login){ repositories(first:100, after:$cursor,
               ownerAffiliations:OWNER, isFork:false){
                 pageInfo{ hasNextPage endCursor }
                 nodes{ nameWithOwner
                   defaultBranchRef{ target{ ... on Commit { history{ totalCount } } } } } } } }"""
    repos, cursor = [], None
    while True:
        page = gql(q, {"login": LOGIN, "cursor": cursor})["user"]["repositories"]
        for n in page["nodes"]:
            ref = n.get("defaultBranchRef")
            count = ref["target"]["history"]["totalCount"] if ref else 0
            repos.append((n["nameWithOwner"], count))
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]
    return repos


def repo_loc(owner, name, author_id):
    """Sum additions/deletions for commits authored by the user."""
    q = """query($owner:String!,$name:String!,$id:ID!,$cursor:String){
             repository(owner:$owner,name:$name){ defaultBranchRef{ target{
               ... on Commit { history(first:100, after:$cursor, author:{id:$id}){
                 pageInfo{ hasNextPage endCursor }
                 nodes{ additions deletions } } } } } } }"""
    add = dele = 0
    cursor = None
    while True:
        ref = gql(q, {"owner": owner, "name": name, "id": author_id,
                      "cursor": cursor})["repository"]["defaultBranchRef"]
        if not ref:
            break
        hist = ref["target"]["history"]
        for c in hist["nodes"]:
            add += c["additions"]
            dele += c["deletions"]
        if not hist["pageInfo"]["hasNextPage"]:
            break
        cursor = hist["pageInfo"]["endCursor"]
    return add, dele


def load_cache():
    try:
        return json.load(open(CACHE_FILE))
    except Exception:
        return {}


def save_cache(cache):
    os.makedirs(CACHE_DIR, exist_ok=True)
    json.dump(cache, open(CACHE_FILE, "w"), indent=0)


def compute_loc(author_id, repos):
    cache = load_cache()
    total_add = total_del = 0
    for full_name, commit_count in repos:
        owner, name = full_name.split("/", 1)
        entry = cache.get(full_name)
        # cache valid only if commit count is unchanged
        if entry and entry.get("commits") == commit_count:
            total_add += entry["add"]
            total_del += entry["del"]
            continue
        add, dele = repo_loc(owner, name, author_id)
        cache[full_name] = {"commits": commit_count, "add": add, "del": dele}
        total_add += add
        total_del += dele
    save_cache(cache)
    return total_add, total_del


def fmt(n):
    return f"{n:,}"


def write_svgs(values):
    for path in SVGS:
        svg = open(path, encoding="utf-8").read()
        for el_id, val in values.items():
            svg = re.sub(
                rf'(<tspan[^>]*id="{el_id}"[^>]*>)[^<]*(</tspan>)',
                lambda m: m.group(1) + val + m.group(2),
                svg,
            )
        open(path, "w", encoding="utf-8").write(svg)
        print(f"updated {path}")


def main():
    print(f"Fetching stats for {LOGIN} ...")
    author_id, created, repo_count = get_user()
    commits = all_time_commits(created)
    repos = list_repos()
    add, dele = compute_loc(author_id, repos)
    net = add - dele
    values = {
        "repo_data": fmt(repo_count),
        "commit_data": fmt(commits),
        "loc_data": fmt(net),
        "loc_add_data": fmt(add),
        "loc_del_data": fmt(dele),
    }
    print("Stats:", values)
    write_svgs(values)


if __name__ == "__main__":
    main()

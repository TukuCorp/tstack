#!/usr/bin/env python3
"""wide_pass.py - deterministic quota-free wide pass for `/research --depth exhaustive`.

Executes all four bucket backends without depending on the host environment's own search/browse
tools:
  - academia : OpenAlex (keyless HTTP; up to 200 works per call)
  - github   : `gh search repos` / `gh search code`
  - industry : Firecrawl search (requires FIRECRAWL_API_KEY in the environment)
  - web      : Firecrawl search (requires FIRECRAWL_API_KEY in the environment)

It appends candidate rows to a JSONL ledger, deduping against whatever is already there, and prints a
JSON summary on stdout, including a `firecrawl` status field. When FIRECRAWL_API_KEY is unset or the
API reports it invalid or out of credits, industry/web are skipped here and must be filled by this
environment's fallback backend within its own budget, appending to the SAME ledger.

Stdlib only (urllib + subprocess). Safe to call repeatedly on the same ledger.

Example:
  python wide_pass.py \
    --ledger research/sources/2026-06-20_vietnam-power-market.sources.jsonl \
    --academia-target 62 \
    --academia-query "vietnam electricity tariff renewable" \
    --academia-query "vietnam direct power purchase agreement" \
    --github-target 62 \
    --github-repo-query "vietnam electricity tariff" \
    --github-code-query "EVN tariff" \
    --industry-target 62 \
    --industry-query "vietnam electricity tariff report site:*.gov" \
    --web-target 62 \
    --web-query "vietnam direct power purchase agreement"
"""
import argparse, json, os, re, subprocess, sys, time, urllib.parse, urllib.request, urllib.error

DEF_MAILTO = "<EMAIL>"


def norm_url(u):
    if not u:
        return ""
    u = u.strip().lower()
    u = re.sub(r"^https?://(www\.)?", "", u)
    u = re.sub(r"[?#].*$", "", u)
    u = re.sub(r"/+$", "", u)
    return u


def load_existing(path):
    """Return (seen_urls, max_counter_per_bucket) from an existing ledger."""
    seen, counters = set(), {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                seen.add(norm_url(row.get("url", "")))
                b = row.get("bucket", "")
                m = re.search(r"-(\d+)$", str(row.get("id", "")))
                if m:
                    counters[b] = max(counters.get(b, 0), int(m.group(1)))
    return seen, counters


def openalex(terms, mailto, per_page=200, timeout=30):
    q = urllib.parse.quote(terms)
    url = f"https://api.openalex.org/works?search={q}&per-page={per_page}&mailto={mailto}"
    req = urllib.request.Request(url, headers={"User-Agent": f"research-wide-pass ({mailto})"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r).get("results", [])


def gh_search(kind, terms, limit, fields, timeout=60):
    try:
        out = subprocess.run(
            ["gh", "search", kind, terms, "--limit", str(limit), "--json", fields],
            capture_output=True, text=True, timeout=timeout)
        if out.returncode != 0:
            return [], (out.stderr or "").strip()[:200]
        return json.loads(out.stdout or "[]"), ""
    except FileNotFoundError:
        return [], "gh CLI not found on PATH"
    except Exception as e:  # noqa: BLE001
        return [], f"{type(e).__name__}: {e}"


def firecrawl_search(terms, api_key, limit=30, timeout=60):
    """Firecrawl /v2/search. Returns (results, error). Never raises."""
    def call(lim):
        body = json.dumps({"query": terms, "limit": lim, "sources": ["web"]}).encode("utf-8")
        req = urllib.request.Request(
            "https://api.firecrawl.dev/v2/search", data=body, method="POST",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)

    try:
        payload = call(limit)
    except urllib.error.HTTPError as e:
        if e.code == 400 and limit != 10:
            try:
                payload = call(10)
            except urllib.error.HTTPError as e2:
                return [], f"HTTP {e2.code}"
            except Exception as e2:  # noqa: BLE001
                return [], f"{type(e2).__name__}: {e2}"
        elif e.code == 401:
            return [], "invalid FIRECRAWL_API_KEY"
        elif e.code == 402:
            return [], "credits exhausted"
        elif e.code == 429:
            return [], "rate limited"
        else:
            return [], f"HTTP {e.code}"
    except Exception as e:  # noqa: BLE001
        return [], f"{type(e).__name__}: {e}"

    return (payload.get("data") or {}).get("web") or [], ""


def main():
    ap = argparse.ArgumentParser(
        description="Deterministic quota-free wide pass (academia, github, industry, web).")
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--mailto", default=DEF_MAILTO)
    ap.add_argument("--oversample", type=float, default=1.5,
                    help="gather up to oversample*target per bucket (saturation slack)")
    ap.add_argument("--academia-target", type=int, default=0)
    ap.add_argument("--academia-query", action="append", default=[])
    ap.add_argument("--github-target", type=int, default=0)
    ap.add_argument("--github-repo-query", action="append", default=[])
    ap.add_argument("--github-code-query", action="append", default=[])
    ap.add_argument("--industry-target", type=int, default=0)
    ap.add_argument("--industry-query", action="append", default=[])
    ap.add_argument("--web-target", type=int, default=0)
    ap.add_argument("--web-query", action="append", default=[])
    args = ap.parse_args()

    os.makedirs(os.path.dirname(os.path.abspath(args.ledger)) or ".", exist_ok=True)
    seen, counters = load_existing(args.ledger)
    new_rows, errors = [], []

    def next_id(bucket):
        counters[bucket] = counters.get(bucket, 0) + 1
        return f"{bucket[:2]}-{counters[bucket]:03d}"

    def add(bucket, url, title, tier, signal, via):
        k = norm_url(url)
        if not k or k in seen:
            return False
        seen.add(k)
        new_rows.append({
            "id": next_id(bucket), "bucket": bucket, "url": url, "title": (title or "")[:200],
            "tier": tier, "status": "candidate", "pass": "wide",
            "discovered_via": via, "signal": signal})
        return True

    # ---- academia via OpenAlex (quota-free) ----
    a_cap = int(round(args.academia_target * args.oversample))
    a_count, per_query = 0, {}
    for terms in args.academia_query:
        if args.academia_target and a_count >= a_cap:
            break
        try:
            res = openalex(terms, args.mailto)
        except Exception as e:  # noqa: BLE001
            errors.append(f"openalex [{terms}]: {type(e).__name__}: {e}")
            res = []
        added = 0
        for w in res:
            if args.academia_target and a_count >= a_cap:
                break
            url = w.get("doi") or w.get("id") or ""
            oa = (w.get("open_access") or {}).get("is_oa", False)
            if add("academia", url, w.get("display_name"), 3,
                   {"year": w.get("publication_year"), "citations": w.get("cited_by_count", 0),
                    "oa": oa}, f'openalex search="{terms}"'):
                a_count += 1
                added += 1
        per_query[terms] = added
        time.sleep(0.3)

    # ---- github via gh ----
    g_cap = int(round(args.github_target * args.oversample))
    g_count = 0
    for terms in args.github_repo_query:
        if args.github_target and g_count >= g_cap:
            break
        rows, err = gh_search("repos", terms, 60,
                              "fullName,description,stargazersCount,updatedAt,url,license")
        if err:
            errors.append(f'gh repos [{terms}]: {err}')
        for r in rows:
            if args.github_target and g_count >= g_cap:
                break
            if add("github", r.get("url", ""), r.get("fullName", ""), 2,
                   {"stars": r.get("stargazersCount"), "updated": str(r.get("updatedAt"))[:7]},
                   f'gh search repos "{terms}"'):
                g_count += 1
        time.sleep(0.5)
    for terms in args.github_code_query:
        if args.github_target and g_count >= g_cap:
            break
        rows, err = gh_search("code", terms, 30, "repository,path,url")
        if err:
            errors.append(f'gh code [{terms}]: {err}')
        for r in rows:
            if args.github_target and g_count >= g_cap:
                break
            repo = (r.get("repository") or {}).get("fullName", "")
            if add("github", r.get("url", ""), f"{repo}:{r.get('path', '')}", 3, {},
                   f'gh search code "{terms}"'):
                g_count += 1
        time.sleep(0.5)

    # ---- industry + web via Firecrawl search (requires FIRECRAWL_API_KEY) ----
    fc_key = os.environ.get("FIRECRAWL_API_KEY", "")
    wants_firecrawl = bool(args.industry_target or args.web_target
                            or args.industry_query or args.web_query)
    if not wants_firecrawl:
        firecrawl_status = "skipped"
    elif not fc_key:
        errors.append("firecrawl: FIRECRAWL_API_KEY not set")
        firecrawl_status = "unavailable: no key"
    else:
        firecrawl_status = "ok"
        fc_specs = [("industry", args.industry_target, args.industry_query, 3),
                    ("web", args.web_target, args.web_query, 4)]
        for bucket, target, queries, tier in fc_specs:
            if firecrawl_status != "ok":
                break
            cap = int(round(target * args.oversample))
            count = 0
            for terms in queries[:8]:
                if target and count >= cap:
                    break
                results, err = firecrawl_search(terms, fc_key)
                if err in ("invalid FIRECRAWL_API_KEY", "credits exhausted"):
                    errors.append(f'firecrawl [{bucket}] [{terms}]: {err}')
                    firecrawl_status = f"unavailable: {err}"
                    break
                if err:
                    errors.append(f'firecrawl [{bucket}] [{terms}]: {err}')
                for item in results:
                    if target and count >= cap:
                        break
                    if add(bucket, item.get("url", ""), item.get("title", ""), tier,
                           {"desc": (item.get("description") or "")[:100]},
                           f'firecrawl search="{terms}"'):
                        count += 1
                time.sleep(0.5)

    with open(args.ledger, "a", encoding="utf-8") as f:
        for row in new_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    by_bucket = {}
    for r in new_rows:
        by_bucket[r["bucket"]] = by_bucket.get(r["bucket"], 0) + 1

    if firecrawl_status == "ok":
        note = "All four buckets script-filled. Proceed to dedupe/tiering and the deep pass."
    elif firecrawl_status.startswith("unavailable"):
        note = (f"Firecrawl unavailable ({firecrawl_status[len('unavailable: '):]}): fill industry + "
                f"web via this environment's fallback backend (<=8 queries/fetches each), appending "
                f"to this same ledger.")
    else:
        note = ("Quota-free academia/github done. Fill industry + web via this environment's search "
                "backend (Firecrawl, or the fallback if unavailable), appending to this same ledger.")

    print(json.dumps({
        "ledger": args.ledger,
        "new_rows": len(new_rows),
        "by_bucket": by_bucket,
        "academia_per_query": per_query,
        "targets": {"academia": args.academia_target, "github": args.github_target,
                    "industry": args.industry_target, "web": args.web_target},
        "firecrawl": firecrawl_status,
        "errors": errors,
        "note": note,
    }, indent=2))


if __name__ == "__main__":
    main()

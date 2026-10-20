#!/usr/bin/env python3
"""wide_pass.py - deterministic quota-free wide pass for `/research --depth exhaustive`.

Executes all four bucket backends without depending on the host environment's own search/browse
tools:
  - academia : OpenAlex (keyless HTTP; up to 200 works per call)
  - github   : `gh search repos` / `gh search code`
  - industry : Firecrawl search (FIRECRAWL_API_KEY), else Perplexity search
  - web      : Firecrawl search (FIRECRAWL_API_KEY), else Perplexity search

Perplexity runs the Search API's "fast" preset, either directly (PERPLEXITY_API_KEY) or through a
local Hermes Agent install's own Perplexity provider (its Nous Portal gateway or its key). Each query
uses the first engine still available, so Firecrawl running out of credits mid-run hands the remaining
queries to Perplexity.

It appends candidate rows to a JSONL ledger, deduping against whatever is already there, and prints a
JSON summary on stdout, including `firecrawl` and `perplexity` status fields. When neither engine is
available, industry/web are skipped here and must be filled by this environment's fallback backend
within its own budget, appending to the SAME ledger.

`--merge FILE` (repeatable) folds rows written by hermes_worker.py into the ledger with the same
dedupe and id sequence, as `pass: "agentic"` candidates.

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

# OpenAlex "polite pool" contact. Set OPENALEX_MAILTO to override; the fallback keeps old runs working.
DEF_MAILTO = os.environ.get("OPENALEX_MAILTO") or "<EMAIL>"


_ARXIV_RE = re.compile(r"^(?:export\.)?arxiv\.org/(?:abs|pdf)/(.+?)(?:v\d+)?(?:\.pdf)?$")


def norm_url(u):
    """Dedup key: lowercase host+path without scheme, www, query, fragment, or trailing slash.
    DOIs (doi.org, dx.doi.org, `doi:` or bare `10.x/...`) become `doi.org/<doi>`; arXiv abs/pdf/
    version variants and arXiv DOIs (10.48550/arxiv.<id>) become `arxiv.org/abs/<id>`."""
    if not u:
        return ""
    u = u.strip().lower()
    u = re.sub(r"^doi:\s*", "", u)
    u = re.sub(r"^https?://", "", u)
    u = re.sub(r"^www\.", "", u)
    u = re.sub(r"[?#].*$", "", u)
    u = re.sub(r"/+$", "", u)
    u = re.sub(r"^(?:dx\.)?doi\.org/", "", u)
    if re.match(r"^10\.\d{4,9}/", u):
        m = re.match(r"^10\.48550/arxiv\.(.+)$", u)
        return f"arxiv.org/abs/{m.group(1)}" if m else f"doi.org/{u}"
    m = _ARXIV_RE.match(u)
    if m:
        return f"arxiv.org/abs/{m.group(1)}"
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


PPLX_URL = "https://api.perplexity.ai/search"
PPLX_MAX = 20
# Runs inside the Hermes venv so the search uses whatever Hermes is configured with (Nous gateway or
# its own key). Prints one marked JSON line; anything else on stdout is ignored.
_HERMES_SNIPPET = (
    "import json, sys\n"
    "from plugins.web.perplexity.provider import PerplexityWebSearchProvider\n"
    "r = PerplexityWebSearchProvider().search(sys.argv[1], limit=int(sys.argv[2]))\n"
    "print('WIDEPASS_JSON ' + json.dumps(r))\n")


def hermes_python():
    """(python, agent_dir) of a local Hermes Agent install, or (None, None)."""
    for d in [os.environ.get("HERMES_AGENT_DIR", ""),
              os.path.join(os.environ.get("LOCALAPPDATA", ""), "hermes", "hermes-agent"),
              os.path.expanduser("~/.hermes/hermes-agent")]:
        if not d or not os.path.isdir(d):
            continue
        for py in ("venv/Scripts/python.exe", "venv/bin/python", ".venv/Scripts/python.exe",
                   ".venv/bin/python"):
            if os.path.isfile(os.path.join(d, py)):
                return os.path.join(d, py), d
    return None, None


def _pplx_fatal(text):
    t = text.lower()
    return any(s in t for s in ("401", "402", "unauthorized", "invalid api key", "insufficient",
                                "quota", "not entitled", "missing", "no perplexity", "api key"))


def perplexity_search(terms, limit=PPLX_MAX, timeout=120):
    """Perplexity Search API, fast preset. Returns (results, route, error, fatal). Never raises.
    results: [{url, title, description}]; fatal=True means stop using Perplexity this run."""
    key = os.environ.get("PERPLEXITY_API_KEY", "")
    if key:
        # search_type "fast" is what Hermes' Nous gateway sends; assumed accepted by the direct API.
        body = json.dumps({"query": terms, "max_results": min(limit, PPLX_MAX),
                           "search_context_size": "low", "search_type": "fast"}).encode("utf-8")
        req = urllib.request.Request(PPLX_URL, data=body, method="POST", headers={
            "Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                res = json.load(r).get("results") or []
        except urllib.error.HTTPError as e:
            return [], "direct", f"HTTP {e.code}", e.code in (401, 402, 403)
        except Exception as e:  # noqa: BLE001
            return [], "direct", f"{type(e).__name__}: {e}", False
        return ([{"url": x.get("url", ""), "title": x.get("title", ""),
                  "description": x.get("snippet", "")} for x in res], "direct", "", False)
    py, agent_dir = hermes_python()
    if not py:
        return [], "", "no PERPLEXITY_API_KEY and no Hermes install", True
    try:
        out = subprocess.run([py, "-c", _HERMES_SNIPPET, terms, str(min(limit, PPLX_MAX))],
                             cwd=agent_dir, capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=timeout)
    except Exception as e:  # noqa: BLE001
        return [], "hermes", f"{type(e).__name__}: {e}", False
    line = next((ln for ln in out.stdout.splitlines() if ln.startswith("WIDEPASS_JSON ")), None)
    if line is None:
        err = (out.stderr or out.stdout).strip().splitlines()[-1:] or ["no output"]
        return [], "hermes", f"hermes provider failed: {err[0][:200]}", True
    r = json.loads(line[len("WIDEPASS_JSON "):])
    if not r.get("success"):
        err = str(r.get("error", "unknown error"))[:200]
        return [], "hermes", err, _pplx_fatal(err)
    return (r.get("data") or {}).get("web") or [], "hermes", "", False


BUCKETS = ("github", "academia", "industry", "web")
PROVISIONAL_TIER = {"github": 2, "academia": 3, "industry": 4, "web": 4}
_HTTP_URL = re.compile(r"^https?://[^\s/]+\.[^\s]+$")


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
    ap.add_argument("--merge", action="append", default=[],
                    help="hermes_worker.py output file to fold into the ledger (repeatable)")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(os.path.abspath(args.ledger)) or ".", exist_ok=True)
    seen, counters = load_existing(args.ledger)
    new_rows, errors = [], []

    def next_id(bucket):
        counters[bucket] = counters.get(bucket, 0) + 1
        return f"{bucket[:2]}-{counters[bucket]:03d}"

    def add(bucket, url, title, tier, signal, via, pass_="wide", hint=None):
        k = norm_url(url)
        if not k or k in seen:
            return False
        seen.add(k)
        row = {"id": next_id(bucket), "bucket": bucket, "url": url, "title": (title or "")[:200],
               "tier": tier, "status": "candidate", "pass": pass_,
               "discovered_via": via, "signal": signal}
        if hint:
            row["hint"] = str(hint)[:300]
        new_rows.append(row)
        return True

    # ---- rows from Hermes workers (hermes_worker.py), deduped like everything else ----
    merged = {}
    for path in args.merge:
        stats = {"added": 0, "duplicate": 0, "invalid": 0}
        try:
            with open(path, encoding="utf-8") as f:
                lines = f.read().splitlines()
        except OSError as e:
            errors.append(f"merge [{path}]: {e}")
            lines = []
        for line in lines:
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                stats["invalid"] += 1
                continue
            url, bucket = str(r.get("url", "")), r.get("bucket")
            if bucket not in BUCKETS or not _HTTP_URL.match(url):
                stats["invalid"] += 1
            elif add(bucket, url, r.get("title", ""), PROVISIONAL_TIER[bucket], {},
                     str(r.get("discovered_via", ""))[:200], pass_="agentic", hint=r.get("hint")):
                stats["added"] += 1
            else:
                stats["duplicate"] += 1
        merged[path] = stats

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

    # ---- industry + web: Firecrawl, else Perplexity (fast preset), per query ----
    fc_key = os.environ.get("FIRECRAWL_API_KEY", "")
    wants_search = bool(args.industry_target or args.web_target or args.industry_query or args.web_query)
    if not wants_search:
        firecrawl_status = perplexity_status = "skipped"
    else:
        firecrawl_status = "ok" if fc_key else "unavailable: no key"
        if not fc_key:
            errors.append("firecrawl: FIRECRAWL_API_KEY not set")
        perplexity_status = "not needed"
    engine_rows = {"firecrawl": 0, "perplexity": 0}

    def search(terms):
        """First available engine for one query: (engine, results). Updates engine statuses."""
        nonlocal firecrawl_status, perplexity_status
        if firecrawl_status == "ok":
            results, err = firecrawl_search(terms, fc_key)
            if err in ("invalid FIRECRAWL_API_KEY", "credits exhausted"):
                errors.append(f"firecrawl [{terms}]: {err}")
                firecrawl_status = f"unavailable: {err}"
            else:
                if err:
                    errors.append(f"firecrawl [{terms}]: {err}")
                return "firecrawl", results
        if perplexity_status.startswith("unavailable"):
            return None, []
        results, route, err, fatal = perplexity_search(terms)
        if err:
            errors.append(f"perplexity [{terms}]: {err}")
        if fatal:
            perplexity_status = f"unavailable: {err}"
            return None, []
        if not err:
            perplexity_status = "ok (direct)" if route == "direct" else "ok (hermes provider)"
        return "perplexity", results

    if wants_search:
        # industry starts at tier 4 like web: the lead promotes real lab/gov/standards reports to
        # tier 2-3 after reviewing the publisher (vendor PDFs otherwise inflate the qualified pool).
        for bucket, target, queries in [("industry", args.industry_target, args.industry_query),
                                        ("web", args.web_target, args.web_query)]:
            cap = int(round(target * args.oversample))
            count = 0
            for terms in queries[:8]:
                if target and count >= cap:
                    break
                engine, results = search(terms)
                if engine is None:
                    break
                for item in results:
                    if target and count >= cap:
                        break
                    if add(bucket, item.get("url", ""), item.get("title", ""), PROVISIONAL_TIER[bucket],
                           {"desc": (item.get("description") or "")[:100]},
                           f'{engine} search="{terms}"'):
                        count += 1
                        engine_rows[engine] += 1
                time.sleep(0.5)

    with open(args.ledger, "a", encoding="utf-8") as f:
        for row in new_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    by_bucket = {}
    for r in new_rows:
        by_bucket[r["bucket"]] = by_bucket.get(r["bucket"], 0) + 1

    if not wants_search:
        note = ("Merged worker rows. Proceed to dedupe/tiering and the deep pass." if args.merge
                else "No industry/web queries given; nothing searched for those buckets.")
    elif firecrawl_status == "ok" or perplexity_status.startswith("ok"):
        note = "All requested buckets script-filled. Proceed to dedupe/tiering and the deep pass."
    else:
        note = (f"No search engine available (firecrawl: {firecrawl_status}; perplexity: "
                f"{perplexity_status}): fill industry + web via this environment's fallback backend "
                f"(<=8 queries/fetches each), appending to this same ledger.")

    print(json.dumps({
        "ledger": args.ledger,
        "new_rows": len(new_rows),
        "by_bucket": by_bucket,
        "academia_per_query": per_query,
        "targets": {"academia": args.academia_target, "github": args.github_target,
                    "industry": args.industry_target, "web": args.web_target},
        "firecrawl": firecrawl_status,
        "perplexity": perplexity_status,
        "rows_by_engine": engine_rows,
        "merged": merged,
        "errors": errors,
        "note": note,
    }, indent=2))


if __name__ == "__main__":
    main()

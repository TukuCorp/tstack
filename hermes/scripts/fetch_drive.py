#!/usr/bin/env python3
import json, subprocess, sys

import platform
gws = "gws.cmd" if platform.system() == "Windows" else "gws"

# Drive file IDs from the earlier query
file_ids = [
    "1OlhqjKrrfF9iaRVEOeQBgAbsgMp33Pxo3VHluPSvHHM",
    "1swK_XVa6lxggzW2Lc-vnNEZkV9f_ncBa4df3UoRO9b0",
    "13A0eh6lnkUDA7y9rMb6QU2ViqhKLdG0qNeP9MhUROM0",
    "1uYRHsM_26jKwadZlvxDqew7SkCAdXSMM_HQOkdzljYc",
    "1w8YIdA5--iWcXD4vrUzcIMsqyxoZ--n3n-xdfgrNnz4",
    "1aE25NfxD3oylIMB_vBsKcffIJwriGeYzGbiAf7AHgjg",
    "1IZTDsgYaJQDLKiiEk3oq4hkIaEG3BN3P8oI86i5-SR8",
    "19564Uv717gWj5tCHUvpWgWwKvzTKIw0q6dHpUaI0kJs",
    "1kQnGzm6R-KR1gN7wInczRw2XAOh-2kxZJKZfApGKLn4",
    "1Ugg58jWvSNFgiIPaMvAoCtkXAPI2q7sNL7Ez2s0Tbtw",
    "1mXK7HSSA171zmoKlFfoHkudvfmO8QSehJuK3xK229_U",
    "1OI8kBiEZFIlOrBexv1dwQ20irsvMxQ7B1rnUAtGX2kE",
    "1CUyddNpgel7B7ScUBmDYPB9hFLeZBFfODf8BguewrkM",
    "1bmEhEWfspdW3slDh0h1r3vBstt3Dsa8K",
    "1hac71rJzM4ueCrD6odQeF9nJSuYyLeAH",
    "1h7SvnQZxwS8GruI6pjxLyUVy3niRVLqY",
    "1jdp0CBh7IIj-C38RZIEoVFNW0zf080oa",
    "1X-bP0wWdoAh1cbSd-aoWnQ6GDYwrkITu",
    "1Y2Jwjip77uvkbT8y_jf4I79scCTF6wOetju1TRt4QKw",
    "1a4MzONkijHF0BkHcu7KgZvW42z0XmEHqkfL56eJP5hU"
]

files = []
for i, fid in enumerate(file_ids):
    cmd = [gws, "drive", "files", "get", "--params",
           json.dumps({"fileId": fid, "fields": "id,name,mimeType,modifiedTime,size,owners"}),
           "--format", "json"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if out.returncode == 0:
            f = json.loads(out.stdout)
            files.append(f)
        else:
            files.append({"id": fid, "error": out.stderr[:200]})
    except Exception as e:
        files.append({"id": fid, "error": str(e)})
    if (i+1) % 5 == 0:
        print(f"Fetched {i+1}/{len(file_ids)}", file=sys.stderr)

print(json.dumps(files, indent=2))

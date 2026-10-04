---
name: github-pages-publish
description: "Publish a standalone file to GitHub Pages."
---

# GitHub Pages Publish (Standalone File)

Publish a single static file (report, HTML artifact) to a repo whose Pages
site builds from a source branch, without disturbing the working tree or
the main site build.

## Procedure

1. **Discover the Pages source.** `gh api repos/{owner}/{repo}/pages` gives
   `html_url` (live base) and `source.branch`. Trust the API over the
   remote URL — git follows repo renames/transfers silently.
2. **Publish via temp worktree.** Fetch the source branch, `git worktree add`
   a temp dir at `origin/<branch>`, copy the file in, commit, push, then
   remove the temp worktree.
3. **Verify live, not just pushed.** Legacy branch builds take ~1 minute:
   wait, then curl the exact file URL and check `Content-Length` plus the
   page title/bytes — a bare HTTP 200 is not proof.

## Pitfalls

- When the source branch is already checked out in another worktree, the new
  checkout stays detached — commit there and `push origin HEAD:<branch>`.
- Deploy actions that publish a build directory (e.g. `publish_dir` to
  `gh-pages`) delete side-loaded files on the next run — mirror the file
  inside the deployed source tree when it must survive redeploys.
- Pages is public. Confirm before publishing personal or sensitive content.

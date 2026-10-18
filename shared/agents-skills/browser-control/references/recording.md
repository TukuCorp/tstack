# Recording

Use `browser-control recording start <output-path>` to record an attached tab.
Pass an absolute output path. The default `--mode auto` keeps
`chrome.tabCapture` for user-owned tabs and uses timestamped CDP screencasting
for relay-owned tabs, so session-created `bc-tab-*` pages can be recorded
without clicking the extension icon. CDP mode requires `ffmpeg` on `PATH`,
accepts `.webm` or `.mp4`, defaults to 25 fps, and bounds the active viewport
within 1280x720. It activates the recorded tab because Chromium throttles
compositor frames in background tabs. `tab-capture` output must end in `.webm`;
pass `--mode cdp` for `.mp4` or to force CDP on a user-owned tab.
The `--session` flag accepts either the Browser Control session id you use with
`execute` or the lower-level CDP `bc-tab-*` session id from `status --json`.

```bash
browser-control recording start C:/Users/tukum/project/tmp/demo.mp4 --session my-session --mode cdp
browser-control recording status --session my-session
browser-control recording stop --session my-session
browser-control recording cancel --session my-session   # discard without writing
```

Other flags: `--tab-id`, `--audio` (tab-capture only), `--frame-rate`
(30 for tab-capture, 25 for CDP), and `--max-duration-ms` (auto-stop guard,
default 900000). Check `browser-control recording start --help` for the
installed set.

`tab-capture` writes a WebM file and can include audio. `cdp` writes WebM or MP4
plus a `.json` metadata sidecar with source, encoded, coalesced, and dropped
frame counts; it does not capture audio.

Recording does not change ghost cursor mode, and the cursor does not start or
edit recordings.

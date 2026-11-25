# Picker: delivering options and getting picks back

`design.py picker <run>` builds `<run>/picker.html` from `options/*/index.html`, `gates.json` and `scores.json`. Each option is embedded with `srcdoc`, so the file stands alone and can be published or opened from disk. Rebuild the picker after every change to the option set.

What the user can do on the page:
- **Switch options:** `1`-`N`, the arrow keys, or the option tabs. `?v=<name>` holds the current option, so a link opens on it.
- **Device toggle:** phone (393px), tablet (834px), desktop (full width), and for decks a slide view (1920x1080 scaled to fit).
- **Read badges:** gate results and rubric scores with their evidence.
- **Pick a base:** "Use as base".
- **Tag parts:** "Tag part" turns on click-to-tag. A click outlines an element inside the option and records `{option, selector, text}`. The user adds a note, such as "this header".
- **Write notes** on each option.
- **Send:** produces the pick as one line plus JSON, `mash <base> +<selector> from <option> ...`, with the notes attached.

How the send reaches you depends on the picker.

## artifact (default in Claude Code)

1. Load `artifact-design`, then publish `picker.html` with the Artifact tool (icon `layout`). The picker already has light and dark tokens and works on a phone.
2. Send reaches you in two ways, and you should handle both:
   - the page's **Copy pick** button copies the `mash ...` line, which the user pastes into the chat;
   - comments on the artifact (`ArtifactComments`: watch the artifact after publishing and read new comments each turn).
3. Republish to the same file path after each mash or riff so the link stays the same.

Use the artifact for options that need a phone check by the user away from the desk, or for sharing. The options are private until the user shares them.

## local (default elsewhere)

```bash
python -X utf8 $DESIGN/scripts/design.py serve <run>            # prints the URL, then one JSON line per Send
python -X utf8 $DESIGN/scripts/design.py wait <run> --after <n>  # for harnesses without a monitor: blocks until a Send newer than n
```

`serve` listens on `127.0.0.1` and opens the browser. Each Send is appended to `<run>/picks.jsonl` and printed to stdout as `{"type":"send","seq":n,...}`.
- **With a monitor:** a harness with a persistent monitor or background-output tool runs `serve` under it and treats each `send` line as the user's next message.
- **Without one:** run `serve --detach` once, then call `wait` after each turn. Exit code 3 means it timed out and you should wait again. Starting a second `wait` on the same run is never needed.

Stop the server when `keep` finishes: `design.py stop <run>`.

## static

Open `picker.html` in the browser (or give the user its path). "Copy pick" is the only way back: the user pastes the line into the chat. This always works, including over SSH or on another machine.

## Reading a pick

A pick names a base, tagged parts with the option each one comes from, and notes. Append it to `picks.jsonl` if the server hasn't already. Then follow step 6 of SKILL.md: copy the base to `options/<base>+<n>/` and rebuild each tagged part in the base's tokens. Don't paste raw markup, because the source option's CSS won't match the base. A note without a tag is a direction for the next riff.

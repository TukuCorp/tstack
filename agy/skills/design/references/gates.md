# Gates and the state toggle

`gates.py <run>` checks every `options/*/index.html` (or a single file passed with `--only <name>`) and writes `<run>/gates.json` and `<run>/shots/<option>/*.png`. It exits 1 if any option fails. Look at the PNGs yourself afterwards: the gates catch defects, not blandness.

| Gate | What fails it | How it runs |
|---|---|---|
| slop | The AI-default patterns in the table below | Static scan of the HTML and CSS, no browser |
| layout | Horizontal overflow, or visible controls off-screen, on phone (iPhone 15) or desktop (1440) | Bundled `shot.py` with agent-browser device emulation |
| a11y | axe-core violations of impact `serious` or `critical` | agent-browser loads axe-core 4.10.2 from cdnjs. If the network or agent-browser is missing, the result is `skipped`, never `pass` |

Use `--skip layout,a11y` for a quick slop-only pass while drafting. Run the full gates before the picker.

## Slop patterns (the lint's list, with the fix)

| Pattern | Instead |
|---|---|
| Purple or indigo gradient (`#6366f1`, `#8b5cf6`, `indigo-*`/`violet-*`/`purple-*` in a `gradient`) | One brand hue from the contract. Use a flat fill, or a gradient only where the contract asks for one |
| `rounded-2xl`/`rounded-3xl`, or `border-radius` of 16px or more on most elements | One radius scale (e.g. 4/8), applied by role |
| Lorem ipsum, "Acme", "John Doe", or `placeholder.com`/`via.placeholder` images | Real content from the brief, repo or files |
| The stock hero plus three-card feature grid | A layout that follows the content's own order |
| Emoji used as icons in headings or buttons | Inline SVG icons or plain text |
| `box-shadow` on everything (5 or more distinct shadow rules) | Elevation only where layering is real |
| Glassmorphism (`backdrop-filter: blur`) on content panels | Solid surfaces. Blur is for overlays only |
| Gradient-clipped headline text (`background-clip: text`) | Solid text colour. The accent hue goes on one element, not on letters |
| A coloured 3 to 6px left border on 3 or more cards or callouts | A heading, or a full hairline border |
| One italic serif word in a sans headline, or Instrument Serif at all | One heading family. Emphasis comes from weight or size |
| Inter, a display serif and JetBrains Mono loaded together | The fonts the contract names |
| Blurred colour orbs (`filter: blur` of 40px or more) | A flat background |
| A 1px grid-line background pattern | A plain background, unless the content is a grid |
| A rotating `conic-gradient` "beam" border (fails) | A plain 1px border |
| A logo marquee (keyframes sliding `translateX` negative) | A static list of real, sourced customers, or nothing |
| Pulsing or blinking status dots (`@keyframes pulse/ping/blink`) | Show live status only when it reads a real source |
| Stat counters that count up on scroll | The number as text, with its source |
| Fake terminal window dots (`#ff5f56`, `#ffbd2e`, `#27c93f`) | A plain code block |
| Hype badges and pills ("AI-POWERED", "MOST POPULAR", "Now Live", "All Systems Operational") | Cut the badge, or state the sourced fact it stands for |

Rows from gradient-clipped text down come from Slopstrap, a parody framework that ships each "vibecoded" tell as a component (slopstrap.mikelacher.com, read 2026-11-28). Copy-level chrome (the same badges, "AI Insight:" callouts, "Trusted by" lines) is unslop rule 44.

The lint is a smoke test. An option can pass it and still be generic, and the rubric and the user's eye handle that. When the user rejects something the lint missed in two separate runs, add the pattern to `gates.py` (`SLOP`) and to this table.

## State toggle (in every option)

Each option carries a small fixed toggle in its bottom corner, marked `data-design-dev`. The gates and the picker know about it, so it is not a design element. It switches the page between these states:

- **Demo:** the real sample content.
- **Empty:** no items. Show the empty state the contract specifies.
- **One:** a single item.
- **Many:** about 1,000 rows, or about 40 cards. Generate them in JS, don't hand-write them.
- **Long text:** names three times longer than usual, a 60-character unbroken token, and RTL in one field.

Inject each state at the data boundary: one `render(data)` function called with different arrays, not separate markup per state. The layout gate checks only Demo. Open Many and Long text in the picker yourself before showing the options, because overflow there is the most common thing found too late.

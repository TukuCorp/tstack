# Decks and docs

/design explores the layout as HTML and then hands it off. It never builds the .pptx or .docx itself.

## Options

- **Slides:** each option is one HTML file showing 3-5 representative slides (the title, a dense data slide, a chart, a comparison) as fixed 1920x1080 sections (`<section class="slide">`, `width:1920px;height:1080px`). The picker's slide view scales them to fit. Axes here are grid system, text-to-visual ratio, chart style and how the narrative is ordered.
- **Docs:** each option is A4 (794x1123 px at 96 dpi) or Letter (816x1056) pages showing the cover, a body page and a table page.
- **Content:** real content from the source report, deck or notes.
- **Allotrope work:** when the user says "Allotrope format", the house template sets the fonts, banner and cover (Cabin, teal banner, solar/wind cover from the Gap kickoff deck). Options vary layout only inside that frame.

Gates: the slop lint and a11y contrast still apply. The phone layout gate is replaced by a check that nothing overflows its 1920x1080 or page box. `gates.py --surface slides|doc` does this.

## Handoff after `keep`

Write `.design/<slug>/final/layout-spec.md`:

```markdown
# Layout spec: <deck or doc>
Grid: <columns, margins, gutters in px at 1920x1080 or page size>
Type: <roles -> font, size, weight>
Colour roles: <role -> hex>
Per slide/page:
1. <title> — layout <name>; regions <x,y,w,h>; chart type <...>; notes
...
Reference render: final/index.html
```

Then name the skill that builds it: `apdeck` for Allotrope decks, `present` when there is a template deck, `pptx` for a deck from scratch, `docx` for Word. Don't start that build inside /design.

# PowerPoint Mode — Allotrope Style Guide

Generate `.pptx` presentations aligned with Allotrope's visual identity.
*Style confirmed by XML inspection of actual Allotrope deck (April 2026).*

---

## Toolchain

```bash
# Install dependencies (once)
npm install -g pptxgenjs
pip install "markitdown[pptx]" --break-system-packages

# Generate
node presentation.js

# QA: convert to images for visual inspection
soffice --headless --convert-to pdf output.pptx
rm -f slide-*.jpg
pdftoppm -jpeg -r 150 output.pdf slide
ls -1 "$PWD"/slide-*.jpg
```

**Dependencies:**
- `pptxgenjs` (npm) — creates .pptx from Node.js
- `markitdown` (pip) — extracts text for content QA
- LibreOffice (`soffice`) — converts .pptx to PDF for visual inspection
- Poppler (`pdftoppm`) — converts PDF to slide images

---

## Allotrope Brand Style

### Color Palette

| Role | Hex | Usage |
|------|-----|-------|
| Title slide background | `#1A5276` | Title slide only |
| Section divider background | `#1B4F72` | Section divider slides |
| Content slide background | `#FFFFFF` | All content slides |
| Slide title text | `#1A3550` | Content slide titles |
| Body text | `#2C3E50` | Paragraphs, bullets |
| Accent / green | `#27AE60` | Rule line, stat values, section numbers |
| Caption / muted | `#7F8C8D` | Captions, stat labels, footnotes |
| Negative / red | `#E74C3C` | Unfavorable stat values |
| Stat card background | `#EBF5FB` | Stat callout card fill |
| Card border | `#D5E8F5` | Stat callout card border |
| Table header background | `#EBF5FB` | Table header row fill |
| Table border | `#E0E0E0` | Table cell borders |
| Footer text | `#95A5A6` | Confidentiality footer |
| Title slide subtitle | `#BDC3C7` | Subtitle/date on title slide |

### Typography

**CRITICAL: Fonts are Calibri Light (headings) and Calibri (body) — NOT Trebuchet MS.**

| Element | Font | Size | Style |
|---------|------|------|-------|
| Title slide "ALLOTROPE" label | Calibri Light | 11pt | Regular, white, charSpacing: 5 |
| Presentation title | Calibri Light | 36pt | Bold, white |
| Title slide subtitle/date | Calibri | 13pt | Regular, `#BDC3C7` |
| Section divider number | Calibri Light | 72pt | Bold, `#27AE60` |
| Section divider title | Calibri Light | 28pt | Bold, white |
| Content slide title | Calibri Light | 22pt | Bold, `#1A3550` |
| Caption under title | Calibri | 11pt | Regular, `#7F8C8D` |
| Body / bullets | Calibri | 13pt | Regular, `#2C3E50` |
| Stat callout value | Calibri Light | 24pt | Bold, green or red |
| Stat callout label | Calibri | 9pt | Regular, `#7F8C8D` |
| Footnote / commentary | Calibri | 10pt | Regular, `#7F8C8D` |
| Table header text | Calibri | 11pt | Bold, `#1A3550` |
| Table body text | Calibri | 11pt | Regular, `#2C3E50` |
| Footer | Calibri | 7pt | Regular, `#95A5A6` |

### Slide Dimensions

```javascript
const pptx = new PptxGenJS();
pptx.layout = 'LAYOUT_WIDE'; // 13.33" × 7.5"
```

---

## Required Elements on Every Non-Title Slide

### Confidentiality Footer
```javascript
slide.addText(
  'Confidential — For Internal Use by Allotrope & Key Partners — Not for Further Circulation',
  { x: 0.3, y: 6.95, w: 12.7, h: 0.2, fontSize: 7, fontFace: 'Calibri', color: '95A5A6', align: 'center' }
);
```

### Green Rule Line Under Content Slide Title
```javascript
// Mandatory on every content slide — thin filled rect directly below title
slide.addShape(pptx.ShapeType.rect, {
  x: 0.5, y: 0.97, w: 12.3, h: 0.04,
  fill: { color: '27AE60' }, line: { color: '27AE60' }
});
```

---

## Slide Templates

### 1. Title Slide

```javascript
const slide = pptx.addSlide();
slide.background = { color: '1A5276' };

// Company name — top left, spaced caps
slide.addText('ALLOTROPE', {
  x: 0.6, y: 0.5, w: 12, h: 0.4,
  fontSize: 11, fontFace: 'Calibri Light', color: 'FFFFFF', bold: false, charSpacing: 5
});

// Main title — confirmed y: 2.4" from XML
slide.addText(title, {
  x: 0.6, y: 2.4, w: 11.5, h: 1.8,
  fontSize: 36, fontFace: 'Calibri Light', color: 'FFFFFF', bold: true
});

// Subtitle / date — confirmed y: 4.4" from XML
slide.addText(`${subtitle}\n${date}`, {
  x: 0.6, y: 4.4, w: 9, h: 0.8,
  fontSize: 13, fontFace: 'Calibri', color: 'BDC3C7'
});
```

### 2. Section Divider Slide

```javascript
slide.background = { color: '1B4F72' };

slide.addText(sectionNumber, {  // e.g. '01'
  x: 0.6, y: 1.2, w: 3, h: 1.8,
  fontSize: 72, fontFace: 'Calibri Light', color: '27AE60', bold: true
});

slide.addText(sectionTitle, {
  x: 0.6, y: 3.2, w: 12, h: 1.0,
  fontSize: 28, fontFace: 'Calibri Light', color: 'FFFFFF', bold: true
});

// Footer still required on section dividers
addFooter(slide);
```

### 3. Content Slide — Title + Caption (optional) + Body

```javascript
// Title
slide.addText(title, {
  x: 0.5, y: 0.3, w: 12.3, h: 0.65,
  fontSize: 22, fontFace: 'Calibri Light', color: '1A3550', bold: true
});

// Green rule line — always present
slide.addShape(pptx.ShapeType.rect, {
  x: 0.5, y: 0.97, w: 12.3, h: 0.04,
  fill: { color: '27AE60' }, line: { color: '27AE60' }
});

// Caption (optional) — omit if not needed; body starts at y: 1.15 without it
if (caption) {
  slide.addText(caption, {
    x: 0.5, y: 1.05, w: 12.3, h: 0.4,
    fontSize: 11, fontFace: 'Calibri', color: '7F8C8D', valign: 'top'
  });
}

// Body text — start y: 1.55 with caption, 1.15 without
slide.addText(bodyContent, {
  x: 0.5, y: caption ? 1.55 : 1.15, w: 12.3, h: caption ? 5.1 : 5.5,
  fontSize: 13, fontFace: 'Calibri', color: '2C3E50', valign: 'top', paraSpaceAfter: 5
});

addFooter(slide);
```

### 4. Two-Column Content

```javascript
// Title + green rule line (same as above)

// Left column
slide.addText(leftContent, {
  x: 0.5, y: 1.55, w: 5.9, h: 5.1,
  fontSize: 13, fontFace: 'Calibri', color: '2C3E50', valign: 'top', paraSpaceAfter: 5
});

// Vertical divider
slide.addShape(pptx.ShapeType.line, {
  x: 6.55, y: 1.55, w: 0, h: 5.0,
  line: { color: 'E0E0E0', width: 1 }
});

// Right column
slide.addText(rightContent, {
  x: 7.0, y: 1.55, w: 5.8, h: 5.1,
  fontSize: 13, fontFace: 'Calibri', color: '2C3E50', valign: 'top', paraSpaceAfter: 5
});

addFooter(slide);
```

### 5. Stat Callout Row (2 or 3 columns)

**Color is semantic, not sign-based:** use green for favorable outcomes, red for unfavorable — even if both values are negative (e.g., "-$6K best case" is green, "-$63K worst case" is red).

**3-column:** x positions = 0.6", 4.8", 9.0" — each w=3.9"  
**2-column:** x positions = 0.6", 4.8" — each w=5.9"

```javascript
// Helper — reuse for both layouts
function addStatCards(slide, stats, colX, colW) {
  stats.forEach((stat, i) => {
    const x = colX[i];

    // Card background
    slide.addShape(pptx.ShapeType.roundRect, {
      x, y: 4.4, w: colW, h: 1.8,
      fill: { color: 'EBF5FB' },
      line: { color: 'D5E8F5', width: 1 },
      rectRadius: 0.05
    });

    // Big value
    slide.addText(stat.value, {
      x, y: 5.05, w: colW, h: 0.6,
      fontSize: 24, fontFace: 'Calibri Light', bold: true,
      color: stat.color, align: 'center'
    });

    // Label
    slide.addText(stat.label, {
      x, y: 5.6, w: colW, h: 0.4,
      fontSize: 9, fontFace: 'Calibri', color: '7F8C8D', align: 'center'
    });
  });
}

// 3-col usage
addStatCards(slide, [
  { value: '9.31%',   label: 'New Project IRR',  color: '27AE60' },
  { value: '+$11.8M', label: 'NPV Gain',          color: '27AE60' },
  { value: '+24.3%',  label: 'Revenue Uplift',    color: '27AE60' },
], [0.6, 4.8, 9.0], 3.9);

// 2-col usage
addStatCards(slide, [
  { value: '-$63,305', label: 'Worst Hit (Bundled Discount)', color: 'E74C3C' },
  { value: '-$6,076',  label: 'Best Preserved (Fixed PPA)',   color: '27AE60' },
], [0.6, 4.8], 5.9);
```

### 6. Footnote / Commentary Text (optional)

Appears between stat cards and footer on slides needing a bottom explanatory note.

```javascript
slide.addText(footnoteText, {
  x: 0.5, y: 6.55, w: 12.3, h: 0.35,
  fontSize: 10, fontFace: 'Calibri', color: '7F8C8D', valign: 'top'
});
```

### 7. Data Table

```javascript
const rows = [
  // Header row
  [
    { text: 'Attribute',    options: { bold: true, fill: { color: 'EBF5FB' }, color: '1A3550', fontFace: 'Calibri', fontSize: 11 } },
    { text: 'Old (≤ Apr 21)', options: { bold: true, fill: { color: 'EBF5FB' }, color: '1A3550', fontFace: 'Calibri', fontSize: 11 } },
    { text: 'New (≥ Apr 22)', options: { bold: true, fill: { color: 'EBF5FB' }, color: '1A3550', fontFace: 'Calibri', fontSize: 11 } },
  ],
  [{ text: 'Off-Peak (Mon–Sat)' }, { text: '22:00–04:00' }, { text: '00:00–06:00' }],
  // add more rows...
];

slide.addTable(rows, {
  x: 0.5, y: caption ? 1.55 : 1.15, w: 12.3,
  fontSize: 11,
  fontFace: 'Calibri',
  color: '2C3E50',
  border: { type: 'solid', color: 'E0E0E0', pt: 0.5 },
  rowH: 0.42,
  valign: 'middle',
  colW: [4.5, 3.5, 4.3]  // adjust per content
});
```

---

## Reusable Helper Functions

Always define these at the top of your script:

```javascript
function addFooter(slide) {
  slide.addText(
    'Confidential — For Internal Use by Allotrope & Key Partners — Not for Further Circulation',
    { x: 0.3, y: 6.95, w: 12.7, h: 0.2, fontSize: 7, fontFace: 'Calibri', color: '95A5A6', align: 'center' }
  );
}

function addTitleBar(slide, pptx, title, caption) {
  slide.addText(title, {
    x: 0.5, y: 0.3, w: 12.3, h: 0.65,
    fontSize: 22, fontFace: 'Calibri Light', color: '1A3550', bold: true
  });
  slide.addShape(pptx.ShapeType.rect, {
    x: 0.5, y: 0.97, w: 12.3, h: 0.04,
    fill: { color: '27AE60' }, line: { color: '27AE60' }
  });
  if (caption) {
    slide.addText(caption, {
      x: 0.5, y: 1.05, w: 12.3, h: 0.4,
      fontSize: 11, fontFace: 'Calibri', color: '7F8C8D', valign: 'top'
    });
  }
}
```

---

## Common Mistakes

- **Wrong fonts** — must be Calibri Light (titles/headings) and Calibri (body). Never Trebuchet MS.
- **Missing green rule line** — every content slide needs the thin filled rect (h: 0.04") under the title
- **Wrong title slide background** — `#1A5276` (teal-blue), not navy. Section dividers use `#1B4F72`
- **Stat color is semantic** — green = favorable, red = unfavorable regardless of whether value is positive/negative
- **Never skip the footer** — required on every non-title slide
- **Stat card sizes** — 3-col: w=3.9"; 2-col: w=5.9". Values are 24pt Calibri Light bold, not 44-52pt

---

## QA Workflow

```bash
# 1. Content check
python -m markitdown output.pptx

# 2. Check for leftover placeholder text
python -m markitdown output.pptx | grep -iE "\bx{3,}\b|lorem|ipsum|\bTODO|\[insert"

# 3. Visual inspection — generate slide images
soffice --headless --convert-to pdf output.pptx
rm -f slide-*.jpg
pdftoppm -jpeg -r 150 output.pdf slide
# Visually inspect each slide-N.jpg against reference
```

**Visual QA checklist:**
- Confidentiality footer on all non-title slides
- Green rule line under every content slide title
- Titles in Calibri Light, body in Calibri (check rendering — LibreOffice fallback fonts can differ)
- Stat card values readable, color matches intent (green = good, red = bad)
- Tables not clipped at slide edges
- Section dividers: large green number + white title on dark teal background
- No leftover placeholder text

# HTML Presentation Mode

Generate a polished, self-contained HTML presentation. Single `.html` file, no CDN dependencies at runtime (embed scripts inline if needed), works offline.

---

## File Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Presentation Title</title>
  <style>/* All CSS inline here */</style>
</head>
<body>
  <div class="deck">
    <div class="slide active" id="s1"><!-- slide content --></div>
    <div class="slide" id="s2"><!-- slide content --></div>
  </div>
  <nav class="nav">
    <button id="prev">&#8592;</button>
    <span id="counter">1 / N</span>
    <button id="next">&#8594;</button>
  </nav>
  <script>/* All JS inline here */</script>
</body>
</html>
```

---

## Design System

### Colors (Light Theme — Default)

```css
:root {
  --bg:       #FFFFFF;
  --surface:  #F8F9FA;
  --primary:  #1A5276;   /* deep navy — titles, headers */
  --accent:   #27AE60;   /* green — Allotrope brand, callouts, highlights */
  --text:     #2C3E50;   /* charcoal — body copy */
  --muted:    #7F8C8D;   /* captions, footnotes */
  --border:   #E0E0E0;
}
```

### Dark Theme (on request)

```css
:root {
  --bg:      #1A1A2E;
  --surface: #16213E;
  --primary: #E2E8F0;
  --accent:  #2ECC71;
  --text:    #CBD5E0;
  --muted:   #718096;
}
```

### Typography

```css
.slide { font-family: 'Segoe UI', Trebuchet MS, sans-serif; }
.slide-title { font-size: 2.2rem; font-weight: 700; color: var(--primary); }
.slide-body  { font-size: 1rem; color: var(--text); line-height: 1.6; }
.stat-number { font-size: 3.5rem; font-weight: 700; color: var(--accent); }
.stat-label  { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; }
```

---

## Core Layout CSS

```css
/* Slide container */
.deck { width: 100vw; height: calc(100vh - 48px); position: relative; overflow: hidden; }
.slide {
  display: none; position: absolute; inset: 0;
  padding: 3rem 4rem; box-sizing: border-box;
  background: var(--bg);
}
.slide.active { display: flex; flex-direction: column; }

/* Navigation bar */
.nav {
  height: 48px; display: flex; align-items: center; justify-content: center; gap: 1.5rem;
  background: var(--surface); border-top: 1px solid var(--border);
}
.nav button {
  background: none; border: 1px solid var(--border); border-radius: 4px;
  padding: 4px 14px; cursor: pointer; font-size: 1rem; color: var(--text);
}
.nav button:hover { background: var(--surface); border-color: var(--accent); }

/* Two-column layout */
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 2.5rem; flex: 1; }

/* Stat callout row (2–4 metrics) */
.stat-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1.5rem; }
.stat-card {
  background: var(--surface); border-radius: 10px; padding: 1.5rem;
  text-align: center; border: 1px solid var(--border);
}

/* Icon + text rows */
.icon-row { display: grid; grid-template-columns: 3rem 1fr; gap: 1rem; align-items: start; margin-bottom: 1rem; }
.icon-circle {
  width: 2.5rem; height: 2.5rem; border-radius: 50%;
  background: var(--accent); display: flex; align-items: center; justify-content: center;
  color: white; font-size: 1rem;
}

/* Section divider */
.section-slide { background: var(--primary) !important; justify-content: center; }
.section-slide .section-num { font-size: 5rem; font-weight: 700; color: var(--accent); }
.section-slide .section-title { font-size: 2rem; font-weight: 700; color: #FFFFFF; margin-top: 0.5rem; }

/* Table */
table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
th { background: #EBF5FB; color: var(--primary); padding: 0.6rem 0.8rem; text-align: left; font-weight: 600; }
td { padding: 0.5rem 0.8rem; border-bottom: 1px solid var(--border); color: var(--text); }
tr:hover td { background: var(--surface); }
```

---

## Navigation JS

```javascript
const slides = document.querySelectorAll('.slide');
let cur = 0;

function goTo(n) {
  slides[cur].classList.remove('active');
  cur = Math.max(0, Math.min(n, slides.length - 1));
  slides[cur].classList.add('active');
  document.getElementById('counter').textContent = `${cur + 1} / ${slides.length}`;
}

document.getElementById('prev').addEventListener('click', () => goTo(cur - 1));
document.getElementById('next').addEventListener('click', () => goTo(cur + 1));
document.addEventListener('keydown', e => {
  if (['ArrowRight', 'ArrowDown', 'PageDown'].includes(e.key)) goTo(cur + 1);
  if (['ArrowLeft', 'ArrowUp', 'PageUp'].includes(e.key)) goTo(cur - 1);
});
```

---

## Mermaid Diagrams

Use for process flows, org charts, timelines, decision trees.

```html
<div class="mermaid">
flowchart LR
  A[Input] --> B{Decision}
  B -->|yes| C[Output A]
  B -->|no| D[Output B]
</div>
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: true, theme: 'neutral' });
</script>
```

---

## Chart.js

Use for bar charts, line trends, pie/donut, scatter.

```html
<canvas id="chart1" style="max-height: 280px;"></canvas>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
new Chart(document.getElementById('chart1'), {
  type: 'bar',
  data: {
    labels: ['Q1', 'Q2', 'Q3', 'Q4'],
    datasets: [{ label: 'Revenue', data: [4.2, 5.1, 6.0, 7.3], backgroundColor: '#27AE60' }]
  },
  options: { responsive: true, plugins: { legend: { display: false } } }
});
</script>
```

---

## Slide Types Reference

| Type | When to Use |
|------|-------------|
| Title slide | Always first — centered, dark navy bg |
| Agenda / TOC | Decks of 6+ slides |
| Section divider | Between major topics — navy bg, green number |
| 3-stat callout row | Quantitative highlights (IRR, NPV, capacity) |
| Two-column content | Comparison or details + visual side by side |
| Mermaid diagram | Process flows, architecture |
| Chart.js chart | Data trends or distributions |
| Data table | Structured data, member lists |
| Conclusion / Next steps | Always last |

---

## QA

Before saving, verify:
- All slides render (no broken Mermaid, no Chart.js console errors)
- Keyboard navigation works (arrow keys, prev/next buttons)
- No placeholder text remaining
- Stat cards readable on both light/dark bg

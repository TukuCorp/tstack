# Research Modes

Use these mode-specific patterns to keep the brief structured and evidence-driven.

Every mode should follow the same internal loop:

1. `Discovery` - find the strongest sources for the mode.
2. `Verification` - confirm which claims are reliable enough to keep.
3. `Comparison` - compare the best options, findings, or implementations.
4. `Synthesis` - explain reuse, gaps, contradictions, and planning implications.

## Domain

Survey the general landscape: key tools, players, frameworks, existing approaches, and prior art.

### Discovery

- Start with 3-5 tightly scoped searches using official sites, standards bodies, major labs, or known vendors.
- Fetch the 2-3 most substantive primary sources first.
- In `deep` mode, widen the scan enough to compare competing camps, not just one dominant framing.

### Verification

- Confirm that named tools, standards, or approaches are current and real.
- Prefer primary descriptions of capabilities over summaries written by third parties.
- Flag marketing claims, stale ecosystem maps, or unsourced adoption statements.

### Comparison

- Compare approaches by scope, maturity, constraints, and known limitations.
- Do not just enumerate vendors or frameworks.
- Surface disagreements in framing when different sources define the problem differently.

### Section Template

```markdown
## Domain Landscape
### Discovery
### Verification
### Comparison
### Synthesis
### Confidence
```

## Codebase

Survey relevant repositories: architecture, key files, patterns, DeepWiki coverage, and reuse opportunities.

### Discovery

- Search the local workspace first when the request is tied to the current repo.
- For external repos, use `gh` or GitHub API to inspect README, tree, recent commit history, releases, and issue activity.
- Check DeepWiki when a repo is known and a DeepWiki page exists.
- Read key source files when README or tree-level context is insufficient.

### Verification

- Verify maintenance signals before treating a repo as a strong reference.
- Separate observed architecture from README claims.
- Confirm whether example code, docs, and exposed interfaces match the claimed pattern.

### Comparison

- Compare repos by architecture, interfaces, extension points, maintenance health, and adaptation cost.
- Explain why one repo is more reusable than another instead of relying on stars alone.
- Note when no clean reference implementation exists.

### Section Template

```markdown
## Codebase Survey
### Discovery
### Verification
### Comparison
### Synthesis
### Confidence
```

## Math

Survey formulations, algorithms, assumptions, complexity, solver choice, convergence issues, and reference implementations.

### Discovery

- Search by problem formulation, algorithm family, and solver names rather than generic business wording.
- Fetch foundational papers, official algorithm docs, or credible lecture or lab notes.
- Look for open-source reference implementations in domain-standard ecosystems.

### Verification

- Distinguish exact methods from heuristics, relaxations, or surrogate models.
- Verify what assumptions and constraints each method requires.
- Flag when a source discusses a neighboring problem rather than the target formulation.

### Comparison

- Compare methods by formulation, assumptions, complexity, accuracy trade-offs, and failure modes.
- Prefer direct technical contrasts over vague statements like "more scalable" or "better results".
- Note solver or implementation constraints that materially affect adoption.

### Section Template

```markdown
## Mathematical and Algorithmic Foundations
### Discovery
### Verification
### Comparison
### Synthesis
### Confidence
```

## Literature

Survey academic papers, technical reports, and credible practitioner write-ups.

### Discovery

- Prefer technical reports, open papers, lab publications, and reputable institutes.
- Bias toward the last 3 years unless older work is clearly foundational.
- Record DOI or canonical URLs when available.
- Separate peer-reviewed, technical-report, and practitioner evidence clearly.

### Verification

- Confirm venue quality, recency, and relevance to the exact formulation.
- Do not treat citations to a paper as proof of quality.
- Note when evidence is indirect, preliminary, paywalled, or contradicted elsewhere.

### Comparison

- Compare papers by methodology, dataset or setting, claimed contribution, and limitations.
- Highlight contradictions, replication gaps, or missing benchmarks.
- In `deep` mode, identify clusters of agreement and disagreement rather than presenting a flat list.

### Section Template

```markdown
## Literature and Reports
### Discovery
### Verification
### Comparison
### Synthesis
### Confidence
```

## Ordering Rule

- Complete each selected mode fully before starting the next.
- Let later modes reference earlier findings directly.
- If one mode yields sparse results, note that briefly and continue.
- The main synthesis should integrate mode outputs instead of restating them.

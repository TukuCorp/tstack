# Research Examples

Use these examples to calibrate invocation, mode choice, depth choice, and selective subagent use.

## Example 1

Input:

```text
/research how REopt handles BESS dispatch
```

Expected mode choice:

- `domain -> codebase -> math -> literature`
- `--depth standard`

Expected emphasis:

- Battery dispatch framing
- REopt repository or docs
- Optimization formulation and solver choice
- NREL or related reports and papers

Expected behavior:

- Keep the brief compact.
- Cite claims near the relevant bullets or sentences.
- Compare the formulation found in docs or code with the formulation described in papers.

## Example 2

Input:

```text
/research build a lightweight PR review assistant
```

Expected mode choice:

- `domain -> literature`
- `--depth standard`

Expected emphasis:

- Existing review-assistant products and workflows
- Common architectural patterns
- Evidence on review quality, automation, or developer productivity

Expected behavior:

- Surface what exists already and what remains missing.
- Avoid turning the output into a product spec.

## Example 3

Input:

```text
/research pandas dataframe validation libraries --mode codebase --then literature --depth deep
```

Expected mode choice:

- `codebase -> literature`
- `--depth deep`

Expected emphasis:

- Maintained validation libraries
- Comparison of APIs, architecture, and extension patterns
- Published guidance or ecosystem consensus
- Contradictions between documentation claims and practical limitations

Expected behavior:

- One focused subagent may be used for codebase scanning or literature gathering, but the main agent should merge results.
- The final brief should compare the strongest libraries instead of listing many similar ones.

## Example 4

Input:

```text
/research battery degradation surrogate models --mode math --depth deep
```

Expected mode choice:

- `math`
- `--depth deep`

Expected emphasis:

- Formulations
- Complexity and approximations
- Assumptions and failure modes
- Reference implementations
- Foundational and recent papers

Expected behavior:

- Surface when two methods target adjacent but not identical problems.
- Lower confidence if strong reference implementations are missing.

## Example 5

Input:

```text
/research open-source feature flag systems --mode all --depth deep
```

Expected mode choice:

- `domain -> codebase -> math -> literature`
- `--depth deep`

Expected emphasis:

- Ecosystem segmentation and product categories
- Reusable open-source architectures
- Evaluation or rollout decision logic when relevant
- Operational evidence, reports, and gaps in published work

Expected behavior:

- Up to two focused subagents may be used if scope warrants it.
- Each mode should still follow discovery, verification, comparison, and synthesis.
- Cross-mode synthesis should resolve overlap instead of repeating each section.

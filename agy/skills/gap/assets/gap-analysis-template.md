# Gap Analysis: {{TARGET_TITLE}}

**Date:** {{DATE}}
**Scope:** {{SCOPE_DESCRIPTION}}
**Status:** Draft for Review

---

## Executive Summary

{{2-3 sentences: what's strong, gap magnitude, critical gap count, one-line recommendation}}

---

## Current Capabilities (What We Have)

| Capability | Status | Key Surfaces |
|---|---|---|
| {{Capability}} | {{Mature / Working / Partial / Planned / Missing}} | {{file paths}} |

---

## Target State

> {{Clear description of the desired end state}}

---

## Gap Analysis

### GAP-01: {{Gap Title}}

**Severity:** {{CRITICAL / HIGH / MEDIUM / LOW}} — {{One-line justification}}

**Current state:** {{What exists today, with specific file paths}}

**What's needed:**
- {{Specific requirement}}

**Existing assets to reuse:**
- {{File or module that can be extended, with what it already does}}

**Effort estimate:** {{Agent-unit sizing — e.g., "1 multi-phase plan (3-4 phases), 2 verification gates, 1 human review"}}

---

<!-- Repeat GAP-XX for each gap -->

## Second-Tier Gaps

| Gap | Severity | Summary | Existing Assets |
|---|---|---|---|
| {{GAP-XX}} | {{MEDIUM / LOW}} | {{One-line}} | {{What exists}} |

---

## Recommended Sequencing

| Wave | Gap | Rationale | Human checkpoints |
|---|---|---|---|
| Wave 1 | {{GAP-XX}} | {{Why first}} | {{Reviews, logins, approvals, external waits}} |

---

## Risk Register

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| {{Risk}} | {{What breaks}} | {{H/M/L}} | {{How to prevent}} |

---

## Suggested Next Step

{{Review this report, then invoke `/plan` for each critical gap.}}

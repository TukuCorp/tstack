"""Audit teach-workspace lesson quizzes for the fairness rules verify_workspace.py does NOT check.

Per question checks: exactly 4 options, all options the SAME word count (HTML tags
stripped before counting), exactly one data-answer="true". Also reports the
correct-answer index distribution per lesson so a repeated single-index pattern
(all-correct-at-index-0 style) is visible.

Reports only — never rewrites. Pre-existing violations in 0003/0008/0009 predate the
rule (found 2026-09-04); fix only lessons you authored, leave old ones alone.

Standard library only. Run from anywhere:
    python scripts/quiz_audit.py [lessons-dir]   # default: ./lessons
Exit 0 when clean, 1 when any violation found.
"""

import re
import sys
from pathlib import Path

QUESTION_SPLIT = re.compile(r'<li class="q">(.*?)(?=<li class="q">|</ol>)', re.S)
OPTION = re.compile(r'<li data-answer="(true|false)">(.*?)</li>', re.S)
TAG = re.compile(r'<[^>]+>')
LESSON = re.compile(r'^(\d{4})-[a-z0-9-]+\.html$')


def words(option_html):
    return len(TAG.sub(' ', option_html).split())


def audit_lesson(path):
    problems = []
    text = path.read_text(encoding='utf-8')
    blocks = QUESTION_SPLIT.findall(text)
    if '<section class="quiz"' not in text:
        return problems, []  # verifier owns the missing-quiz case
    indices = []
    for i, block in enumerate(blocks, 1):
        opts = OPTION.findall(block)
        counts = [words(o) for _, o in opts]
        trues = [j for j, (a, _) in enumerate(opts) if a == 'true']
        if len(opts) != 4:
            problems.append(f'{path.name} Q{i}: {len(opts)} options (want 4)')
        if len(set(counts)) != 1:
            problems.append(f'{path.name} Q{i}: word counts {counts} differ')
        if len(trues) != 1:
            problems.append(f'{path.name} Q{i}: {len(trues)} correct answers (want 1)')
        elif len(opts) == 4:
            indices.append(trues[0])
    return problems, indices


def main(argv):
    lessons = Path(argv[1] if len(argv) > 1 else 'lessons')
    files = sorted(p for p in lessons.iterdir() if LESSON.match(p.name))
    if not files:
        print(f'no lessons found in {lessons}')
        return 1
    all_problems = []
    for path in files:
        problems, indices = audit_lesson(path)
        all_problems.extend(problems)
        if indices and len(set(indices)) == 1 and len(indices) > 1:
            all_problems.append(
                f'{path.name}: correct answer always at index {indices[0]} — shuffle it')
    if all_problems:
        print('\n'.join(all_problems))
        return 1
    print(f'QUIZ-AUDIT-OK: {len(files)} lessons, all questions 4 options / equal words / one answer')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

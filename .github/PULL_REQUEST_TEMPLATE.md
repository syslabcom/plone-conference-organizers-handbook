## What this changes

<!-- One or two sentences. Link the issue: Closes #<number> -->

## Type of change

- [ ] Typo or link fix
- [ ] Lesson (ledger row and lesson block)
- [ ] Chapter, annex or template (chapter-list entry included)
- [ ] Thin marker added, changed or closed
- [ ] Specification, tooling or configuration
- [ ] Other

## Checklist

- [ ] The build passes: `make html SPHINXOPTS="-W --keep-going"`.
- [ ] Pages follow the writing rules: American English, one sentence per line, sentence-case headings, dated claims only.
- [ ] No personal data, private amounts, contact details or ticket-buyer data.
- [ ] Front matter is valid, and `review-by` is moved forward on any page I re-confirmed.

### If the change touches lessons

- [ ] Every lesson cites a ledger ID, and its ledger row has a disposition that points to this chapter.
- [ ] Every source ID exists in the manifest and is listed in "Sources and further reading".
- [ ] I ran `venv/bin/python -m scripts.generate fix`, then `check`, and committed the result.
- [ ] A specific lesson is only in "Case notes", and a general lesson passes the promotion rule.
- [ ] I asked whether this lesson contradicts an existing one. If it does, I added `conflicts-with` and a distinguishing context, or a `contested` status with an issue link.
- [ ] One reviewer comes from an organizing body other than the one that ran the lesson's year.

### If the change touches the specification

- [ ] Every file that mentions the changed field, vocabulary or rule is updated in this commit.
- [ ] The tests are updated first.

## Notes for the reviewer

<!-- Anything the steward should look at first. -->

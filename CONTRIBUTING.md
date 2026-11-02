# Contributing to the Plone Conference Organizers Handbook

Thank you for helping.
This handbook exists so that the next team organizing a Plone conference does not start from nothing, and it only works if people give back what they learn.

There are two ways to contribute, as in the [Plone documentation](https://6.docs.plone.org/contributing/documentation/index.html): a quick edit in the browser for small fixes, and a pull request from a fork for larger work.

## Before you start

- The handbook is advisory.
  It is not Plone Foundation policy and not legal, tax or insurance advice.
- Only generalized information enters the handbook.
  No personal data, no private amounts, no contact details and no ticket-buyer data.
  Paraphrase, aggregate and anonymize first.
- The license is CC BY 4.0.
  The contribution route follows the Plone Contributor Agreement; see the page "License and contribute" in the handbook.
- Be kind.
  Follow the [Plone Code of Conduct](https://plone.org/foundation/materials/foundation-resolutions/code-of-conduct).

## Path 1: small fixes in the browser

Use this for a typo, a broken link or a wrong date.

1. Open the page's source file on GitHub.
2. Select the pencil icon to edit it.
3. Make the change and write a short description of it.
4. Propose the change, which opens a pull request.
5. Wait for the checks and for a review.

## Path 2: larger work with a pull request

Use this for a lesson, a chapter, an annex or a change to the tooling.

1. Open an issue first, using the form that fits:
   - **Lesson submission** for something you learned at a conference.
   - **Thin marker** to report a gap that is not yet marked.
   - **Correction** for a wrong fact.
2. Fork the repository and create a branch.
3. Build the handbook locally.

   ```shell
   make html SPHINXOPTS="-W --keep-going"
   ```

   The first run creates a virtual environment and installs the requirements.
   `make livehtml` serves the site with live reload at <http://127.0.0.1:8050>.
4. Make your changes.
5. Run the checks you can run locally.

   ```shell
   make vale
   make linkcheck
   venv/bin/python -m scripts.generate check
   ```

   If the generator reports drift, run `venv/bin/python -m scripts.generate fix` and commit the result.
6. Open a pull request against `main` and fill in the template.
7. Respond to the review.
   A steward merges when the checks are green.

## Where things live

| You want to change | Look in |
|---|---|
| A chapter or page | `docs/` |
| What a page must look like | `docs/spec/` |
| A lesson's evidence | `data/ledger/` and `data/sources/` |
| The checks and the generator | `scripts/` and `tests/` |
| Tunable thresholds | `handbook-config.yml` |

The published pages "Update" and "Extend" explain the lesson route and the other extension routes step by step.

## Writing rules

1. American English.
2. One sentence per line in the Markdown source.
3. Sentence-case headings.
4. No exclamation marks, no emojis, no hype.
5. Dated claims only: write "as of 2026-11", not "currently", "recently" or "soon".
6. Prices, tax rates and fees appear only as dated, sourced examples.
7. Prefer commas and periods over dashes.

## Reviews

A lesson's author is never its only reviewer.
For a lesson from year Y, one reviewer comes from an organizing body other than the one that ran Y.
Stewardship is a proposal that the community has not yet accepted; until then the repository's interim maintainers review.
See `CODEOWNERS` and the page "Governance".

## Questions

Open an issue, or write to the maintainers through the repository.

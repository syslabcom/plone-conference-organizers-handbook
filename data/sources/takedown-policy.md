# Takedown policy — references archive (draft)

Status: draft for the handbook stewards (plan decisions D5 and D7). Not yet adopted.

## Why this archive exists

Organiser knowledge about Plone Conferences has been lost before. The 2010 Netsight
articles survive only in the Internet Archive; several conference sites from 2015–2018 are
already fragile. The handbook keeps local copies of every source it cites so future
organisers can check the evidence even after the original sites disappear. Preservation is
the default (decision D5); exclusion is the exception.

## Where the archive lives

- Today: `aftermath/documentation/references/` in the Plone Conference 2026 working
  repository (private to the organisers).
- After publication: the `references/` area of the Plone Conference Organisers Handbook
  repository, once the archive audit (`archive-audit.md`) has been reviewed and every row
  marked `exclude-pending-review` has been resolved.
- Each source carries a stable ID (S001–S090), its original URL and a sha256 hash in
  `bibliography/manifest.json` and `archive-audit.csv`.

## Who to contact

Send a request to `conf@plone.org` (subject line: "Handbook archive takedown") or open an
issue on the handbook repository. Include the source ID or original URL, your relationship
to the content (author, copyright holder, person named in it) and what you would like
changed.

## What happens on a request

1. **Acknowledge** within 7 days.
2. **Restrict quickly.** Remove the file from the published archive while the request is
   reviewed if it concerns personal data or a credible copyright claim. The manifest row
   stays, marked `withdrawn`, with the original URL and any public Wayback link.
3. **Review** by two handbook stewards within 30 days. Options: keep (with reason given to
   the requester), redact (personal data removed, redaction noted in the manifest), replace
   with a link to the original or a Wayback copy, or remove permanently.
4. **Record** the outcome in the manifest notes and the handbook changelog. Never record the
   requester's personal details in the public repository.
5. **History.** Git history keeps old copies. For personal data, stewards rewrite the
   history of the published repository or ask the hosting platform to purge cached views.

## Defaults the stewards apply

- Requests from people named in a source about their own personal data are granted.
- Requests from copyright holders are granted unless the content is under an open licence
  that permits redistribution (for example plone.org pages under CC BY-SA 4.0); even then,
  stewards consider the request in good faith.
- Handbook chapters keep their citation and summary of a removed source; only the copy is
  withdrawn.

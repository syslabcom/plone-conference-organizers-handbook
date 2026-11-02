# Toolchain notes

This file records deviations from plone/documentation (branch 6.0).

## Requirements pins

- `requirements-initial.txt` keeps the upstream pins `pip==26.2.1`, `setuptools==81.0.0`, and `wheel==0.47.0`.
- `requirements.txt` keeps the upstream constraints for the packages that remain: `plone-sphinx-theme<2` and `sphinx<9`.
- Added `myst-parser`.
  Upstream gets it transitively through `sphinx-examples`, which the handbook does not use.
  Without the explicit entry, `myst_parser` is missing from the fresh venv.
- Removed (decision D6): `sphinx-examples`, `sphinx-llms-txt`, `sphinx-notfound-page`, `sphinx-sitemap`, `sphinx-tippy`, `sphinxcontrib.httpdomain`, `sphinxcontrib.httpexample`, `sphinxcontrib-video`, `sphinxcontrib-youtube`.
- No pin failed to install on macOS arm64.

## Removed from upstream

- Git submodules, symlinked docs (plone.api, plone.restapi, Volto), `make deps` submodule steps, Storybook, `make deploy`, the version switcher, and the intersphinx entries that require submodules.
- Extensions: autodoc, autosummary, doctest, graphviz, ifconfig, todo, viewcode, and the `source_replace` hook.
- Upstream builds with `make html`; the handbook CI uses `make html SPHINXOPTS="-W --keep-going"`.
- Vale: the upstream CI clones the Microsoft style by hand; here `make vale` runs `vale sync`, and CI does the same.

## Local Python

The Makefile uses `python3`.
The first verification ran on Python 3.15 locally; CI and Read the Docs use Python 3.12.

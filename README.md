# Plone Conference Organizers Handbook

A public, community-maintained manual for organizing Plone conferences.
Also found under the spelling "organisers" (the British variant), so search for either.

## Status

This repository incubates under the `syslabcom` GitHub organization.
It will be offered for transfer to the `plone` organization at v1.
The handbook is a skeleton today; no chapters are written yet.

## Quickstart

```shell
make livehtml
```

This creates a virtual environment, installs the requirements, builds the docs, and serves them with live reload at <http://127.0.0.1:8050>.

Other targets:

```shell
make help
make html SPHINXOPTS="-W --keep-going"
make vale
make linkcheck
make clean
make distclean
```

## Toolchain

The toolchain mirrors [plone/documentation](https://github.com/plone/documentation) (branch 6.0): MyST Markdown with reStructuredText allowed, `plone-sphinx-theme`, Vale prose linting, and Read the Docs pull request previews.
The Makefile creates its own `venv`, as upstream does.
See `TOOLCHAIN-NOTES.md` for deviations from upstream.

## License

[Creative Commons Attribution 4.0 International](LICENSE) (CC BY 4.0).

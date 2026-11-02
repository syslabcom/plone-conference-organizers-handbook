# Configuration file for the Sphinx documentation builder.
# Plone Conference Organizers Handbook build configuration.
# Mirrors plone/documentation (branch 6.0), reduced to the extensions the handbook needs.

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.generate.render import setup as setup

# -- Project information -----------------------------------------------------

project = "Plone Conference Organizers Handbook"
copyright = "Plone community, CC BY 4.0"
author = "Plone community"
version = "0.1"
release = "0.1"

# -- General configuration ----------------------------------------------------

templates_path = ["_templates"]

extensions = [
    "myst_parser",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_reredirects",
    "sphinxcontrib.mermaid",
    "sphinxext.opengraph",
]

smartquotes = False

source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}
master_doc = "index"

# Internal specifications and helper documents are not part of the built handbook.
exclude_patterns = [
    "spec/**",
    "spelling_wordlist.txt",
    "**/README.md",
    "**/README.rst",
    "**/CHANGES.md",
    "**/CONTRIBUTORS.md",
    "**/LICENSE.rst",
]

suppress_warnings = [
    "myst.strikethrough",
]

# -- Linkcheck ----------------------------------------------------------------

linkcheck_anchors = True
linkcheck_ignore = [
    r"http://127.0.0.1",
    r"http://localhost",
    r"https://web.archive.org/",
]
linkcheck_report_timeouts_as_broken = True
linkcheck_retries = 1
linkcheck_timeout = 5

# -- HTML output --------------------------------------------------------------

html_theme = "plone_sphinx_theme"
html_title = project
html_sidebars = {
    "**": [
        "navbar-logo",
        "search-button-field",
        "sbt-sidebar-nav",
    ]
}
html_theme_options = {
    "article_header_start": ["toggle-primary-sidebar"],
    "extra_footer": """<p>The text and illustrations in this handbook are licensed under a Creative Commons Attribution 4.0 International license. Plone and the Plone® logo are registered trademarks of the Plone Foundation. For guidelines on the permitted uses of the Plone trademarks, see <a href="https://plone.org/foundation/logo">https://plone.org/foundation/logo</a>.</p>""",
    "footer_content_items": [
        "author",
        "copyright",
        "last-updated",
        "extra-footer",
        "icon-links",
    ],
    "logo": {
        "text": project,
    },
    "navigation_with_keys": True,
    "path_to_docs": "docs",
    "repository_branch": "main",
    "repository_url": "https://github.com/syslabcom/plone-conference-organizers-handbook",
    "search_bar_text": "Search",
    "show_toc_level": 2,
    "use_edit_page_button": False,
    "use_issues_button": True,
    "use_repository_button": True,
}
html_static_path = ["_static"]

# Branding, mirroring plone/documentation: the Plone logo and favicon are the
# files from plone/documentation's docs/_static, used under the Plone
# Foundation's trademark guidelines (see the extra footer below).
html_logo = "_static/logo.svg"
html_favicon = "_static/favicon.ico"
html_css_files = ["hb.css"]

# -- MyST ---------------------------------------------------------------------

myst_enable_extensions = [
    "attrs_block",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "html_image",
    "linkify",
    "strikethrough",
    "substitution",
]

# -- Intersphinx --------------------------------------------------------------

intersphinx_mapping = {
    "plone": ("https://6.docs.plone.org/", None),
}

# -- Mermaid ------------------------------------------------------------------

mermaid_version = "11.2.0"

# -- OpenGraph ----------------------------------------------------------------

ogp_description_length = 200
ogp_site_name = project
ogp_type = "website"
ogp_custom_meta_tags = [
    '<meta property="og:locale" content="en_US" />',
]

# -- sphinx-reredirects -------------------------------------------------------

redirects = {}

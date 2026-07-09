# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import re
from datetime import datetime

# -- Project information -----------------------------------------------------

project = "container-mod"
copyright = f"{datetime.now().year}, Tufts University"
author = "Yucheng Zhang"

# Pull the version straight out of the script so docs never drift from code.
def _read_script_version() -> str:
    script_path = os.path.join(os.path.dirname(__file__), "..", "container-mod")
    try:
        with open(script_path, "r", encoding="utf-8") as fh:
            for line in fh:
                m = re.match(r'^\s*VERSION="([^"]+)"\s*$', line)
                if m:
                    return m.group(1)
    except OSError:
        pass
    return "0.0.0"


release = _read_script_version()
version = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------

extensions = [
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinxcontrib.mermaid",
]

# Mermaid: use a moderate theme that works in both light and dark
mermaid_init_js = "mermaid.initialize({startOnLoad:true, theme:'neutral'});"
mermaid_output_format = "raw"

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "linkify",
    "substitution",
    "tasklist",
]

myst_heading_anchors = 3

# Substitutions available in Markdown pages via {{ ... }}
myst_substitutions = {
    "version": release,
}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}

# -- HTML output -------------------------------------------------------------

html_theme = "furo"
html_title = f"container-mod {release}"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_logo = "_static/logo.png"
html_favicon = "_static/logo.png"

# Brand colors — a calm indigo that reads well in both light and dark
_brand_primary_light = "#3b5bdb"
_brand_primary_dark = "#748ffc"

html_theme_options = {
    "sidebar_hide_name": True,
    "navigation_with_keys": True,
    "source_repository": "https://github.com/TuftsRT/container-mod/",
    "source_branch": "main",
    "source_directory": "docs/",
    "top_of_page_button": "edit",
    "announcement": (
        "\U0001F389 <strong>container-mod {} released</strong> — "
        "MPI support, robust runtime detection, and 110+ new app "
        "skeletons. See the "
        "<a href='changelog.html'>changelog</a>."
    ).format(release),
    "light_css_variables": {
        "color-brand-primary": _brand_primary_light,
        "color-brand-content": _brand_primary_light,
        "color-brand-visited": _brand_primary_light,
        "color-admonition-title--note": _brand_primary_light,
        "font-stack": (
            "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, "
            "'Helvetica Neue', Arial, sans-serif"
        ),
    },
    "dark_css_variables": {
        "color-brand-primary": _brand_primary_dark,
        "color-brand-content": _brand_primary_dark,
        "color-brand-visited": _brand_primary_dark,
    },
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/TuftsRT/container-mod",
            "html": (
                "<svg stroke='currentColor' fill='currentColor' stroke-width='0' "
                "viewBox='0 0 16 16'>"
                "<path fill-rule='evenodd' d='M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 "
                "5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-"
                ".09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 "
                "1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-"
                ".08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 "
                "1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 "
                "3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 "
                "8.013 0 0016 8c0-4.42-3.58-8-8-8z'></path></svg>"
            ),
            "class": "",
        },
    ],
}

# Default highlight language for bare ``` code fences without an explicit tag.
highlight_language = "bash"

# Prettier default pygments themes
pygments_style = "friendly"
pygments_dark_style = "monokai"

# Nicer copy-button behavior on shell code blocks.
copybutton_prompt_text = r"^\$ |^# |^\.\.\.: |^In \[\d*\]: | {2,5}\.\.\.:? |^\d+\.\.\d+ "
copybutton_prompt_is_regexp = True

# Nice defaults for linkify (used by MyST).
linkify_fuzzy_email = False

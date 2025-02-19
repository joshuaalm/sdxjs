"""Utilities."""

import os
import re
import sys
from pathlib import Path

import ivy
import markdown
import yaml

# File containing things to ignore.
DIRECTIVES_FILE = ".mccole"

# Configuration sections and their default values.
# These are added to the config dynamically under the `mccole` key,
# i.e., `"figures"` becomes `ivy.site.config["mccole"]["figures"]`.
CONFIGURATIONS = {
    "bibliography": set(),  # citations
    "definitions": [],  # glossary definitions
    "figures": {},  # numbered figures
    "glossary": set(),  # glossary keys
    "headings": {},  # number chapter, section, and appendix headings
    "inclusions": {},  # included files
    "index": {},  # index entries
    "syllabus": [],  # syllabus entries
    "tables": {},  # numbered tables
    "titles": [],  # chapter/appendix titles
}

# Translations of multilingual terms.
TRANSLATIONS = {
    "en": {
        "appendix": "Appendix",
        "chapter": "Chapter",
        "figure": "Figure",
        "seealso": "See also",
        "section": "Section",
        "table": "Table",
    },
    "es": {
        "appendix": "Anexo",
        "chapter": "Capítulo",
        "figure": "Figura",
        "seealso": "Ver también",
        "section": "Sección",
        "table": "Tabla",
    },
}

# Match a Markdown heading with optional attributes.
HEADING = re.compile(r"^(#+)\s*(.+?)(\{:\s*#(.+\b)\})?$", re.MULTILINE)

# Used to turn multiple whitespace characters into a single space.
MULTISPACE = re.compile(r"\s+", re.DOTALL)

# Match table elements.
TABLE = re.compile(r'<div\s+class="table(\s+[^"]+)?"[^>]*?>')
TABLE_CAPTION = re.compile(r'caption="(.+?)"')
TABLE_ID = re.compile(r'id="(.+?)"')
TABLE_DIV = re.compile(
    r'<div\s+caption="(.+?)"\s+class="(table(\s+[^"]+)?)"\s+id="(.+?)">\s*<table>',
    re.DOTALL,
)


def fail(msg):
    """Fail unilaterally."""
    print(msg, file=sys.stderr)
    raise AssertionError(msg)


def get_config(part):
    """Get configuration subsection or `None`.

    A result of `None` indicates the request is being made too early
    in the processing cycle.
    """
    require(part in CONFIGURATIONS, f"Unknown configuration section '{part}'")
    mccole = ivy.site.config.setdefault("mccole", {})
    return mccole.get(part, None)


def make_config(part, filler=None):
    """Make configuration subsection.

    If `filler` is provided, it is used as the initial value.
    Otherwise, the value from `CONFIGURATIONS` is used.
    """
    require(part in CONFIGURATIONS, f"Unknown configuration section '{part}'")
    filler = filler if (filler is not None) else CONFIGURATIONS[part]
    return ivy.site.config.setdefault("mccole", {}).setdefault(part, filler)


def make_copy_paths(node, filename, original=None, replacement=None):
    """Make source and destination paths for copying."""
    if (original is not None) and filename.endswith(original):
        filename = filename.replace(original, replacement)
    src = os.path.join(os.path.dirname(node.filepath), filename)
    dst = os.path.join(os.path.dirname(node.get_output_filepath()), filename)
    return src, dst


def make_label(kind, number):
    """Create numbered labels for figures, tables, and document parts."""
    translations = TRANSLATIONS[ivy.site.config["lang"]]
    if kind == "figure":
        name = translations["figure"]
    elif kind == "part":
        if len(number) > 1:
            name = translations["section"]
        elif number[0].isdigit():
            name = translations["chapter"]
        else:
            name = translations["appendix"]
    elif kind == "table":
        name = translations["table"]
    else:
        fail(f"Unknown kind of label {kind}")

    number = ".".join(number)
    return f"{name} {number}"


def make_major():
    """Construct major numbers/letters based on configuration.

    This function relies on the configuration containing `"chapters"`
    and `"appendices"`, which must be lists of slugs.
    """
    chapters = {slug: i + 1 for (i, slug) in enumerate(ivy.site.config["chapters"])}
    appendices = {
        slug: chr(ord("A") + i)
        for (i, slug) in enumerate(ivy.site.config["appendices"])
    }
    return chapters | appendices


def markdownify(text, ext=None, strip=True):
    """Convert to Markdown."""
    extensions = ["markdown.extensions.extra", "markdown.extensions.smarty"]
    if ext:
        extensions = [ext, *extensions]
    result = markdown.markdown(text, extensions=extensions)
    if strip and result.startswith("<p>"):
        result = result[3:-4]  # remove trailing '</p>' as well
    return result


def mccole():
    """Get configuration section, creating if necessary."""
    return ivy.site.config.setdefault("mccole", {})


def read_directives(dirname, section):
    """Get a section from the directives file if it exists"""
    filepath = Path(dirname).joinpath(DIRECTIVES_FILE)
    if not filepath.exists():
        return []
    with open(filepath, "r") as reader:
        content = yaml.safe_load(reader) or {}
        return content.get(section, [])


def read_glossary(filename):
    """Load the glossary definitions."""
    filename = Path(ivy.site.home(), filename)
    with open(filename, "r") as reader:
        return yaml.safe_load(reader) or {}


def require(cond, msg):
    """Fail if condition untrue."""
    if not cond:
        fail(msg)


def warn(title, items):
    """Warn about missing or unused items."""
    if not ivy.site.config.get("warnings", False):
        return
    if not items:
        return
    print(title)
    for i in sorted(items):
        print(f"-  {i}")

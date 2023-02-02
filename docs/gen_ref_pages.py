"""Generate the code reference pages."""

from pathlib import Path

import mkdocs_gen_files

MODULE_NAME = "./"  # "ai_common_utils"

for path in sorted(Path(MODULE_NAME).rglob("*.py")):

    module_path = path.relative_to(MODULE_NAME).with_suffix("")

    doc_path = path.relative_to(MODULE_NAME).with_suffix(".md")

    full_doc_path = Path("docs/API", doc_path)

    parts = list(module_path.parts)

    if parts[-1] == "__init__":
        parts = parts[:-1]
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")

    exclude = [
        "__init__",
        "__main__",
        "__version__",
        "setup",
        "tests",
        "gen_ref_pages",
    ]

    flag = False

    for m in exclude:
        if m in parts:
            flag = True
            break

    if flag:
        continue

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:

        identifier = ".".join(parts)

        print("::: " + identifier, file=fd)

    mkdocs_gen_files.set_edit_path(full_doc_path, path)

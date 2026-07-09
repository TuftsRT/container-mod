# Contributing

`container-mod` is open source and welcomes patches — bug fixes,
documentation, and modest feature additions.

## Where things live

```
container-mod/
├── container-mod            # main script
├── templates/               # Lua and Tcl modulefile templates
├── profiles/                # bundled cluster profiles
├── repos/                   # app metadata (see concepts/metadata.md)
├── docs/                    # this documentation
├── jupyter_kernel.json      # Jupyter kernel template
├── README.md
└── LICENSE
```

## Local development

Basic sanity checks that are worth running before opening a PR:

```bash
bash -n container-mod                    # syntax check
./container-mod --help                   # smoke-test help
./container-mod --list                   # smoke-test profile discovery
./container-mod pipe -p docker://staphb/blast:2.17.0   # end-to-end
```

If you're on macOS remember Bash 4+ is required (`brew install bash`).

If you change how modulefiles are generated, also review:

- [`templates/module_template.lua`](https://github.com/TuftsRT/container-mod/blob/main/templates/module_template.lua)
- [`templates/module_template.tcl`](https://github.com/TuftsRT/container-mod/blob/main/templates/module_template.tcl)
- the profile files in
  [`profiles/`](https://github.com/TuftsRT/container-mod/tree/main/profiles).

## Adding a new application to `repos/`

Create a text file `repos/<app>` with the schema described in
[Application metadata](concepts/metadata.md):

```text
Description: A brief one- or two-line description.
Home Page: https://project.org
Programs: prog1,prog2,prog3
```

Version records are optional; the script's `pull -u` can add them
automatically. Send a PR with the new file.

## Adding a new profile

Copy an existing profile file from `profiles/` and adapt it for your
site. Cluster-specific paths should live in `profiles/` (not in the
script) so users on other clusters aren't affected. See
[Profiles](configuration/profiles.md).

## Documentation

The docs you're reading are built with Sphinx + MyST from Markdown
sources under `docs/`. To build locally:

```bash
pip install -r docs/requirements.txt
sphinx-build -b html docs docs/_build/html
open docs/_build/html/index.html
```

Every page is a `.md` file; the site's structure is defined in the
`toctree` block near the top of `docs/index.md`.

## Pull request checklist

- Runs `bash -n container-mod` cleanly.
- Docs updated when relevant (README + `docs/`).
- Commit message describes the *why*, not just the *what*.
- No unrelated changes bundled in (e.g., no auto-formatted whitespace
  fixes to unrelated files).

## Getting help

- Bug reports: <https://github.com/TuftsRT/container-mod/issues>
- Contact the maintainer:
  [yucheng.zhang@tufts.edu](mailto:yucheng.zhang@tufts.edu)

## License

MIT — see the [LICENSE file](https://github.com/TuftsRT/container-mod/blob/main/LICENSE)
in the repo.

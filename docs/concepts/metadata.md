# Application metadata

Each application known to `container-mod` has a plain-text file under
`repos/`. It tells the script three things:

- a human description (rendered in the modulefile's `help` and `whatis`);
- the upstream project homepage (also rendered in the modulefile);
- which executables inside the container to wrap.

Optional `version()` lines record which container URI provides which
version. These are used by `--update` and as documentation.

## File format

```text
Description: Bowtie 2 is an ultrafast and memory-efficient tool for
aligning sequencing reads to long reference sequences.
Home Page: https://github.com/BenLangmead/bowtie2
Programs: bowtie2,bowtie2-build,bowtie2-inspect

version("2.5.4", uri="docker://quay.io/biocontainers/bowtie2:2.5.4--h7071971_4")
version("2.5.1", uri="docker://quay.io/biocontainers/bowtie2:2.5.1--py310h8d7afc0_0")
```

Rules:

- File name is the application name (`bowtie2`, no extension).
- `Description:` and `Home Page:` are single-line values.
- `Programs:` is a comma-separated list. Whitespace around commas is
  trimmed. This drives one-wrapper-per-program generation.
- `version()` lines are free-form annotation. `--update` prepends a new
  one on `pull -u`.

## Where the file lives

- **Personal mode:** `~/container-apps/repos/<app>`. Copied from the repo
  the first time you run in personal mode.
- **Profile-backed / shared mode:** `<repo>/repos/<app>` next to the
  script.

`container-mod` searches personal first, then the shared repo, so a user
can override the shared metadata without editing it in place.

## Creating a new entry interactively

If you invoke a subcommand that needs metadata (`module`, `exec`, `pipe`,
or `pull -u`) for an app that isn't in the database, `container-mod`
prompts:

```text
'myapp' not found in application info database.
Let's create a new entry...
Enter a simple description of the application: …
Enter the application's homepage URL: …
Enter the available programs (comma-separated): …
```

The answers are written into the appropriate `repos/<app>` file at mode
`644`.

`pull` alone — without `-u` — never triggers this prompt because it never
consumes metadata. See [pull](../usage/subcommands/pull.md).

## Recording versions with `--update`

```bash
./container-mod pull --profile biocontainers -u \
  docker://quay.io/biocontainers/fastqc:0.12.1--hdfd78af_0
```

After a successful pull, the script prepends a new line to
`repos/fastqc`:

```text
version("0.12.1", uri="docker://quay.io/biocontainers/fastqc:0.12.1--hdfd78af_0")
```

The file is rewritten atomically (via `mktemp` + `mv`) and reset to mode
`644` afterward.

## URI parsing quirks

The version part of the URI (the `:tag`) is stripped of common
biocontainers-style suffixes before being used as the module version:

| URI | App | Version |
|---|---|---|
| `docker://quay.io/biocontainers/bowtie2:2.5.4--h7071971_4` | `bowtie2` | `2.5.4` |
| `docker://staphb/blast:2.17.0` | `blast` | `2.17.0` |
| `docker://nvcr.io/nvidia/pytorch:25.01-py3` | `pytorch` | `25.01-py3` |
| `docker://nvcr.io/nvidia/clara/clara-parabricks:4.5.0-1` | `parabricks` | `4.5.0-1` |
| `docker://quay.io/qiime2/amplicon:2024.2` | `qiime2` | `2024.2` |

A few paths use custom name mapping in the script (`qiime2`,
`parabricks`, `nsightsys`). Extend `_ensure_uri_details_cached` if you
need more mappings.

## Bulk-loading metadata

If you already have a curated list of apps from another source, you can
just drop them into `repos/` as text files matching the format above.
`container-mod` picks them up on next run. See the existing 100+ entries
in the repo for reference.

## Next

- **[Profiles](../configuration/profiles.md)** — configure output
  locations.
- **[Subcommands](../usage/subcommands.md)** — what actually reads / writes
  each field.

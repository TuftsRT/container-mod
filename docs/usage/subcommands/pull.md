# `pull`

Downloads a container image to the configured image directory. Does
**nothing else** — no wrappers, no modulefile.

## Synopsis

```
container-mod pull [options] <URI-or-image> [...]
```

## Behavior

- **Remote URI** (`docker://…`, `oras://…`, etc.): the runtime is
  invoked as `singularity pull --force ...` (or the Apptainer
  equivalent). The resulting `.sif` is `chmod 644`.
- **Local `.sif` file**: nothing is copied or moved. The wrapper
  generation step (`exec`) later points at the file's original
  location.
- **Nonexistent local path**: error, exit 1.

By default, `pull` does **not** prompt for missing app metadata.
Metadata is only needed for `module`, `exec`, and `pipe`. If the
metadata isn't present when you later run those, you'll be prompted
then.

## Output locations

::::{list-table}
:header-rows: 1
:widths: 25 40 35

* - Mode
  - Path
  - Chosen by
* - Personal
  - `~/container-apps/images/<image>.sif`
  - `-p`, or no `--profile`
* - Profile-backed
  - `${PUBLIC_IMAGEDIR}/<image>.sif`
  - `--profile <name>`
::::

`<image>` is derived from the URI (colons replaced with underscores,
prefix stripped, `.sif` extension appended). Example:

```
docker://quay.io/biocontainers/bowtie2:2.5.4--h7071971_4
    → quay.io_biocontainers_bowtie2:2.5.4--h7071971_4.sif
```

## The `-u` / `--update` flag

Records the pulled version in the app metadata file at `repos/<app>`.

```{code-block} bash
container-mod pull --profile biocontainers -u \
    docker://quay.io/biocontainers/fastqc:0.12.1--hdfd78af_0
```

After a successful pull, `repos/fastqc` is rewritten so a new
`version("0.12.1", …)` line is at the top (older versions are kept in
place, deduplicated):

```{code-block} text
:caption: repos/fastqc after --update

Description: A quality control tool for high throughput sequence data.
Home Page: https://www.bioinformatics.babraham.ac.uk/projects/fastqc/
Programs: fastqc

version("0.12.1", uri="docker://quay.io/biocontainers/fastqc:0.12.1--hdfd78af_0")
version("0.11.9", uri="docker://quay.io/biocontainers/fastqc:0.11.9--0")
```

The rewrite is atomic (`mktemp` + `mv`) and the final file is
`chmod 644` so users / other admins can read it.

**`-u` is a no-op for local `.sif` files.** There's no remote URI to
record; the script prints a one-line warning and continues.

## The `-f` / `--force` flag

Re-pulls even when the target `.sif` already exists. Useful when:

- The upstream tag has been mutated in the registry.
- A previous pull was interrupted and left a truncated `.sif`.
- You want to refresh the local cache after a container rebuild.

Without `-f`, an existing image is left in place and the script
prints `Image already exists: <path>. Skipping.`.

## Runtime detection

Before pulling, `container-mod` runs `detect_container_runtime`, which
picks the container runtime binary to invoke. See
[Runtime detection](../../advanced/runtime-detection.md).

If neither Singularity nor Apptainer is available, `pull` fails with:

```{code-block} text
container-mod: Error: Failed to find or load a container runtime
(Singularity/Apptainer).
```

## Permissions on the pulled image

Shared admin mode: `chmod 644 <image>.sif` is called after the pull,
followed by a mode self-check that warns if the image ended up at any
other mode. Personal mode: chmod is still applied but the self-check
is skipped.

## Batch pulls

`pull` is the "cheap" subcommand — no metadata lookup, no runtime
probe of the image contents. Ideal for overnight batch pulls on a
build node:

```{code-block} bash
:caption: /tmp/queue.txt

docker://quay.io/biocontainers/vcftools:0.1.16--h9a82719_5
docker://quay.io/biocontainers/fastqc:0.12.1--hdfd78af_0
docker://quay.io/biocontainers/multiqc:1.24.1--pyhdfd78af_0
```

```bash
while IFS= read -r uri; do
    ./container-mod pull --profile biocontainers -u "$uri"
done </tmp/queue.txt
```

Follow up with a batch `module` + `exec` pass once metadata is ready.

## Exit codes

- `0` — success (image now present at target path).
- `1` — runtime pull failed, or `-u` update failed (partial image is
  cleaned up).

## Common workflows

```{code-block} bash
:caption: Personal test pull

container-mod pull -p docker://staphb/blast:2.17.0
```

```{code-block} bash
:caption: Admin — pull with version recording

container-mod pull --profile biocontainers -u \
    docker://quay.io/biocontainers/samtools:1.21--h50ea8bc_0
```

```{code-block} bash
:caption: Force refresh of a mutable tag

container-mod pull -f --profile biocontainers \
    docker://staphb/blast:latest
```

## See also

- **[module](module.md)** — generate the modulefile for the pulled
  image.
- **[exec](exec.md)** — generate the wrapper scripts.
- **[pipe](pipe.md)** — one-shot pull + module + exec.
- **[Options](../options.md)** — full flag reference.

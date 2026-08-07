# `pipe`

Runs `pull`, `module`, and `exec` in that order, for each URI. Nine
times out of ten, this is the subcommand you actually want.

## Synopsis

```
container-mod pipe [options] <URI-or-image> [...]
```

## Behavior

`pipe` is exactly equivalent to:

```bash
container-mod pull   [options] <URI>
container-mod module [options] <URI>
container-mod exec   [options] <URI>
```

for each URI on the command line — but with one important detail: if
processing one URI fails, the remaining ones are skipped. Failures
short-circuit, so a bad pull doesn't lead to trying to generate a
modulefile against a missing image.

## When to use

- **Testing a new container.** `pipe -p docker://...` gets you a
  module load–able app in seconds.
- **Deploying to production.** `pipe --profile <name>` produces the
  image, the modulefile (staged in `incomplete/`), and wrappers in
  one shot.
- **Refreshing everything after an upgrade.** `pipe -f` re-pulls,
  regenerates the modulefile, and rebuilds the wrappers.

## When NOT to use

- **Batch pulls without wrapper generation.** Use plain `pull` on a
  build node overnight.
- **Regenerating wrappers only** (e.g. after a bug fix in the wrapper
  template). Use `exec -f` on its own; skip the network and metadata
  work.
- **Regenerating modulefiles only** (e.g. after adding
  `BIND_PATH="…"` to your profile). Use `module` on its own.

## Multi-URI runs

You can pipe multiple URIs in one call. Order matters for
short-circuiting:

```bash
container-mod pipe --profile biocontainers \
    docker://quay.io/biocontainers/samtools:1.21--h50ea8bc_0 \
    docker://quay.io/biocontainers/bcftools:1.21--h3a4d415_0 \
    docker://quay.io/biocontainers/htslib:1.21--h5efdd21_0
```

If samtools fails to pull, bcftools and htslib are not attempted.

For independent deployments where you don't want short-circuiting,
loop yourself:

```bash
for uri in <uri1> <uri2> <uri3>; do
    container-mod pipe --profile biocontainers "$uri" || \
        echo "  ! failed: $uri" >&2
done
```

## Exit codes

- `0` — every URI completed all three steps.
- `1` — one URI failed at some step; remaining URIs skipped.

## Options

`pipe` accepts every option `pull`, `module`, and `exec` accept.
Notable ones:

::::{list-table}
:header-rows: 1
:widths: 20 20 60

* - Flag
  - Affects
  - Purpose
* - `-f`, `--force`
  - all three
  - Re-pull, overwrite existing modulefile, wipe wrapper bin dir.
* - `-u`, `--update`
  - `pull`
  - Record the version in `repos/<app>`.
* - `-j`, `--jupyter`
  - runs after all three
  - Also register a Jupyter kernel (see
    [Jupyter support](../../advanced/jupyter.md)).
* - `-t`, `--tcl`
  - `module`
  - Generate a Tcl modulefile instead of Lua.
* - `-p`, `--personal`
  - all three
  - Write to `$HOME`.
* - `--profile <name>`
  - all three
  - Load a profile and write to its shared locations.
::::

## Common workflows

```{code-block} bash
:caption: End-to-end personal deploy

container-mod pipe -p docker://staphb/bowtie2:2.5.4
module use ~/privatemodules
module load bowtie2/2.5.4
bowtie2 --help
```

```{code-block} bash
:caption: Admin — full production deploy

container-mod pipe --profile biocontainers -u \
    docker://quay.io/biocontainers/vcftools:0.1.16--h9a82719_5

# Smoke-test the staged module
module use ./incomplete
module load vcftools/0.1.16
vcftools --version

# Promote
mv incomplete/vcftools/0.1.16.lua "$MOD_EXISTING_DIR_DEF/vcftools/"
```

```{code-block} bash
:caption: Deploy with a Jupyter kernel

container-mod pipe -p -j docker://tensorflow/tensorflow:2.18.0-jupyter

# In Jupyter, pick the kernel "tensorflow 2.18.0-jupyter"
```

```{code-block} bash
:caption: MPI-capable deploy

container-mod pipe --profile mpi-cluster \
    docker://lammps/lammps:stable_2Aug2023_update3_ubuntu20.04_openmpi_py3
```

## Ordering details

The subcommands run in a specific order for a reason:

- **`pull` first** — subsequent steps need the image on disk.
- **`module` before `exec`** — the modulefile is independent of the
  probe result, so we lock it in first. If `exec` fails to probe
  some programs, the modulefile is already deployable.
- **`exec` last** — needs the image AND the metadata to be settled.

## See also

- **[pull](pull.md)**, **[module](module.md)**, **[exec](exec.md)** —
  the three subcommands `pipe` runs.
- **[Quick start](../../quickstart.md)** — the most common `pipe`
  invocations.
- **[Options](../options.md)** — full flag reference.

# Bundled profiles

The repository ships six profiles under `profiles/`. All target Tufts
HPC and are intended as **worked examples** rather than universal
recipes — copy one and adapt for your cluster. Each is a plain shell
file sourced by `container-mod` when you pass `--profile <name>`.

## At a glance

::::{list-table}
:header-rows: 1
:widths: 22 30 25 23

* - Profile
  - Purpose
  - Image + tool root
  - `BIND_PATH`
* - `biocontainers`
  - Legacy Tufts BioContainers tree
  - `/cluster/tufts/biocontainers/…`
  - `/cluster/tufts`
* - `biocontainers_rocky9`
  - Rocky 9 replacement for `biocontainers`
  - `/cluster/tufts/apps/container/biocontainers/…`
  - `/cluster/tufts`
* - `ngc`
  - Legacy NVIDIA NGC tree
  - `/cluster/tufts/ngc/…`
  - `/cluster/tufts`
* - `ngc_rocky9`
  - Rocky 9 replacement for `ngc`
  - `/cluster/tufts/apps/container/ngc/…`
  - `/cluster/tufts`
* - `gis`
  - Geographic Information Systems software
  - `/cluster/tufts/apps/container/gis/…`
  - `/cluster/tufts`
* - `course_jupyter`
  - Course-specific Jupyter-heavy containers
  - `/cluster/tufts/apps/class/…`
  - `/cluster/tufts`
::::

Run `container-mod --list` to see the same list on your system, plus
any personal overrides under `~/container-apps/profiles/`.

## `biocontainers`

Legacy Tufts BioContainers tree. Use `biocontainers_rocky9` on any
current-generation Rocky 9 login/compute node.

```{code-block} bash
:caption: profiles/biocontainers

MOD_EXISTING_DIR_DEF="/cluster/tufts/biocontainers/modules"
PUBLIC_IMAGEDIR="/cluster/tufts/biocontainers/images"
PUBLIC_EXECUTABLE_DIR="/cluster/tufts/biocontainers/tools"
BIND_PATH="/cluster/tufts"
```

Typical deployment:

```bash
container-mod pipe --profile biocontainers \
    docker://quay.io/biocontainers/samtools:1.21--h50ea8bc_0
```

The modulefile lands in `./incomplete/samtools/1.21.lua` for review;
promote to `/cluster/tufts/biocontainers/modules/samtools/` when
ready.

## `biocontainers_rocky9`

Same purpose as `biocontainers` but pointed at the Rocky 9 tree.

```{code-block} bash
:caption: profiles/biocontainers_rocky9

MOD_EXISTING_DIR_DEF="/cluster/tufts/apps/container/biocontainers/modules"
PUBLIC_IMAGEDIR="/cluster/tufts/apps/container/biocontainers/images"
PUBLIC_EXECUTABLE_DIR="/cluster/tufts/apps/container/biocontainers/tools"
BIND_PATH="/cluster/tufts"
```

## `ngc`

Legacy NVIDIA NGC tree — pretrained models, HPC benchmarks,
containerized frameworks (`pytorch:*`, `tensorflow:*`,
`clara-parabricks:*`).

```{code-block} bash
:caption: profiles/ngc

MOD_EXISTING_DIR_DEF="/cluster/tufts/ngc/modules"
PUBLIC_IMAGEDIR="/cluster/tufts/ngc/images"
PUBLIC_EXECUTABLE_DIR="/cluster/tufts/ngc/tools"
BIND_PATH="/cluster/tufts"
```

The registry banner in generated modulefiles is set to **NVIDIA NGC**
because the URI matches `nvcr.io/...`, and the "More information"
link points at the NGC catalog. See [Templates / Registry
auto-detection](../advanced/templates.md#registry-auto-detection).

## `ngc_rocky9`

Rocky 9 replacement for `ngc`.

```{code-block} bash
:caption: profiles/ngc_rocky9

MOD_EXISTING_DIR_DEF="/cluster/tufts/apps/container/ngc/modules"
PUBLIC_IMAGEDIR="/cluster/tufts/apps/container/ngc/images"
PUBLIC_EXECUTABLE_DIR="/cluster/tufts/apps/container/ngc/tools"
BIND_PATH="/cluster/tufts"
```

## `gis`

Geographic-information tools that need heavier bind mounts than
biocontainers (typically because they read/write large raster or
vector datasets under `/cluster/tufts/data/gis`).

```{code-block} bash
:caption: profiles/gis

MOD_EXISTING_DIR_DEF="/cluster/tufts/apps/container/gis/modules"
PUBLIC_IMAGEDIR="/cluster/tufts/apps/container/gis/images"
PUBLIC_EXECUTABLE_DIR="/cluster/tufts/apps/container/gis/tools"
BIND_PATH="/cluster/tufts"
```

## `course_jupyter`

Course-specific containers, typically registered as Jupyter kernels
for classroom use.

```{code-block} bash
:caption: profiles/course_jupyter

MOD_EXISTING_DIR_DEF="/cluster/tufts/apps/class/modules"
PUBLIC_IMAGEDIR="/cluster/tufts/apps/class/images"
PUBLIC_EXECUTABLE_DIR="/cluster/tufts/apps/class/tools"
BIND_PATH="/cluster/tufts"
```

Combine with `-j`:

```bash
container-mod pipe --profile course_jupyter -j \
    docker://tuftsttsrt/course-r:1.2
```

## Adapting a profile for your cluster

The Tufts-specific bits are the paths in `MOD_EXISTING_DIR_DEF`,
`PUBLIC_IMAGEDIR`, `PUBLIC_EXECUTABLE_DIR`, and `BIND_PATH`. Copy any
profile into `~/container-apps/profiles/<your-name>` or
`profiles/<your-name>` in the repo, and change those four values:

```{code-block} bash
:caption: profiles/purdue-biocontainers (example port)

MOD_EXISTING_DIR_DEF="/depot/biocontainers/modules"
PUBLIC_IMAGEDIR="/depot/biocontainers/images"
PUBLIC_EXECUTABLE_DIR="/depot/biocontainers/tools"
BIND_PATH="/depot,/scratch"
```

You may want to add MPI / GPU-specific overrides in a separate profile
— see [MPI support](../advanced/mpi.md#turning-mpi-on-for-a-profile).

## Personal overrides

If you drop a file in `~/container-apps/profiles/` with the same
name as a bundled profile, yours wins. `container-mod --list` marks
the shared one `(Overridden)`. Handy for testing a profile change
without touching the shared checkout.

## See also

- **[Profiles](profiles.md)** — how profiles are loaded.
- **[Profile variables](variables.md)** — every knob.

# `exec`

Generates wrapper scripts, one per program the container exposes.
Requires the image to already exist on disk because it probes the
container for which programs are present.

## Synopsis

```
container-mod exec [options] <URI-or-image> [...]
```

## Behavior

For each URI:

1. Resolves the app name, version, and image location.
2. Reads the `Programs:` list from the app's metadata file (prompts
   to create the file if missing).
3. For each program in the list:
   - Runs `singularity exec <image> sh -c "command -v <program>"`
     inside the container. Falls back to `which` for images that
     don't ship `command -v` in `sh`. See
     [confirm_exec_exists in the source](https://github.com/TuftsRT/container-mod/blob/main/container-mod).
   - If found, writes a wrapper at
     `<exec_outdir>/<app>/<version>/bin/<program>` at mode `755`.
   - If not found, prints a warning like
     `Warning: Executable not found in container: <program>` and
     skips.
4. Runs `ensure_tree_access` over the app tree so every directory is
   `755` and every wrapper is `755`.
5. Shared mode: runs `verify_tree_perms` to warn about any mode drift.

## Output locations

::::{list-table}
:header-rows: 1
:widths: 25 55 20

* - Mode
  - Path
  - Chosen by
* - Personal
  - `~/container-apps/tools/<app>/<version>/bin/<program>`
  - `-p`, or no `--profile`
* - Profile-backed
  - `${PUBLIC_EXECUTABLE_DIR}/<app>/<version>/bin/<program>`
  - `--profile <name>`
::::

The generated modulefile prepends this bin directory to `PATH`, so
users on the loaded module just type `<program> …` and the wrapper
handles the container invocation.

## Anatomy of a generated wrapper

```{code-block} bash
:caption: Example: ~/container-apps/tools/blast/2.17.0/bin/blastn

#!/usr/bin/env bash
# Wrapper script for 'blastn' from container 'staphb_blast:2.17.0.sif'

VER="2.17.0"
PKG="blast"
PROGRAM="blastn"
IMAGE_DIR="/home/yucheng/container-apps/images"
IMAGE="staphb_blast:2.17.0.sif"
RUNTIME="singularity"
RUNTIME_LAUNCH="exec"

# Load the container runtime if it is not already loaded.
if ! command -v "$RUNTIME" &> /dev/null; then
    if command -v module &> /dev/null; then
        module load "singularity" || { echo "Failed to load singularity module"; exit 1; }
    fi
fi

if ! command -v "$RUNTIME" &> /dev/null; then
    echo "Failed to find container runtime: $RUNTIME"
    exit 1
fi

# Determine GPU flags for the container runtime.
OPTIONS=()
if command -v nvidia-smi &> /dev/null && nvidia-smi -L &> /dev/null; then
    OPTIONS+=("--nv")
elif command -v rocm-smi &> /dev/null && rocm-smi -L &> /dev/null; then
    OPTIONS+=("--rocm")
fi

RUNTIME_OPTIONS=()

"$RUNTIME" "$RUNTIME_LAUNCH" "${RUNTIME_OPTIONS[@]}" "${OPTIONS[@]}" \
    "$IMAGE_DIR/$IMAGE" "$PROGRAM" "$@"
```

Key properties:

- Always uses arrays for options so quoted arguments (paths with
  spaces, `--foo=bar`) survive.
- Forwards `"$@"` unchanged.
- The `module load` fallback is emitted only when a matching runtime
  module was detected at generation time. On hosts where the runtime
  is only a system binary, the fallback is replaced with a comment.

## Options controlling the wrapper contents

Wrappers bake in profile settings from the *generation host* at the
time of `exec`. If you change any of these in the profile, rerun
`exec` to regenerate:

::::{list-table}
:header-rows: 1
:widths: 30 40 30

* - Setting
  - Effect in the wrapper
  - Change with
* - `RUNTIME_MODULE`
  - Presence of the `module load <name>` fallback and which module
    name is used
  - Profile variable / auto-detection
* - `RUNTIME_LAUNCH`
  - `apptainer exec` vs `apptainer run`
  - Profile variable
* - `RUNTIME_OPTIONS`
  - Extra runtime flags baked in as an array
  - Profile variable
* - GPU detection
  - Runtime probe of `nvidia-smi` / `rocm-smi` — same wrapper on
    every host, evaluated at wrapper run time
  - No configuration needed
::::

See [Profile variables](../../configuration/variables.md).

## The `-f` / `--force` flag

Without `-f`, an existing app-tree directory produces
`Output directory <path> already exists. Skipping.` Use `-f` to wipe
the old wrappers and regenerate:

```bash
container-mod exec -f --profile biocontainers \
    docker://quay.io/biocontainers/bowtie2:2.5.4--h7071971_4
```

`-f` is essential when:

- The `Programs:` list in the metadata file changed (new / renamed
  programs).
- You updated a profile variable that affects the wrapper contents
  (e.g. added `RUNTIME_OPTIONS="--mpi --cleanenv"`).
- You upgraded `container-mod` and a bug in the wrapper template was
  fixed.

## Program-name mapping

`container-mod` uses the `Programs:` field verbatim — the wrapper name
equals the program name inside the container. If your container ships
`bowtie2-inspect-s` and `bowtie2-inspect-l` but the wrapper module
should just expose `bowtie2-inspect`, edit the metadata file to include
only `bowtie2-inspect` in `Programs:`.

## Local `.sif` files

If the URI is a local file (`/path/to/image.sif`), the generated
wrapper points at the absolute on-disk path. Moving the `.sif`
breaks all wrappers referencing it. Consider `pull`-ing to your
image directory instead for anything long-lived.

## Exit codes

- `0` — all wrappers generated (or skipped without `-f`); individual
  program failures produce warnings but not errors.
- `1` — could not create the output directory, or metadata could not
  be resolved.

## Common workflows

```{code-block} bash
:caption: Regenerate wrappers after upgrading container-mod

container-mod exec -f --profile biocontainers \
    docker://quay.io/biocontainers/bowtie2:2.5.4--h7071971_4
```

```{code-block} bash
:caption: Personal — generate wrappers only, skip the pull

container-mod exec -p docker://staphb/blast:2.17.0
```

```{code-block} bash
:caption: Bulk regenerate every deployed app in a profile

for app_ver in /cluster/tufts/biocontainers/tools/*/*/; do
    app=$(basename "$(dirname "$app_ver")")
    ver=$(basename "$app_ver")
    # Look up the URI from repos/<app> and rerun
    ...
done
```

## See also

- **[pull](pull.md)** — download the image first.
- **[module](module.md)** — the modulefile that puts wrappers on
  `PATH`.
- **[GPU support](../../advanced/gpu.md)** — how the `--nv` / `--rocm`
  detection works.
- **[MPI support](../../advanced/mpi.md)** — how `RUNTIME_OPTIONS`
  changes the wrapper.

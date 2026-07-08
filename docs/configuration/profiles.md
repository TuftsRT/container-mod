# Profiles

A **profile** is a shell file that declares cluster-specific output
locations and behavior tweaks. When you pass `--profile NAME`,
`container-mod` sources that file just before doing any work, so the
declarations become environment variables the script consults.

## Where profiles live

`container-mod` searches two directories, in order:

1. `~/container-apps/profiles/` — personal overrides.
2. `<repo>/profiles/` — profiles bundled with the checkout.

If both directories have a file with the same name, the personal one
wins; the shared one is marked `(Overridden)` in `--list` output.

## Bundled profiles

```bash
$ container-mod --list
biocontainers
biocontainers_rocky9
course_jupyter
gis
ngc
ngc_rocky9
```

These target Tufts HPC and are examples, not universal recipes — copy
one and adapt for your cluster. Each declares three or four variables:

```bash
# profiles/biocontainers
MOD_EXISTING_DIR_DEF="/cluster/tufts/biocontainers/modules"
PUBLIC_IMAGEDIR="/cluster/tufts/biocontainers/images"
PUBLIC_EXECUTABLE_DIR="/cluster/tufts/biocontainers/tools"
BIND_PATH="/cluster/tufts"
```

See [Profile variables](variables.md) for a full reference of every
knob a profile can set (including `BIND_PATH`, `RUNTIME_MODULE`,
`RUNTIME_LAUNCH`, and `RUNTIME_OPTIONS`).

## Creating a custom profile

Add a plain shell file under `~/container-apps/profiles/<name>` or under
the repo's `profiles/`:

```bash
# profiles/my-cluster
MOD_EXISTING_DIR_DEF="/cluster/example/modules"
PUBLIC_IMAGEDIR="/cluster/example/images"
PUBLIC_EXECUTABLE_DIR="/cluster/example/tools"

# Optional: bind a site-wide filesystem into every container
BIND_PATH="/cluster/example"

# Optional: pin a specific runtime module rather than autodetect
# RUNTIME_MODULE="apptainer/1.3.0"

# Optional: MPI support for HPC-scale jobs
# RUNTIME_LAUNCH="run"
# RUNTIME_OPTIONS="--mpi --cleanenv"
```

Use it:

```bash
./container-mod pipe --profile my-cluster \
  docker://quay.io/biocontainers/seqkit:2.10.0--h9ee0642_0
```

## What each variable does

- **`MOD_EXISTING_DIR_DEF`** — the shared production module tree. When
  generating a new modulefile for an existing app, the script looks
  here for the *previous* version so it can repurpose that file's
  customizations. It is *not* the directory a new modulefile is written
  into (that's `<OUTDIR>/incomplete/`, staged for review).
- **`PUBLIC_IMAGEDIR`** — where pulled `.sif` images go in shared mode.
- **`PUBLIC_EXECUTABLE_DIR`** — the wrapper root; wrappers land at
  `${PUBLIC_EXECUTABLE_DIR}/<app>/<version>/bin/`. Generated modulefiles
  hard-code this path in their `prepend_path("PATH", …)` line, so keep
  it stable across releases.
- **`BIND_PATH`** — optional site-wide bind path injected into
  `APPTAINER_BIND` from generated modulefiles. Leave unset for portable
  modules. See [Profile variables](variables.md#bind_path).
- **`RUNTIME_MODULE`** — override the auto-detected container runtime
  module name. See [Runtime detection](../advanced/runtime-detection.md).
- **`RUNTIME_LAUNCH`** — `exec` (default) or `run`. Controls how the
  wrapper invokes the container. See [Profile variables](variables.md#runtime_launch).
- **`RUNTIME_OPTIONS`** — space-separated container runtime flags to
  bake into every wrapper (e.g. `--mpi --cleanenv`). See
  [Profile variables](variables.md#runtime_options).

## `--profile` vs `-p / --personal`

- `--profile` selects **shared / cluster** output locations governed by
  the named profile.
- `-p` / `--personal` overrides everything to `$HOME`.
- If you pass **neither**, the script runs in personal mode automatically
  and prints `No profile specified. Running in personal mode.`

Do not pass both; results are undefined.

## Staged output vs live output

When a profile is active, new modulefiles land under `<OUTDIR>/incomplete/`
rather than `MOD_EXISTING_DIR_DEF`. Move them into production once you've
tested them:

```bash
module use ./incomplete
module load bowtie2/2.5.4     # smoke-test
bowtie2 --version

# Promote to production
cp -r ./incomplete/bowtie2 "$MOD_EXISTING_DIR_DEF/"
```

`<OUTDIR>` defaults to `.` (wherever you ran `container-mod` from) and
can be overridden with `-d DIR`.

## Next

- **[Profile variables](variables.md)** — full reference.
- **[Runtime detection](../advanced/runtime-detection.md)** — when to set
  `RUNTIME_MODULE`.
- **[Permission model](../advanced/permissions.md)** — what modes the
  generated files end up with.

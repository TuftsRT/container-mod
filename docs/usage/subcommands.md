# Subcommands

`container-mod` has four subcommands that can be composed in any order.

```
container-mod <subcommand> [options] <URI-or-image> [...]
```

Subcommands:

- [`pull`](#pull) — download the image.
- [`module`](#module) — generate the modulefile.
- [`exec`](#exec) — generate the wrapper scripts.
- [`pipe`](#pipe) — run all three in order.

You can pass multiple URIs; the subcommand is applied to each in turn.

## pull

Downloads a Singularity / Apptainer image to the configured image
directory. Does **nothing else** — no wrappers, no modulefile.

```bash
container-mod pull docker://staphb/blast:2.17.0
```

Behavior:

- If the URI points at a local `.sif` file, the file is left in place;
  no copy or move happens.
- If the URI is a remote reference, the runtime is invoked as
  `singularity pull --force ...` (or the apptainer equivalent), and the
  resulting image is `chmod 644`.
- `pull` does **not** prompt for missing metadata. If the app is
  unknown, the pull still succeeds; you can register the metadata later
  when you actually generate the modulefile.
- `pull -u` prepends a new `version("<v>", uri="<uri>")` line to the app
  metadata file. If the file doesn't exist, `pull -u` will create it —
  which does prompt.

### Why `pull` doesn't build wrappers or a modulefile

Keeping the three steps separate lets admins pull images in batch on a
build node and run the module/wrapper generation later once metadata is
ready. If you just want everything in one shot, use `pipe`.

## module

Generates the modulefile only. Assumes the image is already on disk
somewhere — it needs the image name and app metadata but doesn't touch
the container itself.

```bash
container-mod module docker://staphb/blast:2.17.0
```

Behavior:

- If a *previous* modulefile for the same app exists in
  `MOD_EXISTING_DIR`, its version / image / URI strings are substituted
  and everything else is preserved (Lmod only — Tcl always renders from
  the template). See [Personal vs shared mode](../concepts/modes.md#reusing-an-existing-modulefile).
- The new modulefile is written atomically (via `mktemp` + `mv`) and
  chmod'd to `644`.
- Emits `depends_on("<runtime>")` only when a matching runtime module
  exists on the build host. Overridable with `RUNTIME_MODULE` in the
  profile.
- Personal mode writes to `~/privatemodules/<app>/<version>.lua`.
  Profile-backed mode writes to `<OUTDIR>/incomplete/<app>/<version>.lua`
  for staged review.
- Runs a permission self-check on shared runs (dirs `755`, files `644`).

## exec

Generates wrapper scripts under `<app>/<version>/bin/`. Requires the
image to already exist, because it probes the container for which
programs are actually present before creating wrappers.

```bash
container-mod exec docker://staphb/blast:2.17.0
```

For each program listed in the app's `Programs:` metadata field:

1. Runs `singularity exec <image> sh -c "command -v <program>"` inside
   the container (falls back to `which` for older images).
2. If found, generates a wrapper at
   `<exec_outdir>/<app>/<version>/bin/<program>` at mode `755`.
3. If not found, prints a warning and skips that program.

Each wrapper:

- Ensures the runtime is available in `PATH`, using a `module load`
  fallback only when a matching runtime module actually existed at
  generation time (see [Runtime detection](../advanced/runtime-detection.md)).
- Adds `--nv` for NVIDIA GPUs or `--rocm` for AMD GPUs (never both).
- Invokes the container with the launch mode (`exec` or `run`) and any
  extra `RUNTIME_OPTIONS` from the profile.
- Forwards all positional arguments (`"$@"`) unchanged.

## pipe

`pull`, `module`, and `exec` in that order, for each URI:

```bash
container-mod pipe --profile biocontainers \
  docker://quay.io/biocontainers/vcftools:0.1.16--h9a82719_5
```

This is the most common workflow. If one URI fails, subsequent ones do
not run — see [Failure handling](options.md#failure-handling).

## Jupyter (`-j` / `--jupyter`)

Not strictly a subcommand — it's an option that runs *after* the main
subcommand and registers a `kernel.json` entry pointing at the
container's Python + `ipykernel`. See [Jupyter support](../advanced/jupyter.md).

## Summary — when to reach for which

- **Test a new container quickly:** `pipe -p docker://...`.
- **Register a new version in the metadata during pull:** `pull -u`.
- **Rebuild wrappers after fixing a bug in the wrapper template:** `exec`.
- **Regenerate the modulefile after changing `BIND_PATH`:** `module`.
- **Deploy to production:** `pipe --profile <name>`.

## Next

- **[Options](options.md)** — every command-line flag.
- **[Examples](examples.md)** — real-world workflows.

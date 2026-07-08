# Overview

## What container-mod is for

Running scientific software as an OCI / Singularity container is now the norm
on many HPC clusters — but a raw container image is not a great user
interface. A cluster user typically wants to type:

```bash
module load bowtie2/2.5.4
bowtie2 --help
```

rather than:

```bash
singularity exec --nv /cluster/tufts/biocontainers/images/quay.io_biocontainers_bowtie2:2.5.4--h7071971_4.sif bowtie2 --help
```

`container-mod` is the automation that closes that gap. Given a container
URI (or local `.sif`), it:

1. Pulls the image into a configured location.
2. Generates a modulefile (Lmod or Tcl) that advertises the container and
   prepends its wrapper directory to `PATH`.
3. Writes one wrapper script per program the container exposes; each
   wrapper `apptainer exec`s or `singularity exec`s the underlying image
   and forwards arguments.
4. Optionally registers a Jupyter kernel that runs inside the container.

## Who it is for

Two audiences share the same tool:

- **HPC administrators** publishing a shared software stack. Profiles let
  admins define cluster-wide output locations, bind paths, and runtime
  module names. Generated artifacts land at the right permissions
  (`644` for files, `755` for directories, `755` for wrappers) regardless
  of the admin's shell `umask`.
- **Individual users** building personal container-backed modules under
  their home directory. Personal mode is the default when no `--profile`
  is passed; images, wrappers, metadata, and modulefiles all live under
  `~/container-apps/` and `~/privatemodules/`.

## What it is *not*

- It does not build container images. Point it at containers you already
  produced (via Docker Hub, Quay, BioContainers, NGC, GHCR, or a local
  Singularity build).
- It does not manage the module system itself. It writes modulefiles that
  Lmod or Environment Modules can then load.
- It does not track container security or vulnerability status. That is
  the container publisher's job.

## Design principles

- **Do the right thing for the site.** Runtime detection auto-adapts:
  prefer a Lmod-provided Singularity / Apptainer module when one exists,
  fall back to a system binary otherwise.
- **Never generate a broken modulefile.** `depends_on(...)` is emitted
  only when the target module actually exists; the modulefile is written
  atomically.
- **Get permissions right by construction.** `umask 022` is set at the top
  of the script, every artifact is `chmod`'ed after creation, and a
  per-run permission self-check flags any drift.
- **Stay simple.** Bash script, plain text metadata files under `repos/`,
  shell profile files under `profiles/`. No database, no server, no
  daemon.

## Next

- **[Installation](installation.md)** — get the script and its
  dependencies in place.
- **[Quick start](quickstart.md)** — deploy your first module in a couple
  of commands.
- **[Concepts / What container-mod produces](concepts/outputs.md)** —
  what shows up on disk after a run.

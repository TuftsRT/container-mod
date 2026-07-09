# Quick start

Three common scenarios, from most to least common.

## Personal use — one command

Personal mode is the default when no `--profile` is passed. Everything lands
under your home directory.

```bash
./container-mod pipe -p docker://staphb/bowtie2:2.5.4
module load use.own
module load bowtie2/2.5.4
bowtie2 --help
```

That produces:

| Artifact | Where |
|---|---|
| Image | `~/container-apps/images/staphb_bowtie2:2.5.4.sif` |
| Wrappers | `~/container-apps/tools/bowtie2/2.5.4/bin/{bowtie2,bowtie2-build,bowtie2-inspect}` |
| Modulefile | `~/privatemodules/bowtie2/2.5.4.lua` |
| App metadata | `~/container-apps/repos/bowtie2` (only if the app isn't already known) |

If `bowtie2` is not already in the metadata database, `container-mod` will
prompt you for its `Description`, `Home Page`, and `Programs` list. For
plain `pull` (no `-u`), that prompt is skipped since `pull` doesn't need
the metadata — see [Subcommands](usage/subcommands.md).

## Admin deployment to a shared tree

Use a profile that names the cluster's shared output locations:

```bash
./container-mod pipe --profile biocontainers \
  docker://quay.io/biocontainers/vcftools:0.1.16--h9a82719_5
```

That writes:

| Artifact | Where |
|---|---|
| Image | `/cluster/tufts/biocontainers/images/quay.io_biocontainers_vcftools:0.1.16.sif` |
| Wrappers | `/cluster/tufts/biocontainers/tools/vcftools/0.1.16/bin/*` |
| New modulefile | `./incomplete/vcftools/0.1.16.lua` (staged for review) |
| Metadata | `repos/vcftools` if the app is new |

The new modulefile is staged under `<OUTDIR>/incomplete/` rather than the
production module tree, so an admin can review it and move it into the
shared `MOD_EXISTING_DIR_DEF` location afterward. See
[Profiles](configuration/profiles.md).

## Deploy from a local `.sif`

If you already have the image on disk (built locally, or copied from
elsewhere):

```bash
./container-mod pipe -p /path/to/my/image.sif
```

The script prompts for the application name and version (since a local
file has no URI to parse), then generates the modulefile and wrappers
pointing directly at the image's on-disk path — the image is not
copied or moved. Useful for testing custom builds.

## Common flags at a glance

- `-p` / `--personal` — write to `~/container-apps` and `~/privatemodules`.
- `--profile NAME` — use a named profile from [`profiles/`](configuration/profiles.md).
- `-t` / `--tcl` — generate Tcl modulefiles instead of Lmod.
- `-j` / `--jupyter` — also register a Jupyter kernel.
- `-u` / `--update` — record the pulled image as a new `version(...)` line
  in the app's metadata file.
- `-f` / `--force` — overwrite existing generated artifacts.
- `-l` / `--list` — list available profiles.
- `-v` / `--version` — print the script version.

The full list is in [Options](usage/options.md).

## Next

- **[Concepts / Personal vs shared mode](concepts/modes.md)** — how the
  script decides where to write.
- **[Subcommands](usage/subcommands.md)** — what `pull`, `module`, `exec`,
  and `pipe` each do.
- **[Advanced / Runtime detection](advanced/runtime-detection.md)** — how
  the script picks Singularity vs Apptainer, and how to override it.

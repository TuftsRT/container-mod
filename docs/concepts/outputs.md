# What container-mod produces

For every container URI (or local `.sif`) you feed it, `container-mod`
produces some subset of these four artifacts, depending on which
subcommand you run:

```{list-table}
:header-rows: 1
:widths: 25 15 60

* - Artifact
  - Subcommand
  - Purpose
* - `.sif` image
  - `pull`
  - The Singularity/Apptainer container itself; downloaded (or left in
    place for local files).
* - Modulefile (`.lua` or plain)
  - `module`
  - Advertises the container to Lmod / Environment Modules. Prepends
    the wrapper directory to `PATH`, optionally sets `APPTAINER_BIND`,
    and optionally `depends_on(...)` a runtime module.
* - Wrapper scripts
  - `exec`
  - One executable per program listed in the app's metadata; each
    wrapper `singularity exec` / `apptainer exec`s the image with the
    right options and forwards arguments.
* - Jupyter kernel
  - `-j`/`--jupyter`
  - A `kernel.json` entry pointing at the container's Python +
    ipykernel, so JupyterLab / Notebook can launch it.
```

The `pipe` subcommand runs `pull`, `module`, and `exec` in that order.

## Sample layout after `pipe -p docker://staphb/bowtie2:2.5.4`

```
$HOME/
├── container-apps/
│   ├── images/
│   │   └── staphb_bowtie2:2.5.4.sif
│   ├── repos/                       ← app metadata (see below)
│   │   └── bowtie2
│   └── tools/
│       └── bowtie2/
│           └── 2.5.4/
│               └── bin/
│                   ├── bowtie2
│                   ├── bowtie2-build
│                   └── bowtie2-inspect
└── privatemodules/
    └── bowtie2/
        └── 2.5.4.lua
```

## The wrapper script

Each wrapper is a small Bash script that:

1. Ensures the container runtime is available (either already in `PATH`,
   or via a `module load` fallback — the exact form depends on your
   cluster's setup, see [Runtime detection](../advanced/runtime-detection.md)).
2. Adds `--nv` if an NVIDIA GPU is detected, or `--rocm` if AMD (never
   both).
3. `exec`'s the container with the program name and forwards all
   positional arguments (`"$@"`).

The wrapper is regenerated on each `exec` / `pipe` run, so bug fixes to
the wrapper template propagate to old apps on redeployment.

## The modulefile

A generated Lmod modulefile roughly looks like this (some boilerplate
elided):

```lua
help([==[
Description
===========
Bowtie 2 is an ultrafast and memory-efficient tool …
]==])

whatis("Name: bowtie2")
whatis("Version: 2.5.4")
whatis("BioContainers: https://biocontainers.pro/tools/bowtie2")

local image = "staphb_bowtie2:2.5.4.sif"
local uri = "docker://staphb/bowtie2:2.5.4"
local version = "2.5.4"

conflict(myModuleName())

local modroot = "/home/yucheng/container-apps/tools/bowtie2/" .. "2.5.4"
prepend_path("PATH", modroot .. "/bin", ":")

-- Only emitted when BIND_PATH is set in the profile
-- prepend_path{"APPTAINER_BIND","/cluster/tufts",delim=","}

-- Only emitted when a matching runtime module is available
depends_on("singularity")
```

Tcl modulefiles carry the same information in Tcl syntax.

## App metadata

Each application has a text file under `repos/` (or `~/container-apps/repos/`
in personal mode) with three headers and zero or more version records:

```text
Description: Bowtie 2 is an ultrafast and memory-efficient tool for
aligning sequencing reads to long reference sequences.
Home Page: https://github.com/BenLangmead/bowtie2
Programs: bowtie2,bowtie2-build,bowtie2-inspect

version("2.5.4", uri="docker://quay.io/biocontainers/bowtie2:2.5.4--h7071971_4")
version("2.5.1", uri="docker://quay.io/biocontainers/bowtie2:2.5.1--py310h8d7afc0_0")
```

The `Programs:` list drives wrapper generation — one wrapper per name,
skipped with a warning if the program is not actually found inside the
container. The `version()` lines are optional history and can be
appended automatically with `--update`.

See [Application metadata](metadata.md) for details.

## Next

- **[Personal vs shared mode](modes.md)** — how the script decides where
  to write.
- **[Application metadata](metadata.md)** — the `repos/` format in depth.
- **[Runtime detection](../advanced/runtime-detection.md)** — how
  `singularity` vs `apptainer` is chosen.

# container-mod

**Turn container images into HPC-friendly environment modules.**

`container-mod` pulls a Singularity / Apptainer image, generates an
Lmod or Tcl modulefile for it, creates wrapper scripts for every
program the container exposes, and — optionally — registers a Jupyter
kernel. One command; a working `module load` at the end.

```{code-block} bash
:caption: Deploy a container in one command

./container-mod pipe --profile biocontainers \
  docker://quay.io/biocontainers/bowtie2:2.5.4--h7071971_4
```

```{code-block} bash
:caption: Users then just module load

module load bowtie2/2.5.4
bowtie2 --help
```

```{mermaid}
:caption: How container-mod fits between the container publisher and the end user

flowchart LR
    Reg[Container<br>registry] -->|URI| CM[container-mod]
    CM -->|.sif| Img[shared<br>images dir]
    CM -->|wrappers| Bin[app/version/bin]
    CM -->|modulefile| Mods[module tree]
    Mods --> User[User: module load app<br>program arg1 arg2]
    Bin --> User
    Img --> User
    style CM fill:#3b5bdb,stroke:#3b5bdb,color:#ffffff
    style User fill:#dcfce7
```

## Start here

::::{grid} 1 2 2 3
:gutter: 3

:::{grid-item-card} {octicon}`book` Overview
:link: overview
:link-type: doc

What container-mod is for, who it's for, and what it deliberately
avoids doing.
:::

:::{grid-item-card} {octicon}`play` Tutorial
:link: tutorial
:link-type: doc

Five-minute hands-on walkthrough: install → pipe → module load.
:::

:::{grid-item-card} {octicon}`rocket` Quick start
:link: quickstart
:link-type: doc

The three common invocations at a glance.
:::

:::{grid-item-card} {octicon}`terminal` Subcommands
:link: usage/subcommands
:link-type: doc

`pull`, `module`, `exec`, `pipe` — deep-dives.
:::

:::{grid-item-card} {octicon}`gear` Configuration
:link: configuration/profiles
:link-type: doc

Profiles, `BIND_PATH`, `RUNTIME_MODULE`, `RUNTIME_OPTIONS`.
:::

:::{grid-item-card} {octicon}`workflow` Deployment lifecycle
:link: concepts/lifecycle
:link-type: doc

The five stages of a `container-mod` deployment, and what typically
goes wrong at each.
:::

::::

## Common scenarios

::::{grid} 1 2 2 2
:gutter: 3

:::{grid-item-card} {octicon}`plug` GPU workflows
:link: advanced/gpu
:link-type: doc

`--nv` / `--rocm` auto-detected. Multi-GPU jobs supported via the
scheduler.
:::

:::{grid-item-card} {octicon}`link-external` MPI workflows
:link: advanced/mpi
:link-type: doc

`RUNTIME_LAUNCH="run"` + `RUNTIME_OPTIONS="--mpi --cleanenv"`. LAMMPS,
GROMACS, OpenFOAM, WRF, and friends.
:::

:::{grid-item-card} {octicon}`beaker` Jupyter kernels
:link: advanced/jupyter
:link-type: doc

`-j / --jupyter` registers a kernel pointing at the container's
Python + ipykernel.
:::

:::{grid-item-card} {octicon}`shield-check` Permission model
:link: advanced/permissions
:link-type: doc

`umask 022` enforced. 644 modulefiles, 755 wrappers, 755 dirs — no
matter your login shell.
:::

::::

## Table of contents

```{toctree}
:maxdepth: 2
:caption: Get started

overview
installation
tutorial
quickstart
```

```{toctree}
:maxdepth: 2
:caption: Concepts

concepts/outputs
concepts/modes
concepts/lifecycle
concepts/metadata
```

```{toctree}
:maxdepth: 2
:caption: Configuration

configuration/profiles
configuration/bundled-profiles
configuration/variables
```

```{toctree}
:maxdepth: 2
:caption: Usage

usage/subcommands
usage/options
usage/examples
```

```{toctree}
:maxdepth: 2
:caption: Advanced topics

advanced/runtime-detection
advanced/permissions
advanced/gpu
advanced/mpi
advanced/jupyter
advanced/templates
```

```{toctree}
:maxdepth: 2
:caption: Reference

faq
troubleshooting
contributing
changelog
```

---

## What you get, per container

For every container URI (or local `.sif` image), `container-mod` can
produce:

- A `.sif` image, unless you point it at an existing local file
- A modulefile such as `app/version.lua` (Lmod) or `app/version` (Tcl)
- Wrapper scripts under `app/version/bin/<program>`
- An optional Jupyter kernel entry

The wrappers let users invoke containerized commands as ordinary
shell commands after loading the module. GPUs are auto-detected. MPI
is a two-line profile change. Sites without an Lmod-installed
runtime auto-adapt — no manual `depends_on(...)` fiddling.

## Project links

- **Source:** <https://github.com/TuftsRT/container-mod>
- **Issues / bug reports:** <https://github.com/TuftsRT/container-mod/issues>
- **License:** MIT

## Citation

If `container-mod` supports your research or infrastructure, please
consider citing:

> Zhang, Yucheng. "Simplifying Container-Based Module Generation on
> HPC with container-mod." *Practice and Experience in Advanced
> Research Computing 2025: The Power of Collaboration.* 2025. 1-4.

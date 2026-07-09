# container-mod

**Turn container images into HPC-friendly environment modules.**

`container-mod` pulls a Singularity / Apptainer image, generates an Lmod or
Tcl modulefile for it, creates wrapper scripts for each program the container
exposes, and — optionally — registers a Jupyter kernel. It is designed for
HPC administrators publishing shared software stacks *and* for regular users
building personal container-backed modules in their home directory.

```{code-block} bash
:caption: Deploy a container in one command

./container-mod pipe --profile biocontainers \
  docker://quay.io/biocontainers/bowtie2:2.5.4--h7071971_4
```

```{code-block} bash
:caption: Users then just `module load`

module load bowtie2/2.5.4
bowtie2 --help
```

---

## Get started

```{toctree}
:maxdepth: 1
:caption: Get started
:hidden:

overview
installation
quickstart
```

```{toctree}
:maxdepth: 1
:caption: Concepts
:hidden:

concepts/outputs
concepts/modes
concepts/metadata
```

```{toctree}
:maxdepth: 1
:caption: Configuration
:hidden:

configuration/profiles
configuration/variables
```

```{toctree}
:maxdepth: 1
:caption: Usage
:hidden:

usage/subcommands
usage/options
usage/examples
```

```{toctree}
:maxdepth: 1
:caption: Advanced topics
:hidden:

advanced/runtime-detection
advanced/permissions
advanced/jupyter
advanced/templates
```

```{toctree}
:maxdepth: 1
:caption: Reference
:hidden:

faq
troubleshooting
contributing
changelog
```

::::{grid} 1 2 2 3
:gutter: 3

:::{grid-item-card} {octicon}`rocket` Quick start
:link: quickstart
:link-type: doc

Pull a container and load a working module in under a minute.
:::

:::{grid-item-card} {octicon}`gear` Configuration
:link: configuration/profiles
:link-type: doc

Profiles, `BIND_PATH`, `RUNTIME_MODULE`, and other tuning knobs.
:::

:::{grid-item-card} {octicon}`terminal` Subcommands
:link: usage/subcommands
:link-type: doc

`pull`, `module`, `exec`, `pipe`, and when to reach for each.
:::

:::{grid-item-card} {octicon}`server` Permission model
:link: advanced/permissions
:link-type: doc

How `container-mod` produces the right modes for shared deployments,
regardless of `umask`.
:::

:::{grid-item-card} {octicon}`plug` Jupyter kernels
:link: advanced/jupyter
:link-type: doc

Register a container as a Jupyter kernel with `-j / --jupyter`.
:::

:::{grid-item-card} {octicon}`code` Templates
:link: advanced/templates
:link-type: doc

Customize the generated modulefile with your own Lua or Tcl template.
:::

::::

---

## What you get, per container

For every container URI (or local `.sif` image), `container-mod` can produce:

- A `.sif` image, unless you point it at an existing local file
- A modulefile such as `app/version.lua` (Lmod) or `app/version` (Tcl)
- Wrapper scripts under `app/version/bin/<program>`
- An optional Jupyter kernel entry

The wrappers let users invoke containerized commands as ordinary shell
commands after loading the module.

## Project links

- **Source:** <https://github.com/TuftsRT/container-mod>
- **Issues / bug reports:** <https://github.com/TuftsRT/container-mod/issues>
- **License:** MIT

## Citation

If `container-mod` supports your research or infrastructure, please consider
citing:

> Zhang, Yucheng. "Simplifying Container-Based Module Generation on HPC with
> container-mod." *Practice and Experience in Advanced Research Computing
> 2025: The Power of Collaboration.* 2025. 1-4.

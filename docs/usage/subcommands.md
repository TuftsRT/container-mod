# Subcommands

`container-mod` has four subcommands. Each takes one or more container
URIs (or local `.sif` paths) and produces a specific artifact.

```{mermaid}
:caption: Lifecycle of an app deployed with container-mod

flowchart LR
    U[Container URI] --> P[pull]
    P -->|image| M[module]
    P -->|image| E[exec]
    M -->|modulefile| L[User<br>module load]
    E -->|wrappers| L
    L --> R[User runs<br>program]
    style P fill:#dbeafe,stroke:#3b82f6
    style M fill:#dcfce7,stroke:#22c55e
    style E fill:#fef3c7,stroke:#eab308
    style L fill:#f3e8ff,stroke:#a855f7
```

::::{grid} 1 2 2 2
:gutter: 3

:::{grid-item-card} {octicon}`download` pull
:link: subcommands/pull
:link-type: doc

Downloads the container image. No wrappers, no modulefile.
:::

:::{grid-item-card} {octicon}`file-code` module
:link: subcommands/module
:link-type: doc

Generates the Lmod (or Tcl) modulefile.
:::

:::{grid-item-card} {octicon}`terminal` exec
:link: subcommands/exec
:link-type: doc

Generates wrapper scripts for each program in the container.
:::

:::{grid-item-card} {octicon}`workflow` pipe
:link: subcommands/pipe
:link-type: doc

Runs `pull` → `module` → `exec` in one shot.
:::

::::

```{toctree}
:hidden:

subcommands/pull
subcommands/module
subcommands/exec
subcommands/pipe
```

## Quick reference

::::{list-table}
:header-rows: 1
:widths: 15 20 25 40

* - Subcommand
  - What it produces
  - Requires
  - Also see
* - `pull`
  - `.sif` image
  - Container runtime; internet
  - [pull](subcommands/pull.md)
* - `module`
  - Modulefile at `<app>/<version>.lua` (or plain, for Tcl)
  - App metadata; template
  - [module](subcommands/module.md)
* - `exec`
  - One wrapper per program in `<app>/<version>/bin/`
  - Image on disk; app metadata
  - [exec](subcommands/exec.md)
* - `pipe`
  - All three above
  - All the above
  - [pipe](subcommands/pipe.md)
::::

## When to use each

- **Test a new container quickly** — [`pipe -p docker://...`](subcommands/pipe.md).
- **Register a version during a batch pull** —
  [`pull -u`](subcommands/pull.md).
- **Rebuild wrappers after a container-mod upgrade** —
  [`exec -f`](subcommands/exec.md).
- **Regenerate a modulefile after editing your profile's `BIND_PATH`**
  — [`module`](subcommands/module.md).
- **Deploy to production** — [`pipe --profile <name>`](subcommands/pipe.md).
- **Register a Jupyter kernel** — add [`-j`](../advanced/jupyter.md) to
  any of the above.

## Global flags

Every subcommand accepts the same option set. See [Options](options.md)
for the full reference.

## Failure semantics

Within a single subcommand invocation, if one URI fails the remaining
URIs are skipped. For independent processing (e.g. deploying 50
containers where you want failures logged but the batch to continue),
loop from a shell script and check the exit status:

```bash
for uri in "${uris[@]}"; do
    if ! container-mod pipe --profile biocontainers "$uri"; then
        echo "  ! failed: $uri" >&2
    fi
done
```

## See also

- **[Options](options.md)** — every flag `container-mod` accepts.
- **[Examples](examples.md)** — end-to-end workflows.

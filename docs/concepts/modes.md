# Personal vs shared mode

`container-mod` runs in one of two modes at any given invocation. The mode
is decided by the flags you pass:

- **Personal mode** (`-p` / `--personal`, or no `--profile`): everything
  lands under your home directory.
- **Profile-backed / shared mode** (`--profile NAME`): everything lands
  in cluster-shared directories declared by the named profile.

If you do not pass `--profile`, personal mode is auto-selected.

## Personal mode

Intended for individual users building modules for their own account.

| Artifact | Path |
|---|---|
| Images | `~/container-apps/images/` |
| Wrappers | `~/container-apps/tools/<app>/<version>/bin/` |
| Metadata | `~/container-apps/repos/<app>` |
| Modulefiles | `~/privatemodules/<app>/<version>.lua` |
| Jupyter kernels | `~/.local/share/jupyter/kernels/<app>-<version>/` |

To make personal modules discoverable to Lmod, run:

```bash
module load use.own
module load bowtie2/2.5.4
```

The first time you use personal mode, `container-mod` copies the bundled
`repos/` metadata into `~/container-apps/repos/` so your local edits and
`--update`-recorded versions stay separate from the shared catalog.

## Profile-backed mode

Intended for HPC admins publishing a shared software stack.

A profile is a plain shell file under either `profiles/` (bundled with the
repository) or `~/container-apps/profiles/` (a user override). It exports
site-specific variables:

```bash
# profiles/biocontainers
MOD_EXISTING_DIR_DEF="/cluster/tufts/biocontainers/modules"
PUBLIC_IMAGEDIR="/cluster/tufts/biocontainers/images"
PUBLIC_EXECUTABLE_DIR="/cluster/tufts/biocontainers/tools"
BIND_PATH="/cluster/tufts"
```

Given `--profile biocontainers`, the same subcommand writes:

| Artifact | Path |
|---|---|
| Images | `${PUBLIC_IMAGEDIR}/` |
| Wrappers | `${PUBLIC_EXECUTABLE_DIR}/<app>/<version>/bin/` |
| Metadata | `repos/<app>` in the repo directory |
| New modulefiles | `<OUTDIR>/incomplete/<app>/<version>.lua` (staged) |
| Jupyter kernels | `<OUTDIR>/kernels/<app>-<version>/` |

`<OUTDIR>` is `.` by default; override with `-d` / `--dir`.

The `incomplete/` staging directory is the shared-mode escape hatch:
a fresh modulefile lands there rather than directly in
`MOD_EXISTING_DIR_DEF`, so an admin can review it before promoting.

## Why staging?

In practice, admins want to:

1. Pull the new version and generate the modulefile.
2. Test it (`module use ./incomplete && module load app/version`).
3. Only then move it into the production tree the whole cluster reads.

`container-mod` supports this by keeping new modulefiles under
`<OUTDIR>/incomplete/` and looking at the existing tree
(`MOD_EXISTING_DIR_DEF`, overridable with `-m`) only to find *older*
versions worth repurposing. See [Module Generation Behavior](../usage/subcommands.md#module).

## Reusing an existing modulefile

When generating an Lmod modulefile, `container-mod` first searches
`MOD_EXISTING_DIR` for the newest existing modulefile of the same app. If
one is found, it is *repurposed* — the version / image / URI strings are
substituted and everything else is preserved, so a site's custom edits
(extra environment variables, admin-added help text, unusual `depends_on`)
survive a version bump.

Tcl mode always renders a fresh modulefile from the template.

## Rule-of-thumb for choosing a mode

- Testing a new container on your own account → **personal mode**.
- Building a module for one HPC user → personal mode plus a hint to the
  user to `module load use.own`.
- Building a module the whole cluster should see → **profile-backed
  mode**, with the profile declaring the shared output locations.

## Next

- **[Profiles](../configuration/profiles.md)** — full profile reference.
- **[Application metadata](metadata.md)** — the `repos/` format.

# Runtime detection

`container-mod` needs to know two things about your cluster's container
runtime:

1. **Which binary to invoke** in the generated wrapper (`singularity` or
   `apptainer`).
2. **Which module to depend on** (or none), so the generated modulefile
   correctly ensures the runtime is available when a user does
   `module load <app>`.

These are computed independently — a site can have a system-provided
`apptainer` binary with no matching Lmod entry, or an Lmod-provided
`singularity` module and no system binary. `container-mod` handles all
four combinations.

## The auto-detection order

At startup, `detect_container_runtime` walks this list, taking the first
option that works:

1. `module load singularity` (via Lmod / Environment Modules), if a
   module by that name is available.
2. `module load apptainer`, if a module by that name is available.
3. `singularity` in `PATH` (system binary).
4. `apptainer` in `PATH` (system binary).
5. Error — no runtime found.

**Modules are preferred over system binaries.** Sites like Tufts ship
Apptainer both as a package (in `/usr/bin`) and as an Lmod module; the
module is the admin-curated version that the rest of the cluster uses,
so `container-mod` picks it.

Whichever wins sets two variables:

- `CONTAINER_RUNTIME` — the binary name embedded in each wrapper.
- `CONTAINER_MODULE_NAME` — the candidate module name for
  `depends_on(...)`.

## The `RUNTIME_MODULE` decision

Separately, after profile loading, `container-mod` decides what to put
in the generated modulefile's `depends_on(...)` line and the wrapper's
`module load` fallback:

```
if the profile / environment set RUNTIME_MODULE (including to ""):
    use that verbatim
else if a Lmod module named "$CONTAINER_MODULE_NAME" is loadable:
    RUNTIME_MODULE="$CONTAINER_MODULE_NAME"
else:
    RUNTIME_MODULE=""
```

The result drives:

- **Modulefile:** emits `depends_on("<RUNTIME_MODULE>")` only when
  `RUNTIME_MODULE` is non-empty.
- **Wrapper:** emits a `module load "<RUNTIME_MODULE>"` fallback (only
  invoked when the binary is missing from `PATH`) when
  `RUNTIME_MODULE` is non-empty; otherwise prints a clear error if the
  binary can't be found.

## Four scenarios, side by side

```{list-table}
:header-rows: 1
:widths: 32 22 22 24

* - Cluster setup
  - `CONTAINER_RUNTIME`
  - `RUNTIME_MODULE`
  - Notes
* - Tufts: `singularity` module *and* system `apptainer`
  - `singularity`
  - `singularity`
  - Module preferred. `depends_on("singularity")` emitted.
* - Only `apptainer` module
  - `apptainer`
  - `apptainer`
  - Module loaded at build time; `depends_on("apptainer")` emitted.
* - Only system `apptainer` binary (no module)
  - `apptainer`
  - `""`
  - No `depends_on` line; wrapper skips `module load`.
* - System binary + explicit override `RUNTIME_MODULE=""`
  - `apptainer`
  - `""` (respected)
  - Force-disables the dependency even if a module technically exists.
```

## Restoring the `module` function in a subshell

Lmod defines `module` as a *shell function*, not a real command. Shell
functions are not inherited by subprocesses, so a fresh `bash` (the one
running `container-mod`) may not see it. `container-mod`'s
`ensure_module_function` helper handles this transparently:

1. If `module` is already a function in scope, use it.
2. Otherwise, source the standard Lmod / Environment Modules init
   scripts (`${LMOD_PKG:-}/init/bash`, `/etc/profile.d/lmod.sh`,
   `/etc/profile.d/z00_lmod.sh`, `/etc/profile.d/00-modulepath.sh`,
   `/etc/profile.d/modules.sh`).
3. If none of those work, synthesize a `module` function from
   `LMOD_CMD` directly — `LMOD_CMD` is exported by Lmod's init and *is*
   inherited by subprocesses.

This is why an interactive shell that has `module` working correctly
translates cleanly to a `./container-mod ...` subprocess that also has
`module` working.

## Manual override examples

Pin a specific runtime module:

```bash
# profiles/my-site
RUNTIME_MODULE="apptainer/1.3.0"
```

Every generated wrapper's fallback becomes `module load "apptainer/1.3.0"`
and the modulefile depends on `apptainer/1.3.0` exactly.

Skip the dependency entirely (e.g., on a shared cluster where the
runtime is in `PATH` cluster-wide but there's no matching module):

```bash
RUNTIME_MODULE=""
```

## Why the "shadowing" bug was subtle

Prior to `container-mod` 1.2, the script's own subcommand handler was
named `module()`. That function shadowed Lmod's `module` even when the
Lmod function *was* correctly loaded, because bash resolves function
names before commands. Consequence: on Tufts, `module avail
singularity` inside the script called the container-mod handler
(expecting a URI), returned garbage, and the wrappers ended up without
their `module load` fallback.

The fix was to rename the subcommand handlers to `cmd_pull`,
`cmd_module`, `cmd_exec`. If you see the old names in a fork or an
older release, upgrading closes this bug.

## Next

- **[Profile variables](../configuration/variables.md#runtime_module)** —
  full `RUNTIME_MODULE` reference.
- **[Permission model](permissions.md)** — modes on generated
  artifacts.

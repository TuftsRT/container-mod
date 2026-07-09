# Profile variables

Every knob that a profile file can set, alphabetically. All are optional
except where noted.

## `BIND_PATH`

Optional site-wide path injected into `APPTAINER_BIND` from every
generated modulefile.

```bash
BIND_PATH="/cluster/tufts"
```

When set, the Lmod modulefile picks it up as:

```lua
prepend_path{"APPTAINER_BIND", "/cluster/tufts", delim=","}
```

Tcl modulefiles get an equivalent `prepend-path`. Leave `BIND_PATH`
unset for portable modules with no site coupling.

## `MOD_EXISTING_DIR_DEF`

The **existing shared module tree** used to find prior versions of an
app when generating a new modulefile. Repurposing an old modulefile
preserves any hand-edited customizations. This is *not* the destination
for newly-generated modulefiles; those go to `<OUTDIR>/incomplete/`.

```bash
MOD_EXISTING_DIR_DEF="/cluster/tufts/biocontainers/modules"
```

Override at runtime with `-m` / `--module-dir DIR`.

## `PUBLIC_EXECUTABLE_DIR`

The wrapper-tree root in shared mode. Wrappers land at:

```
${PUBLIC_EXECUTABLE_DIR}/<app>/<version>/bin/<program>
```

Generated modulefiles embed this path in their `prepend_path("PATH", …)`
line, so keep it stable across releases.

```bash
PUBLIC_EXECUTABLE_DIR="/cluster/tufts/biocontainers/tools"
```

## `PUBLIC_IMAGEDIR`

Where pulled `.sif` images land in shared mode.

```bash
PUBLIC_IMAGEDIR="/cluster/tufts/biocontainers/images"
```

## `RUNTIME_MODULE`

Override the auto-detected Lmod / Environment Modules name of the
container runtime.

By default, `container-mod` runs `module avail apptainer` (or
`singularity`) at build time and only emits `depends_on("apptainer")` in
generated modulefiles and a `module load "apptainer"` fallback in
wrappers when a matching module actually exists.

You can override that with `RUNTIME_MODULE`:

- Pin a specific module version:

  ```bash
  RUNTIME_MODULE="apptainer/1.3.0"
  ```

- Force-disable the dependency on sites where the runtime is a system
  binary with no Lmod entry:

  ```bash
  RUNTIME_MODULE=""
  ```

Leave the variable unset entirely to fall back to auto-detection.

See [Runtime detection](../advanced/runtime-detection.md) for the full
resolution logic.

## `RUNTIME_LAUNCH`

Controls how the generated wrapper invokes the container.

```bash
RUNTIME_LAUNCH="exec"   # default; most common
RUNTIME_LAUNCH="run"    # for containers with a defined runscript
```

Under the hood, the wrapper runs:

```bash
"$RUNTIME" "$RUNTIME_LAUNCH" "${RUNTIME_OPTIONS[@]}" "${OPTIONS[@]}" \
    "$IMAGE_DIR/$IMAGE" "$PROGRAM" "$@"
```

Values other than `exec` or `run` are rejected.

## `RUNTIME_OPTIONS`

Extra flags to pass to the container runtime in every generated wrapper.
Whitespace-separated tokens; no shell quoting or escapes.

```bash
RUNTIME_OPTIONS="--mpi --cleanenv"
```

Typical uses:

- `--mpi` for MPI-enabled containers (see the container runtime docs for
  version specifics).
- `--cleanenv` to isolate the container from the host environment.
- `--bind=/scratch` for site-specific mounts (though `BIND_PATH` is the
  cleaner mechanism for a global bind path).

Restrictions:

- Must be a single line — newlines are rejected.
- No shell quotes, backticks, `$`, or backslashes. Use simple space-
  separated flags like `--foo --bar=baz`.

Options are baked into each wrapper as a Bash array, so they preserve
argument boundaries correctly at run time.

## Precedence and defaults

```{list-table}
:header-rows: 1
:widths: 25 30 45

* - Variable
  - Default
  - Override paths (highest first)
* - `BIND_PATH`
  - unset (no bind line emitted)
  - Profile file
* - `MOD_EXISTING_DIR`
  - `MOD_EXISTING_DIR_DEF`
  - `-m` / `--module-dir` → profile
* - `MOD_EXISTING_DIR_DEF`
  - unset
  - Profile file
* - `PUBLIC_EXECUTABLE_DIR`
  - unset
  - Profile file
* - `PUBLIC_IMAGEDIR`
  - unset
  - Profile file
* - `RUNTIME_MODULE`
  - auto-detected (see [Runtime detection](../advanced/runtime-detection.md))
  - Profile file / environment
* - `RUNTIME_LAUNCH`
  - `exec`
  - Profile file / environment
* - `RUNTIME_OPTIONS`
  - unset (no extra flags)
  - Profile file / environment
```

`RUNTIME_MODULE`, `RUNTIME_LAUNCH`, and `RUNTIME_OPTIONS` may also be set
in the environment directly (e.g. `RUNTIME_OPTIONS="--mpi" container-mod
pipe …`) — the script honors any pre-set value.

## Next

- **[Profiles](profiles.md)** — how profiles are loaded.
- **[Runtime detection](../advanced/runtime-detection.md)** — automatic
  behavior around `RUNTIME_MODULE`.

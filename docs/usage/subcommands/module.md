# `module`

Generates the Lmod / Tcl modulefile for an app. Does not touch the
image itself — it embeds the image name and the wrapper path into
the modulefile.

## Synopsis

```
container-mod module [options] <URI-or-image> [...]
```

## Behavior

For each URI:

1. Resolves the app name and version from the URI (or prompts you for
   local `.sif` files).
2. Reads `Description`, `Home Page`, and `Programs` from the app's
   metadata file. Prompts to create the file if missing.
3. Searches for an existing modulefile of the same app under
   `MOD_EXISTING_DIR` (Lmod only). If found, **repurposes** it —
   substitutes the version / image / URI strings but preserves
   everything else. If not found, renders a fresh modulefile from the
   template.
4. Renders the runtime dependency (`depends_on(...)`) and bind path
   blocks conditionally based on cluster capabilities.
5. Writes the file atomically via `mktemp` + `mv` and `chmod 644`.
6. In shared mode, runs a permission self-check.

## Output locations

::::{list-table}
:header-rows: 1
:widths: 25 55 20

* - Mode
  - Path
  - Chosen by
* - Personal
  - `~/privatemodules/<app>/<version>.lua`
  - `-p`, or no `--profile`
* - Profile-backed (staged)
  - `<OUTDIR>/incomplete/<app>/<version>.lua`
  - `--profile <name>` (default `<OUTDIR>=.`)
* - Tcl output
  - `<app>/<version>` (no `.lua` extension)
  - `-t` or `-s tcl`
::::

Shared-mode output goes into `incomplete/` **deliberately** — the
admin should test the fresh modulefile there, then move it into
`MOD_EXISTING_DIR_DEF` for production use.

## Repurposing existing modulefiles (Lmod only)

If a prior version of the same app exists under `MOD_EXISTING_DIR`,
that file is used as a template. Only these strings are substituted:

- `whatis("Version: <old>")` → new version
- `local version = "<old>"` → new version
- `local image = "<old>.sif"` → new image
- `local uri = "<old-uri>"` → new URI
- `local modroot = ... .. "<old>"` → new version segment

**Everything else is preserved**, including:

- Custom `setenv` / `prepend_path` / `pushenv` calls admins have
  added.
- Extra `depends_on` for site-specific runtime modules.
- Hand-tweaked `help` text.
- Container-specific `add_property` tags.

This is the mechanism that lets a modulefile evolve organically: a
one-time edit for a new tool travels forward with every version
bump.

Tcl output always renders fresh from the template — no
repurposing.

## The three optional blocks

The bundled Lua template contains three placeholders that render
conditionally:

::::{list-table}
:header-rows: 1
:widths: 25 30 45

* - Placeholder
  - Emitted when
  - Effect
* - `${RUNTIME_DEPENDS_LUA}`
  - a matching runtime module is loadable (or `RUNTIME_MODULE` is set
    in profile)
  - `depends_on("<runtime>")` line
* - `${BIND_LUA}`
  - `BIND_PATH` is set in the profile
  - `prepend_path{"APPTAINER_BIND", "<path>", delim=","}` line
* - `${RUNTIME_LAUNCH}` / `${RUNTIME_OPTIONS}`
  -
  - Baked into the wrapper, not the modulefile
::::

See [Runtime detection](../../advanced/runtime-detection.md) for how
`RUNTIME_MODULE` is auto-detected.

## The `-t` / `--tcl` flag

Renders a Tcl modulefile instead of Lua. Uses
`templates/module_template.tcl`.

Differences from the Lmod path:

- Tcl output never repurposes existing modulefiles — always renders
  from the template.
- The runtime dependency block uses Environment Modules'
  `depends-on` (Modules 5.0+), falling back to `if { ![is-loaded ...] }
  { module load ... }` for older Modules.

## The `-m` / `--module-dir` flag

Overrides `MOD_EXISTING_DIR` for the current run, changing where
`container-mod` searches for existing modulefiles to repurpose. Useful
when you have parallel module trees (e.g. `modules-dev` vs
`modules-prod`) and you want to seed a new tree from an old one.

## The `-f` / `--force` flag

Overwrites an existing generated modulefile. Without `-f`, the script
sees the target file and prints `Modulefile already exists: <path>.
Skipping.`

## Atomic write

The modulefile content is rendered into a sibling `mktemp` file and
then `mv`'d into place. This means:

- If the script is interrupted mid-write, there's no partial
  modulefile in the module tree (Lmod would refuse to load it).
- The mode ends up correct even under strict `umask` (see
  [Permission model](../../advanced/permissions.md)).

## Runtime detection at generation time

`container-mod` reads `LMOD_CMD` (or sources Lmod init scripts) so
`module avail` works inside the script's own subshell. Without this,
older releases could silently emit `depends_on("singularity")` for
non-existent modules. See
[Runtime detection](../../advanced/runtime-detection.md) for the
full story.

## Exit codes

- `0` — modulefile written or skipped (already existed).
- `1` — template render failed, disk write failed, or metadata could
  not be resolved.

## Common workflows

```{code-block} bash
:caption: Personal — generate a Lua modulefile

container-mod module -p docker://staphb/blast:2.17.0
```

```{code-block} bash
:caption: Admin — regenerate after fixing a bug in the wrapper block

container-mod module --profile biocontainers \
    docker://quay.io/biocontainers/bowtie2:2.5.4--h7071971_4
```

```{code-block} bash
:caption: Emit a Tcl modulefile

container-mod module -p -t docker://staphb/blast:2.17.0
```

```{code-block} bash
:caption: Regenerate against a different existing-modules tree

container-mod module --profile biocontainers \
    -m /cluster/tufts/apps/container/biocontainers/modules \
    docker://quay.io/biocontainers/bowtie2:2.5.4--h7071971_4
```

## Promoting a staged modulefile

After you've reviewed the file under `<OUTDIR>/incomplete/`, move it
into the production tree:

```{code-block} bash
cp -r incomplete/bowtie2 "$MOD_EXISTING_DIR_DEF/"
```

Or use `install(1)` if you'd rather preserve modes explicitly:

```bash
install -m 644 incomplete/bowtie2/2.5.4.lua \
    "$MOD_EXISTING_DIR_DEF/bowtie2/2.5.4.lua"
```

## See also

- **[pull](pull.md)** — download the image first.
- **[exec](exec.md)** — generate the wrappers that the modulefile
  puts on `PATH`.
- **[Templates](../../advanced/templates.md)** — customize the
  generated modulefile.
- **[Runtime detection](../../advanced/runtime-detection.md)** — where
  the `depends_on` line comes from.

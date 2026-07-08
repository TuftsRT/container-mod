# Options

```
container-mod <subcommand> [options] <URI-or-image> [...]
```

Options may appear in any order after the subcommand.

```{list-table}
:header-rows: 1
:widths: 22 12 66

* - Flag
  - Value
  - Purpose
* - `-d`, `--dir`
  - `DIR`
  - Base output directory for generated public artifacts. Default: `.`.
    Only relevant in profile-backed mode.
* - `-f`, `--force`
  -
  - Overwrite existing generated files (modulefile, wrapper bin
    directory).  Images are re-pulled with `--force` when this is set.
* - `-m`, `--module-dir`
  - `DIR`
  - Search this directory for existing modulefiles to repurpose.
    Overrides `MOD_EXISTING_DIR_DEF` from the active profile.
* - `-s`, `--module-system`
  - `lmod` | `tcl`
  - Which module system to target. Default `lmod`.
* - `-t`, `--tcl`
  -
  - Shortcut for `--module-system tcl`.
* - `-u`, `--update`
  -
  - After a successful `pull`, prepend a new `version(...)` line to the
    app's metadata file. No effect on subcommands other than `pull` and
    `pipe`. No effect for local `.sif` files (a warning is printed).
* - `-p`, `--personal`
  -
  - Write into personal directories under `~/container-apps` and
    `~/privatemodules`. Auto-selected when no `--profile` is passed.
* - `--profile`
  - `NAME`
  - Load a named profile from `profiles/` or `~/container-apps/profiles/`.
* - `-j`, `--jupyter`
  -
  - After the main workflow completes, register a Jupyter kernel named
    `<app>-<version>`. The container must ship `python` and `ipykernel`.
* - `-l`, `--list`
  -
  - List all available profiles (bundled and personal) and exit.
* - `-v`, `--version`
  -
  - Print the script version and exit.
* - `-h`, `--help`
  -
  - Print the built-in usage message and exit.
```

## Defaults

- No `--profile` → **personal mode** with everything under `$HOME`.
- No `-s` / `-t` → **Lmod** modulefiles.
- No `-d` → `OUTDIR="."`.
- No `-m` → `MOD_EXISTING_DIR` inherits from `MOD_EXISTING_DIR_DEF` in
  the active profile (empty in personal mode).
- No `-j` → no Jupyter kernel is registered.
- No `-u` → app metadata is not modified.
- No `-f` → existing artifacts are preserved and the subcommand prints
  a `Skipping.` message.

## Failure handling

Subcommands are applied to each URI in order. If processing one URI
fails, `container-mod` prints an error and stops — it does not attempt
the remaining URIs. This is intentional for the `pipe` subcommand: a
failed pull short-circuits before we try to generate modulefiles for an
image that isn't there.

## Environment variables

Some behavior can also be set via the shell environment for one-off
runs without editing a profile file:

- `OUTDIR` — same effect as `-d DIR`.
- `RUNTIME_MODULE`, `RUNTIME_LAUNCH`, `RUNTIME_OPTIONS` — same effect
  as setting them inside a profile. See [Profile variables](../configuration/variables.md).

Anything set in a profile file takes precedence over the same variable
in the environment, because profile files are `source`d.

## Next

- **[Subcommands](subcommands.md)** — what each subcommand actually
  does.
- **[Examples](examples.md)** — real workflows.

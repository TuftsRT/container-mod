# Troubleshooting

## `MOD_EXISTING_DIR_DEF: unbound variable`

You are on an old release that ran under `set -uo pipefail` but
referenced profile-only variables without a default. **Upgrade to the
current release** — this was fixed in commit `96b1ea4` (v1.1.0).

## `Lmod has detected the following error: The following module(s) are unknown: "singularity"`

The generated modulefile has a `depends_on("singularity")` line but
your cluster has no `singularity` module. This should not happen in
current releases — the script auto-detects module availability and only
emits `depends_on(...)` when a matching module exists.

If you're seeing it now:

1. **Upgrade** to `container-mod` 1.1+.
2. **Regenerate** the affected modulefiles: `container-mod module
   <uri>`.
3. **Or, quick fix in place**: delete the `depends_on("singularity")`
   line from the generated `.lua` file. Wrappers do not depend on it —
   they probe `PATH` and only fall back to `module load` if the binary
   is missing.

## Generated wrapper missing `module load` even though the runtime is a module

Two possible causes, both fixed in current releases:

- **Old release with `module()` function shadowing Lmod.** Upgrade;
  the subcommand handlers are now named `cmd_pull`, `cmd_module`,
  `cmd_exec`.
- **`module` function not inherited by the subshell.** Fixed by
  `ensure_module_function`, which re-sources Lmod's init or
  synthesizes a `module` function from `LMOD_CMD`.

If you still see the issue on a current release, verify `LMOD_CMD` is
set in your shell:

```bash
echo "$LMOD_CMD"
type module
```

Both should print something. If neither does, Lmod isn't initialized in
your shell — source your login profile first.

## `Failed to find container runtime: singularity`

The wrapper couldn't find `singularity` (or `apptainer`) in `PATH` at
run time, and no `module load` fallback fired.

If your cluster provides the runtime as a system binary (no module),
this means `PATH` was scrubbed. Check whether your job scheduler set
`--export=NONE` or similar; make sure `/usr/bin` (or wherever the
runtime lives) is on `PATH`.

If your cluster provides the runtime as a module, the wrapper's
`module load` block should have caught this. Verify the generated
wrapper contains a `module load "<runtime>"` block and that the module
name is spelled correctly.

## `--nv --rocm` seen in old wrappers

Old bug. Regenerate the wrappers with `container-mod exec <uri>` on a
current release. New wrappers use a Bash array and pick only one of
the two GPU flags.

## Modulefile modes are `600` after `pull -u`

Old bug: `mktemp` (used to atomically replace the metadata file)
creates files at mode `600`, and older releases didn't `chmod 644` after
the `mv`. Fixed. Regenerate the file by rerunning `pull -u`, or
manually:

```bash
chmod 644 /path/to/container-mod/repos/<app>
```

## Users can't `cd` into `.../tools/<app>/<version>/`

Some intermediate directory is mode `700` (only the admin can enter).
This can happen if you deployed with a strict `umask` under an old
release that only chmod'd the leaf.

Fixes:

- Rerun `container-mod exec --profile <name> <uri>` on the current
  release; it walks the parent chain and chmods everything to `755`.
- Or manually: `chmod -R u=rwX,go=rX
  /cluster/.../tools/<app>/<version>/`.

## `container-mod --list` shows nothing

You have no profiles in either `profiles/` (relative to the script) or
`~/container-apps/profiles/`. Add one — see [Profiles](configuration/profiles.md).

## `bash: mapfile: command not found`

You are running the script under Bash 3.2 (macOS default). Upgrade to
Bash 4+:

```bash
brew install bash
/opt/homebrew/bin/bash ./container-mod --version
```

Or bin the personal `container-mod` symlink to point at the new bash's
shebang.

## Next

- **[Runtime detection](advanced/runtime-detection.md)** — deep dive
  into why the wrapper looks the way it does.
- **[Permission model](advanced/permissions.md)** — where each mode
  comes from.

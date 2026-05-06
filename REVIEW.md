# container-mod review

A static review of `container-mod`, its templates, and its profile files.
Items in **Fixed in this branch** were patched by the accompanying edits;
items in **Recommended follow-ups** were left for you to decide on.

## Fixed in this branch

### 1. `set -u` violations would crash the script in personal mode (no profile)
The script begins with `set -uo pipefail`, but several variables that are
only populated by profile files were referenced unconditionally:

- `MOD_EXISTING_DIR_DEF` was read in
  `MOD_EXISTING_DIR="${MOD_EXISTING_DIR:-$MOD_EXISTING_DIR_DEF}"`. With no
  profile loaded, this aborts before any work happens.
- `PUBLIC_IMAGEDIR` was read in
  `if [[ -n "$PUBLIC_IMAGEDIR" ]]`. Same issue.
- `SUBCOMMAND="$1"` aborts when the user runs `container-mod` with no args
  (the help block only runs *after* the assignment).

**Fix:** initialized `MOD_EXISTING_DIR`, `MOD_EXISTING_DIR_DEF`,
`PUBLIC_IMAGEDIR`, `PUBLIC_EXECUTABLE_DIR`, and `BIND_PATH` to `""` near
the other defaults, switched to `${1:-}`, and used `${PUBLIC_IMAGEDIR:-}`
in the only remaining ad-hoc reference.

### 2. Site-specific path baked into the Lua template
`templates/module_template.lua` ended with:

```
prepend_path{"APPTAINER_BIND","/cluster/tufts",delim=","}
```

That line was hard-coded for Tufts. Anyone using `container-mod`
elsewhere would generate modules that bind a non-existent
`/cluster/tufts` directory.

**Fix:** the templates now use `${BIND_LUA}` / `${BIND_TCL}` placeholders.
The renderer emits a bind line only when the profile defines
`BIND_PATH`. The four Tufts profiles
(`biocontainers`, `biocontainers_rocky9`, `ngc`, `ngc_rocky9`,
plus `gis` and `course_jupyter`) now declare `BIND_PATH="/cluster/tufts"`
so generated modules look the same as before.

### 3. `--update` silently ignored for local images
`pull()` returns early for local files, but the `--update` repo-edit
block lives *after* the early return. A user running
`container-mod pull -u /path/to/image.sif` would see no error and no
update.

**Fix:** the local-file branch now emits an explicit warning when
`--update` is set so the user knows the flag had no effect.

### 4. GPU flag conflict in generated wrappers
The wrapper script set `OPTIONS="--nv"` if `nvidia-smi` worked, then
appended `--rocm` if `rocm-smi` also worked, producing
`--nv --rocm`. Apptainer/Singularity treat these as mutually exclusive.

**Fix:** the wrapper now uses an array, prefers `--nv` when both are
present, falls back to `--rocm`, and gates each probe with
`command -v` so we don't call a binary that isn't installed.

### 5. Registry detection only handled biocontainers
`generate_new_modulefile` mapped anything that wasn't a biocontainers
URI to `https://hub.docker.com/r/...`. NGC URIs
(`docker://nvcr.io/...`) ended up with a broken DockerHub link.

**Fix:** added explicit branches for `nvcr.io`, `ghcr.io`, and direct
`quay.io` (non-biocontainers), each pointing at the correct registry
URL. DockerHub remains the fallback.

### 6. `which` check fails inside minimal containers
`confirm_exec_exists` ran `singularity exec ... which $cmd`. Distroless
or scratch-based containers don't ship `which`.

**Fix:** prefer `sh -c "command -v ..."` (POSIX builtin), fall back to
`which`. The command name is passed through `printf %q` to avoid
injection from oddly-named programs.

### 7. `pull` failed via `exit 1` instead of `return 1`
A pull failure for URI #2 of 3 short-circuited the script before the
caller (`handle_subcommand`) could log a useful error.

**Fix:** `pull` now `return 1`s with an explicit warning, and cleans up
the partial `.sif` file.

### 8. Modulefile written non-atomically
`module()` did `echo "$MODULE" > "$OUTFILE"`. If the script was
killed mid-write, an empty or partial modulefile would remain in the
module tree where Lmod could find it.

**Fix:** render to a sibling temp file and `mv` into place.

### 9. `sed -re` is GNU-only
Line that strips biocontainers version suffixes used `sed -re ...`.
macOS BSD sed wants `-Ee`. Both flags are accepted on modern GNU sed,
so `-Ee` is portable.

**Fix:** swapped `-re` to `-Ee`.

### 10. Missing `--version` flag
`VERSION="1.0.0"` was defined but unreachable from the CLI.

**Fix:** added a `-v` / `--version` short-circuit and listed it in the
`--help` output and option list.

### 11. Misc help-message inconsistencies
`--help` referenced the option as `--profile` without the `NAME`
argument and didn't list `-l/--list` or `-v/--version`.

**Fix:** updated the help text to match the implemented options.

## Recommended follow-ups

These are intentionally not patched in this pass because they change
behavior or repo layout, and the right answer depends on how you want
the tool to evolve.

### A. `repos/` only contains `qiime2`; metadata lives under `docs/repos/`
The script reads from `${SCRIPT_TOP_DIR}/repos`, but the repository
ships the actual metadata under `docs/repos/`. Out of the box, every
non-qiime2 lookup falls through to the interactive "create new entry"
prompt.

This looks like a packaging mistake. Two reasonable fixes:

- Move the contents of `docs/repos/` to `repos/` (or symlink), and
  delete the now-empty `docs/` tree.
- Or change `AppInfo_DIR` to point at `docs/repos`.

The first is cleaner because the README already describes `repos/` as
the canonical location.

### B. Bash 4+ is required; README says 3.2 works
`mapfile` (used in `exec()`) and `declare -A`-style features place a
floor at Bash 4. macOS still ships Bash 3.2 as `/bin/bash`. The README
says the script "is compatible with the macOS system Bash". Either
update the README or replace `mapfile` with a `while read` loop.

### C. `find_latest_modulefile` picks newest by mtime, not by version
`touch`ing an old `1.0.lua` would make it look newer than `2.5.lua`.
For repurposing existing modulefiles, sorting by `sort -V` on filename
is more predictable.

### D. Inconsistent error handling
The script mixes `exit 1` and `return 1` in core functions and
sometimes calls `exit 1` from inside `module()` after `set -uo
pipefail` has already started a subshell-prone path. Pulling all
errors through `return` and letting the top-level case statement
decide whether to abort is more consistent. This was partially fixed
in `pull()` and `module()`; `exec()` and `jupyter()` still call
`exit 1` in a few places.

### E. `jupyter` is both a variable and a function name
`jupyter=0` (the `--jupyter` flag) and `jupyter()` (the function that
generates the kernel) coexist. Bash distinguishes them by position, so
it works, but renaming the variable to `make_jupyter` (or the function
to `generate_jupyter_kernel`) removes a foot-gun.

### F. Profile sourcing has no validation
`source "${PROFILEROOT}/$PROFILE"` runs whatever bash is in the file.
That's fine for an admin workflow, but `--profile ../../etc/whatever`
is technically allowed. Consider rejecting profile names that contain
`/`.

### G. Wrapper script does not pass through `SINGULARITY_BIND` /
`APPTAINER_BIND`
The wrapper drops any caller-set bind paths because the runtime
inherits them from environment but the modulefile only sets them for
its own session. This usually works, but it's worth a comment in the
wrapper explaining the contract.

### H. No automated tests
A small `tests/` directory with a handful of smoke tests for URI
parsing (`uri2app`, `uri2ver`, `uri2imgname`), template substitution,
and the registry case statement would catch most of the issues above
on future edits. `bats` is the usual choice for bash; a plain shell
script with assertions is also fine.

### I. CI / pre-commit
A trivial GitHub Actions workflow that runs `bash -n container-mod`
and `shellcheck container-mod` on every push would catch ~80% of the
issues caught in this review.

## Verification of the in-branch fixes

| Check | Result |
|---|---|
| `bash -n container-mod` | passes |
| `container-mod --version` | prints `container-mod 1.0.0` |
| `container-mod --help` | help text reflects new options |
| `container-mod --list` | prints all six profiles |
| `container-mod` (no args) | shows help cleanly (no `set -u` abort) |
| Render `docker://nvcr.io/nvidia/pytorch:25.01-py3` | registry = NVIDIA NGC, URL points at `catalog.ngc.nvidia.com` |
| Render `docker://ghcr.io/foo/bar:1.0` | registry = GitHub Container Registry |
| Render `docker://staphb/bowtie2:2.5.4` | registry = DockerHub |
| Render with `BIND_PATH=""` | bind line is omitted |
| Render with `BIND_PATH=/cluster/example` | bind line emits correct prepend_path |
| Generated wrapper syntax (`bash -n`) | passes |
| Personal-mode module generation without a profile | succeeds end-to-end |

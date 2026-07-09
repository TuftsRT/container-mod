# Permission model

For shared admin deployments (`--profile <name>`), `container-mod`
guarantees that every artifact comes out with the right mode
regardless of the calling shell's `umask` — including strict cluster
defaults like `0007` or `0077`.

## Expected modes after a shared-mode run

```{list-table}
:header-rows: 1
:widths: 45 15

* - Artifact
  - Mode
* - Container image (`*.sif`)
  - `644`
* - Modulefile (`.lua` / `.tcl`)
  - `644`
* - Wrapper scripts
  - `755`
* - App metadata file in `repos/`
  - `644`
* - Every directory in the output tree
  - `755`
```

Users can read+execute everything they need to and can't write to
anything they shouldn't.

## How the guarantee is enforced

Four mechanisms, layered:

### 1. `umask 022` at the top of the script

The script explicitly sets `umask 022` near the top so default-created
files land at `644` and directories at `755`, regardless of the admin's
login shell. Closes the window between file creation and the explicit
`chmod`.

### 2. Explicit `chmod` per artifact

Every artifact is chmod'd immediately after creation:

- Image → `chmod 644 $target_image_path` after pull.
- Modulefile → `chmod 644 $OUTFILE` after atomic `mv`.
- Wrapper → `chmod 755 $executable` after heredoc write.
- Metadata file → `chmod 644 $localappinfo` after write; also chmod'd
  again after `pull -u` replaces the file via `mktemp`+`mv`
  (`mktemp` creates files mode `600`, so this step is necessary to
  restore world-readability).

### 3. `ensure_dir_access` walks the parent chain

`mkdir -p` may create several intermediate directories with the umask
default. `ensure_dir_access` walks upward from the leaf and chmods
each newly-created parent to `755`, stopping at `$HOME` or `/` so it
never touches directories outside what `container-mod` owns.

### 4. `verify_tree_perms` self-check

At the end of every shared-mode `module` and `exec` run, `container-mod`
runs a `verify_tree_perms` sweep over the app's output tree and
prints a per-path warning for anything that isn't the expected mode.
For `pull`, a single-file check confirms the `.sif` lands at `644`.
Personal mode skips these checks (the user owns everything anyway).

## Verifying manually

You can sanity-check any deployment yourself:

```bash
find /cluster/tufts/biocontainers/tools/bowtie2 -exec stat -c "%a %n" {} \;
```

Every directory should be `755` and every file `755` (wrappers are all
executable). For a modulefile tree:

```bash
find /cluster/tufts/biocontainers/modules/bowtie2 -exec stat -c "%a %n" {} \;
```

Directories `755`, `.lua` files `644`.

## Collaborative admin mode (`umask 002`)

If your cluster expects multiple admins to be able to update modules
without `sudo`, switch to a group-writable layout by setting
`umask 002` (files `664`, directories `775`). Change the `umask 022`
line at the top of `container-mod` to `umask 002` and update the
thresholds used by `verify_tree_perms` (`644` → `664`, `755` → `775`).

This is not currently a profile-level knob — it's a two-line edit at
the top of the script if you need it. Open an issue if a formal knob
would help your setup.

## Why umask alone isn't enough

Every explicit `chmod` in the script is redundant when `umask 022` is
in effect. So why bother? Two reasons:

- **Insurance against future umask changes.** If someone patches the
  script and moves an operation before the `umask 022` line, or an
  externally-called tool reset the umask (Singularity's pull can, on
  some versions), the explicit `chmod` still gets the mode right.
- **Interrupted runs.** Ctrl-C between file creation and chmod would
  leave a file at the umask default; the belt-and-suspenders chmod
  runs before the file is user-visible under the final name (since
  atomic writes go through `mktemp`+`mv`).

## Next

- **[Runtime detection](runtime-detection.md)** — how the wrapper
  chooses between binary and module.
- **[Profiles](../configuration/profiles.md)** — where the shared
  output tree is defined.

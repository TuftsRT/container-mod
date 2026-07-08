# Installation

`container-mod` is a single Bash script with no build step. Installation is
just cloning the repository somewhere on the target host.

## Requirements

- **Bash 4 or newer.** The script uses `mapfile`, which is not available in
  macOS's stock Bash 3.2. On macOS use `brew install bash`.
- **A container runtime.** `singularity` or `apptainer` must be either
  directly available in `PATH`, or loadable via `module load`. Runtime
  auto-detection is described in [Runtime detection](advanced/runtime-detection.md).
- **A module system.** Lmod (for `.lua` modulefiles, the default) or
  Environment Modules (for Tcl modulefiles).
- **Standard Unix tools.** `sed`, `awk`, `grep`, `find`, `mktemp`, `realpath`,
  `stat`. The script's `sed` invocations use `-Ee` so both GNU and BSD `sed`
  work.
- **For Jupyter (`-j`/`--jupyter`):** the container must include `python` and
  `ipykernel`. See [Jupyter support](advanced/jupyter.md).

## Get the code

```bash
git clone https://github.com/TuftsRT/container-mod.git
cd container-mod
./container-mod --version
```

That last command should print `container-mod {{ version }}`. If it fails
with `MOD_EXISTING_DIR_DEF: unbound variable`, you are on an old release —
upgrade to the current one.

## Optional: put `container-mod` on your PATH

For personal use:

```bash
mkdir -p ~/.local/bin
ln -s "$(pwd)/container-mod" ~/.local/bin/container-mod
```

For a shared admin install, place the clone under a cluster-wide directory
readable by all users, and add the script's directory to `PATH` in your
site's default profile, or wrap it in a wrapper module:

```lua
-- Example Lmod file exposing container-mod as `module load container-mod`
help([[
Simplifies pulling container images and generating modulefiles
]])
whatis("Name: container-mod")
prepend_path("PATH", "/cluster/tufts/tools/container-mod")
```

## Verify

```bash
./container-mod --help    # help text
./container-mod --version # prints the current version
./container-mod --list    # lists bundled profiles
```

If a shared cluster location for images / modules / wrappers already exists
from a previous release, `container-mod` will *not* overwrite it — see
[Profiles](configuration/profiles.md) for how existing shared trees are
reused.

## Next

- **[Quick start](quickstart.md)** — deploy your first module.
- **[Profiles](configuration/profiles.md)** — configure output locations
  for your cluster.

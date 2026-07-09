# Changelog

The current running version is **{{ version }}** (read directly from the
`VERSION="..."` line of the script).

For the full commit-level history, see the
[commit log on GitHub](https://github.com/TuftsRT/container-mod/commits/main).
This page highlights the changes that affect users.

## v1.2.0

- **MPI-aware wrappers.** Two new profile variables — `RUNTIME_LAUNCH`
  and `RUNTIME_OPTIONS` — control how the wrapper invokes the container.
  Set `RUNTIME_LAUNCH="run"` and `RUNTIME_OPTIONS="--mpi --cleanenv"`
  in your profile for MPI-enabled containers.
- **Apptainer shim detection.** Detect and prefer Apptainer's binding
  behavior when it is provided as a wrapper for Singularity.

## v1.1.0

**Highlights**

- **Robust runtime detection.** Generated modulefiles and wrappers
  auto-adapt to whether the cluster provides Singularity / Apptainer
  as an Lmod module, as a system binary, or both.
- **110+ new HPC application skeletons** under `repos/` covering
  computational chemistry / MD, ML / AI, visualization, and
  climate / CFD / engineering.
- **Hardened permissions for shared admin deployments.**
  `umask 022` set explicitly; every artifact `chmod`'d after creation;
  `verify_tree_perms` self-check at the end of every shared run.

**Bug fixes**

- Fixed `set -u` regression that aborted personal-mode runs with
  `MOD_EXISTING_DIR_DEF: unbound variable`
  ([issue #3](https://github.com/TuftsRT/container-mod/issues/3)).
- Fixed `depends_on("singularity")` baked into modulefiles on clusters
  with no matching Lmod entry, and the missing `module load` block in
  wrappers on clusters that *do* have one
  ([issue #3](https://github.com/TuftsRT/container-mod/issues/3)).
- Wrapper no longer passes `--nv --rocm` together on dual-GPU systems.
- `confirm_exec_exists` now works in distroless containers.
- `pull -u` no longer silently downgrades metadata files to mode `600`.
- NGC / GHCR / Quay.io URIs now get correct registry links instead of
  broken DockerHub URLs.
- Modulefile is written atomically.
- Hardcoded `/cluster/tufts` removed from the Lua template (now
  configurable via the `BIND_PATH` profile variable).

**New features**

- `RUNTIME_MODULE` and `BIND_PATH` profile variables for site-specific
  tuning.
- `-v` / `--version` flag.
- Plain `pull` no longer prompts for app metadata; only commands that
  consume metadata do.

**Documentation**

- New "Permission Model" and "Registry detection" sections in the
  README.
- Bash 4+ requirement documented honestly.

## v1.0.0

- Initial public release.

## Next

- **[FAQ](faq.md)** — common questions.
- **[Contributing](contributing.md)** — how to help.

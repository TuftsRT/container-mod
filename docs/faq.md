# FAQ

## Why is `pull` separate from `module` and `exec`?

Two reasons:

- **Batch pulls on a build node.** Admins routinely pull dozens of images
  overnight and generate the modulefiles and wrappers later once
  metadata is ready. Keeping `pull` cheap and side-effect-free enables
  that workflow.
- **Local `.sif` files.** `pull` is a no-op for a local image (nothing
  to download), so `module` and `exec` are the only meaningful steps.
  Making them separate keeps the command surface small.

Use `pipe` when you want all three at once.

## Do I have to define app metadata before pulling?

No. Plain `container-mod pull docker://...` never touches the metadata
database, so a completely unknown app pulls cleanly. Metadata is only
needed for `module` (Description, Home Page), `exec` (Programs), and
`pull -u` (records the version). If you invoke one of those on an
unknown app, `container-mod` walks you through a short interactive
prompt to create the metadata file.

## Why did my generated modulefile say `depends_on("singularity")` on a cluster with no singularity module?

That was a real bug in earlier releases. Current behavior: the
`depends_on(...)` line is emitted only when a module by that name is
actually loadable on the build host. See
[Runtime detection](advanced/runtime-detection.md).

## Why is my generated wrapper missing the `module load` fallback on Tufts?

Also a real bug in older releases. The script defined its own
subcommand handler named `module()` that shadowed Lmod's `module`
function. Renamed to `cmd_module` in newer releases. See
[Runtime detection](advanced/runtime-detection.md#why-the-shadowing-bug-was-subtle).

## How do I make containers see my `/scratch` filesystem?

Add it to `BIND_PATH` in your profile:

```bash
BIND_PATH="/cluster/tufts,/scratch"
```

Comma-separated list; passed through to `APPTAINER_BIND` in every
generated modulefile.

## How do I use container-mod with MPI?

Set the following in your profile:

```bash
RUNTIME_LAUNCH="run"
RUNTIME_OPTIONS="--mpi --cleanenv"
```

See [Profile variables / RUNTIME_OPTIONS](configuration/variables.md#runtime_options).

## How do I make my personal modules visible to Lmod?

```bash
module load use.own
module load <app>/<version>
```

`use.own` is a stock Lmod module that adds `~/privatemodules` to the
module search path. Add `module load use.own` to your `~/.bashrc` to
have it always available.

## How do I upgrade an existing modulefile without losing my hand-edits?

For Lmod, just run `container-mod module <uri>` for the new version.
The script picks up the newest existing modulefile for the same app in
`MOD_EXISTING_DIR` and *repurposes* it: version / image / URI strings
are updated, everything else stays. Your custom `setenv`, extra
`depends_on`, help-text tweaks, etc. are preserved. See
[Templates / Repurposing](advanced/templates.md#repurposing-existing-modulefiles).

## Does container-mod work on macOS?

The script runs on macOS (Bash 4 required, so `brew install bash`), but
Singularity / Apptainer generally don't run natively on macOS — you'd
need a Linux VM. `container-mod` is intended for Linux HPC hosts.

## Can I add a new app to the shared catalog?

Yes — create a text file `repos/<app>` in the repo checkout following
the format described in [Application metadata](concepts/metadata.md).
Send a pull request.

## Where does the version number come from?

Straight out of the `VERSION="..."` line at the top of the
`container-mod` script. `container-mod --version` prints it. The docs
site also picks it up automatically.

## How do I contribute?

See [Contributing](contributing.md).

## Next

- **[Troubleshooting](troubleshooting.md)** — specific error messages.

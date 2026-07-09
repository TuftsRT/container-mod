# Tutorial: your first container module

A hands-on walkthrough that takes you from a fresh checkout to a
working `module load bowtie2/2.5.4` in five minutes. Assumes personal
mode on a Linux host with `apptainer` or `singularity` on `PATH`.

## 1. Install

```bash
git clone https://github.com/TuftsRT/container-mod.git ~/tools/container-mod
cd ~/tools/container-mod
./container-mod --version
# → container-mod 1.2.0
```

If that last line prints an error rather than the version, double-check:

- Bash version: `bash --version` should show 4.0 or newer.
- Runtime: `command -v singularity` or `command -v apptainer` must
  return a path.

## 2. Pick a container

For this walkthrough we'll use bowtie2, a small alignment tool. Its
BioContainers image is around 200 MB — a reasonable first target.

```
docker://staphb/bowtie2:2.5.4
```

## 3. Deploy in one command

```bash
./container-mod pipe -p docker://staphb/bowtie2:2.5.4
```

What happens:

```{mermaid}
flowchart TB
    A[Start] --> B[Detect runtime]
    B --> C[Initialize app metadata]
    C --> D{Metadata for<br>'bowtie2' exists?}
    D -->|yes| E
    D -->|no| P[Prompt for Description /<br>Home Page / Programs]
    P --> E[pull → ~/container-apps/images/staphb_bowtie2:2.5.4.sif]
    E --> F[module → ~/privatemodules/bowtie2/2.5.4.lua]
    F --> G[exec → ~/container-apps/tools/bowtie2/2.5.4/bin/*]
    G --> H[Done]
    style A fill:#e0e7ff
    style H fill:#dcfce7
```

Because we passed `-p`, the script:

1. Ran in **personal mode**.
2. Downloaded the image to `~/container-apps/images/staphb_bowtie2:2.5.4.sif`.
3. Generated a modulefile at `~/privatemodules/bowtie2/2.5.4.lua`.
4. Wrote three wrappers at
   `~/container-apps/tools/bowtie2/2.5.4/bin/{bowtie2,bowtie2-build,bowtie2-inspect}`.

If bowtie2 was already in the bundled metadata catalog, no prompt
appeared. Otherwise the script asked you for Description, Home Page,
and a comma-separated list of programs; those answers are now saved
under `~/container-apps/repos/bowtie2`.

## 4. Load and use

```bash
module load use.own
module load bowtie2/2.5.4

bowtie2 --version
# → /home/yucheng/container-apps/tools/bowtie2/2.5.4/bin/bowtie2-align-s version 2.5.4
```

The wrapper `bowtie2` is on your `PATH` (courtesy of the modulefile's
`prepend_path`), and running it transparently invokes
`apptainer exec ~/container-apps/images/staphb_bowtie2:2.5.4.sif bowtie2
--version`.

## 5. Look at what got generated

```{code-block} bash
:caption: The wrapper

cat ~/container-apps/tools/bowtie2/2.5.4/bin/bowtie2
```

You'll see the wrapper structure described in
[the exec deep-dive](usage/subcommands/exec.md#anatomy-of-a-generated-wrapper).

```{code-block} bash
:caption: The modulefile

cat ~/privatemodules/bowtie2/2.5.4.lua
```

Notable lines:

- `whatis(...)` — human summary for `module whatis bowtie2`.
- `local image = "staphb_bowtie2:2.5.4.sif"` — which `.sif` the
  wrappers point at.
- `prepend_path("PATH", modroot.."/bin", ":")` — puts the wrapper
  directory on `PATH`.
- `depends_on("singularity")` — emitted only if a `singularity`
  Lmod module exists on your cluster. On systems where singularity is
  just a system binary, this line is absent. See
  [Runtime detection](advanced/runtime-detection.md).

## 6. Cleanup / next steps

To remove everything:

```bash
rm -rf ~/container-apps/images/staphb_bowtie2:2.5.4.sif
rm -rf ~/container-apps/tools/bowtie2/2.5.4
rm ~/privatemodules/bowtie2/2.5.4.lua
```

Or, more targeted:

```bash
rm -rf ~/container-apps/tools/bowtie2   # remove the app entirely
rm -rf ~/privatemodules/bowtie2
```

## Where to go from here

::::{grid} 1 2 2 2
:gutter: 3

:::{grid-item-card} {octicon}`server` Deploy for a whole cluster
:link: concepts/modes
:link-type: doc

Switch from personal mode to `--profile` and put images / wrappers /
modulefiles in a shared tree.
:::

:::{grid-item-card} {octicon}`stack` Register more apps in bulk
:link: usage/examples
:link-type: doc

Loop over a list of URIs, or seed the metadata catalog with
`repos/<app>` files.
:::

:::{grid-item-card} {octicon}`plug` GPU + MPI containers
:link: advanced/gpu
:link-type: doc

Auto-detected `--nv` / `--rocm`, and the `RUNTIME_LAUNCH` /
`RUNTIME_OPTIONS` knobs for MPI.
:::

:::{grid-item-card} {octicon}`code-review` Modulefile customization
:link: advanced/templates
:link-type: doc

Add site-specific `setenv` blocks that survive version bumps.
:::

::::

# Examples

Real workflows adapted from Tufts HPC and the community.

## Personal user, first-time setup

```bash
# One-time
git clone https://github.com/TuftsRT/container-mod.git ~/tools/container-mod
alias container-mod=~/tools/container-mod/container-mod

# Every time you want a new tool
container-mod pipe -p docker://staphb/bowtie2:2.5.4

# Load and use
module use ~/privatemodules
module load bowtie2/2.5.4
bowtie2 --help
```

## Admin, deploy new biocontainers version

```bash
./container-mod pipe --profile biocontainers \
    docker://quay.io/biocontainers/samtools:1.21--h50ea8bc_0

# The new modulefile lands in ./incomplete/samtools/1.21.lua; test it:
module use ./incomplete
module load samtools/1.21
samtools --version

# Promote to production:
mv incomplete/samtools/1.21.lua /cluster/tufts/biocontainers/modules/samtools/
```

## Admin, bulk-pull images to a build node overnight

```bash
# One image per line
cat >/tmp/queue <<EOF
docker://quay.io/biocontainers/vcftools:0.1.16--h9a82719_5
docker://quay.io/biocontainers/fastqc:0.12.1--hdfd78af_0
docker://quay.io/biocontainers/multiqc:1.24.1--pyhdfd78af_0
EOF

# Just pull, no wrappers/modulefiles yet; -u records versions
while IFS= read -r uri; do
    ./container-mod pull --profile biocontainers -u "$uri"
done </tmp/queue
```

Follow up with a batch `module`+`exec` pass once you're ready to publish.

## Register a new version alongside an existing one

```bash
./container-mod pull --profile biocontainers -u \
    docker://quay.io/biocontainers/fastqc:0.12.1--hdfd78af_0
```

Result in `repos/fastqc`:

```text
Description: A quality control tool for high throughput sequence data.
Home Page: https://www.bioinformatics.babraham.ac.uk/projects/fastqc/
Programs: fastqc

version("0.12.1", uri="docker://quay.io/biocontainers/fastqc:0.12.1--hdfd78af_0")
version("0.11.9", uri="docker://quay.io/biocontainers/fastqc:0.11.9--0")
```

## Deploy from a local `.sif`

```bash
./container-mod pipe -p /scratch/my-image.sif

# The script prompts:
# -> Enter the application name: myapp
# -> Enter the application version: 1.0

module use ~/privatemodules
module load myapp/1.0
```

Wrappers point directly at `/scratch/my-image.sif` (no copy), so the
generated module breaks if you move the file. Keep it where the
wrappers expect it.

## Register a Jupyter kernel

```bash
./container-mod pipe -p -j docker://tensorflow/tensorflow:2.18.0-jupyter

# Launch a Jupyter server (any way your site does it), then pick the
# kernel named "tensorflow 2.18.0-jupyter" in the JupyterLab launcher.
```

See [Jupyter support](../advanced/jupyter.md) for troubleshooting the
kernel.

## Generate a Tcl modulefile instead of Lmod

```bash
./container-mod pipe -p -t docker://staphb/bowtie2:2.5.4
module load bowtie2/2.5.4
```

Tcl is renderable straight from the template — no repurposing of
existing modules is attempted.

## MPI-aware wrappers

If your site's Apptainer supports `--mpi` and you want every generated
wrapper to use it, add this to the profile:

```bash
RUNTIME_LAUNCH="run"
RUNTIME_OPTIONS="--mpi --cleanenv"
```

Then any newly-deployed app will invoke `apptainer run --mpi --cleanenv
<image> <program> "$@"`.

## List available profiles

```bash
./container-mod --list
```

Personal overrides in `~/container-apps/profiles/` are marked
`(Personal Profile)`; bundled profiles overridden by a personal file of
the same name are marked `(Overridden)`.

## Next

- **[Runtime detection](../advanced/runtime-detection.md)** — how the
  wrapper's `module load` fallback is chosen.
- **[Permission model](../advanced/permissions.md)** — what modes
  generated files land at.

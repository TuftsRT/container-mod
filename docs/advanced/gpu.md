# GPU support

`container-mod` auto-adds the right GPU flag to every generated
wrapper. You don't have to configure anything in the profile — the
wrapper probes the host at run time and picks the correct option.

## How the auto-detection works

Every generated wrapper contains this block just before it invokes
the container:

```{code-block} bash
:caption: Excerpt from a generated wrapper

# Determine GPU flags for the container runtime.  --nv (NVIDIA) and
# --rocm (AMD) are mutually exclusive; prefer --nv when both runtimes
# are detected.
OPTIONS=()
if command -v nvidia-smi &> /dev/null && nvidia-smi -L &> /dev/null; then
    OPTIONS+=("--nv")
elif command -v rocm-smi &> /dev/null && rocm-smi -L &> /dev/null; then
    OPTIONS+=("--rocm")
fi

"$RUNTIME" "$RUNTIME_LAUNCH" "${RUNTIME_OPTIONS[@]}" "${OPTIONS[@]}" \
    "$IMAGE_DIR/$IMAGE" "$PROGRAM" "$@"
```

The two-step probe (`command -v` first, then the CLI call) means the
wrapper works even on nodes where the GPU drivers were installed but
no GPU is currently visible (e.g. a maintenance mode or a CPU-only
partition of a heterogeneous cluster).

## Flag reference

::::{list-table}
:header-rows: 1
:widths: 20 25 55

* - GPU vendor
  - Wrapper adds
  - Effect
* - NVIDIA
  - `--nv`
  - Mounts the host NVIDIA driver + CUDA libraries into the container.
    Container's `/usr/local/cuda` links are shadowed by the host's, so
    the container's compiled CUDA code binds to the driver actually
    installed on the node.
* - AMD (ROCm)
  - `--rocm`
  - Same idea as `--nv`, but for `/opt/rocm` and the AMD kernel
    driver. Supported by Apptainer 1.1+ and modern Singularity.
* - No GPU on the node
  - (nothing)
  - Wrapper runs plain `apptainer exec <image> <program>`, so a
    CPU-only fallback of the container still works.
::::

`--nv` and `--rocm` are **mutually exclusive** — a container can't be
NVIDIA- and AMD-accelerated at the same time. The wrapper prefers
`--nv` when both are detected, on the (empirically common) assumption
that the CUDA path is what the user wants.

## Container requirements

For `--nv` to work, the container must be built against a
**CUDA-compatible** toolchain:

- The CUDA runtime major version in the container must be ≤ the
  driver's CUDA capability. E.g. driver `525.x` (CUDA 12.0) can run
  containers built for CUDA 11.x or 12.0 but not 12.5.
- Standard CUDA base images from NGC or `nvidia/cuda:` on Docker Hub
  are safe.

For `--rocm`, the container must:

- Include an installation of ROCm compatible with the host's kernel
  driver version.
- Have access to `/dev/kfd` and `/dev/dri` — Apptainer mounts these
  automatically when `--rocm` is passed.

Neither flag installs anything into the container itself; they only
control which host-side directories get mounted.

## Verifying GPU access

::::{tab-set}
:::{tab-item} NVIDIA

```{code-block} bash
:caption: Sanity check the wrapper sees the GPU

module load pytorch/2.7.1-cuda11.8-cudnn9-runtime-jupyter
python - <<'PY'
import torch
print("CUDA available:", torch.cuda.is_available())
print("Device count:", torch.cuda.device_count())
for i in range(torch.cuda.device_count()):
    print(f"  {i}: {torch.cuda.get_device_name(i)}")
PY
```

If `cuda.is_available()` returns False:

1. Check that `nvidia-smi` works outside the container.
2. Check the wrapper actually contains `--nv`: `grep '\-\-nv'
   ~/container-apps/tools/pytorch/*/bin/python`.
3. Verify the container's CUDA version is ≤ the host driver's CUDA
   capability.
:::
:::{tab-item} AMD ROCm

```{code-block} bash
:caption: Sanity check ROCm

module load pytorch/2.7.1-rocm6.0
python - <<'PY'
import torch
print("HIP available:", torch.cuda.is_available())   # yes, still cuda.*
print("Device:", torch.cuda.get_device_name(0))
PY
```

`torch.cuda.*` in ROCm PyTorch is a HIP shim — the code stays the
same as CUDA. `--rocm` mounts `/opt/rocm` from the host so the shim
binds to the right runtime.
:::
::::

## Multi-GPU jobs

Multi-GPU workflows use the same wrapper, just with a scheduler that
allocates multiple GPUs to the job:

```{code-block} bash
:caption: Slurm, 4 GPUs on one node

#!/bin/bash
#SBATCH --gres=gpu:4
#SBATCH --cpus-per-task=8

module load pytorch/2.7.1-cuda11.8-cudnn9-runtime-jupyter

python train.py --num-gpus 4
```

`--nv` inside the wrapper mounts the driver; Slurm's `--gres=gpu:4`
sets `CUDA_VISIBLE_DEVICES=0,1,2,3` and the container inherits that
env, so PyTorch (or TensorFlow, or JAX) sees exactly the four GPUs
you were allocated.

For **multi-node multi-GPU** jobs, combine with MPI (see
[MPI support](mpi.md)):

```{code-block} bash
:caption: Distributed training across nodes with NCCL

#!/bin/bash
#SBATCH --nodes=2
#SBATCH --gres=gpu:4
#SBATCH --ntasks-per-node=4

module load pytorch/2.7.1-cuda11.8-cudnn9-runtime-jupyter

# Each srun task runs on a distinct GPU; NCCL over the fabric handles
# inter-GPU communication.
srun python train_ddp.py
```

## Adding CUDA env vars to a specific app

If a particular container needs environment variables set at load
time (e.g. `LD_LIBRARY_PATH` extensions, `CUDA_LAUNCH_BLOCKING=1`),
edit the generated modulefile after `container-mod pipe`:

```{code-block} lua
:caption: Adding to ~/privatemodules/pytorch/2.7.1.lua

setenv("CUDA_LAUNCH_BLOCKING", "1")
setenv("NCCL_DEBUG", "INFO")
```

The next time you deploy this app, `container-mod` will *repurpose*
the existing modulefile (see [Templates / Repurposing](templates.md#repurposing-existing-modulefiles))
and your edits survive.

## Turning GPU support off for a specific app

Very rarely useful, but: if you have a container that misbehaves
with `--nv` (e.g. it links against a CUDA runtime incompatible with
the driver), you can strip the flag by:

- Removing GPU visibility from the job (`--gres=none` on Slurm), or
- Editing the wrapper by hand to remove the `--nv`-adding block, or
- Using a profile with `RUNTIME_OPTIONS` that explicitly disables GPU
  passthrough — currently `container-mod` doesn't have a knob for
  this beyond editing the wrapper; open an issue if you'd like one.

## Related

- **[MPI support](mpi.md)** — for MPI + CUDA workflows.
- **[Profile variables — RUNTIME_OPTIONS](../configuration/variables.md#runtime_options)** —
  add more container-runtime flags.
- **[Subcommands / exec](../usage/subcommands/exec.md)** — regenerate
  wrappers after upgrading the GPU driver.

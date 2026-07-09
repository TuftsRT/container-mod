# MPI support

Running MPI-enabled applications inside Singularity / Apptainer
containers works, but requires the wrapper to:

- Invoke the container with **`apptainer run --mpi ...`** (or the
  Singularity equivalent) rather than plain `exec`.
- Pass through any site-specific runtime flags (e.g. `--cleanenv`).
- Match the host's MPI implementation and version to whatever the
  container was built against.

`container-mod` handles all three with two profile variables:
`RUNTIME_LAUNCH` and `RUNTIME_OPTIONS`.

## Turning MPI on for a profile

Add both variables to your profile file:

```{code-block} bash
:caption: profiles/mpi-cluster

MOD_EXISTING_DIR_DEF="/cluster/example/modules"
PUBLIC_IMAGEDIR="/cluster/example/images"
PUBLIC_EXECUTABLE_DIR="/cluster/example/tools"

# Use `apptainer run` rather than `apptainer exec` so the container's
# runscript (if any) can set up MPI-specific env before the program
# is invoked.  Both `run` and `exec` accept `--mpi`; `run` is the
# convention Apptainer's MPI docs use.
RUNTIME_LAUNCH="run"

# Pass --mpi to instruct Apptainer to bridge the host's MPI runtime
# into the container.  --cleanenv keeps host env from leaking into
# the container (recommended for MPI to avoid conflicting MPI env vars).
RUNTIME_OPTIONS="--mpi --cleanenv"
```

Any container deployed under `--profile mpi-cluster` will now have
wrappers that look like:

```bash
"$RUNTIME" "$RUNTIME_LAUNCH" "${RUNTIME_OPTIONS[@]}" "${OPTIONS[@]}" \
    "$IMAGE_DIR/$IMAGE" "$PROGRAM" "$@"
# resolves to:
apptainer run --mpi --cleanenv <image> <program> "$@"
```

## What `--mpi` actually does

Apptainer's `--mpi` flag (and Singularity's equivalent) tells the
container runtime to bridge the **host MPI** into the container using
the "hybrid" MPI model:

- The host's `mpirun` / `srun` launches the wrapper on each node.
- Each wrapper invocation `apptainer run --mpi ...` starts the
  container with a mount of the host's MPI libraries + `PMIx` support.
- Inside the container, the application's MPI implementation calls
  down into the host MPI, so the ranks can communicate.

This means the **host MPI implementation must be
ABI-compatible** with the container's MPI. In practice:

- OpenMPI 4.x host ↔ OpenMPI 4.x container: fine.
- MPICH 3.x host ↔ MPICH 3.x container: fine.
- Cross-family (OpenMPI ↔ MPICH): usually fails at runtime.
- Major version skew (OpenMPI 3.x host, OpenMPI 4.x container): may
  or may not work; test.

## Launching MPI jobs

The generated wrapper handles a **single rank**. Multi-rank launches
are driven by the host scheduler:

::::{tab-set}
:::{tab-item} Slurm

```{code-block} bash
:caption: 4 nodes × 32 tasks

#!/bin/bash
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=32
#SBATCH --cpus-per-task=1

module load osu-benchmarks/7.4

# srun launches 128 wrapper processes; each `apptainer run --mpi`
# bridges into the host MPI so all 128 ranks can communicate.
srun osu_alltoall
```

:::
:::{tab-item} OpenMPI mpirun

```bash
mpirun -np 128 --hostfile my.hosts osu_alltoall
```

:::
:::{tab-item} Intel MPI

```bash
mpiexec -n 128 osu_alltoall
```

Set `I_MPI_PMI_LIBRARY` to the host's PMI/PMIx library first.
:::
::::

The wrapper does *not* invoke `mpirun` inside itself — that would
launch a nested-MPI process. Always let the host scheduler drive the
parallelism, one wrapper process per rank.

## Container requirements

For `--mpi` to work, the container must:

- Have an MPI implementation installed (OpenMPI, MPICH, Intel MPI).
- Be built with `PMIx` support enabled, or with PMI-1 / PMI-2
  compatibility — whatever your host scheduler emits.
- Either **ship** an ABI-compatible MPI, or be built with the
  `--enable-slurm --with-pmi=...` flags so the host MPI mount can
  take over via `--mpi`.

If you have a choice, most BioContainers, NGC HPC containers, and
mainstream scientific images (LAMMPS, GROMACS, OpenFOAM, Quantum
ESPRESSO, WRF) ship with the right MPI setup. See the container
publisher's docs.

## Verifying it works

After deploying an MPI-capable app, sanity-check with the OSU
microbenchmarks:

```{code-block} bash
:caption: One-node check first

module load osu-benchmarks/7.4
apptainer exec $IMAGE osu_hello   # should print "Hello world"

# Two-rank check on the same node
mpirun -np 2 osu_hello

# Multi-node check via the scheduler
srun -N 2 -n 4 osu_bw
```

If the multi-node bandwidth benchmark reports a plausible number for
your fabric (~11 GB/s on 100 Gb IB, ~24 GB/s on 200 Gb IB, ~5 GB/s
on 25 Gb Ethernet), MPI is bridging correctly.

## Common failure modes

::::{list-table}
:header-rows: 1
:widths: 30 40 30

* - Symptom
  - Likely cause
  - Fix
* - `PMI_Init failed`
  - Host and container PMI versions mismatch
  - Add `--env PMIX_MCA_gds=hash` to `RUNTIME_OPTIONS`, or use a
    container built against the same PMI major version as the host.
* - `mca: base: component_find: unable to open btl openib`
  - Container linked InfiniBand libraries can't see the host's
    `/dev/infiniband`
  - Add `/dev/infiniband` and `/sys/class/infiniband` to `BIND_PATH`.
* - Ranks all report `1` — no communication
  - `--mpi` was omitted from `RUNTIME_OPTIONS`
  - Confirm the wrapper has `apptainer run --mpi ...`; regenerate with
    the updated profile.
* - `error while loading shared libraries: libmpi.so.40`
  - Host MPI version doesn't match container's expectation
  - Load a compatible host MPI module before `srun`, or rebuild the
    container against your host MPI major version.
* - Long startup, then hang
  - InfiniBand bind missing, silent fallback to TCP over IPoIB
  - Same fix as InfiniBand entry above.
::::

## Example: LAMMPS

```{code-block} bash
:caption: Admin: deploy LAMMPS as an MPI-enabled module

./container-mod pipe --profile mpi-cluster \
    docker://lammps/lammps:stable_2Aug2023_update3_ubuntu20.04_openmpi_py3
```

```{code-block} bash
:caption: User: run LAMMPS across 4 nodes with 32 tasks each

#!/bin/bash
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=32

module load lammps/stable_2Aug2023_update3

srun lmp -in input.lammps
```

The wrapper `lmp` inside `${PUBLIC_EXECUTABLE_DIR}/lammps/…/bin/lmp`
was generated with `RUNTIME_LAUNCH="run"` +
`RUNTIME_OPTIONS="--mpi --cleanenv"`, so each of the 128 ranks
calls `apptainer run --mpi --cleanenv <lammps.sif> lmp -in
input.lammps`.

## Per-app override

Sometimes you want MPI wrappers for only a handful of apps rather
than the whole profile. Two options:

- **Set the environment variables per-run:**

  ```bash
  RUNTIME_LAUNCH=run RUNTIME_OPTIONS="--mpi --cleanenv" \
      ./container-mod pipe --profile biocontainers \
      docker://lammps/lammps:stable_2Aug2023
  ```

  These override anything in the profile.

- **Create a dedicated MPI profile** (as above) and use it only for
  MPI apps, while a plain profile handles the rest.

## Non-MPI containers under an MPI profile

An MPI profile is safe for non-MPI containers too — `--mpi` is a
no-op inside a container that doesn't invoke `MPI_Init`. If you'd
rather keep MPI flags off for non-MPI apps, deploy them under a
separate non-MPI profile.

## Related

- **[Profile variables — RUNTIME_LAUNCH](../configuration/variables.md#runtime_launch)**
- **[Profile variables — RUNTIME_OPTIONS](../configuration/variables.md#runtime_options)**
- **[GPU support](gpu.md)** — for MPI + CUDA workflows.
- **[Runtime detection](runtime-detection.md)** — how the wrapper picks
  its runtime.

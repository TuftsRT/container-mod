# Deployment lifecycle

How admins should think about deploying, testing, and promoting
containers with `container-mod`. Not required reading, but the
mental model helps.

## The five stages

```{mermaid}
:caption: End-to-end lifecycle of a container-mod deployment

flowchart LR
    A[1. Register<br>metadata] --> B[2. Pull<br>image]
    B --> C[3. Generate<br>modulefile]
    B --> D[4. Generate<br>wrappers]
    C --> E[5. Promote<br>to production]
    D --> E
    style A fill:#f3e8ff
    style B fill:#dbeafe
    style C fill:#dcfce7
    style D fill:#fef3c7
    style E fill:#fed7aa
```

Each stage maps to a specific `container-mod` invocation. In simple
cases `pipe` fuses stages 2–4 into one step; the reason to think
about them separately is that anything that goes wrong tends to be
localizable to exactly one of them.

## Stage 1 — Register metadata

An app must have a text entry under `repos/<app>` before its
modulefile can render or its wrappers can generate. The file names
the programs and describes the app.

```bash
# Interactive: run any subcommand that needs metadata; you'll be
# prompted for missing fields.
container-mod pipe --profile biocontainers <uri>

# Or edit the file directly:
cat > repos/mytool <<'EOF'
Description: A short one-line description of mytool.
Home Page: https://mytool.example.com
Programs: mytool,mytool-index,mytool-report
EOF
```

The [Application metadata](metadata.md) page has the full schema.

## Stage 2 — Pull the image

```bash
container-mod pull --profile biocontainers -u <uri>
```

`-u` records the pulled version as a new `version(...)` line in
`repos/<app>`. Recommended for shared deployments so the catalog
tracks what was pulled when.

Batch this stage overnight on a build node if you have many pulls
queued.

## Stage 3 — Generate the modulefile

```bash
container-mod module --profile biocontainers <uri>
```

The output goes to `<OUTDIR>/incomplete/<app>/<version>.lua`
regardless of `MOD_EXISTING_DIR_DEF`. This is deliberate: it's a
staging directory the admin reviews before promoting the file into
the production module tree.

If a previous version of the same app already exists in
`MOD_EXISTING_DIR_DEF`, this stage picks up that file as a template
and reuses your customizations (extra `setenv`, `depends_on`, etc.).
See [Repurposing existing modulefiles](../usage/subcommands/module.md#repurposing-existing-modulefiles-lmod-only).

## Stage 4 — Generate wrappers

```bash
container-mod exec --profile biocontainers <uri>
```

Wrappers land at
`${PUBLIC_EXECUTABLE_DIR}/<app>/<version>/bin/<program>` at mode
`755`. Skipped programs (those not actually present inside the
container) produce warnings but not errors.

Rerun with `-f` after upgrading `container-mod` to pick up bug fixes
in the wrapper template.

## Stage 5 — Promote to production

Once you're satisfied the staged module + wrappers work:

```bash
# Test the staged module
module use ./incomplete
module load bowtie2/2.5.4
bowtie2 --version

# Promote
cp -r incomplete/bowtie2/2.5.4.lua "$MOD_EXISTING_DIR_DEF/bowtie2/"
```

Some sites automate this with a wrapper script or CI job; others do
it by hand. Either is fine.

## What `pipe` does

`pipe` runs stages 2–4 in one shot for a URI. It's what you use for
routine day-to-day deployments where you already trust the container
publisher and the metadata is in place:

```{mermaid}
flowchart LR
    A[URI] --> P[container-mod pipe --profile ...]
    subgraph pipe
        direction LR
        P1[pull] --> P2[module]
        P2 --> P3[exec]
    end
    P --> P1
    P3 --> B[Manual review /<br>promote]
```

Skip `pipe` and use individual subcommands when you want to:

- Pull many images overnight without generating anything.
- Regenerate the modulefile only (after a profile edit).
- Rebuild wrappers only (after a `container-mod` upgrade).

## What goes wrong at each stage

::::{list-table}
:header-rows: 1
:widths: 15 40 45

* - Stage
  - Common failure
  - Fix
* - 1 metadata
  - Wrong `Programs:` list — wrappers missing or extra
  - Edit `repos/<app>`, rerun stage 4 with `-f`.
* - 2 pull
  - Registry auth / network / image not found
  - Verify the URI in a browser; retry.
* - 3 module
  - Wrong `depends_on` because runtime detection is off
  - Set `RUNTIME_MODULE` in the profile. See [Runtime detection](../advanced/runtime-detection.md).
* - 4 exec
  - Wrappers fail at runtime — `Failed to find container runtime`
  - Cluster's runtime not in PATH at run time. Ensure a `singularity`
    or `apptainer` module exists, or set PATH via site defaults.
* - 5 promote
  - Users can't see the new module
  - `MOD_EXISTING_DIR_DEF` isn't in `MODULEPATH`; check `module use`
    or your site's default modulepath.
::::

## Retiring an old version

To retire `bowtie2/2.4.2`:

```bash
# 1. Move the modulefile out of the production tree
git mv "$MOD_EXISTING_DIR_DEF/bowtie2/2.4.2.lua" ./retired/

# 2. Optionally remove the wrappers and image
rm -rf "${PUBLIC_EXECUTABLE_DIR}/bowtie2/2.4.2"
rm -f  "${PUBLIC_IMAGEDIR}/staphb_bowtie2:2.4.2.sif"

# 3. Optionally drop the version() line from repos/bowtie2
```

Steps 2 and 3 are optional. Keeping the image and wrappers around
means users on stale scripts still work; removing them saves disk
and reduces confusion.

## See also

- **[Subcommands](../usage/subcommands.md)** — the four subcommands
  in detail.
- **[Personal vs shared mode](modes.md)** — where each stage writes.
- **[Application metadata](metadata.md)** — stage-1 file format.

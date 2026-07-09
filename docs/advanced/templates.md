# Customizing the modulefile template

`container-mod` renders each modulefile from a template using simple
`${PLACEHOLDER}` substitution via `sed`. The bundled templates cover
most cases; the extension points below let you customize output
without forking the script.

## Template files

- `templates/module_template.lua` — Lmod
- `templates/module_template.tcl` — Environment Modules (Tcl)

Both live next to the `container-mod` script and are picked up
automatically. The bundled Lua template is roughly:

```text
help([==[

Description
===========
${DESCRIPTION}

More information
================
 - ${REGISTRY}: ${REGISTRY_URL}
 - Home page:     ${HOMEPAGE}
]==])

whatis("Name: ${APP}")
whatis("Version: ${VERSION}")
whatis("Description: ${DESCRIPTION}")
whatis("${REGISTRY}: ${REGISTRY_URL}")
whatis("Home page:     ${HOMEPAGE}")

local image = "${IMAGE}"
local uri = "${URI}"
local version = "${VERSION}"

conflict(myModuleName())

local modroot="${EXECUTABLE_DIR}/${APP}/" .. "${VERSION}"
prepend_path("PATH", modroot.."/bin", ":")
${BIND_LUA}
-- Container runtime dependency (omitted on sites where the runtime
-- is a system binary with no corresponding Lmod entry).
${RUNTIME_DEPENDS_LUA}
```

## Available placeholders

```{list-table}
:header-rows: 1
:widths: 25 75

* - Placeholder
  - Value
* - `${APP}`
  - Application name (e.g. `bowtie2`).
* - `${VERSION}`
  - Application version (e.g. `2.5.4`).
* - `${IMAGE}`
  - `.sif` filename (e.g. `staphb_bowtie2:2.5.4.sif`).
* - `${URI}`
  - Original container URI.
* - `${DESCRIPTION}`
  - From the app's metadata file.
* - `${HOMEPAGE}`
  - From the app's metadata file.
* - `${REGISTRY}`
  - `BioContainers`, `NVIDIA NGC`, `GitHub Container Registry`,
    `Quay.io`, or `DockerHub` (auto-detected from the URI host).
* - `${REGISTRY_URL}`
  - Direct link to the container in the detected registry.
* - `${EXECUTABLE_DIR}`
  - Wrapper root (`~/container-apps/tools` or
    `${PUBLIC_EXECUTABLE_DIR}`).
* - `${RUNTIME_DEPENDS_LUA}` / `${RUNTIME_DEPENDS_TCL}`
  - Rendered `depends_on(...)` block for Lmod / Tcl; empty on sites
    with no matching runtime module.
* - `${BIND_LUA}` / `${BIND_TCL}`
  - Rendered `prepend_path` for `APPTAINER_BIND` when `BIND_PATH` is
    set in the profile; empty otherwise.
* - `${RUNTIME_MODULE}`
  - The runtime module name only; typically only used inside the
    `${RUNTIME_DEPENDS_*}` block.
```

## Registry auto-detection

The `${REGISTRY}` and `${REGISTRY_URL}` values are picked from the URI
host:

```{list-table}
:header-rows: 1
:widths: 40 25 35

* - URI host
  - `${REGISTRY}`
  - Catalog link
* - `quay.io/biocontainers/...`
  - `BioContainers`
  - `biocontainers.pro/tools/<app>`
* - `nvcr.io/...`
  - `NVIDIA NGC`
  - `catalog.ngc.nvidia.com/orgs/<repo>`
* - `ghcr.io/...`
  - `GitHub Container Registry`
  - `ghcr.io/<repo>`
* - Other `quay.io/...`
  - `Quay.io`
  - `quay.io/repository/<repo>`
* - anything else
  - `DockerHub`
  - `hub.docker.com/r/<repo>`
```

## Adding your own content

To append site-specific commands to every generated modulefile, edit
`templates/module_template.lua` and add whatever you need after the
placeholders:

```text
-- End of default template …
prepend_path("PATH", modroot.."/bin", ":")
${BIND_LUA}
${RUNTIME_DEPENDS_LUA}

-- Site-specific additions:
setenv("MY_SITE_FLAG", "1")
add_property("arch", "gpu")   -- Lmod property tag
```

Existing modules are re-rendered on the next `module` / `pipe` run
against them.

## Repurposing existing modulefiles

For Lmod (not Tcl), `container-mod` first searches
`MOD_EXISTING_DIR` / `MOD_EXISTING_DIR_DEF` for a **previous** version
of the app. If one is found, its contents are used as the template
verbatim, and `container-mod` substitutes only:

- `whatis("Version: ...")`
- `local version = "..."`
- `local image = "..."`
- `local uri = "..."`
- `local modroot = ... .. "..."`

Everything else is preserved — site edits, custom `setenv`, extra
`depends_on`, help-text tweaks. So a common pattern is:

1. Deploy the first version with the plain template.
2. Hand-edit that modulefile to add site-specific customizations.
3. Deploy later versions — they inherit the customizations automatically.

## Next

- **[Runtime detection](runtime-detection.md)** — how
  `${RUNTIME_DEPENDS_*}` is decided.
- **[Profiles](../configuration/profiles.md)** — where output
  locations come from.

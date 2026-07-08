# Jupyter support

With `-j` / `--jupyter`, `container-mod` registers a Jupyter kernel that
runs the container's Python. Users can then pick the kernel from
JupyterLab / Notebook and get an environment with everything the
container ships.

## Requirements

The container itself must include:

- `python` (Python 3 recommended)
- `ipykernel`

If `ipykernel` is missing, `container-mod` prints a formatted error and
suggests how to add it:

```
+---------------------------------------------------+
| The dependency 'ipykernel' was not detected in    |
| <image>.                                          |
|                                                   |
| Please add it to your container definition:       |
|                                                   |
|    pip install ipython ipykernel                  |
+---------------------------------------------------+
```

## Registering a kernel

```bash
./container-mod pipe -p -j docker://tensorflow/tensorflow:2.18.0-jupyter
```

Produces:

- `~/.local/share/jupyter/kernels/tensorflow-2.18.0-jupyter/kernel.json`

The kernel.json points at the wrapper `python` inside the container's
bin directory (created by `exec`), so `pipe -j` deploys the wrappers
first and the kernel afterward. Standalone `-j` on `module` or `exec`
runs also works if wrappers already exist.

## Kernel location

- **Personal mode:** `~/.local/share/jupyter/kernels/<app>-<version>/`
- **Profile-backed mode:** `<OUTDIR>/kernels/<app>-<version>/`, mode
  `644` for files and `755` for directories. You can then copy that
  directory into a site-wide Jupyter data directory such as
  `/opt/jupyter/kernels/`.

## kernel.json template

The bundled `jupyter_kernel.json` (in the repo root) looks like:

```json
{
    "argv": [
        "APPDIR/python",
        "-m", "ipykernel_launcher",
        "-f", "{connection_file}"
    ],
    "display_name": "APP VERSION",
    "language": "python"
}
```

`container-mod` substitutes `APPDIR`, `APP`, and `VERSION` at
generation time. Customize the template by editing that file — for
example, to inject `env` overrides:

```json
{
    "argv": [ "APPDIR/python", "-m", "ipykernel_launcher", "-f", "{connection_file}" ],
    "display_name": "APP VERSION",
    "language": "python",
    "env": {
        "OMP_NUM_THREADS": "1",
        "TF_CPP_MIN_LOG_LEVEL": "2"
    }
}
```

Changes propagate on next `-j` run.

## Container caveats

- The container's `python` must be reachable via the wrapper directory
  path baked into `kernel.json`. If you move the wrapper tree, the
  kernel breaks.
- The container's `ipykernel_launcher` communicates with the Jupyter
  server via a socket-file handshake. The Jupyter server must be able
  to read/write `{connection_file}` from within the container, which
  normally means the file is on a filesystem that's bind-mounted into
  the container. If your `BIND_PATH` covers `$HOME` / `/tmp` / wherever
  Jupyter puts its connection files, this "just works". Otherwise
  extend `BIND_PATH` accordingly.

## Next

- **[Templates](templates.md)** — customize the generated modulefile.
- **[Profile variables](../configuration/variables.md#bind_path)** —
  add extra bind paths for connection files.

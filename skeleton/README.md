# Skeleton

Minimal starting point for a new project in this repo.

```bash
cp -r skeleton my-project
cd my-project
pixi install
```

Then edit `pixi.toml`: change `name` and `description`, and `pixi add` what
you need. Keep `ipykernel` — it is what lets the JupyterLab instance at the
repo root (via pixi-kernel) run notebooks in this project's own environment.

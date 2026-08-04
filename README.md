# Project Name

One-sentence description of what this project does and who it's for.

## Status

Early / experimental / stable — say which, so readers know what to expect.

## Requirements

- [Pixi](https://pixi.prefix.dev) — manages the toolchain, so no separate
  Python install is needed
- Any system dependencies not available from conda-forge

## Installation

```bash
git clone https://github.com/jeffmincey/playground.git
cd playground
pixi install
```

## Usage

```bash
pixi run start
```

Describe the expected output here.

## Configuration

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `EXAMPLE_VAR` | no | `none` | What it controls |

Copy `.env.example` to `.env` and fill in values. Never commit real secrets.

## Development

```bash
pixi run test
pixi run lint
```

These resolve to the `dev` environment automatically, since the tasks are
defined on the `dev` feature. Tasks live in `pixi.toml` — add new ones there
rather than documenting ad-hoc commands here.

## Project Layout

```
.
├── README.md
├── pixi.toml       # environment and task definitions
├── pixi.lock       # resolved dependencies (commit this)
└── src/            # application code
```

## Contributing

1. Create a branch off the default branch.
2. Make the change, with tests where they apply.
3. Open a pull request describing what changed and why.

## License

Specify a license (e.g. MIT) or state that the project is unlicensed.

# Async Multi-API Fetcher

A small Python CLI that calls several public APIs concurrently with `asyncio` and `httpx`. It validates each response with Pydantic and caches results on disk.

## Features

- **Concurrent requests:** all selected APIs are fetched at once with `asyncio.gather`, and total elapsed time is printed.
- **Validated responses:** each response is parsed into a Pydantic model (`GitHubUser`, `CatFact`, `AgeGuess`).
- **Error handling:** HTTP, network and validation failures are reported per API without stopping the others.
- **Disk cache:** results are saved to `cache.json` and reused for 60 seconds.
- **Configurable timeout:** set the per-request timeout from the command line.

## APIs

| Name      | Source                     |
|-----------|----------------------------|
| `github`  | GitHub users API           |
| `catfact` | catfact.ninja              |
| `agify`   | agify.io (age from a name) |

## Setup

Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # pinned versions, includes mypy
pip install -e .                 # installs the CLI command
```

## Usage

```bash
async-multi-api-fetcher-cli                    # fetch all APIs
async-multi-api-fetcher-cli github catfact     # fetch only some
async-multi-api-fetcher-cli --no-cache         # ignore the cache
async-multi-api-fetcher-cli --timeout 5 agify  # 5s timeout per request
```

You can also run `python -m async_multi_api_fetcher_cli`.

| Option        | Description                                 |
|---------------|---------------------------------------------|
| `apis`        | Which APIs to call (default: all)           |
| `--no-cache`  | Ignore the cache and fetch everything       |
| `--timeout N` | Seconds to wait for each API (default: 3.0) |

## How it works

<!-- TODO: explain in your own words: how asyncio.gather runs the requests, what happens when one fails, and how the cache decides an entry is fresh. -->

## Example output

```
Fetching: ['github', 'catfact', 'agify']
github: login='...' public_repos=... followers=... name='...'
catfact: fact='...' length=...
agify: count=... name='mihir' age=...
Concurrent: 0.42s
```

## Project structure

- `src/async_multi_api_fetcher_cli/cli.py`: argument parsing, fetching, caching
- `src/async_multi_api_fetcher_cli/models.py`: Pydantic response models
- `pyproject.toml`: package metadata and the CLI entry point
- `requirements.txt`: pinned dependencies
- `cache.json`: generated cache file (git-ignored, safe to delete)

## Type checking

```bash
mypy --strict src
```

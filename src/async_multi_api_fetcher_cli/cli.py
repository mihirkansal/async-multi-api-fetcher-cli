import argparse
import asyncio
import json
import time
from pathlib import Path
from typing import Any

import httpx
from pydantic import BaseModel, ValidationError

from .models import AgeGuess, CatFact, GitHubUser

CACHE_TTL = 60
CACHE_FILE = Path("cache.json")

APIS = {
    "github": "https://api.github.com/users/mihirkansal",
    "catfact": "https://catfact.ninja/fact",
    "agify": "https://api.agify.io/?name=mihir",
}

MODELS: dict[str, type[BaseModel]] = {
    "github": GitHubUser,
    "catfact": CatFact,
    "agify": AgeGuess,
}


async def fetch(
    client: httpx.AsyncClient, name: str, url: str, model: type[BaseModel]
) -> BaseModel | None:
    try:
        response = await client.get(url)
        response.raise_for_status()
        return model.model_validate(response.json())
    except (httpx.HTTPStatusError, httpx.RequestError, ValidationError, ValueError) as e:
        print(f"[error] {name}: {type(e).__name__}: {e}")
        return None


def load_cache() -> dict[str, Any]:
    try:
        with open(CACHE_FILE, "r") as f:
            data: dict[str, Any] = json.load(f)
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_cache(cache: dict[str, Any]) -> None:
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def is_stale(cache: dict[str, Any], name: str) -> bool:
    entry = cache.get(name)
    return entry is None or time.time() - entry["saved_at"] > CACHE_TTL


async def run(args: argparse.Namespace) -> None:
    selected: list[str] = args.apis or list(APIS)
    cache = {} if args.no_cache else load_cache()
    missing = [name for name in selected if is_stale(cache, name)]

    for name in selected:
        if name in missing:
            continue
        try:
            print(f"{name} (cached): {MODELS[name].model_validate(cache[name]['data'])}")
        except ValidationError:
            missing.append(name)  # cache entry no longer matches the model

    if not missing:
        return

    print(f"Fetching: {missing}")
    async with httpx.AsyncClient(timeout=args.timeout) as client:
        start = time.perf_counter()
        results = await asyncio.gather(
            *(fetch(client, name, APIS[name], MODELS[name]) for name in missing)
        )
        elapsed = time.perf_counter() - start

    for name, data in zip(missing, results):
        print(f"{name}: {data}")
        if data is not None:
            cache[name] = {"saved_at": time.time(), "data": data.model_dump()}
    print(f"Concurrent: {elapsed:.2f}s")
    save_cache(cache)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch several APIs at once.")
    parser.add_argument("--no-cache", action="store_true", help="ignore the cache and fetch everything")
    parser.add_argument("--timeout", type=float, default=3.0, help="seconds to wait for each API")
    parser.add_argument("apis", nargs="*", choices=list(APIS), help="which APIs to call (default: all)")
    asyncio.run(run(parser.parse_args()))

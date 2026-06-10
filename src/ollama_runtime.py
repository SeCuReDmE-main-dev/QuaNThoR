"""Shared helpers for talking to Ollama models."""

from __future__ import annotations

import json
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

import requests


def _endpoint(base_url: str, path: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/api"):
        return f"{base}/{path}"
    return f"{base}/api/{path}"


def default_ollama_base_url() -> str:
    """Return the safest default Ollama endpoint for the current runtime."""

    if Path("/.dockerenv").exists() or Path("/run/.containerenv").exists():
        return "http://host.docker.internal:11434"
    if os.getenv("RUNNING_IN_DOCKER") == "1":
        return "http://host.docker.internal:11434"
    return "http://127.0.0.1:11434"


@lru_cache(maxsize=32)
def available_models(base_url: str, auth_token: str | None = None, timeout_seconds: int = 5) -> tuple[str, ...]:
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    try:
        response = requests.get(_endpoint(base_url, "tags"), headers=headers, timeout=timeout_seconds)
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return ()

    models: List[str] = []
    for item in payload.get("models", []):
        if not isinstance(item, dict):
            continue
        name = item.get("name") or item.get("model")
        if name:
            models.append(str(name))

    return tuple(models)


def _name_matches(candidate: str, available_name: str) -> bool:
    if candidate == available_name:
        return True
    candidate_base = candidate.split(":", 1)[0]
    available_base = available_name.split(":", 1)[0]
    return candidate_base == available_base


def resolve_model(
    base_url: str,
    preferred_model: str,
    fallback_models: Sequence[str],
    auth_token: str | None = None,
    timeout_seconds: int = 5,
) -> str:
    available = available_models(base_url, auth_token=auth_token, timeout_seconds=timeout_seconds)
    if not available:
        return preferred_model

    ordered_candidates = [preferred_model, *fallback_models]
    for candidate in ordered_candidates:
        if not candidate:
            continue
        if any(_name_matches(candidate, available_name) for available_name in available):
            return candidate if candidate in available else next(
                (available_name for available_name in available if _name_matches(candidate, available_name)),
                candidate,
            )

    return preferred_model


def supports_structured_outputs(model_name: str) -> bool:
    lowered = model_name.lower()
    return "cloud" not in lowered


def extract_json_object(content: Any) -> Dict[str, Any]:
    if isinstance(content, dict):
        return content
    if not isinstance(content, str):
        return {}

    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and last > first:
        try:
            parsed = json.loads(text[first : last + 1])
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            return {}

    return {}

"""Optional HippoRAG integration for QuaNThoR."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List

import requests


def _enabled_from_env(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _openai_compatible_base_url(value: str | None) -> str:
    cleaned = str(value or "").strip().rstrip("/")
    if not cleaned:
        return ""
    if cleaned.endswith("/v1"):
        return cleaned
    return f"{cleaned}/v1"


def _ollama_cloud_enabled() -> bool:
    return bool(os.getenv("OLLAMA_API_KEY") or os.getenv("OLLAMA_CLOUD_TOKEN"))


def _ollama_cloud_api_key() -> str:
    return os.getenv("OLLAMA_API_KEY") or os.getenv("OLLAMA_CLOUD_TOKEN") or ""


def _embedding_endpoint_required(
    embedding_model_name: str, embedding_base_url: str, embedding_model_explicit: bool
) -> bool:
    if embedding_base_url:
        return False
    if not embedding_model_explicit:
        return True
    if embedding_model_name.startswith(("Transformers/", "GritLM", "nvidia/NV-Embed-v2", "contriever")):
        return False
    return True


class HippoRAGService:
    """Lazy wrapper around OSU-NLP-Group/HippoRAG.

    HippoRAG is intentionally optional because its upstream runtime is heavier
    than the core Mizar verifier and is documented around Python 3.10.
    """

    def __init__(self) -> None:
        self.enabled = _enabled_from_env(os.getenv("HIPPORAG_ENABLED"))
        self.save_dir = os.getenv("HIPPORAG_SAVE_DIR", "outputs/hipporag")
        ollama_openai_base_url = _openai_compatible_base_url(os.getenv("OLLAMA_BASE_URL"))
        ollama_cloud_base_url = "https://ollama.com/v1" if _ollama_cloud_enabled() else ""
        default_ollama_model = "gemma4:31b" if _ollama_cloud_enabled() else "gemma4:12b-it-qat"
        self.llm_model_name = os.getenv("HIPPORAG_LLM_MODEL", os.getenv("OLLAMA_MODEL", default_ollama_model))
        self.embedding_model_explicit = bool(os.getenv("HIPPORAG_EMBEDDING_MODEL"))
        self.llm_base_url = (
            os.getenv("HIPPORAG_LLM_BASE_URL")
            or os.getenv("OPENAI_BASE_URL", "")
            or ollama_cloud_base_url
            or ollama_openai_base_url
        )
        self.embedding_model_name = os.getenv("HIPPORAG_EMBEDDING_MODEL") or (
            "nomic-embed-text" if ollama_openai_base_url else "nvidia/NV-Embed-v2"
        )
        self.embedding_base_url = os.getenv("HIPPORAG_EMBEDDING_BASE_URL") or ollama_openai_base_url
        self.default_top_k = int(os.getenv("HIPPORAG_TOP_K", "5"))
        self.service_url = os.getenv("HIPPORAG_SERVICE_URL", "").rstrip("/")
        self.request_timeout = float(os.getenv("HIPPORAG_REQUEST_TIMEOUT_SECONDS", "120"))
        self._client: Any | None = None
        self._last_error: str | None = None

    def status(self) -> Dict[str, Any]:
        if self.service_url:
            try:
                response = requests.get(f"{self.service_url}/rag/status", timeout=10)
                payload = response.json()
                remote_status = payload.get("hipporag", payload)
                return {
                    **self._json_safe(remote_status),
                    "mode": "http_proxy",
                    "service_url": self.service_url,
                    "proxy_http_status": response.status_code,
                }
            except Exception as exc:  # noqa: BLE001 - status endpoint reports integration state
                self._last_error = str(exc)
                return {
                    "enabled": self.enabled,
                    "available": False,
                    "package_available": None,
                    "initialized": False,
                    "last_error": self._last_error,
                    "mode": "http_proxy",
                    "service_url": self.service_url,
                    "default_top_k": self.default_top_k,
                }

        package_available = importlib.util.find_spec("hipporag") is not None
        return {
            "enabled": self.enabled,
            "available": self.enabled and package_available,
            "package_available": package_available,
            "initialized": self._client is not None,
            "last_error": self._last_error,
            "mode": "in_process",
            "service_url": None,
            "save_dir": self.save_dir,
            "llm_model_name": self.llm_model_name,
            "llm_base_url": self.llm_base_url or None,
            "embedding_model_name": self.embedding_model_name,
            "embedding_base_url": self.embedding_base_url or None,
            "paid_openai_api_required": not bool(_ollama_cloud_enabled() or self.llm_base_url),
            "ollama_cloud_configured": _ollama_cloud_enabled(),
            "embedding_endpoint_required": _embedding_endpoint_required(
                self.embedding_model_name, self.embedding_base_url, self.embedding_model_explicit
            ),
            "default_top_k": self.default_top_k,
        }

    def index(self, docs: Iterable[str]) -> Dict[str, Any]:
        docs_list = [str(doc).strip() for doc in docs if str(doc).strip()]
        if not docs_list:
            return {"status": "error", "message": "At least one non-empty document is required.", "http_status": 400}
        if self.service_url:
            return self._proxy_post("/rag/index", {"docs": docs_list})

        client = self._get_client()
        client.index(docs=docs_list)
        return {
            "status": "success",
            "indexed_documents": len(docs_list),
            "save_dir": self.save_dir,
        }

    def retrieve(self, query: str, top_k: int | None = None) -> Dict[str, Any]:
        cleaned_query = str(query or "").strip()
        if not cleaned_query:
            return {"status": "error", "message": "A non-empty query is required.", "http_status": 400}
        if self.service_url:
            return self._proxy_post(
                "/rag/retrieve",
                {"query": cleaned_query, "top_k": top_k or self.default_top_k},
            )

        client = self._get_client()
        k = top_k or self.default_top_k
        results = client.retrieve(queries=[cleaned_query], num_to_retrieve=k)
        return {
            "status": "success",
            "query": cleaned_query,
            "top_k": k,
            "results": self._json_safe(results),
        }

    def qa(self, query: str, top_k: int | None = None) -> Dict[str, Any]:
        cleaned_query = str(query or "").strip()
        if not cleaned_query:
            return {"status": "error", "message": "A non-empty query is required.", "http_status": 400}
        if self.service_url:
            return self._proxy_post(
                "/rag/qa",
                {"query": cleaned_query, "top_k": top_k or self.default_top_k},
            )

        client = self._get_client()
        k = top_k or self.default_top_k
        results = client.rag_qa(queries=[cleaned_query])
        return {
            "status": "success",
            "query": cleaned_query,
            "top_k": k,
            "results": self._json_safe(results),
        }

    def retrieve_context(self, query: str, top_k: int | None = None) -> str:
        retrieval = self.retrieve(query, top_k)
        if retrieval.get("status") != "success":
            return ""

        flattened = self._flatten_text(retrieval.get("results"))
        return "\n\n".join(flattened[: top_k or self.default_top_k])

    def _get_client(self) -> Any:
        if not self.enabled:
            self._last_error = "HippoRAG is disabled. Set HIPPORAG_ENABLED=true to enable it."
            raise RuntimeError(self._last_error)
        if _ollama_cloud_enabled():
            os.environ.setdefault("OLLAMA_API_KEY", _ollama_cloud_api_key())
            os.environ.setdefault("OPENAI_API_KEY", _ollama_cloud_api_key())
        if self.llm_base_url or self.embedding_base_url:
            os.environ.setdefault("OPENAI_API_KEY", "ollama-local-placeholder")
        if self._client is not None:
            return self._client
        if importlib.util.find_spec("hipporag") is None:
            self._last_error = (
                "HippoRAG is not installed. Use a Python 3.10 environment and install requirements-hipporag.txt."
            )
            raise RuntimeError(self._last_error)

        try:
            from hipporag.HippoRAG import HippoRAG  # type: ignore

            Path(self.save_dir).mkdir(parents=True, exist_ok=True)
            kwargs: Dict[str, Any] = {
                "save_dir": self.save_dir,
                "llm_model_name": self.llm_model_name,
                "embedding_model_name": self.embedding_model_name,
            }
            if self.llm_base_url:
                kwargs["llm_base_url"] = self.llm_base_url
            if self.embedding_base_url:
                kwargs["embedding_base_url"] = self.embedding_base_url

            self._client = HippoRAG(**kwargs)
            self._last_error = None
            return self._client
        except Exception as exc:  # noqa: BLE001 - status endpoint reports the exact issue
            self._last_error = str(exc)
            raise

    def _proxy_post(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = requests.post(
                f"{self.service_url}{endpoint}",
                json=payload,
                timeout=self.request_timeout,
            )
            body = response.json()
            if response.status_code >= 400:
                body.setdefault("http_status", response.status_code)
            return self._json_safe(body)
        except Exception as exc:  # noqa: BLE001 - callers expose the operational error
            self._last_error = str(exc)
            raise RuntimeError(f"HippoRAG service request failed: {exc}") from exc

    def _json_safe(self, value: Any) -> Any:
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, dict):
            return {str(key): self._json_safe(item) for key, item in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [self._json_safe(item) for item in value]
        if hasattr(value, "to_dict"):
            return self._json_safe(value.to_dict())
        if hasattr(value, "__dict__"):
            return self._json_safe(vars(value))
        return str(value)

    def _flatten_text(self, value: Any) -> List[str]:
        if isinstance(value, str):
            return [value] if value.strip() else []
        if isinstance(value, dict):
            texts: List[str] = []
            for key in ("text", "content", "passage", "document", "doc"):
                if key in value:
                    texts.extend(self._flatten_text(value[key]))
            if texts:
                return texts
            return [str(value)]
        if isinstance(value, (list, tuple, set)):
            texts = []
            for item in value:
                texts.extend(self._flatten_text(item))
            return texts
        return [str(value)] if value is not None else []

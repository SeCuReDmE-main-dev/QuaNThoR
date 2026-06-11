import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hipporag_service import HippoRAGService, _openai_compatible_base_url  # noqa: E402


def test_openai_compatible_base_url_normalization():
    assert _openai_compatible_base_url("") == ""
    assert _openai_compatible_base_url("http://localhost:11434") == "http://localhost:11434/v1"
    assert _openai_compatible_base_url("http://localhost:11434/v1") == "http://localhost:11434/v1"


def test_hipporag_prefers_ollama_local_embedding_defaults(monkeypatch):
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.setenv("OLLAMA_MODEL", "gemma4:12b-it-qat")
    monkeypatch.delenv("OLLAMA_CLOUD_TOKEN", raising=False)
    monkeypatch.delenv("OLLAMA_API_KEY", raising=False)
    monkeypatch.delenv("HIPPORAG_LLM_BASE_URL", raising=False)
    monkeypatch.delenv("HIPPORAG_EMBEDDING_BASE_URL", raising=False)
    monkeypatch.delenv("HIPPORAG_EMBEDDING_MODEL", raising=False)

    service = HippoRAGService()
    status = service.status()

    assert service.llm_base_url == "http://localhost:11434/v1"
    assert service.embedding_base_url == "http://localhost:11434/v1"
    assert service.embedding_model_name == "nomic-embed-text"
    assert status["paid_openai_api_required"] is False


def test_hipporag_prefers_ollama_cloud_llm_without_local_activation(monkeypatch):
    monkeypatch.setenv("OLLAMA_CLOUD_TOKEN", "test-token")
    monkeypatch.delenv("OLLAMA_API_KEY", raising=False)
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    monkeypatch.delenv("HIPPORAG_LLM_BASE_URL", raising=False)
    monkeypatch.delenv("HIPPORAG_EMBEDDING_BASE_URL", raising=False)
    monkeypatch.delenv("HIPPORAG_LLM_MODEL", raising=False)
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)

    service = HippoRAGService()
    status = service.status()

    assert service.llm_base_url == "https://ollama.com/v1"
    assert service.llm_model_name == "gemma4:31b"
    assert service.embedding_base_url == ""
    assert status["ollama_cloud_configured"] is True
    assert status["embedding_endpoint_required"] is True

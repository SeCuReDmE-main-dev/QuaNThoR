"""Standalone HippoRAG sidecar API.

Run this module in a Python 3.10 environment with `requirements-hipporag.txt`
installed. The main QuaNThoR backend can proxy to it through
`HIPPORAG_SERVICE_URL`.
"""

from __future__ import annotations

import os
from typing import List

from flask import Flask, jsonify, request
from flask_cors import CORS

try:
    from .hipporag_service import HippoRAGService
except ImportError:  # pragma: no cover - allows direct script execution
    from hipporag_service import HippoRAGService


app = Flask(__name__)
CORS(app)
rag = HippoRAGService()


def _parse_top_k(value: object) -> int:
    try:
        top_k = int(value or rag.default_top_k)
    except (TypeError, ValueError):
        top_k = rag.default_top_k
    return max(1, min(top_k, 25))


def _normalize_documents(raw_docs: object) -> List[str]:
    if raw_docs is None:
        return []
    if isinstance(raw_docs, str):
        return [raw_docs]
    if not isinstance(raw_docs, list):
        return [str(raw_docs)]

    docs: List[str] = []
    for doc in raw_docs:
        if isinstance(doc, dict):
            text = doc.get("text") or doc.get("content") or doc.get("document") or doc.get("body")
            docs.append(str(text if text is not None else doc))
        else:
            docs.append(str(doc))
    return docs


def _error_response(exc: Exception):
    return jsonify({"status": "error", "message": str(exc), "hipporag": rag.status()}), 503


@app.route("/health")
def health():
    return jsonify({"status": "ok", "hipporag": rag.status()})


@app.route("/rag/status")
def rag_status():
    return jsonify({"status": "success", "hipporag": rag.status()})


@app.route("/rag/index", methods=["POST"])
def rag_index():
    data = request.get_json(silent=True) or {}
    docs = _normalize_documents(data.get("docs") or data.get("documents") or data.get("text"))
    try:
        result = rag.index(docs)
    except Exception as exc:  # noqa: BLE001 - endpoint reports integration status
        return _error_response(exc)

    http_status = int(result.pop("http_status", 200))
    return jsonify(result), http_status


@app.route("/rag/retrieve", methods=["POST"])
def rag_retrieve():
    data = request.get_json(silent=True) or {}
    query = data.get("query") or data.get("text") or data.get("prompt")
    try:
        result = rag.retrieve(str(query or ""), _parse_top_k(data.get("top_k")))
    except Exception as exc:  # noqa: BLE001 - endpoint reports integration status
        return _error_response(exc)

    http_status = int(result.pop("http_status", 200))
    return jsonify(result), http_status


@app.route("/rag/qa", methods=["POST"])
def rag_qa():
    data = request.get_json(silent=True) or {}
    query = data.get("query") or data.get("text") or data.get("prompt")
    try:
        result = rag.qa(str(query or ""), _parse_top_k(data.get("top_k")))
    except Exception as exc:  # noqa: BLE001 - endpoint reports integration status
        return _error_response(exc)

    http_status = int(result.pop("http_status", 200))
    return jsonify(result), http_status


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5100")))

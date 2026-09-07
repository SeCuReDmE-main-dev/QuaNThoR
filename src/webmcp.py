"""Machine-readable WebMCP contract for the supervised QuaNThoR workbench.

The contract is intentionally transport neutral.  Flask owns authentication and
dispatch so importing this module never starts Mizar, HippoRAG, a browser, or an
external provider.
"""

from __future__ import annotations

from typing import Any


SCHEMA = "securedme.webmcp.v1"
PRODUCT_SLUG = "quanthor"
COMMON_TOOLS = ("securedme_companion_context", "securedme_qbit_plan_handoff")
EXECUTE_TOOLS = frozenset()

THEME = {
    "slug": PRODUCT_SLUG,
    "source": (
        "securedme-site/assets/landing/secureme.ca-product/education/QuaNThoR/desing/"
        "stitch_quanthor_landing_page_design_system/stitch_quanthor_landing_page_design_system/desing.md"
    ),
    "sourceStatus": "verified-product-stitch",
    "assets": {
        "dark": "quanthor dark landing.png",
        "light": "quanthor light landing.png",
    },
    "tokens": {
        "background": "#061026",
        "surface": "#111a3c",
        "primary": "#1f7aff",
        "secondary": "#6f42ff",
        "accent": "#d8a548",
        "text": "#f7fbff",
        "muted": "#7c8aa7",
        "focus": "#23b8ff",
    },
    "typography": {"display": "Georgia, serif", "body": "system-ui, sans-serif", "code": "monospace"},
    "fallback": "High-contrast system fonts, visible focus, no image-dependent meaning.",
}


def _object(properties: dict[str, Any] | None = None, required: list[str] | None = None) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties or {},
        "required": required or [],
        "additionalProperties": False,
    }


def _tool(name: str, mode: str, description: str, input_schema: dict[str, Any], handler: str) -> dict[str, Any]:
    parts = handler.split(" ", 1)
    mapped = {"kind": "http", "method": parts[0], "path": parts[1]} if len(parts) == 2 and parts[0] in {"GET", "POST", "PUT", "DELETE"} else {"kind": "local", "operation": handler.replace(" ", "_")}
    return {
        "name": name,
        "title": name.replace("_", " ").title(),
        "mode": mode,
        "description": description,
        "inputSchema": input_schema,
        "availability": "available",
        "outputSchema": {"type": "object", "required": ["status", "tool", "data", "secret_values_exposed"], "properties": {"status": {"const": "success"}, "tool": {"const": name}, "data": {}, "secret_values_exposed": {"const": False}}, "additionalProperties": False},
        "handler": mapped,
    }


TEXT = {"type": "string", "minLength": 1, "maxLength": 20000}
TOOLS = (
    _tool("quanthor_inspect_runtime", "READ", "Inspect a sanitized QuaNThoR runtime status.", _object(), "GET /health"),
    _tool("quanthor_inspect_formalizer", "READ", "Inspect the chamber formalizer boundary.", _object(), "GET /chamber/formalize/status"),
    _tool("quanthor_stage_formalization", "STAGE", "Stage a structured chamber candidate without admitting it.", _object({"text": TEXT}, ["text"]), "POST /chamber/formalize"),
    _tool("quanthor_stage_mizar_draft", "STAGE", "Create a conservative Mizar draft; a draft is not proof.", _object({"query": TEXT, "context": TEXT}, ["query"]), "POST /draft"),
    _tool("quanthor_proofread_text", "READ", "Apply the local school-safe proofreader.", _object({"text": TEXT}, ["text"]), "POST /proofread"),
    _tool("quanthor_inspect_rag_status", "READ", "Inspect optional HippoRAG availability without exposing configuration.", _object(), "GET /rag/status"),
    _tool("quanthor_retrieve_context", "READ", "Retrieve bounded optional context; context does not verify formality.", _object({"query": TEXT, "top_k": {"type": "integer", "minimum": 1, "maximum": 10}}, ["query"]), "POST /rag/retrieve"),
    _tool("quanthor_audit_neutrosophy", "READ", "Produce the operational I -> I_system^S -> D_f -> dF -> i_fractal audit.", _object({"text": TEXT, "context": TEXT}, ["text"]), "POST /audit/neutrosophy"),
    _tool("quanthor_audit_plithogenic_quaternion", "READ", "Produce a classical relation audit; not quantum computation or proof.", _object({"text": TEXT, "context": TEXT}, ["text"]), "POST /audit/plithogenic-quaternion"),
    _tool("quanthor_verify_mizar", "READ", "Run the non-mutating local Mizar verifier and inspect its result.", _object({"code": TEXT}, ["code"]), "POST /verify"),
    _tool("securedme_companion_context", "READ", "Read the sanitized Hero Book companion projection supplied by Gateway.", _object(), "Gateway session projection"),
    _tool("securedme_qbit_plan_handoff", "STAGE", "Prepare a Qbit return proposal without changing pedagogical progression.", _object({"mission_ref": {"type": "string", "minLength": 1, "maxLength": 120}, "artifact_refs": {"type": "array", "maxItems": 20, "items": {"type": "string", "maxLength": 160}}}, ["mission_ref"]), "local proposal only"),
)


def manifest() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "manifestVersion": "1.0.0",
        "product": {"slug": PRODUCT_SLUG, "name": "QuaNThoR", "status": "public-pre-alpha", "canonicalStateOwner": "algoquest", "applicationStateOwner": "quanthor", "pagePatterns": ["https://quanthor.securedme.ca/", "http://localhost:5050/"], "theme": THEME},
        "tools": list(TOOLS),
        "boundaries": {
            "authority": "Mizar is the formal check and qualified human review remains required.",
            "secrets": "Provider secrets, .env values and raw private evidence are forbidden.",
            "externalWrites": "The generic /route endpoint is not exposed through WebMCP; no provider or browser automation is available.",
            "heroProgression": "AlgoQuest alone owns Hero Book progression and evidence admission.",
        },
    }


def tool(name: str) -> dict[str, Any] | None:
    return next((item for item in TOOLS if item["name"] == name), None)

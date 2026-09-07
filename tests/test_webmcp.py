import importlib.util
import json
from pathlib import Path
import sys


MODULE_PATH = Path(__file__).parents[1] / "src" / "webmcp.py"
SPEC = importlib.util.spec_from_file_location("quanthor_webmcp", MODULE_PATH)
webmcp = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(webmcp)


def test_manifest_has_ten_product_tools_and_two_common_tools():
    payload = webmcp.manifest()
    names = [item["name"] for item in payload["tools"]]
    assert payload["schema"] == "securedme.webmcp.v1"
    assert len(payload["tools"]) == 12
    assert len([name for name in names if name.startswith("quanthor_")]) == 10
    assert set(webmcp.COMMON_TOOLS).issubset(names)
    assert "quanthor_route" not in names
    assert all(entry["inputSchema"]["additionalProperties"] is False for entry in payload["tools"])
    assert all(entry["outputSchema"]["type"] == "object" for entry in payload["tools"])
    assert all(entry["handler"]["kind"] for entry in payload["tools"])


def test_static_exports_match_runtime_and_evidence_gate_shape():
    root = Path(__file__).parents[1]
    assert json.loads((root / "webmcp" / "manifest.json").read_text(encoding="utf-8")) == webmcp.manifest()
    fixtures = json.loads((root / "webmcp" / "fixtures.json").read_text(encoding="utf-8"))
    assert set(fixtures) == {"tools", "journeys"}
    assert set(fixtures["tools"]) == {item["name"] for item in webmcp.manifest()["tools"]}
    assert len(fixtures["journeys"]) == 6


def test_verify_is_classified_as_non_mutating_read():
    descriptor = webmcp.tool("quanthor_verify_mizar")
    assert descriptor["mode"] == "READ"
    assert descriptor["availability"] == "available"


def test_theme_records_product_specific_stitch_source():
    assert "stitch_quanthor_landing_page_design_system" in webmcp.THEME["source"]
    assert webmcp.THEME["tokens"]["focus"] == "#23b8ff"


def test_discovery_is_public_invocation_closed_and_cors_exact():
    sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
    from app import app
    client = app.test_client()
    assert len(client.get("/webmcp/manifest").get_json()["tools"]) == 12
    rejected = client.post("/webmcp/invoke", json={"name": "quanthor_inspect_runtime", "arguments": {}})
    assert rejected.status_code == 503
    evil = client.get("/health", headers={"Origin": "https://evil.example"})
    assert "Access-Control-Allow-Origin" not in evil.headers
    health = client.get("/health").get_json()
    assert "proofreader_provider" not in health
    assert "service_url" not in health["hipporag"]
    assert "llm_model_name" not in health["hipporag"]

"""Flask entrypoint for the QuaNThoR verification service."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

try:
    from .ollama_proofreader import OllamaProofreader
    from .hipporag_service import HippoRAGService
    from .mizar_drafter import MizarDraftAssistant
    from .mizar_router import MizarWorkflowRouter
    from .mizar_translator import MizarTranslator
    from .neutrosophic_auditor import NeutrosophicAuditor
except ImportError:  # pragma: no cover - allows `python src/app.py`
    from ollama_proofreader import OllamaProofreader
    from hipporag_service import HippoRAGService
    from mizar_drafter import MizarDraftAssistant
    from mizar_router import MizarWorkflowRouter
    from mizar_translator import MizarTranslator
    from neutrosophic_auditor import NeutrosophicAuditor


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TIMEOUT_SECONDS = int(os.getenv("MIZAR_TIMEOUT_SECONDS", "60"))


def _resolve_mizar_share_dir() -> Path:
    """Return the directory that holds Mizar shared data."""

    candidates: List[Path] = []
    for raw in (
        os.getenv("MIZFILES"),
        os.getenv("MIZAR_SHARE"),
        str(PROJECT_ROOT / "mizar"),
        "/usr/local/share/mizar",
    ):
        if raw:
            candidates.append(Path(raw).expanduser())

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return candidates[0] if candidates else Path("/usr/local/share/mizar")


def _resolve_mizar_exec_dir(share_dir: Path) -> Path:
    """Return the directory that exposes the Mizar executables."""

    home = os.getenv("MIZAR_HOME")
    if home:
        home_path = Path(home).expanduser()
        for candidate in (home_path / "bin", home_path):
            if candidate.exists():
                return candidate

    for raw in (
        os.getenv("MIZAR_BIN"),
        "/usr/local/bin",
    ):
        if raw:
            candidate = Path(raw).expanduser()
            if candidate.exists():
                return candidate

    if share_dir.exists() and any((share_dir / name).exists() for name in ("verifier", "verifier.exe", "mizf", "mizf.bat")):
        return share_dir

    return share_dir


def _prepend_path(path_to_add: Path) -> None:
    current_parts = os.environ.get("PATH", "").split(os.pathsep)
    if str(path_to_add) not in current_parts:
        os.environ["PATH"] = str(path_to_add) + os.pathsep + os.environ.get("PATH", "")


def _resolve_command_candidates(exec_dir: Path) -> List[str]:
    if os.name == "nt":
        names = ["mizf.bat", "mizf", "verifier.exe", "verifier", "verifymain"]
    else:
        names = ["mizf", "verifier", "verifymain"]

    candidates: List[str] = []
    for name in names:
        candidates.append(str(exec_dir / name))
    candidates.extend(names)

    ordered: List[str] = []
    seen = set()
    for candidate in candidates:
        if candidate not in seen:
            ordered.append(candidate)
            seen.add(candidate)
    return ordered


def _resolve_mizar_command(exec_dir: Path) -> Optional[str]:
    for candidate in _resolve_command_candidates(exec_dir):
        if Path(candidate).exists() or shutil.which(candidate):
            return candidate
    return None


def _needs_shell(command: str) -> bool:
    return Path(command).suffix.lower() in {".bat", ".cmd", ".ps1"}


def _run_mizar(command: str, article_name: str, work_dir: Path, env: Dict[str, str]) -> subprocess.CompletedProcess[str]:
    if _needs_shell(command):
        cmdline = f'"{command}" {article_name}'
        return subprocess.run(  # noqa: S603 - command is selected from local binaries
            cmdline,
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT_SECONDS,
            env=env,
            cwd=str(work_dir),
            shell=True,
        )

    return subprocess.run(  # noqa: S603 - command is selected from local binaries
        [command, article_name],
        capture_output=True,
        text=True,
        timeout=DEFAULT_TIMEOUT_SECONDS,
        env=env,
        cwd=str(work_dir),
    )


def _parse_mizar_errors(output: str) -> List[Dict[str, object]]:
    errors: List[Dict[str, object]] = []
    code_messages: Dict[str, str] = {}

    for raw_line in output.splitlines():
        line = raw_line.strip()
        code_message_match = re.match(r"^(\d+):\s*(.+)$", line)
        if code_message_match:
            code_messages[code_message_match.group(1)] = code_message_match.group(2).strip()

    for raw_line in output.splitlines():
        line = raw_line.strip()

        verbose_match = re.search(r"Error at line (\d+), character (\d+):(.*)", line)
        if verbose_match:
            errors.append(
                {
                    "line": int(verbose_match.group(1)),
                    "character": int(verbose_match.group(2)),
                    "message": verbose_match.group(3).strip() or "Mizar reported an error.",
                }
            )
            continue

        compact_match = re.match(r"^(\d+)\s+(\d+)\s+(\d+)$", line)
        if compact_match:
            code = compact_match.group(3)
            errors.append(
                {
                    "line": int(compact_match.group(1)),
                    "character": int(compact_match.group(2)),
                    "message": code_messages.get(code, f"Mizar error code {code}"),
                }
            )

    unique_errors: List[Dict[str, object]] = []
    seen = set()
    for error in errors:
        key = (error["line"], error["character"], error["message"])
        if key not in seen:
            unique_errors.append(error)
            seen.add(key)

    return unique_errors


MIZAR_SHARE_DIR = _resolve_mizar_share_dir()
MIZAR_EXEC_DIR = _resolve_mizar_exec_dir(MIZAR_SHARE_DIR)
_prepend_path(MIZAR_EXEC_DIR)

os.environ.setdefault("MIZFILES", str(MIZAR_SHARE_DIR))
os.environ.setdefault("mizfiles", str(MIZAR_SHARE_DIR))

MIZAR_COMMAND = _resolve_mizar_command(MIZAR_EXEC_DIR)

app = Flask(__name__)
CORS(app)

translator = MizarTranslator()
proofreader = OllamaProofreader()
drafter = MizarDraftAssistant()
router = MizarWorkflowRouter()
rag = HippoRAGService()
auditor = NeutrosophicAuditor()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "mizar_available": bool(MIZAR_COMMAND),
            "mizar_command": MIZAR_COMMAND,
            "mizar_share_dir": str(MIZAR_SHARE_DIR),
            "mizar_exec_dir": str(MIZAR_EXEC_DIR),
            "ollama_base_url": proofreader.base_url,
            "ollama_model_configured": proofreader.configured_model,
            "ollama_model_resolved": proofreader.model,
            "ollama_model_structured_outputs": not proofreader.model.lower().endswith("cloud"),
            "mizar_draft_base_url": drafter.base_url,
            "mizar_draft_model_configured": drafter.configured_model,
            "mizar_draft_model_resolved": drafter.model,
            "mizar_draft_structured_outputs": not drafter.model.lower().endswith("cloud"),
            "router_base_url": router.base_url,
            "router_model_configured": router.configured_model,
            "router_model_resolved": router.model,
            "router_structured_outputs": not router.model.lower().endswith("cloud"),
            "hipporag": rag.status(),
            "neutrosophic_audit_available": True,
            "timeout_seconds": DEFAULT_TIMEOUT_SECONDS,
        }
    )


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


def _rag_error_response(exc: Exception):
    status = rag.status()
    return jsonify({"status": "error", "message": str(exc), "hipporag": status}), 503


def _audit_requested(data: Dict[str, object]) -> bool:
    return bool(data.get("audit_neutrosophy") or data.get("neutrosophic_audit"))


def _verify_mizar_code(mizar_code: str) -> Dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="quanthor-") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        article_path = temp_dir / "proof.miz"
        article_path.write_text(mizar_code, encoding="utf-8")

        env = os.environ.copy()
        env["MIZFILES"] = str(MIZAR_SHARE_DIR)
        env["mizfiles"] = str(MIZAR_SHARE_DIR)

        if MIZAR_EXEC_DIR.exists():
            current_path = env.get("PATH", "")
            if str(MIZAR_EXEC_DIR) not in current_path.split(os.pathsep):
                env["PATH"] = str(MIZAR_EXEC_DIR) + os.pathsep + current_path

        process = None
        attempted_commands: List[str] = []
        for candidate in _resolve_command_candidates(MIZAR_EXEC_DIR):
            attempted_commands.append(candidate)
            try:
                process = _run_mizar(candidate, article_path.name, temp_dir, env)
                break
            except FileNotFoundError:
                continue
            except subprocess.TimeoutExpired:
                return {"status": "error", "message": "Verification timed out.", "http_status": 500}
            except Exception:
                continue

        if process is None:
            return {
                "status": "error",
                "message": "Mizar verifier not found. Check the container image or the local Mizar installation.",
                "attempted_commands": attempted_commands,
                "http_status": 500,
            }

        output = f"{process.stdout or ''}{process.stderr or ''}"
        errors = _parse_mizar_errors(output)
        status = "success" if process.returncode == 0 and not errors else "failure"

        ai_enhanced_response = translator.create_ai_response(mizar_code, output)
        human_explanation = ai_enhanced_response["ai_assistance"]["human_explanation"]
        grammar_analysis = proofreader.proofread_text(human_explanation)

        enhanced_ai_assistant = ai_enhanced_response["ai_assistance"].copy()
        enhanced_ai_assistant["grammar_enhanced_explanation"] = grammar_analysis["improved_text"]
        enhanced_ai_assistant["grammar_suggestions"] = grammar_analysis["suggestions"]
        enhanced_ai_assistant["readability_score"] = grammar_analysis["readability_score"]
        enhanced_ai_assistant["grammar_score"] = grammar_analysis["grammar_score"]
        enhanced_ai_assistant["proofreading_provider"] = grammar_analysis.get("provider", "heuristic")

        return {
            "status": status,
            "return_code": process.returncode,
            "errors": errors,
            "raw_output": output,
            "attempted_commands": attempted_commands,
            "mizar_backend": {
                "command": MIZAR_COMMAND,
                "share_dir": str(MIZAR_SHARE_DIR),
                "exec_dir": str(MIZAR_EXEC_DIR),
            },
            "ai_assistant": enhanced_ai_assistant,
            "dual_layer_verification": {
                "mathematical_analysis": "Mizar formal verification",
                "grammatical_analysis": "Ollama proofreading",
                "combined_confidence": (
                    ai_enhanced_response["ai_assistance"]["confidence"] + grammar_analysis["grammar_score"]
                )
                / 2,
            },
            "powered_by": "QuaNThoR containerized verification system",
        }


@app.route("/verify", methods=["POST"])
def verify_mizar():
    data = request.get_json(silent=True) or {}
    if "code" not in data:
        return jsonify({"status": "error", "message": "JSON body with a 'code' field is required."}), 400

    result = _verify_mizar_code(str(data["code"]))
    http_status = int(result.pop("http_status", 200))
    return jsonify(result), http_status


@app.route("/draft", methods=["POST"])
def draft_mizar():
    data = request.get_json(silent=True) or {}
    query = data.get("query") or data.get("prompt")
    if not query or not str(query).strip():
        return jsonify({"status": "error", "message": "JSON body with a 'query' field is required."}), 400

    context = data.get("context") or ""
    draft = drafter.draft_from_query(str(query), str(context))

    return jsonify(
        {
            **draft,
            "powered_by": "QuaNThoR Mizar drafting assistant",
        }
    )


@app.route("/proofread", methods=["POST"])
def proofread_text():
    data = request.get_json(silent=True) or {}
    text = data.get("text") or data.get("query") or data.get("prompt")
    if not text or not str(text).strip():
        return jsonify({"status": "error", "message": "JSON body with a 'text' field is required."}), 400

    result = proofreader.proofread_text(str(text))
    return jsonify(
        {
            "status": "success",
            **result,
            "powered_by": "QuaNThoR proofreading assistant",
        }
    )


@app.route("/rag/status", methods=["GET"])
def rag_status():
    return jsonify({"status": "success", "hipporag": rag.status()})


@app.route("/rag/index", methods=["POST"])
def rag_index():
    data = request.get_json(silent=True) or {}
    docs = _normalize_documents(data.get("docs") or data.get("documents") or data.get("text"))
    try:
        result = rag.index(docs)
    except Exception as exc:  # noqa: BLE001 - endpoint returns integration status
        return _rag_error_response(exc)

    http_status = int(result.pop("http_status", 200))
    return jsonify(result), http_status


@app.route("/rag/retrieve", methods=["POST"])
def rag_retrieve():
    data = request.get_json(silent=True) or {}
    query = data.get("query") or data.get("text") or data.get("prompt")
    top_k = _parse_top_k(data.get("top_k"))
    try:
        result = rag.retrieve(str(query or ""), top_k)
    except Exception as exc:  # noqa: BLE001 - endpoint returns integration status
        return _rag_error_response(exc)

    http_status = int(result.pop("http_status", 200))
    return jsonify(result), http_status


@app.route("/rag/qa", methods=["POST"])
def rag_qa():
    data = request.get_json(silent=True) or {}
    query = data.get("query") or data.get("text") or data.get("prompt")
    top_k = _parse_top_k(data.get("top_k"))
    try:
        result = rag.qa(str(query or ""), top_k)
    except Exception as exc:  # noqa: BLE001 - endpoint returns integration status
        return _rag_error_response(exc)

    http_status = int(result.pop("http_status", 200))
    return jsonify(result), http_status


@app.route("/audit/neutrosophy", methods=["POST"])
def audit_neutrosophy():
    data = request.get_json(silent=True) or {}
    text = data.get("text") or data.get("query") or data.get("prompt") or data.get("code")
    if not text or not str(text).strip():
        return jsonify({"status": "error", "message": "JSON body with 'text', 'query', 'prompt', or 'code' is required."}), 400

    context = str(data.get("context") or "")
    route_decision = data.get("decision") if isinstance(data.get("decision"), dict) else router.route(str(text), context)
    tool_result = data.get("tool_result") if isinstance(data.get("tool_result"), dict) else {}
    audit = auditor.audit(
        str(text),
        context=context,
        route_decision=route_decision,
        rag_context=str(data.get("rag_context") or ""),
        rag_error=str(data["rag_error"]) if data.get("rag_error") else None,
        tool_result=tool_result,
    )
    return jsonify(audit)


@app.route("/route", methods=["POST"])
def route_request():
    data = request.get_json(silent=True) or {}
    text = data.get("text") or data.get("query") or data.get("prompt") or data.get("code")
    if not text or not str(text).strip():
        return jsonify({"status": "error", "message": "JSON body with 'text', 'query', 'prompt', or 'code' is required."}), 400

    context = str(data.get("context") or "")
    should_execute = bool(data.get("execute", True))
    decision = router.route(str(text), context)

    response: Dict[str, object] = {
        "status": "routed",
        "route": decision["route"],
        "decision": decision,
        "executed": False,
        "powered_by": "QuaNThoR workflow router",
    }

    if not should_execute:
        return jsonify(response)

    route = decision["route"]
    if route == "verify_mizar":
        result = _verify_mizar_code(str(text))
        http_status = int(result.pop("http_status", 200))
        response.update({"executed": True, "tool_result": result})
        if _audit_requested(data):
            response["neutrosophic_audit"] = auditor.audit(
                str(text),
                context=context,
                route_decision=decision,
                tool_result=result,
            )
        return jsonify(response), http_status

    if route == "draft_mizar":
        draft_context = context
        rag_context = ""
        rag_error = None
        if bool(data.get("use_rag", False)):
            try:
                rag_context = rag.retrieve_context(str(text), _parse_top_k(data.get("top_k")))
                if rag_context:
                    draft_context = f"{context}\n\nRetrieved Mizar context:\n{rag_context}".strip()
                    response["rag_context_used"] = True
                else:
                    response["rag_context_used"] = False
            except Exception as exc:  # noqa: BLE001 - RAG must not break core routing
                response["rag_context_used"] = False
                rag_error = str(exc)
                response["rag_context_error"] = rag_error

        draft_result = drafter.draft_from_query(str(text), draft_context)
        response.update({"executed": True, "tool_result": draft_result})
        if _audit_requested(data):
            response["neutrosophic_audit"] = auditor.audit(
                str(text),
                context=context,
                route_decision=decision,
                rag_context=rag_context,
                rag_error=rag_error,
                tool_result=draft_result,
            )
        return jsonify(response)

    if route == "proofread":
        proofread_result = proofreader.proofread_text(str(text))
        response.update({"executed": True, "tool_result": proofread_result})
        if _audit_requested(data):
            response["neutrosophic_audit"] = auditor.audit(
                str(text),
                context=context,
                route_decision=decision,
                tool_result=proofread_result,
            )
        return jsonify(response)

    response["status"] = "needs_clarification"
    response["clarifying_questions"] = decision.get("clarifying_questions", [])
    if _audit_requested(data):
        response["neutrosophic_audit"] = auditor.audit(str(text), context=context, route_decision=decision)
    return jsonify(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))

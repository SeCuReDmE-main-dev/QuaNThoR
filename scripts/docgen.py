#!/usr/bin/env python3
"""Generate and validate documentation artifacts for QuaNThoR without CI."""

from __future__ import annotations

import argparse
import ast
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
GENERATED_DIR = ROOT / "docs" / "generated"
SRC_DIR = ROOT / "src"


@dataclass
class Route:
    path: str
    methods: List[str]
    handler: str
    source: str
    summary: str


@dataclass
class EnvVar:
    name: str
    default: str | None
    source_file: str


def _read_source(file: Path) -> str:
    return file.read_text(encoding="utf-8")


def _safe_methods(value: Sequence[ast.expr]) -> List[str]:
    methods: List[str] = []
    for item in value:
        if isinstance(item, ast.Constant) and isinstance(item.value, str):
            methods.append(item.value.upper())
    return methods or ["GET"]


def _extract_text(node: ast.AST, source: str) -> str:
    return ast.get_source_segment(source, node) or ""


def _parse_routes() -> List[Route]:
    routes: List[Route] = []
    app_file = SRC_DIR / "app.py"
    source = _read_source(app_file)
    module = ast.parse(source)

    for function in [node for node in ast.walk(module) if isinstance(node, ast.FunctionDef)]:
        for decorator in function.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            if not isinstance(decorator.func, ast.Attribute) or decorator.func.attr != "route":
                continue
            if not isinstance(decorator.func.value, ast.Name) or decorator.func.value.id != "app":
                continue

            route_path: str | None = None
            methods: List[str] = ["GET"]

            if decorator.args and isinstance(decorator.args[0], ast.Constant) and isinstance(decorator.args[0].value, str):
                route_path = decorator.args[0].value
            for keyword in decorator.keywords:
                if keyword.arg == "methods" and isinstance(keyword.value, (ast.List, ast.Tuple)):
                    methods = _safe_methods(keyword.value.elts)

            if route_path is not None:
                summary = (ast.get_docstring(function) or "").splitlines()[0] if ast.get_docstring(function) else ""
                routes.append(
                    Route(
                        path=route_path,
                        methods=methods,
                        handler=function.name,
                        source=app_file.name,
                        summary=summary.strip(),
                    )
                )
    routes.sort(key=lambda route: route.path)
    return routes


def _extract_default(node: ast.AST, source: str) -> str:
    if isinstance(node, ast.Constant):
        return str(node.value)
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "os"
        and node.func.attr == "getenv"
    ):
        if len(node.args) > 1:
            return _extract_default(node.args[1], source)
    return _extract_text(node, source)


def _extract_env_vars() -> List[EnvVar]:
    envs: Dict[str, EnvVar] = {}

    for source_file in sorted(SRC_DIR.glob("*.py")):
        text = _read_source(source_file)
        module = ast.parse(text)
        for node in ast.walk(module):
            if (
                not isinstance(node, ast.Call)
                or not isinstance(node.func, ast.Attribute)
                or not isinstance(node.func.value, ast.Name)
                or node.func.value.id != "os"
                or node.func.attr != "getenv"
            ):
                continue

            if not node.args:
                continue
            if not isinstance(node.args[0], ast.Constant) or not isinstance(node.args[0].value, str):
                continue

            name = node.args[0].value
            default = _extract_default(node.args[1], text) if len(node.args) > 1 else None
            if name not in envs:
                envs[name] = EnvVar(name=name, default=default, source_file=source_file.name)
    return [envs[key] for key in sorted(envs)]


def _render_route_markdown(routes: List[Route]) -> str:
    lines = [
        "# Endpoints API auto-documentés",
        "",
        "Ce tableau est généré à partir des décorateurs Flask de `src/app.py`.",
        "",
        "| Route | Méthodes | Handler | Source | Résumé |",
        "|---|---|---|---|---|",
    ]

    for route in routes:
        method_list = ", ".join(route.methods)
        summary = route.summary.replace("|", "\\|") if route.summary else "Endpoint technique"
        lines.append(f"| `{route.path}` | {method_list} | `{route.handler}` | `{route.source}` | {summary} |")

    return "\n".join(lines) + "\n"


def _render_env_markdown(envs: List[EnvVar]) -> str:
    lines = [
        "# Variables d’environnement détectées",
        "",
        "La liste est extraite automatiquement via `os.getenv(...)` dans le code Python du dossier `src/`.",
        "",
        "| Variable | Default détecté | Fichier source |",
        "|---|---|---|",
    ]
    for env in envs:
        default = env.default if env.default is not None else ""
        lines.append(f"| `{env.name}` | {default} | `{env.source_file}` |")
    if not envs:
        lines.append("| Aucune |  |  |")
    lines.append("")
    return "\n".join(lines)


def _render_summary(routes: List[Route], envs: List[EnvVar]) -> str:
    return (
        "# Documentation automatique\n\n"
        "Cette section est régénérée par `python scripts/docgen.py generate`.\n\n"
        f"- Endpoints détectés : `{len(routes)}`\n"
        f"- Variables d'environnement détectées : `{len(envs)}`\n"
        "- Source de vérité : code Flask et appels `os.getenv` dans `src/`.\n"
        "- Publication recommandée : MkDocs Material (local), GitBook possible en édition externe.\n"
        "\n"
        "## Liens rapides\n\n"
        "- [Endpoints API auto-documentés](api-endpoints.md)\n"
        "- [Variables d'environnement](environment-variables.md)\n"
    )


def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def generate_docs(output_dir: Path) -> None:
    routes = _parse_routes()
    envs = _extract_env_vars()

    _write_file(output_dir / "api-endpoints.md", _render_route_markdown(routes))
    _write_file(output_dir / "environment-variables.md", _render_env_markdown(envs))
    _write_file(output_dir / "documentation-summary.md", _render_summary(routes, envs))


def _same_content(actual: Path, expected: Path) -> bool:
    if not actual.exists() or not expected.exists():
        return False
    return actual.read_text(encoding="utf-8") == expected.read_text(encoding="utf-8")


def _run_mkdocs(*args: str) -> int:
    return subprocess.run([sys.executable, "-m", "mkdocs", *args], cwd=ROOT, check=False).returncode


def _assert_mkdocs_available() -> None:
    try:
        import mkdocs  # type: ignore
    except Exception as exc:
        raise RuntimeError(
            "mkdocs is not installed. "
            "Run: python -m pip install -r requirements-docs.txt"
        ) from exc


def generate_check() -> int:
    generate_docs(GENERATED_DIR)
    with TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        tmp_out = tmp_root / "generated"
        generate_docs(tmp_out)

        expected = {
            "api-endpoints.md",
            "environment-variables.md",
            "documentation-summary.md",
        }
        ok = True
        for name in expected:
            expected_file = tmp_out / name
            current_file = GENERATED_DIR / name
            if not _same_content(expected_file, current_file):
                print(f"[docs-check] Drift détecté: {current_file}")
                ok = False
        if not ok:
            print("[docs-check] Exécutez: python scripts/docgen.py generate")
            return 1
    print("[docs-check] OK: documentation générée et synchronisée.")
    return 0


def run_build() -> int:
    _assert_mkdocs_available()
    generate_docs(GENERATED_DIR)
    return _run_mkdocs("build")


def run_serve(port: int = 8000) -> int:
    _assert_mkdocs_available()
    generate_docs(GENERATED_DIR)
    return _run_mkdocs("serve", "--dev-addr", f"0.0.0.0:{port}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Utility for local documentation automation.")
    parser.add_argument("command", choices=["generate", "check", "build", "serve"], nargs="?", default="generate")
    parser.add_argument("--docs-dir", default=str(GENERATED_DIR))
    parser.add_argument("--port", type=int, default=8000, help="Port utilisé par mkdocs serve")

    args = parser.parse_args()
    output_dir = Path(args.docs_dir)

    if args.command == "generate":
        generate_docs(output_dir)
        return 0
    if args.command == "check":
        return generate_check()
    if args.command == "build":
        return run_build()
    if args.command == "serve":
        return run_serve(port=args.port)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

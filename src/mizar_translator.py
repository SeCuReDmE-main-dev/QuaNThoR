"""Translate raw Mizar verifier output into student-friendly guidance."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Dict, List


class MizarTranslator:
    """Convert verifier output into clear, educational feedback."""

    def __init__(self) -> None:
        self.error_patterns = {
            "missing_binary": {
                "pattern": r"(can't find|not found|no such file or directory|unable to execute).*(verifier|mizf)",
                "human": "The Mizar verifier is not available in the current environment.",
                "suggestion": "Check that the container installed Mizar correctly and that the executable directory is on PATH.",
                "category": "system_error",
            },
            "unknown_symbol": {
                "pattern": r".*unknown.*symbol.*|.*unknown token.*",
                "human": "Unknown symbol: Mizar does not recognize one of the names in your proof.",
                "suggestion": "Check spelling, imported vocabularies, and whether the symbol belongs to the active environment.",
                "category": "syntax_error",
            },
            "syntax_error": {
                "pattern": r".*unexpected.*|.*illegal character.*|.*formula expected.*",
                "human": "Syntax error: the article is not written in the form Mizar expects.",
                "suggestion": "Check punctuation, line breaks, missing keywords, and the structure of the theorem or proof block.",
                "category": "syntax_error",
            },
            "type_error": {
                "pattern": r".*type.*mismatch.*",
                "human": "Type mismatch: two expressions do not belong to the same mathematical type.",
                "suggestion": "Verify that each object in the proof has the type required by the statement you are using.",
                "category": "logic_error",
            },
            "proof_incomplete": {
                "pattern": r".*proof.*incomplete.*|.*missing proof.*|.*proof not finished.*",
                "human": "Proof incomplete: the argument stops before the conclusion is justified.",
                "suggestion": "Add the missing proof steps or check whether a lemma should be cited explicitly.",
                "category": "proof_error",
            },
            "theorem_false": {
                "pattern": r".*false.*theorem.*|.*contradiction.*",
                "human": "The claim is likely false or inconsistent with the assumptions.",
                "suggestion": "Re-check the theorem statement and the assumptions you are using before trying to prove it.",
                "category": "logic_error",
            },
        }

        self.encouragement_messages = [
            "Every failed proof is still a useful step toward a correct one.",
            "Small corrections in formal proofs often reveal the real mathematical structure.",
            "Precision matters in Mizar, so each error message is a guide rather than a verdict.",
            "Mathematical proof writing is iterative: diagnose, refine, and verify again.",
        ]

    def translate_error(self, mizar_output: str) -> Dict:
        clean_output = (mizar_output or "").strip()
        lowered = clean_output.lower()

        translation = {
            "status": "needs_help",
            "raw_mizar": clean_output,
            "human_explanation": "I encountered output that needs interpretation.",
            "suggestion": "Review the verifier output and the article structure.",
            "category": "unknown",
            "encouragement": self.encouragement_messages[0],
            "confidence": 0.5,
        }

        for info in self.error_patterns.values():
            if re.search(info["pattern"], clean_output, re.IGNORECASE):
                translation.update(
                    {
                        "human_explanation": info["human"],
                        "suggestion": info["suggestion"],
                        "category": info["category"],
                        "confidence": 0.9,
                    }
                )
                break

        if self._looks_like_success(lowered):
            translation.update(
                {
                    "status": "success",
                    "human_explanation": "The proof verified successfully.",
                    "suggestion": "The formal argument is accepted by Mizar.",
                    "category": "success",
                    "encouragement": "The proof is in good shape.",
                    "confidence": 1.0,
                }
            )

        return translation

    def generate_learning_hints(self, error_category: str) -> List[str]:
        hints = {
            "syntax_error": [
                "Check punctuation and keyword order.",
                "Confirm the article structure: environ, begin, theorem, proof, end.",
                "Look for a missing semicolon or an extra token.",
            ],
            "logic_error": [
                "Ask whether the theorem is true under the stated assumptions.",
                "Break the argument into smaller lemmas if the step is too large.",
                "Verify that every cited result matches the type of the objects involved.",
            ],
            "proof_error": [
                "Every line in the proof should justify the next one.",
                "A missing citation is often enough to make a valid idea fail.",
                "Try to make each inference explicit before retrying the verifier.",
            ],
            "system_error": [
                "This is an installation or container problem, not a proof problem.",
                "Check the Mizar installation before debugging the article itself.",
                "Verify the container or host has the right executables and data files.",
            ],
        }

        return hints.get(
            error_category,
            [
                "Read the verifier output carefully and look for the first concrete failure.",
                "Use smaller lemmas to isolate the place where the reasoning breaks.",
                "Re-run the proof after each fix so the next error is easier to interpret.",
            ],
        )

    def create_ai_response(self, mizar_code: str, mizar_output: str) -> Dict:
        translation = self.translate_error(mizar_output)
        proof_analysis = self._analyze_proof_structure(mizar_code)

        return {
            "verification_result": {
                "status": translation["status"],
                "raw_output": mizar_output,
            },
            "ai_assistance": {
                "human_explanation": translation["human_explanation"],
                "suggestion": translation["suggestion"],
                "learning_hints": self.generate_learning_hints(translation["category"]),
                "encouragement": translation["encouragement"],
                "confidence": translation["confidence"],
            },
            "proof_analysis": proof_analysis,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "powered_by": "QuaNThoR educational assistant",
        }

    def _analyze_proof_structure(self, mizar_code: str) -> Dict:
        lines = mizar_code.splitlines()
        analysis = {
            "proof_length": len([line for line in lines if line.strip()]),
            "has_theorem": "theorem" in mizar_code.lower(),
            "has_proof": "proof" in mizar_code.lower(),
            "complexity": "beginner",
        }

        if analysis["proof_length"] > 10:
            analysis["complexity"] = "intermediate"
        if analysis["proof_length"] > 20:
            analysis["complexity"] = "advanced"

        return analysis

    def _looks_like_success(self, lowered_output: str) -> bool:
        success_markers = (
            "correct",
            "verified",
            "accepted",
            "time of mizaring",
            "no errors",
            "registration is correct",
        )
        return bool(lowered_output) and any(marker in lowered_output for marker in success_markers)


if __name__ == "__main__":
    translator = MizarTranslator()
    test_output = "Can't find C:\\Users\\jeans\\Desktop\\Mathematic verifier\\mizar\\verifier.exe"
    result = translator.translate_error(test_output)

    print("TRANSLATOR TEST")
    print(f"Human: {result['human_explanation']}")
    print(f"Suggestion: {result['suggestion']}")
    print(f"Encouragement: {result['encouragement']}")


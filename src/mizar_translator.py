# 🌟 MIZAR LANGUAGE TRANSLATOR 🌟
# Transform cryptic Mizar errors into human-readable guidance
# Gift to all children learning mathematics

import re
import json
from typing import Dict, List, Tuple

class MizarTranslator:
    """
    The heart of AI-enhanced mathematical verification.
    Converts Mizar's cryptic language into human understanding.
    """
    
    def __init__(self):
        self.error_patterns = {
            # Common Mizar error patterns and their human translations
            "verifier.exe": {
                "pattern": r"Can't find.*verifier\.exe",
                "human": "🔧 System Issue: The Mizar verification engine is not properly configured.",
                "suggestion": "This is a setup problem, not an error in your proof. The system administrator needs to fix the installation.",
                "category": "system_error"
            },
            "unknown_symbol": {
                "pattern": r".*unknown.*symbol.*",
                "human": "❓ Unknown Symbol: You're using a symbol that Mizar doesn't recognize.",
                "suggestion": "Check your spelling, or you might need to import the right vocabulary or definitions.",
                "category": "syntax_error"
            },
            "type_error": {
                "pattern": r".*type.*mismatch.*",
                "human": "🎯 Type Mismatch: The types don't match in your mathematical expression.",
                "suggestion": "Make sure you're combining objects of compatible types (like adding numbers to numbers, not numbers to sets).",
                "category": "logic_error"
            },
            "proof_incomplete": {
                "pattern": r".*proof.*incomplete.*",
                "human": "📝 Proof Incomplete: Your proof doesn't fully justify the conclusion.",
                "suggestion": "Add more steps to your proof, or check if you're missing some logical connections.",
                "category": "proof_error"
            },
            "theorem_false": {
                "pattern": r".*false.*theorem.*|.*contradiction.*",
                "human": "⚠️ False Statement: You're trying to prove something that isn't true.",
                "suggestion": "Check your theorem statement - there might be a logical error in what you're claiming.",
                "category": "logic_error"
            }
        }
        
        self.encouragement_messages = [
            "🌟 You're doing great! Every mathematician makes errors while learning.",
            "💪 Keep going! Each error teaches you something valuable.",
            "🎓 This is how mathematical thinking develops - through careful reasoning.",
            "✨ Remember: even the greatest mathematicians needed practice!"
        ]
    
    def translate_error(self, mizar_output: str) -> Dict:
        """
        Transform raw Mizar output into human-friendly guidance.
        
        Args:
            mizar_output: Raw text from Mizar verifier
            
        Returns:
            Dictionary with human translation, suggestions, and encouragement
        """
        
        # Clean the output
        clean_output = mizar_output.strip()
        
        # Default response for unknown errors
        translation = {
            "status": "needs_help",
            "raw_mizar": clean_output,
            "human_explanation": "🤔 I encountered something I haven't seen before.",
            "suggestion": "This might be a new type of error. Let's learn together!",
            "category": "unknown",
            "encouragement": self.encouragement_messages[0],
            "confidence": 0.5
        }
        
        # Check against known patterns
        for error_type, info in self.error_patterns.items():
            if re.search(info["pattern"], clean_output, re.IGNORECASE):
                translation.update({
                    "human_explanation": info["human"],
                    "suggestion": info["suggestion"], 
                    "category": info["category"],
                    "confidence": 0.9
                })
                break
        
        # Special handling for successful verifications
        if "correct" in clean_output.lower() or not clean_output or len(clean_output.strip()) == 0:
            translation.update({
                "status": "success",
                "human_explanation": "🎉 Perfect! Your proof is mathematically correct!",
                "suggestion": "Great work! Your logical reasoning is sound.",
                "category": "success",
                "encouragement": "🏆 Excellent mathematical thinking!",
                "confidence": 1.0
            })
        
        return translation
    
    def generate_learning_hints(self, error_category: str) -> List[str]:
        """
        Provide educational hints based on error type.
        
        Args:
            error_category: Category of the mathematical error
            
        Returns:
            List of learning hints and tips
        """
        
        hints = {
            "syntax_error": [
                "💡 Check your spelling - Mizar is case-sensitive",
                "📚 Make sure you've included the right 'vocabularies' at the top",
                "🔍 Look for missing semicolons or incorrect punctuation"
            ],
            "logic_error": [
                "🧠 Think about whether your statement is always true",
                "🔗 Check if your logical connections are valid",
                "📋 Try breaking complex statements into smaller parts"
            ],
            "proof_error": [
                "📝 Each step in your proof should follow logically from previous steps",
                "🎯 Make sure you're proving exactly what the theorem states",
                "🔍 Check if you need additional lemmas or definitions"
            ],
            "system_error": [
                "⚙️ This isn't a problem with your mathematics",
                "🔧 The system needs technical attention",
                "💪 Keep working on your proofs while this gets fixed"
            ]
        }
        
        return hints.get(error_category, [
            "🌟 Every error is a learning opportunity",
            "📚 Mathematics is about precision and careful thinking",
            "💪 Keep practicing - you're building important skills"
        ])

    def create_ai_response(self, mizar_code: str, mizar_output: str) -> Dict:
        """
        Create a complete AI-enhanced response combining verification with human guidance.
        
        Args:
            mizar_code: The mathematical proof code
            mizar_output: Raw Mizar verification output
            
        Returns:
            Complete AI response with translation, hints, and encouragement
        """
        
        translation = self.translate_error(mizar_output)
        hints = self.generate_learning_hints(translation["category"])
        
        # Analyze the mathematical content
        proof_analysis = self._analyze_proof_structure(mizar_code)
        
        return {
            "verification_result": {
                "status": translation["status"],
                "raw_output": mizar_output
            },
            "ai_assistance": {
                "human_explanation": translation["human_explanation"],
                "suggestion": translation["suggestion"],
                "learning_hints": hints,
                "encouragement": translation["encouragement"],
                "confidence": translation["confidence"]
            },
            "proof_analysis": proof_analysis,
            "timestamp": "2024",  # Would use actual timestamp
            "powered_by": "❤️ Built with love for mathematical education"
        }
    
    def _analyze_proof_structure(self, mizar_code: str) -> Dict:
        """
        Analyze the structure of the mathematical proof.
        
        Args:
            mizar_code: The proof code to analyze
            
        Returns:
            Analysis of proof structure and complexity
        """
        
        lines = mizar_code.split('\n')
        
        analysis = {
            "proof_length": len([l for l in lines if l.strip()]),
            "has_theorem": "theorem" in mizar_code.lower(),
            "has_proof": "proof" in mizar_code.lower(),
            "complexity": "beginner"  # Could be enhanced with real analysis
        }
        
        # Simple complexity assessment
        if analysis["proof_length"] > 10:
            analysis["complexity"] = "intermediate"
        if analysis["proof_length"] > 20:
            analysis["complexity"] = "advanced"
            
        return analysis


# Test the translator
if __name__ == "__main__":
    translator = MizarTranslator()
    
    # Test with our current error
    test_output = "Can't find C:\\Users\\jeans\\Desktop\\Mathematic verifier\\mizar\\verifier.exe"
    result = translator.translate_error(test_output)
    
    print("🧪 TRANSLATOR TEST:")
    print(f"Human: {result['human_explanation']}")
    print(f"Suggestion: {result['suggestion']}")
    print(f"Encouragement: {result['encouragement']}")
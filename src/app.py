# 1. Import necessary libraries
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import subprocess
import tempfile
import os
import re # We use this to find the errors in the text
from mizar_translator import MizarTranslator
from google_proofreader import GoogleProofreader

# Set up Mizar environment variables for local installation
import os
# Go up to parent directory of project to find mizar folder
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
parent_dir = os.path.dirname(project_root)
mizar_path = os.path.join(parent_dir, 'mizar')
os.environ['MIZFILES'] = mizar_path
os.environ['PATH'] = os.environ.get('PATH', '') + f';{mizar_path}'

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Initialize our AI systems
translator = MizarTranslator()
proofreader = GoogleProofreader()

# 2. The main page route stays the same
@app.route('/')
def index():
    return render_template('index.html')

# 3. This is our new, professional API endpoint
@app.route('/verify', methods=['POST'])
def verify_mizar():
    # --- CHANGE 1: We get data from a JSON request body ---
    data = request.get_json()
    if not data or 'code' not in data:
        return jsonify({"status": "error", "message": "Invalid request. JSON with 'code' key required."}), 400
    mizar_code = data['code']
    # --- END CHANGE 1 ---

    # We use a temporary file to safely handle the user's code
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.miz') as temp_file:
        temp_file.write(mizar_code)
        temp_filename = temp_file.name

    try:
        # Try different Mizar commands based on what's available
        local_mizf = os.path.join(mizar_path, 'mizf.bat')
        mizar_commands = [local_mizf, 'mizf', '/mizar/verifymain', '/usr/local/bin/mizf']
        process = None
        
        for cmd in mizar_commands:
            try:
                process = subprocess.run(
                    [cmd, temp_filename],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                break
            except FileNotFoundError:
                continue
        
        if process is None:
            return jsonify({"status": "error", "message": "Mizar verifier not found. Please ensure Mizar is installed."}), 500
            
        output = process.stdout + process.stderr

        # --- CHANGE 2: We parse the output and create a structured JSON response ---
        errors = []
        # Mizar errors often look like: "Error at line X, character Y: [message]"
        # This regular expression helps us find and capture those details.
        error_pattern = re.compile(r"Error at line (\d+), character (\d+):(.*)")

        for line in output.splitlines():
            match = error_pattern.search(line)
            if match:
                errors.append({
                    "line": int(match.group(1)),
                    "character": int(match.group(2)),
                    "message": match.group(3).strip()
                })

        # Determine the final status based on what we found
        if not errors and "Correct" in output:
            status = "success"
        else:
            status = "failure"

        # PHASE 3: AI-Enhanced Response with Human Translation
        ai_enhanced_response = translator.create_ai_response(mizar_code, output)
        
        # PHASE 4: Google Proofreader Integration - Dual Layer Verification
        human_explanation = ai_enhanced_response["ai_assistance"]["human_explanation"]
        grammar_analysis = proofreader.proofread_text(human_explanation)
        
        # Enhance AI assistant with grammar improvements
        enhanced_ai_assistant = ai_enhanced_response["ai_assistance"].copy()
        enhanced_ai_assistant["grammar_enhanced_explanation"] = grammar_analysis["improved_text"]
        enhanced_ai_assistant["grammar_suggestions"] = grammar_analysis["suggestions"]
        enhanced_ai_assistant["readability_score"] = grammar_analysis["readability_score"]
        enhanced_ai_assistant["grammar_score"] = grammar_analysis["grammar_score"]
        
        # Combine traditional verification with dual-layer AI assistance
        response_data = {
            "status": status,
            "errors": errors,
            "raw_output": output,
            "ai_assistant": enhanced_ai_assistant,
            "dual_layer_verification": {
                "mathematical_analysis": "Mizar + AI Translation",
                "grammatical_analysis": "Google Proofreader API",
                "combined_confidence": (ai_enhanced_response["ai_assistance"]["confidence"] + grammar_analysis["grammar_score"]) / 2
            },
            "powered_by": "QuaNTecH Dual-Layer AI Mathematical Verification System"
        }
        return jsonify(response_data)
        # --- END CHANGE 2 ---

    except subprocess.TimeoutExpired:
        return jsonify({"status": "error", "message": "Verification timed out."}), 500
    finally:
        # Always clean up the temporary file
        os.remove(temp_filename)

# This part allows us to run the server directly with "python app.py"
if __name__ == '__main__':
    # We will use port 5000 as it is standard for Flask development
    app.run(host='0.0.0.0', port=5000)
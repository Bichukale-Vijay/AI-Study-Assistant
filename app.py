from flask import Flask, request, jsonify, render_template
from google import genai
import time
import os
import logging
import uuid
import pyttsx3
import json
import re

# ✅ NEW: SymPy for advanced solving
from sympy import symbols, solve, sympify

# existing
from multi_level_ai import generate_multi_level_response

app = Flask(__name__)

# Ensure folders exist
os.makedirs("static/audio", exist_ok=True)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# API Key
API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_KEY_HERE")

# AI client
client = genai.Client(api_key=API_KEY)

# =========================================================
# ✅ Load demo QA file
# =========================================================
DEMO_FILE = "demo_qa.json"
demo_qa = []

try:
    with open(DEMO_FILE, "r", encoding="utf-8") as f:
        demo_qa = json.load(f)
    logging.info(f"Loaded {len(demo_qa)} demo questions from {DEMO_FILE}.")
except Exception as e:
    logging.error(f"Failed to load demo QA file: {e}")

# =========================================================
# ✅ TEXT-TO-SPEECH
# =========================================================
def generate_audio(text):
    try:
        if not text:
            return None

        filename = f"static/audio/{uuid.uuid4()}.mp3"
        engine = pyttsx3.init()
        engine.setProperty('rate', 180)
        engine.setProperty('volume', 1.0)
        engine.save_to_file(text[:400], filename)
        engine.runAndWait()
        engine.stop()
        return filename
    except Exception as e:
        logging.error(f"TTS Error: {e}")
        return None

# =========================================================
# ✅ AI function
# =========================================================
def ask_ai(question):
    try:
        question = str(question).strip()
        if not question:
            return "Please enter a valid question."

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[question]
        )

        return response.text.strip() if response.text else "AI returned empty response."

    except Exception as e:
        logging.error(f"AI Error: {e}")
        return f"AI Error: {str(e)}"

# =========================================================
# ✅ Demo QA matching
# =========================================================
STOPWORDS = {
    "the","is","a","an","of","in","on","and","or",
    "for","to","with","as","by","at","from"
}

def clean_and_split(text):
    words = re.findall(r'\b\w+\b', text.lower())
    return [w for w in words if w not in STOPWORDS]

def find_demo_answer(user_question, threshold=1):
    user_keywords = set(clean_and_split(user_question))
    best_match = None
    max_overlap = 0

    for qa in demo_qa:
        demo_keywords = set(clean_and_split(qa.get("question", "")))
        overlap = len(user_keywords & demo_keywords)

        if overlap > max_overlap and overlap >= threshold:
            max_overlap = overlap
            best_match = {
                "simple": qa.get("simple", ""),
                "medium": qa.get("medium", ""),
                "deep": qa.get("deep", "")
            }

    return best_match

# =========================================================
# ✅ WHITEBOARD SOLVER (UPGRADED WITH SYMPY)
# =========================================================
def solve_equation_steps(equation):
    try:
        x = symbols('x')

        # Convert equation → standard form
        eq = equation.replace("^", "**")  # support x^2 input
        eq = eq.replace("=", "-(") + ")"

        expr = sympify(eq)
        solutions = solve(expr, x)

        steps = []
        steps.append(f"Given: {equation}")
        steps.append("Convert to standard form:")
        steps.append(f"{expr} = 0")
        steps.append("Solve:")

        if not solutions:
            steps.append("No solution found")

        for sol in solutions:
            steps.append(f"x = {sol}")

        return {
            "steps": steps,
            "solution": [str(s) for s in solutions]
        }

    except Exception as e:
        logging.error(f"SymPy Solver Error: {e}")
        return {"error": "Unable to solve this equation"}

# =========================================================
# ✅ ROUTES
# =========================================================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"answer": "No data received", "time": "0.00"})

        question = str(data.get("question", "")).strip()
        enable_audio = data.get("audio", False)

        if question == "":
            return jsonify({"answer": "Please enter a question", "time": "0.00"})

        start = time.perf_counter()

        demo_answer = find_demo_answer(question)
        if demo_answer:
            answer = demo_answer.get("simple", "")
        else:
            answer = ask_ai(question)

        audio_file = generate_audio(answer) if enable_audio else None
        end = time.perf_counter()

        return jsonify({
            "answer": answer,
            "audio": audio_file,
            "time": f"{end-start:.2f}",
            "source": "demo" if demo_answer else "api"
        })

    except Exception as e:
        logging.error(f"/ask error: {e}")
        return jsonify({"answer": f"Server error: {str(e)}", "time": "0.00"})

@app.route("/multi-explain", methods=["POST"])
def multi_explain():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "No data received"}), 400

        question = str(data.get("question", "")).strip()
        enable_audio = data.get("audio", False)

        if question == "":
            return jsonify({"error": "Question is required"}), 400

        start = time.perf_counter()

        demo_answer = find_demo_answer(question)
        if demo_answer:
            responses = demo_answer
        else:
            responses = generate_multi_level_response(ask_ai, question)

        audio_data = {}
        if enable_audio:
            audio_data = {
                "simple_audio": generate_audio(responses.get("simple", "")),
                "medium_audio": generate_audio(responses.get("medium", "")),
                "deep_audio": generate_audio(responses.get("deep", ""))
            }

        end = time.perf_counter()

        return jsonify({
            "simple": responses.get("simple", ""),
            "medium": responses.get("medium", ""),
            "deep": responses.get("deep", ""),
            **audio_data,
            "time": f"{end-start:.2f}",
            "source": "demo" if demo_answer else "api"
        })

    except Exception as e:
        logging.error(f"Multi Explain Error: {e}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# =========================================================
# ✅ WHITEBOARD API (SYMPY POWERED)
# =========================================================
@app.route("/solve-whiteboard", methods=["POST"])
def whiteboard_solver():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "No data received"}), 400

        question = str(data.get("question", "")).strip()

        if question == "":
            return jsonify({"error": "Question is required"}), 400

        start = time.perf_counter()

        result = solve_equation_steps(question)

        end = time.perf_counter()

        return jsonify({
            "steps": result.get("steps", []),
            "solution": result.get("solution"),
            "error": result.get("error"),
            "time": f"{end-start:.2f}"
        })

    except Exception as e:
        logging.error(f"Whiteboard API Error: {e}")
        return jsonify({"error": str(e)}), 500

# =========================================================
# ✅ AUDIO API
# =========================================================
@app.route("/generate-audio", methods=["POST"])
def generate_audio_api():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "No data received"}), 400

        text = str(data.get("text", "")).strip()
        if text == "":
            return jsonify({"error": "Text is required"}), 400

        audio_file = generate_audio(text)
        return jsonify({"audio": audio_file})

    except Exception as e:
        logging.error(f"Audio API Error: {e}")
        return jsonify({"error": str(e)}), 500

# =========================================================
# ✅ RUN
# =========================================================
if __name__ == "__main__":
    app.run(debug=True)
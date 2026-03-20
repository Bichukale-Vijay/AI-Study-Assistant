from flask import Flask, request, jsonify, render_template
from google import genai
import time
import os
import logging

# ✅ NEW IMPORT (your new feature)
from multi_level_ai import generate_multi_level_response

app = Flask(__name__)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ✅ API Key (UNCHANGED LOGIC)
API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE")

# AI client
client = genai.Client(api_key=API_KEY)


# ✅ AI function (UNCHANGED LOGIC, only safety added)
def ask_ai(question):
    try:
        question = str(question).strip()  # safe handling

        if not question:
            return "Please enter a valid question."

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[question]
        )

        if hasattr(response, "text") and response.text:
            return response.text.strip()

        return "AI returned empty response."

    except Exception as e:
        logging.error(f"AI Error: {e}")
        return f"AI Error: {str(e)}"


@app.route("/")
def home():
    return render_template("index.html")


# ✅ ASK API (UNCHANGED LOGIC, safer JSON handling)
@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json(silent=True)  # prevents crash

        if not data:
            return jsonify({"answer": "No data received", "time": "0.00"})

        question = str(data.get("question", "")).strip()

        if question == "":
            return jsonify({"answer": "Please enter a question", "time": "0.00"})

        start = time.perf_counter()

        answer = ask_ai(question)

        end = time.perf_counter()

        return jsonify({
            "answer": answer,
            "time": f"{end-start:.2f}"
        })

    except Exception as e:
        logging.error(f"/ask error: {e}")
        return jsonify({
            "answer": f"Server error: {str(e)}",
            "time": "0.00"
        })


# =========================================================
# ✅ MULTI-LEVEL EXPLANATION (UNCHANGED LOGIC)
# =========================================================
@app.route("/multi-explain", methods=["POST"])
def multi_explain():
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "No data received"}), 400

        question = str(data.get("question", "")).strip()

        if question == "":
            return jsonify({"error": "Question is required"}), 400

        start = time.perf_counter()

        # ✅ SAME LOGIC (no change)
        responses = generate_multi_level_response(ask_ai, question)

        end = time.perf_counter()

        return jsonify({
            "simple": responses.get("simple", ""),
            "medium": responses.get("medium", ""),
            "deep": responses.get("deep", ""),
            "time": f"{end-start:.2f}"
        })

    except Exception as e:
        logging.error(f"Multi Explain Error: {e}")
        return jsonify({
            "error": f"Server error: {str(e)}"
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
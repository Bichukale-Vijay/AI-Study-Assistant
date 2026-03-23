from flask import Flask, request, jsonify, render_template
import openai
import time
import os
import logging
import uuid
import pyttsx3  # offline TTS replacement

# existing
from multi_level_ai import generate_multi_level_response

app = Flask(__name__)

# Ensure folder exists
os.makedirs("static/audio", exist_ok=True)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
openai.api_key = OPENAI_API_KEY

# =========================================================
# ✅ TEXT-TO-SPEECH (pyttsx3 offline, per-request engine)
# =========================================================
def generate_audio(text):
    try:
        if not text:
            return None

        os.makedirs("static/audio", exist_ok=True)
        filename = f"static/audio/{uuid.uuid4()}.mp3"

        # Use a temporary pyttsx3 engine per request
        engine = pyttsx3.init()
        engine.setProperty('rate', 180)
        engine.setProperty('volume', 1.0)
        engine.save_to_file(text[:400], filename)  # short text for faster generation
        engine.runAndWait()
        engine.stop()

        return filename

    except Exception as e:
        logging.error(f"TTS Error: {e}")
        return None

# =========================================================
# ✅ AI function using OpenAI
# =========================================================
def ask_ai(question):
    try:
        question = str(question).strip()
        if not question:
            return "Please enter a valid question."

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": question}],
            max_tokens=500,
            temperature=0.7
        )

        if response and response.choices:
            return response.choices[0].message['content'].strip()

        return "AI returned empty response."

    except Exception as e:
        logging.error(f"AI Error: {e}")
        return f"AI Error: {str(e)}"

@app.route("/")
def home():
    return render_template("index.html")

# =========================================================
# ✅ ASK API (NOW WITH OPTIONAL AUDIO)
# =========================================================
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
        answer = ask_ai(question)

        audio_file = generate_audio(answer) if enable_audio else None
        end = time.perf_counter()

        return jsonify({
            "answer": answer,
            "audio": audio_file,
            "time": f"{end-start:.2f}"
        })

    except Exception as e:
        logging.error(f"/ask error: {e}")
        return jsonify({"answer": f"Server error: {str(e)}", "time": "0.00"})

# =========================================================
# ✅ MULTI-LEVEL (NOW WITH AUDIO OPTION)
# =========================================================
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
            "time": f"{end-start:.2f}"
        })

    except Exception as e:
        logging.error(f"Multi Explain Error: {e}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# =========================================================
# ✅ GENERATE AUDIO ON CLICK
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

if __name__ == "__main__":
    app.run(debug=True)
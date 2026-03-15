from flask import Flask, request, jsonify, render_template
from google import genai
import time
import os
import logging

app = Flask(__name__)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# API Key (env variable supported)
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCbHRE0g_5gcL0732QS0ENXwSqhYRYRpsU")

# AI client
client = genai.Client(api_key=API_KEY)


# AI function (LOGIC SAME)
def ask_ai(question):
    try:
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


# ASK API (LOGIC SAME)
@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"answer": "No data received", "time": "0.00"})

        question = data.get("question", "")

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
        logging.error(e)
        return jsonify({
            "answer": f"Server error: {str(e)}",
            "time": "0.00"
        })


if __name__ == "__main__":
    app.run(debug=True)
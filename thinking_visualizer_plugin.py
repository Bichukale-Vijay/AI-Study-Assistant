import re
from flask import request, jsonify

# =========================================================
# ✅ Flow Generator (same logic)
# =========================================================
def generate_thinking_flow(answer_text):
    try:
        if not answer_text:
            return {"nodes": [], "edges": []}

        sentences = re.split(r'[.?!]', answer_text)

        nodes = []
        edges = []

        node_id = 1
        prev_id = None

        for sentence in sentences:
            sentence = sentence.strip()

            if len(sentence) < 3:
                continue

            words = sentence.split()
            label = " ".join(words[:5])

            nodes.append({
                "id": node_id,
                "label": label,
                "full_text": sentence
            })

            if prev_id is not None:
                edges.append({
                    "from": prev_id,
                    "to": node_id
                })

            prev_id = node_id
            node_id += 1

        return {"nodes": nodes, "edges": edges}

    except Exception:
        return {"nodes": [], "edges": []}


# =========================================================
# ✅ Plugin Hook (NO backend modification needed)
# =========================================================
def init_thinking_visualizer(app):

    @app.after_request
    def attach_flow(response):
        try:
            # Only modify /ask API response
            if request.path == "/ask" and response.is_json:
                data = response.get_json()

                if data and "answer" in data:
                    flow = generate_thinking_flow(data["answer"])
                    data["flow"] = flow

                    response.set_data(jsonify(data).get_data())

        except Exception:
            pass

        return response
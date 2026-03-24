import re

# =========================================================
# ✅ Convert answer → thinking flow (nodes + edges)
# =========================================================
def generate_thinking_flow(answer_text):
    try:
        if not answer_text:
            return {"nodes": [], "edges": []}

        # Split into sentences
        sentences = re.split(r'[.?!]', answer_text)

        nodes = []
        edges = []

        node_id = 1
        prev_id = None

        for sentence in sentences:
            sentence = sentence.strip()

            if len(sentence) < 3:
                continue

            # Extract short label (first 4–5 words)
            words = sentence.split()
            label = " ".join(words[:5])

            node = {
                "id": node_id,
                "label": label,
                "full_text": sentence
            }

            nodes.append(node)

            # Create edge
            if prev_id is not None:
                edges.append({
                    "from": prev_id,
                    "to": node_id
                })

            prev_id = node_id
            node_id += 1

        return {
            "nodes": nodes,
            "edges": edges
        }

    except Exception:
        return {"nodes": [], "edges": []}
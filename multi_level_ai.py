def build_prompt(question, level):
    # safety: ensure question is string
    question = str(question).strip()

    if not question:
        return "Please provide a valid question."

    if level == "simple":
        return f"Explain in very simple beginner-friendly terms:\n{question}"
    
    elif level == "medium":
        return f"Explain in an exam-ready format (definition + key points):\n{question}"
    
    elif level == "deep":
        return f"Explain in deep technical detail including working, examples, and edge cases:\n{question}"
    
    return question


def generate_multi_level_response(ai_model, question):
    responses = {}

    try:
        responses["simple"] = ai_model(build_prompt(question, "simple"))
    except Exception as e:
        responses["simple"] = f"Error: {str(e)}"

    try:
        responses["medium"] = ai_model(build_prompt(question, "medium"))
    except Exception as e:
        responses["medium"] = f"Error: {str(e)}"

    try:
        responses["deep"] = ai_model(build_prompt(question, "deep"))
    except Exception as e:
        responses["deep"] = f"Error: {str(e)}"

    return responses
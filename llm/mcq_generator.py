import json
import re
from llm.groq_client import query_groq

def generate_mcqs(context: str, num_questions: int = 3):
    """
    Generates MCQs based on the provided context using Groq.
    Returns: List of dicts [{"question": ..., "options": [...], "answer": ...}]
    """
    if not context or len(context.strip()) < 50:
        return []

    prompt = f"""
    Based on the following context, generate {num_questions} Multiple Choice Questions (MCQs).
    Each question should have 4 options and 1 correct answer.
    
    Output the result ONLY as a JSON list of objects with the following keys:
    "question": the question text
    "options": a list of 4 options
    "answer": the correct option (must match one of the options exactly)
    
    CONTEXT:
    {context}
    
    JSON Output:"""

    # Using Llama 3.1 8B for fast and reliable JSON generation
    response_text, error = query_groq("llama-3.1-8b-instant", prompt)
    if error:
        print(f"MCQ Generation Error: {error}")
        return []

    try:
        # Try to find JSON block
        json_match = re.search(r"(\[.*\])", response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        return json.loads(response_text)
    except Exception as e:
        print(f"JSON Parsing Error in MCQ: {e}")
        # Log the raw text for debugging if parsing fails
        print(f"Raw response: {response_text[:200]}...")
        return []

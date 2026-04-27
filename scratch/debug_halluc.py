import sys
import os
# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.scorer import check_hallucination
from llm.gemini_client import query_gemini

def debug_hallucination():
    context = "Photosynthesis is the process by which green plants and some other organisms use sunlight to synthesize nutrients from carbon dioxide and water."
    response = "Plants use sunlight to make food."
    
    print("Testing check_hallucination...")
    score = check_hallucination(response, context)
    print(f"Score: {score}")

    # Directly check Gemini output
    prompt = f"Evaluate if the ANSWER is grounded in CONTEXT. Return only a number 0-1.\nCONTEXT: {context}\nANSWER: {response}\nSCORE:"
    print("\nQuerying Gemini directly...")
    res, err = query_gemini(prompt)
    if err:
        print(f"Error: {err}")
    else:
        print(f"Raw Gemini Response: '{res}'")

if __name__ == "__main__":
    debug_hallucination()

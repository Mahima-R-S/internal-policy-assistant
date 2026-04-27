import sys
import os
# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm.comparator import compare_llm_responses

def test_comparison():
    context = "Photosynthesis is a process used by plants and other organisms to convert light energy into chemical energy."
    question = "What is photosynthesis?"
    
    print("Testing LLM Comparison...")
    results = compare_llm_responses(question, context)
    
    for res in results:
        print(f"\nModel: {res['model']}")
        print(f"Response: {res['response'][:100]}...")
        print(f"Metrics: {res['metrics']}")

if __name__ == "__main__":
    test_comparison()

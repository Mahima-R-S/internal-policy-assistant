# test.py
from llm.comparator import compare_llm_responses

rag_context = "Photosynthesis is the process where plants convert light energy into chemical energy."

question = "What is photosynthesis?"

results = compare_llm_responses(question, rag_context)

for r in results:
    print(f"\n{r['model']}")
    print(f"Response: {r['response'][:100]}...")
    print(f"Metrics: {r['metrics']}")
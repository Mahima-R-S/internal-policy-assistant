from utils.rag_engine import retrieve
from llm.generator import generate_answer

q = "What unit is dissolved oxygen reported in?"
chunks = retrieve(q, top_k=1)
for c in chunks:
    print(f"[page {c['page']}] {c['text']}\n")

answer, err = generate_answer(q, chunks)
print("ANSWER:", answer or err)
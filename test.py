from utils.rag_engine import ingest_pdf, retrieve
from llm.generator import generate_answer

ok, msg = ingest_pdf("marine_sensing_notes.pdf")
print(msg)

q = "What is the standard sampling rate of a Veyra probe?"
for c in retrieve(q):
    print(c["page"], round(c["distance"], 3), c["text"][:80])

answer, err = generate_answer(q, retrieve(q))
print("\nANSWER:", answer or err)
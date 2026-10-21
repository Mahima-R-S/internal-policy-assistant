import json
from utils.rag_engine import retrieve
from llm.generator import generate_answer
from llm.groq_client import query_groq
from llm.judge import JUDGE_PROMPT, SYSTEM, JUDGE_MODEL

questions = [
    "A Veyra probe has been running for 40 hours without calibration at 800 m. Is it within rated depth, and is it due for calibration?",
    "Is the Halden-Ruiz method sufficient on its own to keep a Veyra probe accurate?",
]

for q in questions:
    chunks = retrieve(q, top_k=4)
    answer, _ = generate_answer(q, chunks)
    context = "\n\n".join(c["text"] for c in chunks)
    raw, err = query_groq(JUDGE_MODEL, SYSTEM, JUDGE_PROMPT.format(context=context, answer=answer))
    print("=" * 80)
    print("Q:", q)
    print("ANSWER:", answer)
    print("RAW JUDGE:", raw or err)
import re
from llm.groq_client import query_groq

GENERATOR_MODEL = "openai/gpt-oss-120b"  # change in one place
ABSTAIN = "NOT_IN_NOTES"

SYSTEM = "You answer questions using only the numbered excerpts provided. You never use outside knowledge."

ANSWER_PROMPT = """Answer the question using ONLY the numbered excerpts.
Cite the excerpt number after each claim, like [1].
If the excerpts do not contain the answer, reply exactly: NOT_IN_NOTES
If excerpts conflict, say so and give both values.

EXCERPTS:
{excerpts}

QUESTION: {question}
ANSWER:"""

def strip_think(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()

def generate_answer(question: str, chunks: list[dict]):
    excerpts = "\n\n".join(
        f"[{i+1}] ({c['source']}, p.{c['page']}) {c['text']}"
        for i, c in enumerate(chunks)
    )
    text, err = query_groq(GENERATOR_MODEL, SYSTEM,
                           ANSWER_PROMPT.format(excerpts=excerpts, question=question))
    if err:
        return None, err
    return strip_think(text), None
import json, re
from llm.groq_client import query_groq

# Must be a different model family from the generator.
JUDGE_MODEL = "qwen/qwen3.8-27b"  # check availability on Groq; fall back to another non-Llama model

SYSTEM = "You are a strict fact-checker. You output only JSON."

JUDGE_PROMPT = """Split the ANSWER into atomic factual claims.
For each claim, decide whether the EXCERPTS directly support it.
Return ONLY JSON: {{"claims": [{{"text": "...", "supported": true}}]}}

EXCERPTS:
{context}

ANSWER:
{answer}"""

def faithfulness(answer: str, chunks: list[dict]):
    """Returns (score 0-1 or None, error or None)."""
    context = "\n\n".join(c["text"] for c in chunks)
    raw, err = query_groq(JUDGE_MODEL, SYSTEM,
                          JUDGE_PROMPT.format(context=context, answer=answer))
    if err:
        return None, err
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.S)
    try:
        claims = json.loads(re.search(r"\{.*\}", raw, re.S).group(0))["claims"]
    except Exception:
        return None, "judge output not parseable"
    if not claims:
        return None, "no claims extracted"
    return sum(bool(c["supported"]) for c in claims) / len(claims), None
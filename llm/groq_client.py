import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
_client = None

def _get_client():
    global _client
    if _client is None:
        key = os.getenv("GROQ_API_KEY")
        if not key or "your_" in key:
            return None
        _client = Groq(api_key=key)
    return _client

def query_groq(model_id: str, system: str, prompt: str, temperature: float = 0.0):
    """Returns (response_text, error_message)."""
    client = _get_client()
    if client is None:
        return "", "GROQ_API_KEY not set in .env"
    try:
        resp = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=1024,
        )
        return resp.choices[0].message.content.strip(), None
    except Exception as e:
        return "", str(e)
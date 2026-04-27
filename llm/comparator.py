import time
from typing import Dict, List
from llm.groq_client import query_groq
from llm.gemini_client import query_gemini
from utils.scorer import compute_rouge, compute_readability, compute_groundedness


def compare_llm_responses(question: str, rag_context: str) -> List[Dict]:
    """
    Takes question + RAG context, returns responses from 3 LLMs with metrics.
    
    Args:
        question: User's question
        rag_context: Retrieved context from RAG (from Person 1)
    
    Returns:
        List of dicts: [
            {
                "model": "LLaMA 3.1 (8B)",
                "response": "answer text",
                "metrics": {
                    "groundedness": 0.85,
                    "readability": 65,
                    "rouge_l": 0.42,
                    "latency": 1.2
                }
            },
            ...
        ]
    """
    
    prompt = f"""Answer ONLY using this context:

{rag_context}

Question: {question}

Answer:"""
    
    results = []
    
    # LLaMA 3.1
    print("LLaMA 3.1...", end="", flush=True)
    start = time.time()
    response, error = query_groq("llama-3.1-8b-instant", prompt)
    latency = round(time.time() - start, 2)
    print(" DONE" if not error else f" ERROR")
    
    results.append({
        "model": "LLaMA 3.1 (8B)",
        "response": response if not error else f"Error: {error}",
        "metrics": {
            "groundedness": compute_groundedness(response, rag_context) if not error else 0,
            "readability": compute_readability(response) if not error else 0,
            "rouge_l": compute_rouge(response, rag_context) if not error else 0,
            "latency": latency
        }
    })
    
    # Qwen 3 (32B)
    print("Qwen 3 (32B)...", end="", flush=True)
    start = time.time()
    response, error = query_groq("qwen/qwen3-32b", prompt)
    latency = round(time.time() - start, 2)
    print(" DONE" if not error else f" ERROR")
    
    results.append({
        "model": "Qwen 3 (32B)",
        "response": response if not error else f"Error: {error}",
        "metrics": {
            "groundedness": compute_groundedness(response, rag_context) if not error else 0,
            "readability": compute_readability(response) if not error else 0,
            "rouge_l": compute_rouge(response, rag_context) if not error else 0,
            "latency": latency
        }
    })
    
    # Gemini 2.0 Flash
    print("Gemini 2.0...", end="", flush=True)
    start = time.time()
    response, error = query_gemini(prompt)
    latency = round(time.time() - start, 2)
    print(" DONE" if not error else f" ERROR")
    
    results.append({
        "model": "Gemini 2.0 Flash",
        "response": response if not error else f"Error: {error}",
        "metrics": {
            "groundedness": compute_groundedness(response, rag_context) if not error else 0,
            "readability": compute_readability(response) if not error else 0,
            "rouge_l": compute_rouge(response, rag_context) if not error else 0,
            "latency": latency
        }
    })
    
    return results
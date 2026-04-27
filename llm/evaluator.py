from llm.gemini_client import query_gemini

def check_hallucination(response: str, context: str) -> float:
    """
    Uses Gemini to check if the response is grounded in the given context.
    Returns a score from 0 to 1 (1 = fully grounded, 0 = pure hallucination).
    """
    if not response or not context:
        return 0.0
        
    prompt = f"""
    Evaluate if the following ANSWER is grounded in the provided CONTEXT.
    Provide a score between 0 and 1, where 1 means all facts in the answer are present in the context, 
    and 0 means the answer contains significant information not found in the context (hallucinations).
    
    ONLY return the numerical score, nothing else.
    
    CONTEXT:
    {context}
    
    ANSWER:
    {response}
    
    SCORE:"""
    
    score_text, error = query_gemini(prompt)
    if error:
        return 0.0
        
    try:
        # Extract float from response
        import re
        match = re.search(r"([0-9.]+)", score_text)
        if match:
            return min(1.0, max(0.0, float(match.group(1))))
        return 0.0
    except:
        return 0.0

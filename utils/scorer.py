import re
from rouge_score import rouge_scorer
import textstat


def compute_rouge(response: str, context: str) -> float:
    """ROUGE-L score (0-1). Higher = more overlap with context."""
    if not response or not context:
        return 0.0
    try:
        scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
        scores = scorer.score(context, response)
        return round(scores["rougeL"].fmeasure, 4)
    except:
        return 0.0


def compute_readability(text: str) -> float:
    """Flesch Reading Ease (0-100). Higher = easier to read."""
    if not text or len(text.strip()) < 10:
        return 0.0
    try:
        score = textstat.flesch_reading_ease(text)
        return round(max(0, min(100, score)), 2)
    except:
        return 0.0


def compute_groundedness(response: str, context: str) -> float:
    """
    Word overlap groundedness (0-1).
    Higher = more words from response found in context.
    LIMITATION: Only checks word overlap, not semantic correctness.
    """
    if not response or not context:
        return 0.0
    try:
        response_words = set(re.findall(r'\b[a-zA-Z]{5,}\b', response.lower()))
        context_words = set(re.findall(r'\b[a-zA-Z]{5,}\b', context.lower()))
        
        if not response_words:
            return 0.0
        
        overlap = len(response_words.intersection(context_words))
        return round(overlap / len(response_words), 4)
    except:
        return 0.0


def check_hallucination(response: str, context: str) -> float:
    """
    Uses Groq (Llama 3.1) to check if the response is grounded in the given context.
    Returns a score from 0 to 1 (1 = fully grounded, 0 = pure hallucination).
    """
    from llm.groq_client import query_groq
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
    
    # Using Llama 3.1 8B for fast scoring
    score_text, error = query_groq("llama-3.1-8b-instant", prompt)
    if error:
        print(f"Fact-Check Error: {error}")
        return 0.0
        
    try:
        # Extract float from response
        match = re.search(r"([0-9.]+)", score_text)
        if match:
            return min(1.0, max(0.0, float(match.group(1))))
        return 0.0
    except:
        return 0.0
import re
import textstat
from rouge_score import rouge_scorer

def compute_rouge(response: str, context: str) -> float:
    if not response or not context:
        return 0.0
    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    return round(scorer.score(context, response)["rougeL"].fmeasure, 4)

def compute_readability(text: str) -> float:
    if not text or len(text.strip()) < 10:
        return 0.0
    return round(max(0, min(100, textstat.flesch_reading_ease(text))), 2)
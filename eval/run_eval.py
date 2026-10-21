import json, time, sys
sys.path.append(".")
from utils.rag_engine import retrieve
from llm.generator import generate_answer, ABSTAIN
from llm.judge import faithfulness

def run(path="eval/questions.jsonl", k=4):
    rows = []
    for line in open(path):
        q = json.loads(line)
        chunks = retrieve(q["question"], top_k=k)
        t0 = time.time()
        ans, err = generate_answer(q["question"], chunks)
        latency = round(time.time() - t0, 2)
        if err:
            rows.append({**q, "error": err}); continue

        abstained = ABSTAIN in ans
        hit = None
        if q["answerable"]:
            hit = any(c["source"] == q["gold_source"] and c["page"] in q["gold_pages"] for c in chunks)

        faith, ferr = (None, None) if abstained else faithfulness(ans, chunks)
        rows.append({
            "question": q["question"], "type": q["type"], "answerable": q["answerable"],
            "retrieved_hit": hit, "abstained": abstained,
            "faithfulness": faith, "judge_error": ferr,
            "latency": latency, "answer": ans,
        })

    answerable = [r for r in rows if r["answerable"] and "error" not in r]
    unanswerable = [r for r in rows if not r["answerable"] and "error" not in r]
    summary = {
        "hit_at_k": sum(bool(r["retrieved_hit"]) for r in answerable) / max(len(answerable), 1),
        "abstain_recall": sum(r["abstained"] for r in unanswerable) / max(len(unanswerable), 1),
        "answer_rate_on_answerable": sum(not r["abstained"] for r in answerable) / max(len(answerable), 1),
        "mean_faithfulness": (lambda xs: sum(xs) / len(xs) if xs else None)(
            [r["faithfulness"] for r in answerable if r["faithfulness"] is not None]),
        "judge_failures": sum(1 for r in rows if r.get("judge_error")),
    }
    return rows, summary

# at the bottom of eval/run_eval.py, replace the __main__ block with:
if __name__ == "__main__":
    import csv
    for k in [1, 2, 4]:
        rows, summary = run(k=k)
        print(f"k={k}", json.dumps(summary, indent=2))
        with open(f"eval/results_k{k}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=sorted({key for r in rows for key in r}))
            w.writeheader(); w.writerows(rows)
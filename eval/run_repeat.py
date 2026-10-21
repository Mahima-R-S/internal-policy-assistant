import os, sys, re, json, time, csv
sys.path.insert(0, ".")
from utils.rag_engine import retrieve
from llm.generator import generate_answer, ABSTAIN
from llm.judge import faithfulness

N_RUNS = 3
K = 4

# Key terms per answerable question. Each inner list is a group: at least one
# alternative in the group must appear. All groups must be satisfied.
# Patterns are regex, matched at word starts, lowercase.
KEYS = {
    "What is the standard sampling rate of a Veyra probe?": [[r"240"], [r"hz"]],
    "How often must a Veyra probe be calibrated?": [[r"36"], [r"hour"]],
    "How long is the warm-up time for a Veyra probe?": [[r"12"], [r"minute"]],
    "What unit is dissolved oxygen reported in?": [[r"mg/l", r"milligram"]],
    "What is the penalty for a late lab report?": [[r"10"], [r"zero"]],
    "Who is the instructor and when are office hours?": [[r"varga"], [r"tuesday"]],
    "How are the course grades weighted?": [[r"30"], [r"40"]],
    "Who developed the Halden-Ruiz method, and when?": [[r"halden"], [r"ruiz"], [r"2017"]],
    "How many readings does step 1 of the Halden-Ruiz method collect?": [[r"three", r"3"], [r"surface"]],
    "Does the Halden-Ruiz method replace calibration?": [[r"no", r"not"], [r"calibrat"]],
    "What was dissolved oxygen at 300 m at the Ondine station?": [[r"4\.8"]],
    "What caused the drift at the Ondine station, and how large was it?": [[r"60"], [r"0\.4"]],
    "A Veyra probe has been running for 40 hours without calibration at 800 m. Is it within rated depth, and is it due for calibration?": [[r"900"], [r"36"]],
    "Is the Halden-Ruiz method sufficient on its own to keep a Veyra probe accurate?": [[r"no", r"not"], [r"calibrat"]],
    "What is the maximum rated depth of a Veyra probe?": [[r"900"], [r"1200"]],  # conflict: both values required
}

CITE = re.compile(r"[\[【](\d+)[\]】]")

def _norm(s):
    s = s.replace("\u202f", " ").replace("\u00a0", " ").lower()
    return re.sub(r"(?<=\d),(?=\d)", "", s)  # "1,200" -> "1200"

def _has(text, pattern):
    return re.search(r"\b" + pattern, text) is not None

def _groups_met(text, groups):
    return all(any(_has(text, p) for p in g) for g in groups)

def correct(question, answer):
    groups = KEYS.get(question)
    if groups is None:
        return None
    return _groups_met(_norm(answer), groups)

def citation_check(question, answer, chunks):
    idx = {int(i) for i in CITE.findall(answer)}
    valid = [i for i in idx if 1 <= i <= len(chunks)]
    cited_text = _norm(" ".join(chunks[i - 1]["text"] for i in valid))
    groups = KEYS.get(question)
    return {
        "cite_present": bool(idx),
        "cite_in_range": bool(idx) and len(valid) == len(idx),
        "cite_supports": bool(valid) and groups is not None and _groups_met(cited_text, groups),
    }

def judge_with_retry(answer, chunks, tries=3):
    for _ in range(tries):
        score, err = faithfulness(answer, chunks)
        if not (err and "429" in err):
            return score, err
        time.sleep(5)
    return score, err

def mean(xs):
    xs = [x for x in xs if x is not None]
    return round(sum(xs) / len(xs), 3) if xs else None

def main():
    questions = [json.loads(l) for l in open("eval/questions.jsonl", encoding="utf-8") if l.strip()]
    rows = []

    for q in questions:
        chunks = retrieve(q["question"], top_k=K)  # retrieval once per question
        for run in range(1, N_RUNS + 1):           # generation varies run to run
            t0 = time.time()
            answer, err = generate_answer(q["question"], chunks)
            latency = round(time.time() - t0, 2)
            if err:
                rows.append({"question": q["question"], "type": q["type"], "run": run, "error": err})
                continue

            abstained = ABSTAIN in answer
            if abstained:
                faith, ferr = None, None
                cit = {"cite_present": None, "cite_in_range": None, "cite_supports": None}
            else:
                faith, ferr = judge_with_retry(answer, chunks)
                cit = citation_check(q["question"], answer, chunks)

            if q["answerable"]:
                corr = correct(q["question"], answer)
            else:
                corr = abstained  # for unanswerable, correct means abstaining

            rows.append({
                "question": q["question"], "type": q["type"], "answerable": q["answerable"],
                "run": run, "abstained": abstained, "correct": corr,
                "faithfulness": faith, "judge_error": ferr, **cit,
                "latency": latency, "answer": answer,
            })
            time.sleep(1)

    # Per-run CSV
    fields = sorted({k for r in rows for k in r})
    with open("eval/repeat_runs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)

    # Per-question summary
    by_q = {}
    for r in rows:
        by_q.setdefault(r["question"], []).append(r)

    print(f"{'type':<18}{'n':>3}{'correct':>9}{'abstain':>9}{'faith_mean':>12}{'faith_min':>11}{'faith_max':>11}{'cite_ok':>9}  question")
    for question, rs in by_q.items():
        ok = [r for r in rs if "error" not in r]
        fs = [r["faithfulness"] for r in ok if r["faithfulness"] is not None]
        print(f"{rs[0]['type']:<18}{len(ok):>3}"
              f"{str(mean([r['correct'] and 1.0 or 0.0 for r in ok])):>9}"
              f"{str(mean([float(r['abstained']) for r in ok])):>9}"
              f"{str(mean(fs)):>12}"
              f"{str(min(fs)) if fs else 'None':>11}"
              f"{str(max(fs)) if fs else 'None':>11}"
              f"{str(mean([float(r['cite_supports']) for r in ok if r['cite_supports'] is not None])):>9}"
              f"  {question[:60]}")

    # Overall
    ans = [r for r in rows if "error" not in r and r["answerable"]]
    un = [r for r in rows if "error" not in r and not r["answerable"]]
    all_f = [r["faithfulness"] for r in rows if r.get("faithfulness") is not None]
    print("\nOVERALL")
    print(f"  answerable runs: {len(ans)}  correctness: {mean([float(r['correct']) for r in ans])}")
    print(f"  unanswerable runs: {len(un)}  abstention: {mean([float(r['abstained']) for r in un])}")
    print(f"  faithfulness: mean {mean(all_f)} over n={len(all_f)}, "
          f"judge failures: {sum(1 for r in rows if r.get('judge_error'))}")
    print(f"  generation errors: {sum(1 for r in rows if 'error' in r)}")
    print("\nPer-run detail: eval/repeat_runs.csv")

if __name__ == "__main__":
    main()
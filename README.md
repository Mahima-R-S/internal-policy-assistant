# Internal Policy Assistant

A question-answering system over internal policy documents. It answers only from the uploaded PDFs, cites the source page for each claim, and says "not in notes" when the documents don't cover the question.

## How it works

1. **Ingest:** PDFs are read page by page, split into chunks, and stored in ChromaDB with source file and page number.
2. **Retrieve:** The top matching chunks are fetched for each question.
3. **Generate:** A Groq-hosted LLaMA 3.3 model answers using only those chunks, with citations.
4. **Evaluate:** A test set with known answers measures retrieval, abstention, correctness, and faithfulness.

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_key_here
```

## Usage

Generate the test document and run the app:

```bash
python make_test_pdf.py
streamlit run app.py
```

Run the evaluation:

```bash
python eval/run_repeat.py
```

## Evaluation

The test set has 18 questions over a fictional document: direct, multi-hop, conflicting-source, and unanswerable cases. Each answerable question is run three times.

Results on this pilot set:
- Retrieval hit rate was high, but the test document has only 4 chunks, so this is a weak test.
- Abstention was correct on all unanswerable runs. These questions have little overlap with the document, so they are an easy case.
- Faithfulness is judged by a model from a different family than the generator. One multi-hop question consistently scored 0.8, which is still unexplained.
- Correctness uses keyword matching, which is loose and has not been checked by hand.

## Limitations

- Small pilot document and question set.
- No human review of answers yet.
- No access control or per-user permissions.
- Runs through a hosted API, so document text is sent to Groq.

## Next steps

- Test on a larger document set with more chunks.
- Add harder abstention questions that overlap the document's wording.
- Hand-label a sample of answers to check the keyword correctness.

## 🌟 Premium Aesthetics
The application features a modern "Glassmorphism" inspired design with:
*   **Card-based UI:** For clear model comparison.
*   **Interactive Tabs:** To switch between Study and Practice modes.
*   **Real-time Feedback:** Visual spinners and progress indicators for AI processing.

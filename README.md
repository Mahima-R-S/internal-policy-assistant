# 🎓 Adaptive AI Tutor

Adaptive AI Tutor is a premium, AI-powered learning platform designed to help students master their study materials through intelligent retrieval, multi-model analysis, and interactive assessments. This project leverages the latest LLM technologies (Gemini, LLaMA, Qwen) to provide a comparative and grounded learning experience.

---

## 🚀 Key Features

### 📖 Intelligent Study Mode (RAG)
*   **Knowledge Ingestion:** Upload any PDF study material. The system automatically processes, chunks, and indexes the content for instant retrieval.
*   **Contextual Q&A:** Ask questions directly about your documents. The tutor uses Retrieval-Augmented Generation (RAG) to ensure answers are based on your specific material.
*   **Multi-Model Comparison:** View and compare answers from three different state-of-the-art LLMs:
    *   **Google Gemini 3.0 Flash**
    *   **LLaMA 3.1 (8B)**
    *   **Qwen 3 (32B)**

### 📊 Performance Metrics Dashboard
Every AI response is evaluated in real-time across critical dimensions to ensure accuracy and clarity.

#### How Metrics are Calculated:
*   **Groundedness (Word Overlap):** A custom algorithm that extracts unique keywords (length ≥ 5) from the response and checks their presence in the retrieved context. It represents the percentage of key terms in the answer that are explicitly found in the source material.
*   **Readability (Flesch Ease):** Calculated using the `textstat` library. It analyzes sentence length and syllable count to provide a score from 0-100. Higher scores indicate content that is easier to read and understand.
*   **ROUGE-L Score:** A standard NLP metric that measures the longest common subsequence between the AI response and the source context. It evaluates how much of the original document's phrasing or structure is preserved.
*   **AI Fact-Check Score:** A high-level evaluation performed by a dedicated **LLaMA 3.1 8B Agent**. The agent cross-references factual claims in the answer against the context to detect hallucinations, returning a score from 0 (hallucinated) to 1 (fully grounded).
*   **Latency:** The total round-trip time (in seconds) from the moment the query is sent to the API until the final response is received and processed.

### 📝 Practice Zone
*   **Dynamic MCQ Generation:** Automatically creates customized Multiple Choice Questions (MCQs) based on the key concepts in your document.
*   **Self-Assessment:** Includes an expandable answer key for instant feedback on your knowledge.

---

## 🛠️ How It Works

### 1. Ingestion Pipeline (`utils/rag_engine.py`)
*   **Extraction:** Uses `PyPDF2` to read text from uploaded files.
*   **Chunking:** Employs `RecursiveCharacterTextSplitter` from LangChain to divide text into semantic blocks (1000 characters with 100-character overlap).
*   **Vectorization:** Processes chunks into embeddings and stores them in **ChromaDB**, a persistent vector database.

### 2. Retrieval Mechanism
*   When a user asks a question, the system performs a semantic search in ChromaDB to find the most relevant document sections (Top-K retrieval).

### 3. Execution & Evaluation (`llm/comparator.py` & `utils/scorer.py`)
*   The retrieved context is injected into a specialized prompt.
*   Three models are queried in parallel via **Gemini** and **Groq** APIs.
*   Each response is passed through the scoring engine to calculate metrics and the fact-check score.

---

## 💻 Tech Stack

*   **Frontend:** Streamlit (Custom CSS for Premium UI)
*   **Vector Database:** ChromaDB
*   **Orchestration:** LangChain (Text Splitting)
*   **LLMs:** Google Gemini 3.0, Meta LLaMA 3.1, Alibaba Qwen 3
*   **API Gateways:** Google AI Studio, Groq Cloud

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd mini_project
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory and add your API keys:
```env
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Run the Application
```bash
streamlit run app.py
```

---

## 📁 Project Structure

```text
├── app.py                # Main Streamlit Application
├── .env                  # Environment Variables (API Keys)
├── requirements.txt      # Project Dependencies
├── chroma_db/            # Persistent Vector Database storage
├── llm/
│   ├── gemini_client.py   # Google Gemini API Interface
│   ├── groq_client.py     # Groq API Interface (LLaMA/Qwen)
│   ├── comparator.py      # Multi-model query & comparison logic
│   ├── mcq_generator.py   # AI Quiz generation logic
│   └── evaluator.py       # (Optional) Model evaluation utilities
└── utils/
    ├── rag_engine.py      # PDF processing and ChromaDB logic
    └── scorer.py          # Metric calculations (ROUGE, Readability, Fact-Check)
```

---

## 🌟 Premium Aesthetics
The application features a modern "Glassmorphism" inspired design with:
*   **Card-based UI:** For clear model comparison.
*   **Interactive Tabs:** To switch between Study and Practice modes.
*   **Real-time Feedback:** Visual spinners and progress indicators for AI processing.

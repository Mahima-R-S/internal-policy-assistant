import streamlit as st
import os
import tempfile
from utils.rag_engine import ingest_pdf, retrieve_context, clear_db
from llm.comparator import compare_llm_responses
from llm.mcq_generator import generate_mcqs
from utils.scorer import check_hallucination

# Page Config
st.set_page_config(page_title="Adaptive AI Tutor", page_icon="🎓", layout="wide")

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stCard {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .metric-text {
        font-size: 0.9rem;
        color: #666;
    }
    .model-name {
        font-weight: bold;
        color: #2c3e50;
        font-size: 1.2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🎓 Adaptive AI Tutor")
st.sidebar.markdown("---")
uploaded_file = st.sidebar.file_uploader("Upload Study Material (PDF)", type="pdf")

if uploaded_file:
    if st.sidebar.button("Ingest & Process"):
        with st.spinner("Processing PDF..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            success, msg = ingest_pdf(tmp_path)
            os.unlink(tmp_path) # Clean up
            
            if success:
                st.sidebar.success(msg)
                st.session_state["context_ready"] = True
            else:
                st.sidebar.error(msg)

if st.sidebar.button("Clear Data"):
    clear_db()
    st.sidebar.info("Knowledge base cleared.")
    st.session_state["context_ready"] = False

# Main UI
st.title("Welcome to your Smart Tutor")
st.markdown("Ask anything about your uploaded documents.")

tabs = st.tabs(["📖 Study Mode", "📝 Practice Zone"])

with tabs[0]:
    query = st.text_input("What would you like to know?", placeholder="Explain the main concept of...")
    
    if query:
        if not st.session_state.get("context_ready"):
            st.warning("Please upload and ingest a document first!")
        else:
            with st.spinner("Consulting our AI experts..."):
                context = retrieve_context(query)
                results = compare_llm_responses(query, context)
                
                # Display Results
                cols = st.columns(3)
                for i, res in enumerate(results):
                    with cols[i]:
                        st.markdown(f'<div class="stCard">', unsafe_allow_html=True)
                        st.markdown(f'<p class="model-name">{res["model"]}</p>', unsafe_allow_html=True)
                        st.markdown(res["response"])
                        
                        st.markdown("---")
                        # Detailed metrics
                        st.markdown("**Metrics:**")
                        st.markdown(f"- Groundedness: `{res['metrics']['groundedness']}`")
                        st.markdown(f"- Readability: `{res['metrics']['readability']}`")
                        st.markdown(f"- ROUGE-L: `{res['metrics']['rouge_l']}`")
                        st.markdown(f"- Latency: `{res['metrics']['latency']}s`")
                        
                        # Add Hallucination Check (Separate from core metrics for UI visibility)
                        halluc_score = check_hallucination(res["response"], context)
                        st.markdown(f"- AI Fact-Check Score: `{halluc_score}`")
                        
                        st.markdown('</div>', unsafe_allow_html=True)

with tabs[1]:
    st.header("Assess Your Knowledge")
    if not st.session_state.get("context_ready"):
        st.info("Check back here after uploading your material!")
    else:
        if st.button("Generate Practice Questions"):
            with st.spinner("Creating custom quiz..."):
                # We use a broader context or specific part? For now, we'll try to get some context
                # To make it simple, we retrieve context for "general concepts" or just use random samples
                # But retrieve_context needs a query. Let's ask for "summary" to get sample text.
                sample_context = retrieve_context("summary of the key concepts", top_k=5)
                mcqs = generate_mcqs(sample_context)
                st.session_state["mcqs"] = mcqs
        
        if "mcqs" in st.session_state:
            for i, q in enumerate(st.session_state["mcqs"]):
                st.markdown(f"**Q{i+1}: {q['question']}**")
                for j, opt in enumerate(q['options']):
                    st.markdown(f"{chr(65+j)}. {opt}")
                st.markdown("---")
            
            with st.expander("🔑 Show Answer Key"):
                for i, q in enumerate(st.session_state["mcqs"]):
                    st.write(f"**Question {i+1}:** {q['answer']}")

# Footer
st.markdown("---")
st.caption("Powered by Gemini 3 Flash & Groq (LLaMA/Qwen)")

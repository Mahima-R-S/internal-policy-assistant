import streamlit as st
import os, tempfile
from utils.rag_engine import ingest_pdf, retrieve, clear_db
from llm.generator import generate_answer, ABSTAIN

st.set_page_config(page_title="Policy Notes Assistant", layout="wide")
st.title("Ask your notes")

with st.sidebar:
    up = st.file_uploader("Upload PDF", type="pdf")
    if up and st.button("Ingest"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(up.getvalue()); path = tmp.name
        ok, msg = ingest_pdf(path)
        os.unlink(path)
        (st.success if ok else st.error)(msg)
    if st.button("Clear data"):
        clear_db(); st.info("Cleared.")

query = st.text_input("Question")
if query:
    chunks = retrieve(query)
    answer, err = generate_answer(query, chunks)
    if err:
        st.error(err)
    elif ABSTAIN in answer:
        st.warning("Not covered in your notes.")
    else:
        st.markdown(answer)
    with st.expander("Sources retrieved"):
        for i, c in enumerate(chunks, 1):
            st.markdown(f"**[{i}]** {c['source']}, page {c['page']}\n\n> {c['text']}")
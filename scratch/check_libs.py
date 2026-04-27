
try:
    import chromadb
    print("chromadb OK")
except ImportError:
    print("chromadb MISSING")

try:
    import PyPDF2
    print("PyPDF2 OK")
except ImportError:
    print("PyPDF2 MISSING")

try:
    import streamlit
    print("streamlit OK")
except ImportError:
    print("streamlit MISSING")

try:
    import textstat
    print("textstat OK")
except ImportError:
    print("textstat MISSING")

try:
    import rouge_score
    print("rouge_score OK")
except ImportError:
    print("rouge_score MISSING")

import os
from google import genai
from dotenv import load_dotenv
 
load_dotenv()
 
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None
 
def query_gemini(prompt: str):
    """
    Query Gemini API (new google.genai SDK).
    Returns: (response_text, error_message)
    """
    try:
        if not client:
            return "", "GEMINI_API_KEY not in .env"
        
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        
        return response.text.strip(), None
        
    except Exception as e:
        return "", str(e)
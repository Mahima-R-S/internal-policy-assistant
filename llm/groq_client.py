import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def query_groq(model_id: str, prompt: str):
    """
    Query Groq API.
    Returns: (response_text, error_message)
    """
    try:
        # Check if we should use a specific key for Mixtral
        api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key or "your_" in api_key:
            return "", f"API key for {model_id} not set in .env"
        
        # Initialize client with the chosen key
        temp_client = Groq(api_key=api_key)
        
        response = temp_client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": "You are a helpful tutor. Use only the given context."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1024
        )
        
        return response.choices[0].message.content.strip(), None
        
    except Exception as e:
        return "", str(e)
import google.generativeai as genai

API_KEY = "AIzaSyCcGj558R7UOLivs36zkcMpq_EuarwvaI4"
genai.configure(api_key=API_KEY)

def get_call_interpretation(bird_name, *, call_type=None, emotion=None, context=None):
    """
    Generate bird call interpretation using Gemini AI
    
    Args:
        bird_name (str): Name of the bird species
        call_type (str, optional): Type of call detected
        emotion (str, optional): Emotional state detected
        context (str, optional): Behavioral context
    
    Returns:
        str: Interpretation of the bird call
    """
    try:
        prompt = (
            f"You are an ornithologist AI. A '{bird_name}' was detected. "
            f"The AI system analyzed the vocalization and determined it is a '{call_type}'"
            f"{' with emotion: ' + emotion if emotion else ''}"
            f"{' and context: ' + context if context else ''}. "
            "Based on this, what is the likely meaning or intent of this call? "
            "Explain in 1-2 sentences for a general audience."
        )
        
        llm = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = llm.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        print(f"Error in get_call_interpretation: {e}")
        return f"Unable to interpret {bird_name} {call_type} call due to AI service error."
        
def get_bird_encyclopedia(bird_name):
    prompt = (
        f"Write one short and fun paragraph about the bird '{bird_name}' using emojis inline. "
        f"Include 3 things in this single paragraph: where it lives 🏞️, its conservation status 🛡️, and one fun fact 🤯. "
        f"Make it casual, fun, and expressive — no bullet points or line breaks!"
    )
    llm = genai.GenerativeModel("gemini-1.5-flash-latest")
    return llm.generate_content(prompt).text.strip()



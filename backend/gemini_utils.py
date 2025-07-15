import google.generativeai as genai

API_KEY = "AIzaSyCcGj558R7UOLivs36zkcMpq_EuarwvaI4"
genai.configure(api_key=API_KEY)

def get_call_interpretation(bird_name):
    prompt = f"You are an ornithologist AI. A '{bird_name}' was detected. Based on its vocalizations, what's the likely meaning? (e.g., Alarm Call, Mating Song, etc.)"
    llm = genai.GenerativeModel('gemini-1.5-flash-latest')
    return llm.generate_content(prompt).text.strip()

def get_bird_encyclopedia(bird_name):
    prompt = (
        f"Write one short and fun paragraph about the bird '{bird_name}' using emojis inline. "
        f"Include 3 things in this single paragraph: where it lives 🏞️, its conservation status 🛡️, and one fun fact 🤯. "
        f"Make it casual, fun, and expressive — no bullet points or line breaks!"
    )
    llm = genai.GenerativeModel("gemini-1.5-flash-latest")
    return llm.generate_content(prompt).text.strip()



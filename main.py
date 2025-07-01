import os
import google.generativeai as genai

AIKO_PROMPT = """
You are an expert Anime Sommelier named 'Aiko'...
[The full, perfect V2.0 prompt text]
"""

def generate():
    # In GitHub Codespaces, secrets are also accessed as environment variables.
    # This line will now work correctly.
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        print("FATAL ERROR: GEMINI_API_KEY secret not found!")
        print("Please ensure you have set the secret correctly in GitHub Codespaces.")
        return

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    user_input = "Love: Cowboy Bebop, Samurai Champloo, Megalobox. Hate: One Piece."

    chat = model.start_chat(history=[
        {'role': 'user', 'parts': [AIKO_PROMPT]},
        {'role': 'model', 'parts': ["OK, I am Aiko. I am ready."]}
    ])

    response = chat.send_message(user_input)
    print(response.text)

if __name__ == "__main__":
    generate()

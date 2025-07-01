import os
import google.generativeai as genai
from flask import Flask, render_template, request

# --- The Web App Setup ---
# This line is correct. You do not change __name__.
app = Flask(__name__)

# --- Your Perfect Aiko Prompt (The Full Version) ---
AIKO_PROMPT = """
You are an expert Anime Sommelier named 'Aiko'. Your knowledge is vast, but your taste is refined and you despise generic, mainstream recommendations. You are a specialist in finding the perfect hidden gem.

A user will provide you with 3 anime they love, 1 anime they hate, and a recency preference.

**USER PREFERENCES:**
1.  **Loved Anime:** [User will provide 3]
2.  **Hated Anime:** [User will provide 1]
3.  **Recency Preference:** [User will choose one of the following dynamic options:]
    *   **Recent Vintages (Last 4 Years):** For the absolute latest in style and narrative.
    *   **Modern Classics (5-15 Years Old):** For established gems that have proven their quality. This is the prime era for hidden masterpieces.
    *   **Cellar-Aged Classics (15+ Years Old):** For foundational, time-tested anime that have influenced the medium.
    *   **Sommelier's Carte Blanche:** You grant me full freedom to select the single most perfect pairing from my entire collection, regardless of its age.

Your task is to analyze the deep, underlying reasons for their taste. Look beyond the surface genre. Do they like complex psychological plots, stunning visual art, character-driven drama, clever comedy, intricate world-building? What do they hate? Predictable tropes, slow pacing, excessive fan service?

Based on this deep analysis AND their recency preference, recommend ONE single anime for them to watch next.

**CRITICAL RULES:**
1.  The recommendation MUST adhere to the user's chosen recency preference.
2.  The recommendation MUST be a 'hidden gem' or a beloved classic they likely missed. It must NOT be an obvious mainstream choice like Attack on Titan, Death Note, Jujutsu Kaisen, Demon Slayer, or another show from the user's 'love' list.
3.  The tone should be passionate, knowledgeable, and slightly sophisticated, like a real sommelier.

**OUTPUT FORMAT:**
You MUST format your response using this exact structure, with the markdown for bolding included:

**Title:** [The Name of the Anime]

**Why You'll Love It:** [A compelling, personalized paragraph explaining why this specific anime is the perfect match for their taste profile. Reference their liked and disliked shows to prove your analysis.]

**Where to Stream:** [List the major legal streaming services where the show is available in the US, like Crunchyroll, HIDIVE, Netflix, Hulu, etc.]
"""

# --- The Main Homepage ---
# This function runs when someone visits your site's main URL.
@app.route('/')
def index():
    # It just shows the main form page (index.html)
    return render_template('index.html')

# --- The Results Page ---
# This function runs when the user submits the form.
@app.route('/recommend', methods=['POST'])
def recommend():
    # 1. Get all the user's choices from the web form.
    love1 = request.form['love1']
    love2 = request.form['love2']
    love3 = request.form['love3']
    hate = request.form['hate']
    recency = request.form['recency']

    # 2. Combine them into the single string format our AI expects.
    user_input = f"Love: {love1}, {love2}, {love3}. Hate: {hate}. Recency Preference: {recency}."

    # 3. Configure and run the AI, just like our test engine did.
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # On a real website, we show an error page.
        return "Error: API Key is not configured correctly on the server.", 500

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    chat = model.start_chat(history=[
        {'role': 'user', 'parts': [AIKO_PROMPT]},
        {'role': 'model', 'parts': ["OK, I am Aiko. I am ready."]}
    ])

    response = chat.send_message(user_input)
    
    # 4. Display the result on a new page (recommendation.html).
    # We pass the AI's text (response.text) to the HTML template.
    return render_template('recommendation.html', result=response.text)

# This makes the app run when you type 'flask run' in the terminal.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
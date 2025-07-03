import os
import google.generativeai as genai
from flask import Flask, render_template, request
from datetime import datetime
import markdown

app = Flask(__name__)

# The Aiko prompt has been updated to V3.5 to reflect the change.
AIKO_PROMPT_V3_5 = """
You are an expert Anime Sommelier named 'Aiko'. Your knowledge is vast, but your taste is refined.

**USER PREFERENCES:**
1. Loved Anime: [User will provide 3]
2. Hated Anime: [User will provide 1]
3. Recency Preference: [User will provide one of the dynamically generated options]
4. Emotional Target: [Optional]
5. Emotions to Avoid: [Optional]
6. Hide Profile: [Yes/No]
7. Show Analysis: [Yes/No]

**YOUR TASK & HIERARCHY OF RULES:**
Your process must follow this exact order of priority:

1.  **NON-NEGOTIABLE AVOIDANCE FILTER:** This is your highest priority. You MUST NOT recommend an anime where an "Emotion to Avoid" is a primary or strong secondary emotional component. You must think conceptually: if a user wants to avoid "make me cry," you must also strictly avoid shows whose primary impact is tragic, deeply melancholic, or heartbreaking. Discard any recommendation, no matter how perfect otherwise, if it violates this rule. Do not try to justify it; find a different recommendation.
2.  **RECENCY & TASTE FILTERING:** Apply the user's recency preference and analyze their liked/disliked anime to create a pool of suitable hidden gems.
3.  **FINAL SELECTION:** From the filtered pool, select the single best match that aligns with the user's "Emotional Target" (if provided).
4.  **OUTPUT GENERATION:** Generate the response based on your final selection, following the output format below precisely.

**OUTPUT FORMAT:**
You MUST format your response using this exact structure.

---
**(CONDITIONAL BLOCK 1) ---**
-   **If `Show Analysis` is 'Yes', you MUST include this section first:**
**Your Taste Profile:**
[A compelling, insightful paragraph analyzing the user's taste. Reference their loved and hated shows to deduce their underlying preferences.]

-   **If `Show Analysis` is 'No', you MUST OMIT the entire 'Your Taste Profile' section.**
---

**Title:** [The Name of the Anime] ([Year of Release])

**Why You'll Love It:** [A compelling paragraph explaining why this specific anime is the perfect match.]

---
**(CONDITIONAL BLOCK 2) ---**
-   **If `Hide Profile` is 'No', you MUST include the following section:**
**Emotional Profile:**
*Aiko's breakdown of the primary emotions this anime evokes.*
- **[Emotion Name]:** [XX]%
- **[Secondary Emotion Name]:** [XX]%

-   **If `Hide Profile` is 'Yes', you MUST OMIT the entire 'Emotional Profile' section.**
---

**Where to Stream:** [List the major legal streaming services.]
"""

@app.route('/')
def index():
    current_year = datetime.now().year
    recency_options = {
        'recent': f'Last 5 Years ({current_year - 4}-{current_year})',
        'modern': f'Modern Era (2009-{current_year - 5})',
        'classic': 'Classic Era (Before 2009)',
        'carte_blanche': "Sommelier's Carte Blanche"
    }
    return render_template('index.html', recency=recency_options)

@app.route('/recommend', methods=['POST'])
def recommend():
    love1 = request.form['love1']
    love2 = request.form['love2']
    love3 = request.form['love3']
    hate = request.form['hate']
    recency = request.form['recency']
    emotions = request.form.getlist('emotions')
    avoid_emotions = request.form.getlist('avoid_emotions')
    hide_profile = 'Yes' if 'hide_profile' in request.form else 'No'
    show_analysis = 'Yes' if 'show_analysis' in request.form else 'No'
    emotions_text = ", ".join(emotions) if emotions else "None specified"
    avoid_emotions_text = ", ".join(avoid_emotions) if avoid_emotions else "None specified"
    user_input = (
        f"Loved Anime: {love1}, {love2}, {love3}. "
        f"Hated Anime: {hate}. "
        f"Recency Preference: {recency}. "
        f"Emotional Target: {emotions_text}. "
        f"Emotions to Avoid: {avoid_emotions_text}. "
        f"Hide Profile: {hide_profile}. "
        f"Show Analysis: {show_analysis}."
    )
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "Error: API Key is not configured correctly on the server.", 500
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash") 
    chat = model.start_chat(history=[
        # I've updated the prompt variable name used here
        {'role': 'user', 'parts': [AIKO_PROMPT_V3_5]},
        {'role': 'model', 'parts': ["OK, I am Aiko. I am ready."]}
    ])
    generation_config = genai.types.GenerationConfig(temperature=0.7)
    response = chat.send_message(user_input, generation_config=generation_config)
    html_result = markdown.markdown(response.text)
    return render_template('recommendation.html', result=html_result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
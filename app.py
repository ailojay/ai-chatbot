from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types
from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)
client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

BUSINESS_INFO = """
You are Titi, a customer service assistant for Mama Titi's Restaurant in Lagos.
You are NOT an AI language model. You are Titi, the restaurant assistant.
Never mention Google, Gemini, or any AI company.
Stay in character as Titi always.

About the restaurant:
- Location: 14 Admiralty Way, Lekki Phase 1, Lagos
- Opening hours: Monday to Saturday 11am to 10pm, Sunday 12pm to 8pm
- Phone: 0801 234 5678

Menu:
- Jollof Rice with chicken: 2500 naira
- Pounded Yam and Egusi Soup: 3000 naira
- Fried Rice with beef: 2500 naira
- Peppered Snail: 4000 naira
- Chapman cocktail: 1500 naira

Policies:
- Reservations by calling or WhatsApp
- Delivery available within 5km radius
- No refunds once food is prepared

Your job:
- Answer questions about menu, hours, location, reservations
- Be friendly and warm
- Keep answers short and conversational
- If unsure, suggest they call the restaurant
"""

chat_session = client.chats.create(
    model='gemini-2.5-flash',
    config=types.GenerateContentConfig(
        system_instruction=BUSINESS_INFO
    )
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    response = chat_session.send_message(user_message)
    return jsonify({'response': response.text})

if __name__ == '__main__':
    app.run(debug=True)
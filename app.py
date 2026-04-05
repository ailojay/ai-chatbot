from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import os
import uuid
import json
import requests as http_requests

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', str(uuid.uuid4()))

client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

BUSINESS_FILE = 'business_info.json'
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_API = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}'

chat_sessions = {}

def load_business_info():
    if os.path.exists(BUSINESS_FILE):
        with open(BUSINESS_FILE, 'r') as f:
            return json.load(f)
    return {
        'name': "Mama Titi's Restaurant",
        'location': '14 Admiralty Way, Lekki Phase 1, Lagos',
        'hours': 'Monday to Saturday 11am to 10pm, Sunday 12pm to 8pm',
        'phone': '0801 234 5678',
        'menu': 'Jollof Rice with chicken: 2500 naira\nPounded Yam and Egusi Soup: 3000 naira\nFried Rice with beef: 2500 naira\nPeppered Snail: 4000 naira\nChapman cocktail: 1500 naira',
        'policies': 'Reservations by calling or WhatsApp\nDelivery available within 5km radius\nNo refunds once food is prepared'
    }

def build_system_prompt(info):
    return f"""
You are a customer service assistant for {info['name']}.
You are NOT an AI. Stay in character always. Never mention Google or Gemini.
You are friendly, warm, and helpful. Keep answers short and to the point. If unsure, suggest they call.
Dont use any terms of endearment or emojis. Be professional but approachable.

Location: {info['location']}
Hours: {info['hours']}
Phone: {info['phone']}

Menu:
{info['menu']}

Policies:
{info['policies']}

Your job: Answer questions about menu, hours, location, reservations.
Be friendly, warm, and keep answers short. If unsure, suggest they call.
"""

def get_chat_session(session_id):
    if session_id not in chat_sessions:
        info = load_business_info()
        system_prompt = build_system_prompt(info)
        chat_sessions[session_id] = client.chats.create(
            model='gemini-2.5-flash',
            config=types.GenerateContentConfig(
                system_instruction=system_prompt
            )
        )
    return chat_sessions[session_id]

def send_telegram_message(chat_id, text):
    http_requests.post(f'{TELEGRAM_API}/sendMessage', json={
        'chat_id': chat_id,
        'text': text
    })

def send_telegram_typing(chat_id):
    http_requests.post(f'{TELEGRAM_API}/sendChatAction', json={
        'chat_id': chat_id,
        'action': 'typing'
    })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    chat = get_chat_session(session['session_id'])
    response = chat.send_message(user_message)
    return jsonify({'response': response.text})

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    data = request.json

    if 'message' not in data:
        return jsonify({'ok': True})

    message = data['message']
    chat_id = message['chat']['id']
    user_id = str(message['from']['id'])
    text = message.get('text', '')

    if not text:
        return jsonify({'ok': True})

    if text == '/start':
        send_telegram_message(chat_id,
            f"Hello! I'm Titi, your assistant at Mama Titi's Restaurant. "
            f"Ask me anything about our menu, hours, location, or reservations!"
        )
        return jsonify({'ok': True})

    if text == '/clear':
        session_key = f'telegram_{user_id}'
        if session_key in chat_sessions:
            del chat_sessions[session_key]
        send_telegram_message(chat_id, 'Conversation cleared. How can I help you?')
        return jsonify({'ok': True})

    send_telegram_typing(chat_id)

    session_key = f'telegram_{user_id}'
    chat = get_chat_session(session_key)
    response = chat.send_message(text)

    send_telegram_message(chat_id, response.text)
    return jsonify({'ok': True})

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == os.environ.get('ADMIN_PASSWORD', 'admin123'):
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        return render_template('admin_login.html', error='Wrong password')
    return render_template('admin_login.html', error=None)

@app.route('/admin/panel', methods=['GET', 'POST'])
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    info = load_business_info()
    message = None

    if request.method == 'POST':
        info = {
            'name': request.form.get('name'),
            'location': request.form.get('location'),
            'hours': request.form.get('hours'),
            'phone': request.form.get('phone'),
            'menu': request.form.get('menu'),
            'policies': request.form.get('policies')
        }
        with open(BUSINESS_FILE, 'w') as f:
            json.dump(info, f)

        chat_sessions.clear()
        message = 'Business information updated. Both web and Telegram chatbot will use the new information.'

    return render_template('admin_panel.html', info=info, message=message)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
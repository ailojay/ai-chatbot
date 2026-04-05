from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
import os
import json

client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

BUSINESS_FILE = 'business_info.json'

user_sessions = {}

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

def get_user_session(user_id):
    if user_id not in user_sessions:
        info = load_business_info()
        system_prompt = build_system_prompt(info)
        user_sessions[user_id] = client.chats.create(
            model='gemini-2.5-flash',
            config=types.GenerateContentConfig(
                system_instruction=system_prompt
            )
        )
    return user_sessions[user_id]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I'm Titi, your assistant at Mama Titi's Restaurant. "
        "Ask me anything about our menu, hours, location, or reservations!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action='typing'
    )

    chat = get_user_session(user_id)
    response = chat.send_message(user_message)

    await update.message.reply_text(response.text)

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_sessions:
        del user_sessions[user_id]
    await update.message.reply_text(
        "Conversation cleared. How can I help you?"
    )

def main():
    token = os.environ['TELEGRAM_BOT_TOKEN']
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('clear', clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print('Titi Telegram bot is running...')
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
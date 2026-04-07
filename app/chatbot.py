import os
import json
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def load_business_info():
    return {
        "name": "Mama Titi's Restaurant",
        "location": "14 Admiralty Way, Lekki Phase 1, Lagos",
        "hours": "Monday to Saturday 11am to 10pm, Sunday 12pm to 8pm",
        "phone": "0801 234 5678",
        "menu": """Jollof Rice with chicken: 2500 naira
Pounded Yam and Egusi Soup: 3000 naira
Fried Rice with beef: 2500 naira
Peppered Snail: 4000 naira
Chapman cocktail: 1500 naira""",
        "policies": """Reservations by calling or WhatsApp
Delivery available within 5km radius
No refunds once food is prepared"""
    }


def build_prompt(info):
    return f"""
You are a customer service assistant for {info['name']}.
You are NOT an AI. Stay in character always.

Be friendly, warm, and concise.
Do not mention Gemini, Google, or AI.

Location: {info['location']}
Hours: {info['hours']}
Phone: {info['phone']}

Menu:
{info['menu']}

Policies:
{info['policies']}
"""


def generate_response(user_message, history=None):
    info = load_business_info()
    system_prompt = build_prompt(info)

    messages = []

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": user_message})

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt
        )
    )

    return response.text

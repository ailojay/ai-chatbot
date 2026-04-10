import boto3
import time
import os

# DynamoDB setup
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("chat-sessions")


# -----------------------------
# SESSION MEMORY FUNCTIONS
# -----------------------------

def load_business_info(session_id):
    if not session_id:
        return []

    res = table.get_item(Key={"session_id": session_id})
    return res.get("Item", {}).get("messages", [])


def save_business_info(session_id, messages):
    if not session_id:
        return

    table.put_item(Item={
        "session_id": session_id,
        "messages": messages,
        "updated_at": int(time.time())
    })


# -----------------------------
# GLOBAL CONFIG (ADMIN DATA)
# -----------------------------

def get_business_config():
    res = table.get_item(Key={"session_id": "global_config"})
    return res.get("Item", {})


# -----------------------------
# GEMINI CALL (YOU ALREADY HAVE THIS)
# -----------------------------

def call_gemini(history):
    """
    This function should already exist in your code.
    It sends `history` to Gemini and returns the reply text.
    """
    # Example placeholder:
    raise NotImplementedError("Replace with your Gemini API call")


# -----------------------------
# MAIN CHAT FUNCTION
# -----------------------------

def generate_response(message, session_id=None):
    # Load conversation history
    history = load_business_info(session_id) or []

    # Load business config (ADMIN DATA)
    business = get_business_config()

    # Build system prompt (THIS FIXES MENU ISSUE)
    system_prompt = f"""
You are a helpful assistant for a restaurant.

Business Name: {business.get('name', '')}
Location: {business.get('location', '')}
Hours: {business.get('hours', '')}
Phone: {business.get('phone', '')}

Menu:
{business.get('menu', '')}

Policies:
{business.get('policies', '')}

Instructions:
- Answer questions using the business information above
- If asked about the menu, list the menu items clearly
- Be friendly and helpful
"""

    # Inject system prompt ONLY once
    if not any(msg.get("role") == "system" for msg in history):
        history.insert(0, {
            "role": "system",
            "content": system_prompt
        })

    # Add user message
    history.append({
        "role": "user",
        "content": message
    })

    # Call Gemini safely (QUOTA HANDLING)
    try:
        reply = call_gemini(history)

    except Exception as e:
        error_str = str(e)

        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            reply = "I'm currently busy due to high demand. Please try again shortly."
        else:
            reply = "Something went wrong. Please try again."

    # Save assistant reply
    history.append({
        "role": "assistant",
        "content": reply
    })

    # Persist session
    save_business_info(session_id, history)

    return reply

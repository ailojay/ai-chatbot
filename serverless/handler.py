import json
import os
import uuid
import requests as http_requests

from app.chatbot import generate_response, load_config, save_config

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


# ------------------------
# TELEGRAM SEND
# ------------------------
def send_telegram_message(chat_id, text):
    http_requests.post(f"{TELEGRAM_API}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })


# ------------------------
# RESPONSE HELPER
# ------------------------
def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }


# ------------------------
# MAIN HANDLER
# ------------------------
def lambda_handler(event, context):
    print("Incoming event:", event)

    path = event.get("rawPath") or event.get("path", "")
    method = (
        event.get("requestContext", {}).get("http", {}).get("method")
        or event.get("httpMethod", "")
    )

    # ------------------------
    # /chat (WEB)
    # ------------------------
    if path == "/chat" and method == "POST":
        try:
            body = json.loads(event.get("body", "{}"))

            message = body.get("message")
            session_id = body.get("session_id", str(uuid.uuid4()))

            if not message:
                return response(400, {"error": "No message provided"})

            reply = generate_response(message, session_id)

            return response(200, {
                "response": reply,
                "session_id": session_id
            })

        except Exception as e:
            return response(500, {"error": str(e)})

    # ------------------------
    # /webhook (TELEGRAM)
    # ------------------------
    if path == "/webhook" and method == "POST":
        try:
            data = json.loads(event.get("body", "{}"))

            if "message" not in data:
                return response(200, {"ok": True})

            msg = data["message"]

            chat_id = msg["chat"]["id"]
            user_id = str(msg["from"]["id"])
            text = msg.get("text", "")

            if not text:
                return response(200, {"ok": True})

            if text == "/start":
                send_telegram_message(chat_id,
                    "Hello! I'm Titi, your assistant. How can I help you today?"
                )
                return response(200, {"ok": True})

            reply = generate_response(text, f"telegram_{user_id}")
            send_telegram_message(chat_id, reply)

            return response(200, {"ok": True})

        except Exception:
            return response(200, {"ok": True})

    # ------------------------
    # /admin POST (SAVE CONFIG)
    # ------------------------

if path == "/admin" and method == "POST":
    try:
        headers = event.get("headers", {})
        token = headers.get("x-admin-token")

        if token != os.environ.get("ADMIN_TOKEN"):
            return response(403, {"error": "Unauthorized"})

        body = json.loads(event.get("body", "{}"))

        from app.chatbot import save_business_info
        save_business_info("global_config", body)

        return response(200, {"message": "Saved successfully"})

    except Exception as e:
        return response(500, {"error": str(e)})

    # ------------------------
    # /admin GET (FETCH CONFIG)
    # ------------------------
    if path == "/admin" and method == "GET":
        try:
            data = load_config()
            return response(200, data)

        except Exception as e:
            return response(500, {"error": str(e)})

    # ------------------------
    # NOT FOUND
    # ------------------------
    return response(404, {"message": "Not Found"})

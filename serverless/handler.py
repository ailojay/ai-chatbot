import json
from app.chatbot import generate_response

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        message = body.get("message", "")

        if not message:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No message provided"})
            }

        response_text = generate_response(message)

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "response": response_text
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }

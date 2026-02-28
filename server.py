"""Simple Alice skill server with Claude API integration."""

import os
import traceback
from flask import Flask, request, jsonify
import anthropic

app = Flask(__name__)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Store conversation sessions (in-memory, resets on restart)
sessions = {}


def ask_claude(user_text, session_id):
    """Send user message to Claude and get response."""
    if session_id not in sessions:
        sessions[session_id] = []

    sessions[session_id].append({"role": "user", "content": user_text})

    # Keep last 10 messages for context
    messages = sessions[session_id][-10:]

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        system="Ты голосовой ассистент в Яндекс Колонке. Отвечай кратко и по делу, "
               "максимум 1-2 предложения. Не используй markdown, ссылки или спецсимволы — "
               "твой ответ будет озвучен голосом.",
        messages=messages,
    )

    assistant_text = response.content[0].text
    sessions[session_id].append({"role": "assistant", "content": assistant_text})

    return assistant_text


def make_response(text, end_session=False):
    """Build Alice response."""
    return jsonify({
        "response": {
            "text": text,
            "tts": text,
            "end_session": end_session,
        },
        "version": "1.0",
    })


@app.route("/alice", methods=["POST"])
def alice_webhook():
    """Handle incoming requests from Yandex Alice."""
    try:
        data = request.json
        print(f">>> Request: {data.get('request', {}).get('command', '')}")

        session_id = data.get("session", {}).get("session_id", "default")
        command = data.get("request", {}).get("command", "")
        is_new = data.get("session", {}).get("new", False)

        if is_new or not command:
            return make_response("Привет! Я AI-ассистент. Задавай любые вопросы.")

        text = ask_claude(command, session_id)
        print(f"<<< Response: {text}")
        return make_response(text)

    except Exception as e:
        print(f"!!! Error: {traceback.format_exc()}")
        return make_response("Произошла ошибка, попробуйте ещё раз.")


@app.route("/", methods=["GET"])
def health():
    """Health check endpoint."""
    return "Alice AI Agent is running"


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: Set ANTHROPIC_API_KEY environment variable")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        exit(1)

    print("Starting Alice AI Agent on http://localhost:5001")
    print("Webhook URL: http://localhost:5001/alice")
    app.run(host="0.0.0.0", port=5001)

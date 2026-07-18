from flask import Flask, request, jsonify
import os, json, urllib.request

app = Flask(__name__)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
conversations = {}
@app.route("/")
def home():
      return open("public/index.html", encoding="utf-8").read()

@app.route("/api/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return jsonify({"ok": True})
    d = request.json
    msg = d.get("message", "")
    sid = d.get("session_id", "d")
    if sid not in conversations:
        conversations[sid] = []
    h = conversations[sid]
    parts = []
    for m in h[-10:]:
        parts.append({"role": m["role"], "parts": [{"text": m["text"]}]})
    parts.append({"role": "user", "parts": [{"text": msg}]})
    try:
        payload = json.dumps({"contents": parts, "systemInstruction": {"parts": [{"text": "你是用户的温和理性型陪伴者。共情但不煽情。核心：我陪你。怎么走，听你的。"}]}}).encode()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        r = urllib.request.urlopen(urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}), timeout=30)
        reply = json.loads(r.read())["candidates"][0]["content"]["parts"][0]["text"]
        h.append({"role": "user", "text": msg})
        h.append({"role": "model", "text": reply})
        if len(h) > 20:
            conversations[sid] = h[-20:]
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}, 500)

@app.route("/api/reset", methods=["POST", "OPTIONS"])
def reset():
    d = request.json
    conversations.pop(d.get("session_id", "d"), None)
    return jsonify({"ok": True})

import os, json
import urllib.request, urllib.parse

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

def handler(req):
    try:
        body = json.loads(req.get("body", "{}"))
        msg = body.get("message", "")
        sid = body.get("session_id", "d")

        # Simple in-memory storage (Vercel serverless, resets on cold start)
        payload = {
            "contents": [{"role": "user", "parts": [{"text": msg}]}],
            "systemInstruction": {"parts": [{"text": "你是用户的温和理性型陪伴者。共情但不煽情。核心：我陪你。怎么走，听你的。"}]}
        }

        data = json.dumps(payload).encode()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        r = urllib.request.urlopen(urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}), timeout=30)
        reply = json.loads(r.read())["candidates"][0]["content"]["parts"][0]["text"]

        return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"reply": reply})}
    except Exception as e:
        return {"statusCode": 500, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": str(e)})}

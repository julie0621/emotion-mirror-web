from flask import Flask, request, jsonify
import os, json, urllib.request

app = Flask(__name__)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
conversations = {}

HTML_PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>情绪镜子</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,"PingFang SC",sans-serif;background:#f5f0eb;height:100vh;display:flex;flex-direction:column}
header{background:#fff;padding:16px 24px;display:flex;justify-content:space-between;align-items:center}
header h1{font-size:18px;color:#3a3a3a}
header button{background:none;border:1px solid #ddd;padding:6px 14px;border-radius:6px;cursor:pointer;font-size:13px;color:#666}
header button:hover{background:#f5f5f5}
#chat{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:12px}
.msg{max-width:80%;padding:12px 16px;border-radius:16px;line-height:1.7;font-size:15px;white-space:pre-wrap;word-break:break-word}
.msg.user{background:#e8f0fe;align-self:flex-end;border-bottom-right-radius:4px;color:#1a1a1a}
.msg.bot{background:#fff;align-self:flex-start;border-bottom-left-radius:4px;box-shadow:0 1px 3px rgba(0,0,0,.06);color:#2a2a2a}
.welcome{text-align:center;color:#999;padding:40px;font-size:14px;line-height:2}
.welcome h2{color:#555;font-size:18px;margin-bottom:8px}
.typing{background:#fff;align-self:flex-start;padding:12px 16px;border-radius:16px;color:#999;font-size:14px}
#input-area{background:#fff;padding:12px 16px;border-top:1px solid #eee;display:flex;gap:10px}
#input-area textarea{flex:1;border:1px solid #ddd;border-radius:10px;padding:10px 14px;font-size:15px;resize:none;outline:none;font-family:inherit;min-height:44px;max-height:120px}
#input-area textarea:focus{border-color:#8ab4f8}
#input-area button{background:#5c7cba;color:#fff;border:none;border-radius:10px;padding:10px 20px;font-size:15px;cursor:pointer;white-space:nowrap}
#input-area button:hover{background:#4a6aa8}
#input-area button:disabled{background:#ccc;cursor:not-allowed}
</style>
</head>
<body>
<header><div><h1>情绪镜子</h1></div><button onclick="resetChat()">新对话</button></header>
<div id="chat"><div class="welcome"><h2>你好，我是情绪镜子</h2>我在这里陪你。怎么走，听你的。</div></div>
<div id="input-area"><textarea id="input" rows="1" placeholder="说说你的心情…" onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();send()}"></textarea><button id="btn" onclick="send()">发送</button></div>
<script>
let sid='s_'+Date.now();const c=document.getElementById('chat'),i=document.getElementById('input'),b=document.getElementById('btn');
function add(t,r){const d=document.createElement('div');d.className='msg '+r;d.textContent=t;c.appendChild(d);c.scrollTop=c.scrollHeight}
function showTyping(){const t=document.createElement('div');t.className='typing';t.id='typing';t.textContent='思考中…';c.appendChild(t);c.scrollTop=c.scrollHeight}
async function send(){const m=i.value.trim();if(!m)return;i.value='';add(m,'user');b.disabled=true;showTyping()
try{const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m,session_id:sid})});const d=await r.json();document.getElementById('typing')?.remove();add(d.reply||'错误:'+d.error,'bot')}catch(e){document.getElementById('typing')?.remove();add('连接失败','bot')}b.disabled=false;i.focus()}
async function resetChat(){if(!confirm('开始新对话？'))return;sid='s_'+Date.now();c.innerHTML='<div class="welcome"><h2>你好，我是情绪镜子</h2>我在这里陪你。怎么走，听你的。</div>';i.focus()}
</script>
</body>
</html>"""

@app.route("/")
def home():
    return HTML_PAGE, 200, {"Content-Type": "text/html; charset=utf-8"}

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

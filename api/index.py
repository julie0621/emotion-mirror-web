from flask import Flask, request, jsonify
import os, json, urllib.request, urllib.error

app = Flask(__name__)
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()
API_URL = "https://api.deepseek.com/v1/chat/completions"
SYSTEM_MSG = {"role": "system", "content": "你是用户的温和理性型陪伴者。像朋友一样说话，不要像咨询师或AI。\n\n## 说话风格\n- 简短、自然、有温度。不要写很长的大道理。\n- 用口语，不要用书面语。不要用「你的感受是正当的」「我听到了」这种表达。\n- 不要预设用户的状态。用户说心情不好，先问问怎么回事，或者直接陪一会，不要急着给建议。\n- 允许简单回应。不是每句都要给方法。\n\n## 给建议时\n- 给普通人真的会用的方法。不要写教科书式的话术。\n- 给具体、小事、今天就能做的事。\n- 如果不知道说什么，就说「我也不知道该怎么说才好，但我听着呢」。\n\n## 核心原则\n不强制走流程、不评判。如果用户有伤害自己的念头，提供心理援助热线12356。"}
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
let sid='s_'+Date.now();let memory=localStorage.getItem('em_memory')||'';const c=document.getElementById('chat'),i=document.getElementById('input'),b=document.getElementById('btn');
function add(t,r){const d=document.createElement('div');d.className='msg '+r;d.textContent=t;c.appendChild(d);c.scrollTop=c.scrollHeight}
function showTyping(){const t=document.createElement('div');t.className='typing';t.id='typing';t.textContent='思考中…';c.appendChild(t);c.scrollTop=c.scrollHeight}
async function send(){const m=i.value.trim();if(!m)return;i.value='';add(m,'user');b.disabled=true;showTyping()
try{const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m,memory:memory})});const d=await r.json();document.getElementById('typing')?.remove();const reply=d.reply||'错误:'+d.error;add(reply,'bot');if(d.memory){memory=d.memory;localStorage.setItem('em_memory',memory)}}catch(e){document.getElementById('typing')?.remove();add('连接失败','bot')}b.disabled=false;i.focus()}
async function resetChat(){if(!confirm('开始新对话？'))return;memory='';localStorage.removeItem('em_memory');c.innerHTML='<div class="welcome"><h2>你好，我是情绪镜子</h2>我在这里陪你。怎么走，听你的。</div>';i.focus()}
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
    user_memory = d.get("memory", "")

    system_content = "你是用户的温和理性型陪伴者。像朋友一样说话，不要像咨询师或AI。\n\n## 说话风格\n- 简短、自然、有温度。不要写很长的大道理。\n- 用口语，不要用书面语。不要用「你的感受是正当的」「我听到了」这种表达。\n- 不要预设用户的状态。用户说心情不好，先问问怎么回事，或者直接陪一会，不要急着给建议。\n- 允许简单回应。不是每句都要给方法。\n\n## 给建议时\n- 给普通人真的会用的方法。不要写教科书式的话术。\n- 给具体、小事、今天就能做的事。\n- 如果不知道说什么，就说「我也不知道该怎么说才好，但我听着呢」。\n\n## 核心原则\n不强制走流程、不评判。如果用户有伤害自己的念头，提供心理援助热线12356。"

    if user_memory:
        system_content += f"\n\n## 关于这个用户的记忆\n{user_memory}\n\n参考以上信息来回应，但不要直接引用「根据之前的记忆」这类话——自然地融入对话。"

    messages = [{"role": "system", "content": system_content}]
    messages.append({"role": "user", "content": msg})

    try:
        # First call: get reply
        body1 = json.dumps({"model": "deepseek-chat", "messages": messages, "stream": False}).encode()
        req1 = urllib.request.Request(
            API_URL, data=body1,
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + API_KEY}
        )
        resp1 = json.loads(urllib.request.urlopen(req1, timeout=30).read())
        reply = resp1["choices"][0]["message"]["content"]

        # Second call: extract/update memory
        memory_prompt = f"根据以上对话，用一段中文总结用户的重要信息，包括：性格特点、兴趣爱好、人际关系情况、说话风格、当前和过去的情绪状态。如果已有旧记忆：{user_memory}，在此基础上更新补充。只输出总结内容，不要多余的话。"

        messages2 = [{"role": "system", "content": "你是一个专业的用户分析助手，从对话中提取用户画像。"}]
        messages2.append({"role": "user", "content": msg})
        messages2.append({"role": "assistant", "content": reply})
        messages2.append({"role": "user", "content": memory_prompt})

        body2 = json.dumps({"model": "deepseek-chat", "messages": messages2, "stream": False}).encode()
        req2 = urllib.request.Request(
            API_URL, data=body2,
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + API_KEY}
        )
        resp2 = json.loads(urllib.request.urlopen(req2, timeout=30).read())
        new_memory = resp2["choices"][0]["message"]["content"]

        return jsonify({"reply": reply, "memory": new_memory})
    except urllib.error.HTTPError as e:
        detail = str(e)
        try:
            body = e.read().decode("utf-8", errors="replace")
            detail += ": " + body
        except Exception:
            pass
        return jsonify({"error": detail}), e.code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/reset", methods=["POST", "OPTIONS"])
def reset():
    d = request.json
    conversations.pop(d.get("session_id", "d"), None)
    return jsonify({"ok": True})

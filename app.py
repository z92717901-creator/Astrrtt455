import asyncio
import json
import os
import threading
from datetime import datetime
from flask import Flask, jsonify, render_template_string, request
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# ================== 📋 الإعدادات ==================
API_ID = 3993099
API_HASH = "7375b6b2163edc378d949480d066093e"
SOURCE_BOT_ID = "@Gg5677bot"
SESSION_STRING = "1ApWapzMBu7unu6O4wHY30mW1plFpKZOSTWLTCsgJyFyjYa1UwxSTAODTNmqQNxQfaNW71TLIxHySeorVvEPr31JbtdXyTp6i4ZDcvi0hBAa5a3lQYunvw9O5mPalQieos18iCZAKL44u5pWR7v6sMOqsYiBx-C9mC9x7tRClkEQXAFHRqpc_IsaE_5bCCx5NmVNZLMJtibeIUyrzFNDiBXFO67wUTTwmomaAJ2gx8rGxIcf4SJQhzq_dfSDDFIcttffXSr5bs1g2RKBRk3AqdTp6HHXPsEp5UuVihlbryYo9tKMp9x0n3Fl4Qai1K7CWXvgKP80WpS-h5OXWLTh3qP3twyei1sU="

YOUR_TELEGRAM_ID = 7553940284
DATA_FILE = "messages.json"

app = Flask(__name__)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH, loop=loop)

def load_messages():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_messages(messages):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

messages = load_messages()

# ================== 🌐 واجهة الموقع ==================
HTML_CODE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>💧 رسائل البوت</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:'Segoe UI',Tahoma,Arial,sans-serif;background:#f0f9ff;color:#334155;margin:0;padding:0;padding-bottom:90px;}
header{background:linear-gradient(135deg,#0ea5e9,#0284c7);color:#fff;text-align:center;padding:15px;position:sticky;top:0;z-index:100;}
header h1{font-size:20px;margin:0;}
.notification-status{text-align:center;padding:6px;font-size:12px;color:#2563eb;background:#eff6ff;}
.status-bar{text-align:center;padding:8px;font-size:13px;color:#64748b;background:#f8fafc;border-bottom:1px solid #e2e8f0;}
#messages{max-width:700px;margin:20px auto;padding:0 12px;display:flex;flex-direction:column;gap:12px;}
.msg{background:#fff;padding:14px 18px;border-radius:18px 18px 18px 4px;max-width:90%;align-self:flex-start;box-shadow:0 2px 6px rgba(0,0,0,0.05);line-height:1.6;}
.msg-meta{font-size:11px;margin-bottom:6px;color:#94a3b8;}
.msg-text{font-size:15px;white-space:pre-wrap;}
.msg-buttons{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px;}
.bot-btn{background:#e0f2fe;color:#0369a1;border:1px solid #bae6fd;padding:8px 16px;border-radius:20px;font-size:14px;cursor:pointer;}
.empty-state{text-align:center;padding:60px 20px;color:#94a3b8;}
.start-area{position:fixed;bottom:0;left:0;right:0;background:#fff;padding:15px;box-shadow:0 -2px 10px rgba(0,0,0,0.05);text-align:center;}
#start-btn{background:#22c55e;color:#fff;border:none;padding:12px 35px;border-radius:25px;font-size:16px;font-weight:bold;cursor:pointer;}
#start-btn:disabled{background:#94a3b8;}
</style>
</head>
<body>
<header><h1>💧 رسائل البوت</h1></header>
<div class="notification-status" id="nstatus"></div>
<div class="status-bar" id="status">جاري التحميل...</div>
<div id="messages"><div class="empty-state">📭 لا توجد رسائل حتى الآن</div></div>
<div class="start-area"><button id="start-btn" onclick="sendStart()">🚀 إرسال /start</button></div>

<script>
let lastCount = -1;
if (Notification.permission === 'default') {
    Notification.requestPermission().then(p=>{
        document.getElementById('nstatus').textContent = p==='granted'?'🔔 الإشعارات مفعلة':'🔕 الإشعارات متوقفة';
    });
} else {
    document.getElementById('nstatus').textContent = Notification.permission==='granted'?'🔔 الإشعارات مفعلة':'🔕 الإشعارات متوقفة';
}

function alertSound(){try{new AudioContext().createOscillator().start()}catch(e){}}
function notify(t){
    if(Notification.permission==='granted'){
        new Notification('💧 رسالة جديدة',{body:t.length>40?t.slice(0,40)+'...':t});
        alertSound();
    }
}

async function sendStart(){
    const b=document.getElementById('start-btn');
    b.disabled=true;b.textContent='⏳ جاري الإرسال...';
    try{
        const r=await fetch('/api/start',{method:'POST'});
        const d=await r.json();
        b.textContent=d.ok?'✅ تم الإرسال':'❌ خطأ';
    }catch(e){b.textContent='❌ فشل الاتصال';}
    setTimeout(()=>{b.textContent='🚀 إرسال /start';b.disabled=false;},2000);
}

async function pressBtn(t){
    try{await fetch('/api/press',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:t})});}catch(e){}
}

async function loadMessages(){
    try{
        const r=await fetch('/api/messages');
        const msgs=await r.json();
        document.getElementById('status').innerText='✅ متصل — عدد الرسائل: '+msgs.length;
        if(lastCount!==-1 && msgs.length>lastCount) notify(msgs[msgs.length-1].text);
        lastCount=msgs.length;
        const c=document.getElementById('messages');
        c.innerHTML='';
        if(msgs.length===0){
            c.innerHTML='<div class="empty-state">📭 لا توجد رسائل حتى الآن — اضغط على زر إرسال /start ✅</div>';
        }else{
            msgs.forEach(m=>{
                const d=document.createElement('div');
                d.className='msg';
                let html='<div class="msg-meta">💧 البوت • '+(m.time||'')+'</div><div class="msg-text">'+escapeHtml(m.text)+'</div>';
                if(m.buttons&&m.buttons.length){
                    html+='<div class="msg-buttons">';
                    m.buttons.forEach(b=>html+='<button class="bot-btn" onclick="pressBtn(\\''+b.replace(/'/g,"\\\\'")+'\\')">'+escapeHtml(b)+'</button>');
                    html+='</div>';
                }
                d.innerHTML=html;
                c.appendChild(d);
            });
            window.scrollTo(0,document.body.scrollHeight);
        }
    }catch(e){
        document.getElementById('status').innerHTML='<span style="color:red">❌ خطأ في الاتصال</span>';
    }
}
function escapeHtml(t){return $('<div/>').text(t).html();}
setInterval(loadMessages,2000);
loadMessages();
</script>
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_CODE)

@app.route('/api/messages')
def get_all():
    return jsonify(messages)

@app.route('/api/start', methods=['POST'])
def send_start():
    async def task():
        try:
            await client.send_message(SOURCE_BOT_ID, '/start')
            return True
        except: return False
    try:
        fut = asyncio.run_coroutine_threadsafe(task(), loop)
        return jsonify({"ok": fut.result(timeout=10)})
    except:
        return jsonify({"ok": False})

@app.route('/api/press', methods=['POST'])
def press():
    data = request.get_json()
    text = data.get('text','')
    async def task():
        try:
            async for msg in client.iter_messages(SOURCE_BOT_ID, limit=5):
                if msg.buttons:
                    for row in msg.buttons:
                        for btn in row:
                            if btn.text == text:
                                await msg.click(btn)
                                return True
            return False
        except: return False
    try:
        fut = asyncio.run_coroutine_threadsafe(task(), loop)
        return jsonify({"ok": fut.result(timeout=10)})
    except:
        return jsonify({"ok": False})

@client.on(events.NewMessage(from_users=SOURCE_BOT_ID))
async def new_msg(event):
    global messages
    text = event.raw_text
    buttons = []
    if event.message.buttons:
        try: buttons = [btn.text for row in event.message.buttons for btn in row]
        except: pass
    messages.append({"id":event.id,"text":text,"buttons":buttons,"time":datetime.now().strftime("%H:%M:%S")})
    if len(messages)>500: messages=messages[-500:]
    save_messages(messages)
    print(f"📥 رسالة جديدة: {text[:40]}")
    
    if YOUR_TELEGRAM_ID != 0:
        try:
            note = f"🔔 رسالة جديدة!\n━━━━━━━━\n{text}\n🕒 {datetime.now().strftime('%H:%M:%S')}"
            await client.send_message(YOUR_TELEGRAM_ID, note, silent=False)
        except: pass

def start_client():
    async def run():
        try:
            await client.start()
            print("✅ متصل بالتليجرام بنجاح")
            await client.run_until_disconnected()
        except Exception as e:
            print(f"❌ خطأ في الاتصال: {e}")
    loop.run_until_complete(run())

if __name__ == '__main__':
    threading.Thread(target=start_client, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",5000)), debug=False)
    
import asyncio
import json
import os
import threading
from datetime import datetime
from flask import Flask, jsonify, request, render_template_string
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from supabase import create_client, Client

# ================== 📋 الإعدادات ==================
# ✅ عدل القيم التالية ببياناتك الحقيقية
API_ID = 39932829          # ضع API_ID الخاص بك
API_HASH = "af065af801fedce625b300cee1cc7e53"  # ضع API_HASH الخاص بك
SOURCE_BOT_ID = "@Gg5677bot"          # اسم بوتك
SESSION_STRING = "1ApWapzMBu7unu6O4wHY30mW1plFpKZOSTWLTCsgJyFyjYa1UwxSTAODTNmqQNxQfaNW71TLIxHySeorVvEPr31JbtdXyTp6i4ZDcvi0hBAa5a3lQYunvw9O5mPalQieos18iCZAKL44u5pWR7v6sMOqsYiBx-C9mC9x7tRClkEQXAFHRqpc_IsaE_5bCCx5NmVNZLMJtibeIUyrzFNDiBXFO67wUTTwmomaAJ2gx8rGxIcf4SJQhzq_dfSDDFIcttffXSr5bs1g2RKBRk3AqdTp6HHXPsEp5UuVihlbryYo9tKMp9x0n3Fl4Qai1K7CWXvgKP80WpS-h5OXWLTh3qP3twyei1sU="

# ================== 🔗 اتصال قاعدة البيانات ==================
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

app = Flask(__name__)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH, loop=loop)

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase: متصل بنجاح")
    except Exception as e:
        print(f"❌ خطأ في Supabase: {e}")
else:
    print("⚠️ تنبيه: لم يتم العثور على متغيرات Supabase")

# ================== 🌐 واجهة الموقع ==================
HTML_CODE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>💧 محطة نبع الصويرة</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:'Segoe UI',Tahoma,Arial,sans-serif;background:#f0f9ff;color:#334155;margin:0;padding:0;}
header{background:linear-gradient(135deg,#0ea5e9,#0284c7);color:#fff;text-align:center;padding:18px;position:sticky;top:0;z-index:100;box-shadow:0 2px 10px rgba(0,0,0,0.1);}
header h1{font-size:20px;}
.status-bar{text-align:center;padding:6px;font-size:12px;color:#64748b;background:#f8fafc;border-bottom:1px solid #e2e8f0;}
#messages{max-width:700px;margin:15px auto;padding:0 12px;padding-bottom:90px;display:flex;flex-direction:column;gap:12px;min-height:350px;}
.msg{background:#fff;padding:12px 15px;border-radius:18px 18px 18px 4px;max-width:85%;align-self:flex-start;box-shadow:0 1px 3px rgba(0,0,0,0.06);line-height:1.5;}
.msg.me{background:#0ea5e9;color:#fff;border-radius:18px 18px 4px 18px;align-self:flex-end;}
.msg-meta{font-size:11px;margin-bottom:4px;opacity:0.7;}
.msg.me .msg-meta{color:#e0f2fe;}
.msg-text{white-space:pre-wrap;word-break:break-word;}
.btns{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px;}
.bot-btn{background:#f0f9ff;color:#0284c7;border:1px solid #bae6fd;padding:8px 14px;border-radius:20px;cursor:pointer;font-size:14px;transition:0.2s;}
.bot-btn:hover{background:#0ea5e9;color:#fff;}
#input-area{position:fixed;bottom:0;left:0;right:0;background:#fff;padding:12px;box-shadow:0 -2px 10px rgba(0,0,0,0.05);}
.input-row{max-width:700px;margin:0 auto;display:flex;gap:8px;}
#msg-input{flex:1;padding:12px 15px;border:1px solid #cbd5e1;border-radius:25px;font-size:15px;outline:none;}
#msg-input:focus{border-color:#0ea5e9;}
#send-btn{background:#0ea5e9;color:#fff;border:none;padding:12px 20px;border-radius:25px;cursor:pointer;font-weight:bold;}
.welcome{text-align:center;padding:40px 20px;color:#64748b;}
</style>
</head>
<body>
<header><h1>💧 محطة نبع الصويرة</h1></header>
<div class="status-bar" id="status">جاري التحميل...</div>
<div id="messages"><div class="welcome">👋 أهلاً بك! اكتب رسالة أو اضغط على زر أدناه للبدء.</div></div>
<div id="input-area">
  <div class="input-row">
    <input type="text" id="msg-input" placeholder="اكتب رسالتك هنا...">
    <button id="send-btn" onclick="sendMessage()">إرسال</button>
  </div>
</div>

<script>
let lastLen = -1;

async function loadMessages(){
  try{
    const res = await fetch('/api/messages');
    const msgs = await res.json();
    document.getElementById('status').innerText = `✅ متصل — ${msgs.length} رسالة`;
    if(msgs.length === lastLen) return;
    const container = document.getElementById('messages');
    container.innerHTML = '';
    if(msgs.length === 0){
      container.innerHTML = '<div class="welcome">👋 أهلاً بك! اكتب رسالة أو اضغط على زر أدناه للبدء.</div>';
    } else {
      msgs.forEach(m=>{
        const d = document.createElement('div');
        d.className = 'msg' + (m.is_me?' me':'');
        let html = '<div class="msg-meta">' + (m.is_me ? '👤 أنت' : '💧 البوت') + '</div>';
        if(m.text) html += '<div class="msg-text">' + escapeHtml(m.text) + '</div>';
        if(m.buttons && m.buttons.length>0){
          html += '<div class="btns">';
          m.buttons.forEach(btn=>{
            html += '<button class="bot-btn" onclick="sendByButton(\\''+btn.replace(/'/g,"\\\\'").replace(/"/g,'\\\\"')+'\\')">'+escapeHtml(btn)+'</button>';
          });
          html += '</div>';
        }
        d.innerHTML = html;
        container.appendChild(d);
      });
    }
    lastLen = msgs.length;
    window.scrollTo(0, document.body.scrollHeight);
  }catch(e){
    document.getElementById('status').innerHTML = '<span style="color:red">❌ خطأ في الاتصال</span>';
  }
}

async function sendByButton(text){
  document.getElementById('msg-input').value = text;
  await sendMessage();
}

async function sendMessage(){
  const input = document.getElementById('msg-input');
  const text = input.value.trim();
  if(!text) return;
  input.value = '';
  try{
    await fetch('/api/send',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({text:text})
    });
    setTimeout(loadMessages, 800);
    setTimeout(loadMessages, 2000);
  }catch(e){
    alert('❌ فشل الإرسال');
  }
}

function escapeHtml(t){
  const div = document.createElement('div');
  div.textContent = t;
  return div.innerHTML;
}

document.getElementById('msg-input').addEventListener('keydown',e=>{
  if(e.key==='Enter') sendMessage();
});

setInterval(loadMessages, 2500);
loadMessages();
</script>
</body>
</html>
"""

# ================== 🔌 واجهات API ==================
@app.route('/')
def index():
    return render_template_string(HTML_CODE)

@app.route('/api/messages')
def get_messages():
    if not supabase:
        return jsonify([])
    try:
        res = supabase.table('messages').select('*').order('date', desc=False).execute()
        return jsonify(res.data)
    except Exception as e:
        print(f"❌ خطأ جلب الرسائل: {e}")
        return jsonify([])

@app.route('/api/send', methods=['POST'])
def send_msg():
    data = request.get_json()
    text = (data.get('text','')).strip()
    if not text:
        return jsonify({"ok":False,"error":"نص فارغ"}),400
    try:
        async def _send():
            await client.send_message(SOURCE_BOT_ID, text)
        future = asyncio.run_coroutine_threadsafe(_send(), loop)
        future.result(timeout=15)
        
        if supabase:
            supabase.table('messages').insert({
                "id": int(datetime.now().timestamp()*1000000),
                "date": datetime.now().timestamp(),
                "text": text,
                "is_me": True,
                "buttons": []
            }).execute()
        return jsonify({"ok":True})
    except Exception as e:
        print(f"❌ خطأ إرسال: {e}")
        return jsonify({"ok":False,"error":str(e)}),500

# ================== 📥 استقبال رسائل البوت ==================
@client.on(events.NewMessage(from_users=SOURCE_BOT_ID))
async def on_new_message(event):
    msg = event.message
    text = msg.text or msg.caption or ""
    buttons = []
    if msg.buttons:
        try:
            buttons = [btn.text for row in msg.buttons for btn in row if btn.text]
        except:
            pass
    print(f"📥 رسالة من البوت: {text[:40]}")
    
    if supabase:
        try:
            supabase.table('messages').insert({
                "id": msg.id,
                "date": msg.date.timestamp(),
                "text": text,
                "is_me": False,
                "buttons": buttons
            }).execute()
        except Exception as e:
            print(f"❌ خطأ حفظ رسالة: {e}")

# ================== 🚀 التشغيل ==================
def start_telethon():
    async def run():
        try:
            await client.start()
            print("✅ البوت متصل وجاهز للعمل")
            await client.run_until_disconnected()
        except Exception as e:
            print(f"❌ خطأ اتصال Telethon: {e}")
    loop.run_until_complete(run())

if __name__ == '__main__':
    threading.Thread(target=start_telethon, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 الموقع شغال على البورت {port}")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
    
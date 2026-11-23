import asyncio
import json
import os
import threading
from datetime import datetime
from flask import Flask, jsonify, render_template_string
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# ================== 📋 الإعدادات ==================
API_ID = 3993099
API_HASH = "7375b6b2163edc378d949480d066093e"
SOURCE_BOT_ID = "@Gg5677bot"
SESSION_STRING = "1ApWapzMBu7unu6O4wHY30mW1plFpKZOSTWLTCsgJyFyjYa1UwxSTAODTNmqQNxQfaNW71TLIxHySeorVvEPr31JbtdXyTp6i4ZDcvi0hBAa5a3lQYunvw9O5mPalQieos18iCZAKL44u5pWR7v6sMOqsYiBx-C9mC9x7tRClkEQXAFHRqpc_IsaE_5bCCx5NmVNZLMJtibeIUyrzFNDiBXFO67wUTTwmomaAJ2gx8rGxIcf4SJQhzq_dfSDDFIcttffXSr5bs1g2RKBRk3AqdTp6HHXPsEp5UuVihlbryYo9tKMp9x0n3Fl4Qai1K7CWXvgKP80WpS-h5OXWLTh3qP3twyei1sU="

# ⚠️ ضع معرف حسابك في التليجرام هنا
YOUR_TELEGRAM_ID = 0  # ❏ مثال: 7553940284

DATA_FILE = "messages.json"

app = Flask(__name__)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH, loop=loop)

# 📦 تحميل وحفظ الرسائل
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
print(f"✅ تم تحميل {len(messages)} رسالة")

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
body{font-family:'Segoe UI',Tahoma,Arial,sans-serif;background:#f0f9ff;color:#334155;margin:0;padding:0;}
header{background:linear-gradient(135deg,#0ea5e9,#0284c7);color:#fff;text-align:center;padding:15px;position:sticky;top:0;z-index:100;box-shadow:0 2px 10px rgba(0,0,0,0.1);}
header h1{font-size:20px;margin:0 0 10px 0;}
.start-btn-container{text-align:center;padding:8px 0;}
#start-btn{background:#22c55e;color:#fff;border:none;padding:10px 25px;border-radius:25px;font-size:15px;font-weight:bold;cursor:pointer;transition:0.2s;}
#start-btn:hover{background:#16a34a;}
#start-btn:disabled{background:#94a3b8;cursor:not-allowed;}
.status-bar{text-align:center;padding:8px;font-size:13px;color:#64748b;background:#f8fafc;border-bottom:1px solid #e2e8f0;}
#messages{max-width:700px;margin:20px auto;padding:0 12px 40px 12px;display:flex;flex-direction:column;gap:12px;min-height:300px;}
.msg{background:#fff;padding:14px 18px;border-radius:18px 18px 18px 4px;max-width:90%;align-self:flex-start;box-shadow:0 2px 6px rgba(0,0,0,0.05);line-height:1.6;}
.msg-meta{font-size:11px;margin-bottom:6px;color:#94a3b8;}
.msg-text{white-space:pre-wrap;word-break:break-all;font-size:15px;}
.empty-state{text-align:center;padding:80px 20px;color:#94a3b8;font-size:15px;}
</style>
</head>
<body>
<header>
  <h1>💧 رسائل البوت</h1>
  <div class="start-btn-container">
    <button id="start-btn" onclick="sendStart()">🚀 إرسال /start</button>
  </div>
</header>
<div class="status-bar" id="status">جاري التحميل...</div>
<div id="messages"><div class="empty-state">📭 لا توجد رسائل حتى الآن — اضغط على زر إرسال /start ✅</div></div>

<script>
let lastCount = -1;
let shouldScroll = true;

async function sendStart(){
  const btn = document.getElementById('start-btn');
  btn.disabled = true;
  btn.textContent = '⏳ جاري الإرسال...';
  try{
    const res = await fetch('/api/start', {method: 'POST'});
    const data = await res.json();
    if(data.ok){
      btn.textContent = '✅ تم الإرسال';
      setTimeout(()=>{
        btn.textContent = '🚀 إرسال /start';
        btn.disabled = false;
      }, 2000);
    } else {
      btn.textContent = '❌ خطأ — حاول مرة أخرى';
      setTimeout(()=>{
        btn.textContent = '🚀 إرسال /start';
        btn.disabled = false;
      }, 2000);
    }
  }catch(e){
    btn.textContent = '❌ فشل الاتصال';
    setTimeout(()=>{
      btn.textContent = '🚀 إرسال /start';
      btn.disabled = false;
    }, 2000);
  }
}

async function loadMessages(){
  try{
    const res = await fetch('/api/messages');
    const msgs = await res.json();
    document.getElementById('status').innerText = `✅ متصل — عدد الرسائل: ${msgs.length}`;
    
    if(msgs.length === lastCount) return;
    lastCount = msgs.length;
    
    const container = document.getElementById('messages');
    container.innerHTML = '';
    
    if(msgs.length === 0){
      container.innerHTML = '<div class="empty-state">📭 لا توجد رسائل حتى الآن — اضغط على زر إرسال /start ✅</div>';
    } else {
      msgs.forEach(m=>{
        const d = document.createElement('div');
        d.className = 'msg';
        d.innerHTML = `
          <div class="msg-meta">💧 البوت • ${m.time || ''}</div>
          <div class="msg-text">${escapeHtml(m.text)}</div>
        `;
        container.appendChild(d);
      });
      
      // ✅ ينزل تلقائياً لآخر رسالة تحت
      if (shouldScroll) {
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
      }
    }
  }catch(e){
    document.getElementById('status').innerHTML = '<span style="color:red">❌ خطأ في الاتصال</span>';
  }
}

function escapeHtml(t){
  const div = document.createElement('div');
  div.textContent = t;
  return div.innerHTML;
}

setInterval(loadMessages, 2000);
loadMessages();
</script>
</body>
</html>
"""

# ================== 🔌 المسارات ==================
@app.route('/')
def index():
    return render_template_string(HTML_CODE)

@app.route('/api/messages')
def get_msgs():
    return jsonify(messages)

@app.route('/api/start', methods=['POST'])
def send_start():
    async def _send():
        await client.send_message(SOURCE_BOT_ID, '/start')
    try:
        future = asyncio.run_coroutine_threadsafe(_send(), loop)
        future.result(timeout=15)
        return jsonify({"ok": True})
    except Exception as e:
        print(f"❌ خطأ إرسال /start: {e}")
        return jsonify({"ok": False})

# ================== 📥 استقبال رسائل البوت ==================
@client.on(events.NewMessage(from_users=SOURCE_BOT_ID))
async def on_msg(event):
    global messages
    text = event.raw_text
    
    new_msg = {
        "text": text,
        "time": datetime.now().strftime("%H:%M:%S")
    }
    messages.append(new_msg)
    
    if len(messages) > 500:
        messages = messages[-500:]
    
    save_messages(messages)
    print(f"📥 رسالة جديدة من البوت: {text[:50]}")
    
    # 📱 تنبيه على التليجرام — فقط من هذا البوت
    if YOUR_TELEGRAM_ID != 0:
        try:
            notification = f"""
🔔 رسالة جديدة واصلة من البوت!
━━━━━━━━━━━━━━
💬 {text}
🕒 {datetime.now().strftime("%H:%M:%S")}
            """
            await client.send_message(YOUR_TELEGRAM_ID, notification.strip(), silent=False)
        except Exception as e:
            print(f"⚠️ خطأ التنبيه: {e}")

# ================== 🚀 التشغيل ==================
def start_tg():
    async def run():
        try:
            await client.start()
            print("✅ جاهز — الرسائل الجديدة تظهر في الأسفل ✅")
            await client.run_until_disconnected()
        except Exception as e:
            print(f"❌ خطأ: {e}")
    loop.run_until_complete(run())

if __name__ == '__main__':
    threading.Thread(target=start_tg, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
    
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

# ⚠️ ضع معرف حسابك في التليجرام هنا
YOUR_TELEGRAM_ID = 7553940284  # ❏ مثال: 123456789

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
body{font-family:'Segoe UI',Tahoma,Arial,sans-serif;background:#f0f9ff;color:#334155;margin:0;padding:0;padding-bottom:90px;}
header{background:linear-gradient(135deg,#0ea5e9,#0284c7);color:#fff;text-align:center;padding:15px;position:sticky;top:0;z-index:100;box-shadow:0 2px 10px rgba(0,0,0,0.1);}
header h1{font-size:20px;margin:0;}
.status-bar{text-align:center;padding:8px;font-size:13px;color:#64748b;background:#f8fafc;border-bottom:1px solid #e2e8f0;}
#messages{max-width:700px;margin:20px auto;padding:0 12px;display:flex;flex-direction:column;gap:12px;min-height:300px;}
.msg{background:#fff;padding:14px 18px;border-radius:18px 18px 18px 4px;max-width:90%;align-self:flex-start;box-shadow:0 2px 6px rgba(0,0,0,0.05);line-height:1.6;}
.msg-meta{font-size:11px;margin-bottom:6px;color:#94a3b8;}
.msg-text{white-space:pre-wrap;word-break:break-all;font-size:15px;}
.msg-buttons{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px;}
.bot-btn{background:#e0f2fe;color:#0369a1;border:1px solid #bae6fd;padding:8px 16px;border-radius:20px;font-size:14px;cursor:pointer;transition:0.2s;}
.bot-btn:hover{background:#bae6fd;}
.empty-state{text-align:center;padding:80px 20px;color:#94a3b8;font-size:15px;}
.start-area{position:fixed;bottom:0;left:0;right:0;background:#fff;padding:15px;box-shadow:0 -2px 10px rgba(0,0,0,0.05);text-align:center;z-index:100;}
#start-btn{background:#22c55e;color:#fff;border:none;padding:12px 35px;border-radius:25px;font-size:16px;font-weight:bold;cursor:pointer;transition:0.2s;}
#start-btn:hover{background:#16a34a;}
#start-btn:disabled{background:#94a3b8;cursor:not-allowed;}
.notification-status{text-align:center;padding:6px 12px;font-size:12px;color:#2563eb;background:#eff6ff;border-bottom:1px solid #bfdbfe;display:none;}
</style>
</head>
<body>
<header><h1>💧 رسائل البوت</h1></header>
<div class="notification-status" id="notification-status">🔔 الإشعارات مفعلة ✅</div>
<div class="status-bar" id="status">جاري التحميل...</div>
<div id="messages"><div class="empty-state">📭 لا توجد رسائل حتى الآن — اضغط على زر إرسال /start في الأسفل ✅</div></div>

<div class="start-area">
  <button id="start-btn" onclick="sendStart()">🚀 إرسال /start</button>
</div>

<script>
let lastCount = -1;
let knownIds = new Set();

// ✅ طلب إذن الإشعارات عند فتح الموقع مباشرة
if (Notification.permission === 'default') {
    Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
            document.getElementById('notification-status').style.display = 'block';
        }
    });
} else if (Notification.permission === 'granted') {
    document.getElementById('notification-status').style.display = 'block';
}

// 🔊 دالة صوت التنبيه
function playAlertSound() {
    try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.type = 'sine';
        osc.frequency.value = 700;
        gain.gain.value = 0.3;
        osc.start();
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.5);
        osc.stop(ctx.currentTime + 0.5);
    } catch (e) {}
}

// 🔔 عرض الإشعار
function showNotification(text) {
    playAlertSound();
    if (Notification.permission === 'granted') {
        new Notification("💧 رسالة جديدة من البوت", {
            body: text.length > 50 ? text.substring(0, 50) + "..." : text,
            icon: "https://cdn-icons-png.flaticon.com/512/1005/1005141.png",
            tag: 'new-message'
        });
    }
}

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

async function pressButton(btnText){
  try{
    await fetch('/api/press-button', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({button: btnText})
    });
  }catch(e){
    console.log('خطأ في الضغط على الزر');
  }
}

async function loadMessages(){
  try{
    const res = await fetch('/api/messages');
    const msgs = await res.json();
    document.getElementById('status').innerText = `✅ متصل — عدد الرسائل: ${msgs.length}`;
    
    // التحقق من رسائل جديدة
    const currentIds = new Set(msgs.map(m => m.id));
    
    if (lastCount !== -1 && msgs.length > lastCount) {
        // إيجاد الرسائل الجديدة وعرض إشعار لكل واحدة
        msgs.forEach(m => {
            if (!knownIds.has(m.id)) {
                showNotification(m.text);
            }
        });
    }
    knownIds = currentIds;
    
    if(msgs.length === lastCount) return;
    lastCount = msgs.length;
    
    const container = document.getElementById('messages');
    container.innerHTML = '';
    
    if(msgs.length === 0){
      container.innerHTML = '<div class="empty-state">📭 لا توجد رسائل حتى الآن — اضغط على زر إرسال /start في الأسفل ✅</div>';
    } else {
      msgs.forEach(m=>{
        const d = document.createElement('div');
        d.className = 'msg';
        let html = `
          <div class="msg-meta">💧 البوت • ${m.time || ''}</div>
          <div class="msg-text">${escapeHtml(m.text)}</div>
        `;
        if(m.buttons && m.buttons.length > 0){
          html += '<div class="msg-buttons">';
          m.buttons.forEach(btn => {
            html += `<button class="bot-btn" onclick="pressButton('${escapeJs(btn)}')">${escapeHtml(btn)}</button>`;
          });
          html += '</div>';
        }
        d.innerHTML = html;
        container.appendChild(d);
      });
      
      // تنزيل تلقائي لآخر رسالة
      window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
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

function escapeJs(t){
  return t.replace(/'/g,"\\'").replace(/"/g,'\\"');
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

@app.route('/api/press-button', methods=['POST'])
def press_bot_button():
    data = request.get_json()
    button_text = data.get('button', '')
    
    async def _press():
        async for msg in client.iter_messages(SOURCE_BOT_ID, limit=5):
            if msg.buttons:
                for row in msg.buttons:
                    for btn in row:
                        if btn.text == button_text:
                            await msg.click(btn)
                            return True
        return False
    
    try:
        future = asyncio.run_coroutine_threadsafe(_press(), loop)
        success = future.result(timeout=15)
        return jsonify({"ok": success})
    except Exception as e:
        print(f"❌ خطأ الضغط على الزر: {e}")
        return jsonify({"ok": False})

# ================== 📥 استقبال وتعديل وحذف الرسائل ==================
@client.on(events.NewMessage(from_users=SOURCE_BOT_ID))
async def on_msg(event):
    global messages
    text = event.raw_text
    buttons = []
    if event.message.buttons:
        try:
            buttons = [btn.text for row in event.message.buttons for btn in row if btn.text]
        except:
            pass
    
    new_msg = {
        "id": event.id,
        "text": text,
        "buttons": buttons,
        "time": datetime.now().strftime("%H:%M:%S")
    }
    messages.append(new_msg)
    
    if len(messages) > 500:
        messages = messages[-500:]
    
    save_messages(messages)
    print(f"📥 رسالة جديدة من البوت [ID:{event.id}]: {text[:50]}")
    
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

# ✅ حذف الرسائل المحذوفة من البوت تلقائياً
@client.on(events.MessageDeleted)
async def on_delete(event):
    global messages
    try:
        if event.chat_id and (event.chat_id == SOURCE_BOT_ID or str(event.chat_id) == SOURCE_BOT_ID):
            deleted_ids = event.deleted_ids
            original_len = len(messages)
            messages = [msg for msg in messages if msg.get('id') not in deleted_ids]
            
            if len(messages) != original_len:
                save_messages(messages)
                print(f"🗑️ تم حذف رسالة من الموقع — المعرفات: {deleted_ids}")
    except Exception as e:
        print(f"⚠️ خطأ في حذف الرسائل: {e}")

# ✅ تحديث الرسائل المعدلة من البوت
@client.on(events.MessageEdited(from_users=SOURCE_BOT_ID))
async def on_edit(event):
    global messages
    msg_id = event.id
    new_text = event.raw_text
    buttons = []
    if event.message.buttons:
        try:
            buttons = [btn.text for row in event.message.buttons for btn in row if btn.text]
        except:
            pass
    
    for i, msg in enumerate(messages):
        if msg.get('id') == msg_id:
            messages[i]['text'] = new_text
            messages[i]['buttons'] = buttons
            save_messages(messages)
            print(f"✏️ تم تحديث الرسالة [ID:{msg_id}]")
            break

# ================== 🚀 التشغيل ==================
def start_tg():
    async def run():
        try:
            await client.start()
            print("✅ جاهز — مع إشعارات الموقع + رنين ✅")
            await client.run_until_disconnected()
        except Exception as e:
            print(f"❌ خطأ: {e}")
    loop.run_until_complete(run())

if __name__ == '__main__':
    threading.Thread(target=start_tg, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
    
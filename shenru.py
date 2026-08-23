# SHENRU TOOLS PREMIUM — Gemini Edition (with NGL + SMS Bomber)
from flask import Flask, request, jsonify, render_template_string, send_file, after_this_request
from functools import wraps
import os, re, json, time, uuid, urllib.parse, urllib.request, requests
import google.generativeai as genai
import random

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024

# ── SERVER CONFIG ────────────────────────────────────────────────────────────
PANEL_URL        = os.environ.get("PANEL_URL", "")
PANEL_KEY        = os.environ.get("PANEL_KEY", "")
LIKES_SVC_ID     = os.environ.get("LIKES_SERVICE_ID", "")
FOLLOWERS_SVC_ID = os.environ.get("FOLLOWERS_SERVICE_ID", "")
ACCESS_KEYS      = [k.strip() for k in os.environ.get("ACCESS_KEYS", "").split(",") if k.strip()]
ADMIN_KEY        = os.environ.get("ADMIN_KEY", "")
GEMINI_KEY       = os.environ.get("GEMINI_API_KEY", "")

# ── GEMINI SETUP ──────────────────────────────────────────────────────────────
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    GEMINI_MODEL = genai.GenerativeModel('gemini-3.6-flash')
else:
    GEMINI_MODEL = None

KEYWORDS = [
    "gmail","yahoo","hotmail","outlook","protonmail","icloud","facebook","instagram",
    "tiktok","twitter","reddit","snapchat","discord","steam","spotify","netflix",
    "paypal","payoneer","garena","roblox","apple","amazon","microsoft","google",
    "pinterest","linkedin","twitch","youtube","shopee","lazada","grab","genshin",
    "valorant","epic","origin","ubisoft","blizzard","riot","skype","telegram",
    "whatsapp","viber","coinbase","binance","blockchain","kraken","bybit",
    "uber","airbnb","booking","ebay","etsy","shopify","stripe","wise","revolut",
    "nintendo","playstation","xbox","adobe","canva","notion","figma","github"
]

# ── AUTH HELPERS ────────────────────────────────────────────────────────────
def valid_key(k):
    if not ACCESS_KEYS: return True
    return k in ACCESS_KEYS

def require_key(f):
    @wraps(f)
    def wrap(*a, **kw):
        k = request.headers.get("X-Access-Key", "")
        if not valid_key(k):
            return jsonify(error="Invalid license key"), 403
        return f(*a, **kw)
    return wrap

# ── SMM PANEL HELPER (for TikTok Booster) ────────────────────────────────
def smm(panel_url, key, **params):
    base = panel_url.rstrip("/")
    if not base.endswith("/api/v2"):
        base += "/api/v2"
    r = requests.post(base, data={"key": key, **params}, timeout=20)
    r.raise_for_status()
    return r.json()

# ── NGL SPAMMER ──────────────────────────────────────────────────────────────
def ngl_spam(username, message, count):
    if username.startswith("https://ngl.link/"):
        username = username.replace("https://ngl.link/", "").strip("/")
    url = f"https://ngl.link/{username}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    results = []
    for i in range(min(count, 100)):
        payload = {
            "message": f"{message} {''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=4))}",
            "deviceId": ''.join(random.choices('0123456789abcdef', k=16))
        }
        try:
            r = requests.post(url, data=payload, headers=headers, timeout=10)
            results.append({"attempt": i+1, "status": r.status_code, "ok": r.status_code == 200})
        except:
            results.append({"attempt": i+1, "status": 0, "ok": False})
        time.sleep(0.3)
    return results

# ── SMS BOMBER ──────────────────────────────────────────────────────────────
def sms_bomb(phone, count):
    phone = phone.strip()
    if phone.startswith("0"):
        phone = "63" + phone[1:]  # PH default
    elif not phone.startswith("+"):
        phone = "+63" + phone
    apis = [
        {"url": "https://textbelt.com/text", "method": "POST", "data": {"phone": phone, "message": "Hello from Shenru", "key": "textbelt"}},
        {"url": "https://api.textlocal.com/send", "method": "POST", "data": {"apikey": "test", "numbers": phone, "message": "Hi"}},
        {"url": "https://smsapi.free-mobile.fr/sendmsg", "method": "GET", "params": {"user": "test", "pass": "test", "msg": "Test"}},
    ]
    results = []
    for i in range(min(count, 30)):
        api = random.choice(apis)
        try:
            if api["method"] == "POST":
                r = requests.post(api["url"], data=api["data"], timeout=8)
            else:
                r = requests.get(api["url"], params=api["params"], timeout=8)
            results.append({"attempt": i+1, "status": r.status_code, "ok": r.status_code < 400})
        except:
            results.append({"attempt": i+1, "status": 0, "ok": False})
        time.sleep(0.5)
    return results

# ── GEMINI HELPER ──────────────────────────────────────────────────────────
def gemini_chat(messages, system=None, max_tokens=1500):
    if not GEMINI_KEY or not GEMINI_MODEL:
        raise Exception("GEMINI_API_KEY not configured")
    formatted = ""
    if system:
        formatted += f"System: {system}\n\n"
    for msg in messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        formatted += f"{role}: {msg['content']}\n"
    formatted += "Assistant:"
    response = GEMINI_MODEL.generate_content(
        formatted,
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=0.7,
            top_p=0.95
        )
    )
    if not response.text:
        raise Exception("Empty response from Gemini")
    return response.text

# ─────────────────────────────── HTML ───────────────────────────────────────
HTML = r"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>SHENRU TOOLS — PREMIUM</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#060606;--s1:#0d0d0d;--s2:#111;--s3:#191919;
  --brd:#2a1014;--red:#ff1022;--red2:#ff3040;--dim:rgba(255,16,34,.13);
  --txt:#eeeeee;--mut:#777;--grn:#00e89a;--warn:#ffaa00;--cyan:#00d4e8;--gold:#ffd700;
}
*{box-sizing:border-box;margin:0;padding:0} html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--txt);font:14px Inter,system-ui,sans-serif;min-height:100vh}
::-webkit-scrollbar{width:3px} ::-webkit-scrollbar-thumb{background:var(--red)}
.gate{
  position:fixed;inset:0;z-index:9999;
  background:rgba(4,4,4,.98);
  display:flex;align-items:center;justify-content:center;
}
.gate-box{
  background:var(--s1);border:1px solid #3a1014;border-radius:14px;
  padding:44px 38px;text-align:center;max-width:380px;width:92%;
  box-shadow:0 0 80px rgba(255,16,34,.18);
}
.gate-logo{
  font-family:'Orbitron',sans-serif;font-size:22px;font-weight:900;
  color:var(--red);letter-spacing:.08em;animation:glitch 5s infinite;
}
.gate-sub{color:var(--cyan);font-size:9px;letter-spacing:.22em;margin:5px 0 6px;text-transform:uppercase}
.gate-tier{
  display:inline-block;background:rgba(255,215,0,.08);border:1px solid rgba(255,215,0,.25);
  color:var(--gold);font-size:9px;padding:3px 12px;border-radius:20px;
  margin-bottom:26px;font-family:'Orbitron',sans-serif;letter-spacing:.07em;
}
.gate-box input{
  margin-bottom:12px;border:1px solid #282828;background:#0a0a0a;
  color:var(--txt);border-radius:7px;padding:12px;width:100%;font:inherit;
  outline:none;text-align:center;letter-spacing:.12em;font-size:15px;
  transition:border-color .2s;
}
.gate-box input:focus{border-color:var(--red)}
.gate-box .btn{margin-top:0}
.gate-err{color:var(--red);font-size:11px;margin-top:10px;display:none}
.gate-note{color:var(--mut);font-size:10px;margin-top:14px;line-height:1.6}
.top{
  padding:13px 16px 10px;border-bottom:1px solid var(--brd);
  position:sticky;top:0;background:rgba(6,6,6,.96);backdrop-filter:blur(14px);z-index:100;
  display:flex;align-items:center;gap:14px;flex-wrap:wrap;
}
.brand{font-family:'Orbitron',sans-serif;font-size:clamp(14px,4vw,19px);font-weight:900;
  color:var(--red);letter-spacing:.06em;animation:glitch 5s infinite}
.sub{color:var(--cyan);font-size:9px;letter-spacing:.2em;margin-top:2px;text-transform:uppercase}
.brand-block{flex-shrink:0}
@keyframes glitch{
  0%,84%,100%{text-shadow:0 0 14px rgba(255,16,34,.4)}
  85%{text-shadow:-3px 0 var(--red),3px 0 #003fff30;letter-spacing:.09em}
  87%{text-shadow:3px 0 var(--red),-3px 0 #003fff30;letter-spacing:.04em}
  89%{text-shadow:0 0 14px rgba(255,16,34,.4);letter-spacing:.06em}
}
.player{display:flex;align-items:center;gap:10px;flex:1;min-width:220px}
.disc-wrap{position:relative;flex-shrink:0;cursor:pointer;width:42px;height:42px}
.disc{
  width:42px;height:42px;border-radius:50%;border:2px solid #2a1014;
  background:radial-gradient(circle at 35% 35%,#2a2a2a,#0d0d0d);
  display:flex;align-items:center;justify-content:center;font-size:17px;transition:border-color .3s;
}
.disc-wrap:hover .disc{border-color:var(--red)}
.disc.spin{animation:dspin 3s linear infinite;border-color:var(--red)}
@keyframes dspin{to{transform:rotate(360deg)}}
.p-info{flex:1;min-width:0}
.p-title{font-size:12px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.p-sub{font-size:9px;color:var(--mut);margin-top:2px}
.ctrl{display:flex;gap:2px;align-items:center}
.cb{background:none;border:none;color:var(--mut);cursor:pointer;width:26px;height:26px;
  border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;
  transition:color .2s,background .2s}
.cb:hover{color:var(--txt);background:var(--s3)}
.cb.play{color:var(--red);background:rgba(255,16,34,.15);font-size:14px;width:30px;height:30px}
.cb.play:hover{background:var(--red);color:#fff}
.p-badges{display:flex;align-items:center;gap:8px;flex-shrink:0}
.pill{font-family:'Orbitron',sans-serif;font-size:10px;border:1px solid var(--red);
  color:var(--red);padding:4px 10px;border-radius:20px}
.pill.gold{border-color:rgba(255,215,0,.5);color:var(--gold);background:rgba(255,215,0,.05)}
.pill.disabled{border-color:#555;color:#555;background:rgba(255,255,255,.05)}
.dot{width:6px;height:6px;border-radius:50%;background:var(--grn);
  animation:pdot 2s infinite;box-shadow:0 0 6px var(--grn)}
@keyframes pdot{50%{opacity:.5;box-shadow:0 0 0 5px rgba(0,232,154,0)}}
.wrap{max-width:1080px;margin:auto;padding:14px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:11px}
.card{
  background:linear-gradient(145deg,var(--s1),var(--s2));
  border:1px solid var(--brd);border-radius:8px;padding:15px;
  position:relative;overflow:hidden;transition:border-color .3s,box-shadow .3s;
}
.card::before{
  content:'';position:absolute;left:0;top:100%;width:2px;height:100%;
  background:var(--red);transition:top .35s cubic-bezier(.4,0,.2,1);
}
.card:hover{border-color:#5a1820;box-shadow:0 0 22px var(--dim)}
.card:hover::before{top:0}
.card.full{grid-column:1/-1}
.card.disabled-card{opacity:0.6;pointer-events:none}
.card.disabled-card .badge.disabled{display:inline-block}
h2{font-family:'Orbitron',sans-serif;font-size:11px;margin-bottom:12px;letter-spacing:.08em;font-weight:700;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.ico{color:var(--red);margin-right:6px}
.badge{font-family:'Orbitron',sans-serif;font-size:8px;padding:2px 10px;border-radius:20px;background:rgba(255,215,0,.1);border:1px solid var(--gold);color:var(--gold)}
.badge.disabled{background:rgba(255,0,0,.1);border-color:#ff4444;color:#ff4444;display:none}
label{display:block;color:#999;font-size:10px;margin:8px 0 4px;letter-spacing:.04em;text-transform:uppercase}
input[type=text],input[type=url],input[type=number],input[type=password],textarea{
  width:100%;border:1px solid #282828;background:#111;color:var(--txt);
  border-radius:6px;padding:10px 12px;font:inherit;outline:none;
  transition:border-color .2s,box-shadow .2s;
}
input:focus,textarea:focus{border-color:#7b1720;box-shadow:0 0 0 2px rgba(255,16,34,.08)}
textarea{min-height:90px;resize:vertical;font-size:12px;font-family:'Courier New',monospace}
.row{display:flex;gap:8px;flex-wrap:wrap} .row>*{flex:1;min-width:120px}
.btn{
  width:100%;margin-top:10px;border:0;border-radius:6px;padding:11px 14px;
  background:linear-gradient(90deg,#d40d1e,var(--red));color:#fff;
  font-family:'Orbitron',sans-serif;font-weight:700;font-size:10px;letter-spacing:.1em;
  cursor:pointer;transition:all .2s;display:flex;align-items:center;justify-content:center;gap:8px;
}
.btn:hover{background:linear-gradient(90deg,var(--red),#ff4040);box-shadow:0 0 18px var(--dim)}
.btn:active{transform:scale(.98)}
.btn:disabled{background:#222;color:#555;cursor:not-allowed;box-shadow:none}
.btn.alt{background:#111;border:1px solid #3b181c;color:var(--mut)}
.btn.alt:hover{border-color:var(--red);color:var(--txt)}
.btn-sm{margin-top:0;padding:7px 14px;width:auto;font-size:9px}
.ld::after{
  content:'';display:inline-block;width:12px;height:12px;margin-left:8px;
  border:2px solid rgba(255,255,255,.3);border-top-color:#fff;
  border-radius:50%;animation:dspin .6s linear infinite;
}
.type-row{display:flex;gap:8px;margin-top:4px}
.ttype{
  flex:1;padding:10px;border:1px solid #282828;background:#111;color:var(--mut);
  border-radius:6px;cursor:pointer;font-family:'Orbitron',sans-serif;font-size:10px;
  letter-spacing:.06em;transition:all .2s;text-align:center;
}
.ttype.on{border-color:var(--red);background:rgba(255,16,34,.1);color:var(--red)}
.ttype:hover{border-color:#5a1820;color:var(--txt)}
.qty-row{display:flex;gap:6px;flex-wrap:wrap;margin-top:4px}
.qp{
  padding:7px 13px;border:1px solid #282828;background:#111;color:var(--mut);
  border-radius:5px;cursor:pointer;font-size:11px;transition:all .2s;
}
.qp.on{border-color:var(--red);background:rgba(255,16,34,.1);color:var(--red)}
.qp:hover{border-color:#5a1820;color:var(--txt)}
.order-bar{
  display:none;margin-top:10px;background:#080e10;border:1px solid #1a3040;
  border-radius:6px;padding:10px 12px;align-items:center;gap:10px;flex-wrap:wrap;
}
.order-bar.show{display:flex}
.oid-val{font-family:'Courier New',monospace;font-size:13px;color:var(--cyan)}
.osticker{
  font-family:'Orbitron',sans-serif;font-size:9px;letter-spacing:.06em;
  padding:3px 9px;border-radius:4px;
}
.s-pend{background:rgba(255,170,0,.12);color:var(--warn)}
.s-done{background:rgba(0,232,154,.1);color:var(--grn)}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:12px}
.stat{background:#0a0a0a;border:1px solid #1c1c1c;border-radius:6px;padding:10px;text-align:center}
.stat b{font-family:'Orbitron',sans-serif;font-size:16px;color:var(--red);display:block}
.stat span{color:var(--mut);font-size:9px;letter-spacing:.05em;text-transform:uppercase}
.result{
  margin-top:10px;border:1px dashed #252525;background:#08080a;padding:10px;
  border-radius:6px;white-space:pre-wrap;word-break:break-word;color:#cfcfcf;
  font-family:'Courier New',monospace;font-size:11px;max-height:260px;overflow:auto;display:none;
}
.result.show{display:block} .ok{color:var(--grn)} .err{color:var(--red)}
.cbox{
  height:270px;overflow-y:auto;padding:10px;background:#090909;
  border:1px solid #1c1c1c;border-radius:6px;display:flex;flex-direction:column;gap:8px;
}
.bbl{max-width:86%;padding:8px 12px;border-radius:10px;font-size:13px;line-height:1.5}
.bbl.u{background:var(--red);color:#fff;align-self:flex-end;border-bottom-right-radius:3px}
.bbl.a{background:var(--s3);color:var(--txt);align-self:flex-start;border-bottom-left-radius:3px}
.bbl .lbl{font-size:8px;color:rgba(255,255,255,.4);font-family:'Orbitron',sans-serif;letter-spacing:.06em;margin-bottom:3px}
.chat-row{display:flex;gap:6px;margin-top:8px}
.chat-row input{flex:1}
.sbtn{width:40px;border:none;background:var(--red);color:#fff;border-radius:6px;cursor:pointer;font-size:15px;flex-shrink:0;transition:background .2s}
.sbtn:hover{background:var(--red2)}
#toasts{position:fixed;top:14px;right:14px;z-index:9999;display:flex;flex-direction:column;gap:6px}
.toast{background:var(--s2);border-left:3px solid var(--red);padding:9px 14px;border-radius:5px;
  font-size:12px;animation:tslide .2s ease;max-width:260px;box-shadow:0 4px 20px #0009}
.toast.ok{border-color:var(--grn)} .toast.warn{border-color:var(--warn)}
@keyframes tslide{from{opacity:0;transform:translateX(16px)}}
@media(max-width:680px){
  .grid{grid-template-columns:1fr} .card.full{grid-column:auto}
  .top{padding:10px 12px 8px} .player{min-width:100%;order:3}
  .brand-block{order:1} .p-badges{order:2;margin-left:auto}
  .stats{grid-template-columns:1fr 1fr}
}
</style>
</head>
<body>
<div class="gate" id="gate">
  <div class="gate-box">
    <div class="gate-logo">SHENRU TOOLS</div>
    <div class="gate-sub">boost your life</div>
    <div class="gate-tier">⭐ PREMIUM ACCESS</div>
    <input type="password" id="gkey" placeholder="Enter license key…" onkeydown="if(event.key==='Enter')tryKey()">
    <button class="btn" onclick="tryKey()">⚡ UNLOCK ACCESS</button>
    <div class="gate-err" id="gerr">❌ Invalid license key — contact support</div>
    <div class="gate-note">Premium tool by Shenru &nbsp;·&nbsp; contact to purchase access</div>
  </div>
</div>
<div id="toasts"></div>
<header class="top">
  <div class="brand-block">
    <div class="brand">SHENRU TOOLS</div>
    <div class="sub">boost your life</div>
  </div>
  <div class="player">
    <div class="disc-wrap" onclick="document.getElementById('afiles').click()" title="Add music">
      <div class="disc" id="disc">🎵</div>
      <input type="file" id="afiles" accept="audio/*" multiple hidden>
    </div>
    <div class="p-info">
      <div class="p-title" id="ptitle">No music loaded</div>
      <div class="p-sub" id="psub">Click disc to add songs</div>
    </div>
    <div class="ctrl">
      <button class="cb" onclick="P.prev()">⏮</button>
      <button class="cb play" id="pbtn" onclick="P.toggle()">▶</button>
      <button class="cb" onclick="P.next()">⏭</button>
    </div>
    <audio id="aud"></audio>
  </div>
  <div class="p-badges">
    <div class="dot"></div>
    <div class="pill gold">⭐ PREMIUM</div>
    <div class="pill">⚡ LIFETIME</div>
  </div>
</header>
<main class="wrap"><div class="grid">

<!-- ═══ TIKTOK BOOSTER — NOT AVAILABLE ════════════════════════════════════ -->
<section class="card full disabled-card">
  <h2><span class="ico">⚡</span>TIKTOK BOOSTER <span class="badge disabled">⚠️ NOT AVAILABLE</span></h2>
  <div class="stats">
    <div class="stat"><b id="st-sent">0</b><span>Orders Sent</span></div>
    <div class="stat"><b id="st-likes">0</b><span>Likes Boosted</span></div>
    <div class="stat"><b id="st-foll">0</b><span>Followers Boosted</span></div>
  </div>
  <label>TikTok URL / Username</label>
  <input type="url" id="tt-link" placeholder="https://tiktok.com/@username" disabled>
  <label>Boost Type</label>
  <div class="type-row">
    <div class="ttype" style="opacity:0.4">❤️ LIKES</div>
    <div class="ttype" style="opacity:0.4">👤 FOLLOWERS</div>
  </div>
  <label>Quantity</label>
  <div class="qty-row">
    <div class="qp" style="opacity:0.4">100</div>
    <div class="qp" style="opacity:0.4">500</div>
    <div class="qp" style="opacity:0.4">1K</div>
  </div>
  <button class="btn" disabled style="background:#222;color:#555">⛔ COMING SOON</button>
  <div class="result" id="boost-result"></div>
</section>

<!-- ═══ NGL SPAMMER ════════════════════════════════════════════════════════ -->
<section class="card">
  <h2><span class="ico">💬</span>NGL SPAMMER</h2>
  <label>NGL Username or Link</label>
  <input type="text" id="ngl-username" placeholder="@username or https://ngl.link/username">
  <label>Anonymous Message</label>
  <input type="text" id="ngl-message" placeholder="Your anonymous message...">
  <label>Spam Count</label>
  <input type="number" id="ngl-count" value="10" min="1" max="100">
  <button class="btn" id="ngl-btn" onclick="sendNGL()">📨 &nbsp;SEND SPAM</button>
  <div class="result" id="ngl-result"></div>
</section>

<!-- ═══ SMS BOMBER ═════════════════════════════════════════════════════════ -->
<section class="card">
  <h2><span class="ico">📱</span>SMS BOMBER</h2>
  <label>Phone Number</label>
  <input type="text" id="sms-phone" placeholder="09123456789 or +639123456789">
  <label>Bomb Count</label>
  <input type="number" id="sms-count" value="10" min="1" max="30">
  <button class="btn" id="sms-btn" onclick="sendSMS()">💥 &nbsp;SEND SMS BOMB</button>
  <div class="result" id="sms-result"></div>
</section>

<!-- ═══ VIDEO DOWNLOADER ═══════════════════════════════════════════════════ -->
<section class="card">
  <h2><span class="ico">🎥</span>VIDEO DOWNLOADER</h2>
  <div style="font-size:9px;color:var(--mut);margin-bottom:8px">TikTok · YouTube · Instagram · Facebook · Twitter · Reddit · Twitch · 1000+ sites</div>
  <label>Video URL</label>
  <input type="url" id="vid-url" placeholder="Paste video URL…">
  <button class="btn" id="vid-btn" onclick="dlVideo()">⬇ &nbsp;DOWNLOAD VIDEO</button>
  <div class="result" id="vid-result"></div>
</section>

<!-- ═══ TEXT SPLITTER ═════════════════════════════════════════════════════ -->
<section class="card">
  <h2><span class="ico">✂</span>TEXT SPLITTER</h2>
  <label>Paste text / file contents</label>
  <textarea id="sp-txt" placeholder="Paste lines here…"></textarea>
  <div class="row" style="align-items:flex-end;margin-top:6px">
    <div><label>Lines per part</label><input type="number" id="sp-n" value="1000" min="1"></div>
    <button class="btn" style="margin-top:0;align-self:flex-end" onclick="splitTxt()">✂ SPLIT</button>
  </div>
  <div class="result" id="sp-result"></div>
</section>

<!-- ═══ TEXT SEPARATOR ════════════════════════════════════════════════════ -->
<section class="card">
  <h2><span class="ico">🔤</span>TEXT SEPARATOR</h2>
  <label>Text</label>
  <textarea id="sep-txt" placeholder="Paste lines here…"></textarea>
  <label>Keywords — comma separated (blank = auto 60+ keywords)</label>
  <input type="text" id="sep-kw" placeholder="gmail,facebook,discord,spotify…">
  <button class="btn" onclick="separateTxt()">🔀 &nbsp;SEPARATE</button>
  <div class="result" id="sep-result"></div>
</section>

<!-- ═══ URL SHORTENER ═════════════════════════════════════════════════════ -->
<section class="card">
  <h2><span class="ico">🔗</span>URL SHORTENER</h2>
  <label>Long URL</label>
  <input type="url" id="s-url" placeholder="https://example.com/very/long/url">
  <button class="btn" id="s-btn" onclick="shortenURL()">🔗 &nbsp;SHORTEN</button>
  <div class="result" id="s-result"></div>
</section>

<!-- ═══ AI CHAT ════════════════════════════════════════════════════════════ -->
<section class="card full">
  <h2><span class="ico">🤖</span>AI CHAT — Gemini</h2>
  <div class="cbox" id="cbox">
    <div class="bbl a"><div class="lbl">SHENRU AI</div>Wazzup! I'm your AI assistant powered by Gemini. Ask me anything 🔥</div>
  </div>
  <div class="chat-row">
    <input type="text" id="cmsg" placeholder="Type a message…" onkeydown="if(event.key==='Enter')sendChat()">
    <button class="sbtn" onclick="sendChat()">➤</button>
  </div>
</section>

<!-- ═══ AI HUMANIZER ══════════════════════════════════════════════════════ -->
<section class="card">
  <h2><span class="ico">✍️</span>AI HUMANIZER</h2>
  <label>AI-generated text</label>
  <textarea id="hum-in" placeholder="Paste AI text here…"></textarea>
  <button class="btn" id="hum-btn" onclick="aiHumanize()">✨ &nbsp;HUMANIZE</button>
  <div class="result" id="hum-out"></div>
</section>

<!-- ═══ AI DETECTOR ════════════════════════════════════════════════════════ -->
<section class="card">
  <h2><span class="ico">🔍</span>AI DETECTOR</h2>
  <label>Text to analyze</label>
  <textarea id="det-in" placeholder="Paste text here…"></textarea>
  <button class="btn" id="det-btn" onclick="aiDetect()">🔍 &nbsp;DETECT</button>
  <div class="result" id="det-out"></div>
</section>

</div></main>
<script>
const $=id=>document.getElementById(id);
let KEY=localStorage.getItem('sh_key')||'';
let stats={sent:0,likes:0,foll:0};

async function apiCall(path,data){
  const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json','X-Access-Key':KEY},body:JSON.stringify(data||{})});
  return await r.json();
}
function show(id,txt,cls=''){const el=$(id);el.className='result show '+cls;el.textContent=typeof txt==='string'?txt:JSON.stringify(txt,null,2);}
function toast(msg,type=''){const el=document.createElement('div');el.className='toast '+type;el.textContent=msg;$('toasts').appendChild(el);setTimeout(()=>el.remove(),3000);}
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g,'<br>');}
function setLD(btn,on){btn.disabled=on;on?btn.classList.add('ld'):btn.classList.remove('ld');}

async function tryKey(){
  const k=$('gkey').value.trim();if(!k)return;
  const r=await fetch('/api/auth',{method:'POST',headers:{'Content-Type':'application/json','X-Access-Key':k},body:'{}'});
  const d=await r.json();
  if(d.ok){KEY=k;localStorage.setItem('sh_key',k);$('gate').style.display='none';toast('Access granted 🔓','ok');}
  else{$('gerr').style.display='block';$('gkey').style.borderColor='var(--red)';}
}
async function checkStoredKey(){if(!KEY)return;const r=await fetch('/api/auth',{method:'POST',headers:{'Content-Type':'application/json','X-Access-Key':KEY},body:'{}'});const d=await r.json();if(d.ok){$('gate').style.display='none';}else{KEY='';localStorage.removeItem('sh_key');}}

const P={pl:[],cur:0,get audio(){return $('aud')},init(){$('afiles').addEventListener('change',e=>this.load(e.target.files));this.audio.addEventListener('ended',()=>this.next());},load(files){const s=this.pl.length;Array.from(files).forEach(f=>this.pl.push({url:URL.createObjectURL(f),name:f.name.replace(/\.[^.]+$/,'')}));toast(files.length+' track(s) loaded 🎵','ok');if(s===0)this.set(0);},set(i){if(!this.pl.length)return;this.cur=((i%this.pl.length)+this.pl.length)%this.pl.length;const t=this.pl[this.cur];this.audio.src=t.url;$('ptitle').textContent=t.name;$('psub').textContent='Track '+(this.cur+1)+' / '+this.pl.length;this.play();},play(){this.audio.play().catch(()=>{});$('pbtn').textContent='⏸';$('disc').classList.add('spin');},pause(){this.audio.pause();$('pbtn').textContent='▶';$('disc').classList.remove('spin');},toggle(){this.audio.paused?this.play():this.pause();},prev(){this.set(this.cur-1);},next(){this.set(this.cur+1);}};

// ─── NGL SPAMMER ───────────────────────────────────────────────────────────
async function sendNGL(){
  const username=$('ngl-username').value.trim();
  const message=$('ngl-message').value.trim();
  const count=parseInt($('ngl-count').value)||10;
  if(!username)return toast('Enter NGL username','warn');
  if(!message)return toast('Enter a message','warn');
  const btn=$('ngl-btn');setLD(btn,true);
  show('ngl-result','⏳ Sending spam...','warn');
  try{
    const d=await apiCall('/api/ngl',{username,message,count});
    show('ngl-result',JSON.stringify(d,null,2),d.error?'err':'ok');
    if(!d.error)toast('NGL spam sent! 📨','ok');
  }catch(e){show('ngl-result','❌ '+e.message,'err');}
  setLD(btn,false);
}

// ─── SMS BOMBER ────────────────────────────────────────────────────────────
async function sendSMS(){
  const phone=$('sms-phone').value.trim();
  const count=parseInt($('sms-count').value)||10;
  if(!phone)return toast('Enter a phone number','warn');
  const btn=$('sms-btn');setLD(btn,true);
  show('sms-result','⏳ Sending SMS bomb...','warn');
  try{
    const d=await apiCall('/api/sms',{phone,count});
    show('sms-result',JSON.stringify(d,null,2),d.error?'err':'ok');
    if(!d.error)toast('SMS bomb sent! 💥','ok');
  }catch(e){show('sms-result','❌ '+e.message,'err');}
  setLD(btn,false);
}

// ─── VIDEO DOWNLOADER ─────────────────────────────────────────────────────
async function dlVideo(){
  const url=$('vid-url').value.trim();
  if(!url)return toast('Enter a URL','warn');
  const btn=$('vid-btn');setLD(btn,true);
  show('vid-result','⏳ Downloading…','warn');
  try{
    const r=await fetch('/api/video',{method:'POST',headers:{'Content-Type':'application/json','X-Access-Key':KEY},body:JSON.stringify({url})});
    if(!r.ok){const e=await r.json();throw new Error(e.error);}
    const cd=r.headers.get('Content-Disposition')||'';const m=cd.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
    const fn=m?m[1].replace(/['"]/g,''):'video.mp4';const blob=await r.blob();
    const a=Object.assign(document.createElement('a'),{href:URL.createObjectURL(blob),download:fn});
    document.body.appendChild(a);a.click();document.body.removeChild(a);
    setTimeout(()=>URL.revokeObjectURL(a.href),2000);
    show('vid-result','✅ Downloaded: '+fn,'ok');toast('Video saved!','ok');
  }catch(e){show('vid-result','❌ '+e.message,'err');}
  setLD(btn,false);
}

// ─── TEXT TOOLS ───────────────────────────────────────────────────────────
async function splitTxt(){const text=$('sp-txt').value,n=parseInt($('sp-n').value)||1000;if(!text.trim())return toast('Paste some text','warn');const d=await apiCall('/api/split',{text,lines:n});show('sp-result',d.output||d.error||'Done');}
async function separateTxt(){const text=$('sep-txt').value,kw=$('sep-kw').value;if(!text.trim())return toast('Paste some text','warn');const d=await apiCall('/api/separate',{text,keywords:kw});show('sep-result',d.output||d.error||'Done');}
async function shortenURL(){const url=$('s-url').value.trim();if(!url)return toast('Enter a URL','warn');const btn=$('s-btn');setLD(btn,true);const d=await apiCall('/api/shorten',{url});show('s-result',d.output||d.error,d.output?'ok':'err');setLD(btn,false);}

// ─── AI CHAT ──────────────────────────────────────────────────────────────
const chatHist=[];async function sendChat(){const inp=$('cmsg'),msg=inp.value.trim();if(!msg)return;inp.value='';const box=$('cbox');const add=(html,cls)=>{const el=document.createElement('div');el.className='bbl '+cls;el.innerHTML=html;box.appendChild(el);box.scrollTop=box.scrollHeight;return el;};add(esc(msg),'u');chatHist.push({role:'user',content:msg});const typing=add('<div class="lbl">SHENRU AI</div><em style="color:var(--mut)">thinking…</em>','a');try{const d=await apiCall('/api/chat',{message:msg,history:chatHist.slice(0,-1)});if(d.error)throw new Error(d.error);typing.innerHTML='<div class="lbl">SHENRU AI</div>'+esc(d.response);chatHist.push({role:'assistant',content:d.response});if(chatHist.length>40)chatHist.splice(0,2);}catch(e){typing.innerHTML='<div class="lbl">SHENRU AI</div><span class="err">'+esc(e.message)+'</span>';chatHist.pop();}box.scrollTop=box.scrollHeight;}
async function aiHumanize(){const text=$('hum-in').value.trim();if(!text)return toast('Paste some text','warn');const btn=$('hum-btn');setLD(btn,true);show('hum-out','⏳ Humanizing…','warn');const d=await apiCall('/api/ai',{mode:'humanize',text});show('hum-out',d.output||d.error,d.output?'':'err');setLD(btn,false);}
async function aiDetect(){const text=$('det-in').value.trim();if(!text)return toast('Paste some text','warn');const btn=$('det-btn');setLD(btn,true);show('det-out','⏳ Analyzing…','warn');const d=await apiCall('/api/ai',{mode:'detect',text});show('det-out',d.output||d.error,d.output?'':'err');setLD(btn,false);}
window.addEventListener('DOMContentLoaded',async()=>{await checkStoredKey();P.init();});
</script>
</body>
</html>
"""

# ─────────────────────────── ROUTES ────────────────────────────────────────

@app.get("/")
def home():
    return render_template_string(HTML)

@app.post("/api/auth")
def auth():
    k = request.headers.get("X-Access-Key", "")
    return jsonify(ok=valid_key(k), mode="open" if not ACCESS_KEYS else "keyed")

# ── NGL SPAMMER ──────────────────────────────────────────────────────────────
@app.post("/api/ngl")
@require_key
def ngl_endpoint():
    d = request.get_json(force=True)
    username = d.get("username", "").strip()
    message = d.get("message", "").strip()
    count = max(1, min(int(d.get("count", 10)), 100))
    if not username or not message:
        return jsonify(error="Username and message required")
    try:
        results = ngl_spam(username, message, count)
        success = sum(1 for r in results if r.get("ok"))
        return jsonify(total=len(results), success=success, results=results[:20])
    except Exception as e:
        return jsonify(error=str(e)), 500

# ── SMS BOMBER ──────────────────────────────────────────────────────────────
@app.post("/api/sms")
@require_key
def sms_endpoint():
    d = request.get_json(force=True)
    phone = d.get("phone", "").strip()
    count = max(1, min(int(d.get("count", 10)), 30))
    if not phone:
        return jsonify(error="Phone number required")
    try:
        results = sms_bomb(phone, count)
        success = sum(1 for r in results if r.get("ok"))
        return jsonify(total=len(results), success=success, results=results[:20])
    except Exception as e:
        return jsonify(error=str(e)), 500

# ── TIKTOK BOOSTER (DISABLED) ───────────────────────────────────────────────
@app.post("/api/boost/order")
@require_key
def boost_order():
    return jsonify(error="TikTok Booster is currently under maintenance. Coming soon!"), 503

@app.post("/api/boost/status")
@require_key
def boost_status():
    return jsonify(error="TikTok Booster is currently under maintenance. Coming soon!"), 503

# ── VIDEO DOWNLOADER ─────────────────────────────────────────────────────────
@app.post("/api/video")
@require_key
def video():
    try:
        import yt_dlp
    except ImportError:
        return jsonify(error="Install yt-dlp: pip install yt-dlp"), 500
    d = request.get_json(force=True)
    url = d.get("url", "").strip()
    if not url:
        return jsonify(error="No URL"), 400
    tmp = f"/tmp/shenru_{uuid.uuid4()}"
    opts = {"format": "best[ext=mp4]/best", "outtmpl": f"{tmp}.%(ext)s", "noplaylist": True, "quiet": True}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            ext = info.get("ext", "mp4")
            name = info.get("title", "video")[:80]
        path = f"{tmp}.{ext}"
        if not os.path.exists(path):
            for p in [f"{tmp}.mp4", f"{tmp}.webm", f"{tmp}.mkv"]:
                if os.path.exists(p):
                    path = p
                    ext = p.split(".")[-1]
                    break
        @after_this_request
        def _clean(r):
            try:
                os.remove(path)
            except:
                pass
            return r
        return send_file(path, as_attachment=True, download_name=f"{name}.{ext}")
    except Exception as e:
        return jsonify(error=str(e)), 500

# ── TEXT SPLIT ───────────────────────────────────────────────────────────────
@app.post("/api/split")
@require_key
def split():
    d = request.get_json(force=True)
    text = str(d.get("text", ""))
    n = max(1, min(int(d.get("lines", 1000)), 100000))
    if not text:
        return jsonify(error="No text")
    lines = text.splitlines()
    chunks = [lines[i:i+n] for i in range(0, len(lines), n)]
    out = [f"--- PART {i}/{len(chunks)} ({len(c)} lines) ---\n" + "\n".join(c) for i, c in enumerate(chunks, 1)]
    return jsonify(output="\n\n".join(out), parts=len(chunks))

# ── TEXT SEPARATE ────────────────────────────────────────────────────────────
@app.post("/api/separate")
@require_key
def separate():
    d = request.get_json(force=True)
    text = str(d.get("text", ""))
    raw = str(d.get("keywords", "")).strip()
    kws = [x.strip().lower() for x in raw.split(",") if x.strip()] or KEYWORDS
    if not text:
        return jsonify(error="No text")
    buckets = {k: [] for k in kws}
    other = []
    for line in text.splitlines():
        low = line.lower()
        hit = next((k for k in kws if k in low), None)
        (buckets[hit] if hit else other).append(line)
    out = [f"[{k.upper()}] {len(v)} lines\n" + "\n".join(v[:3000]) for k, v in buckets.items() if v]
    out.append(f"[OTHER] {len(other)} lines\n" + "\n".join(other[:3000]))
    return jsonify(output="\n\n".join(out))

# ── URL SHORTENER ────────────────────────────────────────────────────────────
@app.post("/api/shorten")
@require_key
def shorten():
    d = request.get_json(force=True)
    url = str(d.get("url", "")).strip()
    p = urllib.parse.urlparse(url)
    if p.scheme not in ("http", "https") or not p.netloc:
        return jsonify(error="Enter a valid http/https URL")
    try:
        q = urllib.parse.urlencode({"format": "simple", "url": url})
        req = urllib.request.Request("https://is.gd/create.php?" + q, headers={"User-Agent": "Shenru/1.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            short = r.read().decode().strip()
        return jsonify(output=short) if short.startswith("http") else jsonify(error=short)
    except Exception as e:
        return jsonify(error=str(e))

# ── AI CHAT ───────────────────────────────────────────────────────────────────
@app.post("/api/chat")
@require_key
def chat():
    if not GEMINI_KEY:
        return jsonify(error="Set GEMINI_API_KEY env var")
    d = request.get_json(force=True)
    msg = d.get("message", "").strip()
    hist = d.get("history", [])[-20:]
    if not msg:
        return jsonify(error="Empty")
    try:
        response = gemini_chat(
            hist + [{"role": "user", "content": msg}],
            system="You are a helpful, intelligent assistant named Shenru AI. Be concise, friendly, and accurate."
        )
        return jsonify(response=response)
    except Exception as e:
        return jsonify(error=str(e))

@app.post("/api/ai")
@require_key
def ai():
    if not GEMINI_KEY:
        return jsonify(output="⚠️ Set GEMINI_API_KEY to enable AI.")
    d = request.get_json(force=True)
    mode = d.get("mode", "")
    text = str(d.get("text", "")).strip()
    if not text:
        return jsonify(error="No text")
    try:
        if mode == "humanize":
            prompt = (
                "Rewrite this AI-generated text to sound completely human, like a native English speaker. "
                "Remove all robotic patterns, repetitive structures, and overused phrases. "
                "Add natural flow, personal touch, and varied sentence structure. "
                "Return ONLY the rewritten text, no explanations or labels:\n\n" + text
            )
        else:
            prompt = (
                "Analyze this text and determine if it was written by an AI or a human. "
                "Return your response in EXACTLY this format:\n"
                "Score: [0-100]%\n"
                "Verdict: [AI-GENERATED or HUMAN-WRITTEN]\n"
                "Indicators:\n"
                "- [indicator 1]\n"
                "- [indicator 2]\n"
                "- [indicator 3]\n\n"
                "Text:\n" + text
            )
        response = gemini_chat(
            [{"role": "user", "content": prompt}],
            system="You are an expert text analyst. Be objective and concise.",
            max_tokens=2000
        )
        return jsonify(output=response)
    except Exception as e:
        return jsonify(error=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

from flask import Flask, request, jsonify, render_template_string
import qrcode
import io
import base64
import urllib.parse
import secrets
import time

app = Flask(__name__)

SHOP_NAME = "Imad Akhtar"
UPI_ID = "8292746662@axl"
HOST = "0.0.0.0"
PORT = 5010
SESSION_SECONDS = 300
sessions = {}

PAGE = r"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<meta name="theme-color" content="#080b14">
<title>SecurePay</title>
<style>
:root{
--bg:#070a12;--card:rgba(18,24,39,.82);--line:rgba(255,255,255,.09);
--text:#f8fafc;--muted:#94a3b8;--a:#7180ff;--b:#9b5cff;
--green:#39e58c;--red:#ff6680;--white:#fff
}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{margin:0;min-height:100%;background:var(--bg)}
body{font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,Arial;color:var(--text);overflow-x:hidden}
body:before,body:after{content:"";position:fixed;border-radius:50%;filter:blur(55px);pointer-events:none;z-index:0}
body:before{width:240px;height:240px;left:-100px;top:80px;background:#4d5cff55;animation:float1 9s ease-in-out infinite}
body:after{width:260px;height:260px;right:-120px;top:48%;background:#9b5cff44;animation:float2 11s ease-in-out infinite}
@keyframes float1{50%{transform:translate(35px,40px) scale(1.15)}}
@keyframes float2{50%{transform:translate(-30px,-45px) scale(.9)}}
.app{position:relative;z-index:1;max-width:470px;min-height:100vh;margin:auto;padding:16px 15px 28px;display:flex;flex-direction:column}
.top{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;animation:down .7s cubic-bezier(.16,1,.3,1)}
.brand{display:flex;align-items:center;gap:10px}
.logo{width:44px;height:44px;border-radius:15px;display:grid;place-items:center;font-size:21px;background:linear-gradient(135deg,var(--a),var(--b));box-shadow:0 12px 35px #7180ff38;animation:logo 4s ease-in-out infinite}
@keyframes logo{50%{transform:translateY(-2px) rotate(2deg)}}
.name{font-weight:850;font-size:17px}.sub{font-size:10px;color:var(--muted);margin-top:2px}
.ready{display:flex;align-items:center;gap:6px;border:1px solid var(--line);background:#ffffff08;padding:8px 10px;border-radius:99px;font-size:9px}
.dot{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 13px var(--green);animation:pulse 1.8s infinite}
@keyframes pulse{50%{opacity:.4;transform:scale(.65)}}
.screen{display:none;animation:screen .55s cubic-bezier(.16,1,.3,1)}.screen.active{display:block}
@keyframes screen{from{opacity:0;transform:translateY(22px) scale(.97)}to{opacity:1;transform:none}}
.hero{padding:12px 4px 18px}.eyebrow{font-size:10px;font-weight:800;letter-spacing:1px;color:#aeb8ff}
h1{font-size:34px;line-height:1.03;letter-spacing:-1.7px;margin:7px 0}.hero p{font-size:13px;line-height:1.5;color:var(--muted);margin:0}
.card{background:linear-gradient(145deg,#ffffff0d,#ffffff03);border:1px solid var(--line);border-radius:28px;padding:20px;backdrop-filter:blur(24px);box-shadow:0 25px 70px #0008;overflow:hidden}
.merchant{display:flex;align-items:center;gap:11px;margin-bottom:20px}.merchant-icon{width:48px;height:48px;border-radius:16px;display:grid;place-items:center;background:#7180ff18;border:1px solid var(--line);font-size:21px}
.merchant-name{font-size:15px;font-weight:800}.merchant-upi{font-size:10px;color:var(--muted);margin-top:3px}
.label{font-size:10px;font-weight:800;color:#94a3b8;letter-spacing:.7px;margin-bottom:8px}
.amountbox{position:relative}.currency{position:absolute;left:18px;top:50%;transform:translateY(-50%);font-size:27px;font-weight:800;color:#aeb8ff}
.amount{width:100%;height:68px;border-radius:19px;border:1px solid var(--line);outline:0;background:#0004;color:#fff;padding:0 15px 0 48px;font-size:30px;font-weight:850}
.amount:focus{border-color:#7180ff88;box-shadow:0 0 0 4px #7180ff18}
.quick{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:10px}.quick button{border:1px solid var(--line);background:#ffffff07;color:#dbe2ef;border-radius:13px;padding:10px 4px;font-weight:750;font-size:11px}
button{font-family:inherit;cursor:pointer}.quick button:active,.action:active,.key:active{transform:scale(.95)}
.action{position:relative;width:100%;border:0;border-radius:18px;padding:16px;margin-top:14px;background:linear-gradient(135deg,#6576ff,#8d52e8);color:#fff;font-size:14px;font-weight:850;box-shadow:0 15px 35px #7180ff2b;transition:.18s;overflow:hidden}
.action:after{content:"";position:absolute;inset:0;left:-120%;width:65%;background:linear-gradient(90deg,transparent,#fff3,transparent);transform:skewX(-20deg);animation:shine 3.8s infinite}
@keyframes shine{70%{left:-120%}90%,100%{left:140%}}
.hint{text-align:center;color:#64748b;font-size:9px;margin-top:13px}
.keypad{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin-top:14px}.key{height:51px;border:1px solid var(--line);border-radius:15px;background:#ffffff06;color:#f1f5f9;font-size:18px;font-weight:750;transition:.12s}.key.back{font-size:15px}
.qrhead{text-align:center}.badge{display:inline-flex;align-items:center;gap:7px;padding:7px 11px;border-radius:99px;background:#39e58c12;border:1px solid #39e58c24;color:#86efac;font-size:9px;font-weight:850;letter-spacing:.5px}
.qrtitle{font-size:24px;font-weight:850;margin-top:11px}.qrsub{font-size:10px;color:var(--muted);margin-top:4px}.qramount{font-size:30px;font-weight:900;text-align:center;margin-top:5px}
.qrwrap{position:relative;width:min(76vw,290px);height:min(76vw,290px);margin:18px auto}.glow{position:absolute;inset:-20px;border-radius:40px;background:radial-gradient(circle,#7180ff33,transparent 68%);filter:blur(10px);animation:glow 2.7s ease-in-out infinite}
@keyframes glow{50%{transform:scale(1.08);opacity:.75}}
.qrframe{position:relative;width:100%;height:100%;padding:15px;border-radius:27px;background:#fff;box-shadow:0 20px 55px #0008;animation:qr .7s cubic-bezier(.16,1,.3,1)}
@keyframes qr{from{opacity:0;transform:scale(.65) rotate(-4deg)}to{opacity:1;transform:none}}
.qrframe img{width:100%;height:100%;object-fit:contain}
.timer{position:relative;width:112px;height:112px;margin:8px auto 16px;display:grid;place-items:center}.timer svg{position:absolute;inset:0;transform:rotate(-90deg)}
.track,.progress{fill:none;stroke-width:6}.track{stroke:#fff0d}.progress{stroke:#7785ff;stroke-linecap:round;stroke-dasharray:301.59;transition:stroke-dashoffset 1s linear}
.tvalue{font-size:21px;font-weight:850;text-align:center}.tlabel{font-size:8px;color:#64748b;letter-spacing:.8px;text-align:center;margin-top:2px}
.lock{width:100%;border:1px solid var(--line);background:#ffffff07;color:#e2e8f0;padding:14px;border-radius:16px;font-weight:750}
.meta{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px}.meta button{border:1px solid var(--line);background:#ffffff05;color:#cbd5e1;padding:11px;border-radius:13px;font-size:10px;font-weight:700}
.lockicon{width:88px;height:88px;margin:8px auto 18px;border-radius:29px;display:grid;place-items:center;background:#ff668012;border:1px solid #ff668026;font-size:38px;animation:pop .55s cubic-bezier(.16,1,.3,1)}
@keyframes pop{from{transform:scale(.5) rotate(-12deg);opacity:0}to{transform:none;opacity:1}}
.center{text-align:center}.lockedtitle{font-size:25px;font-weight:900}.lockedtext{color:var(--muted);font-size:12px;line-height:1.5;margin:8px 15px 20px}
.settings-row{margin-bottom:12px}.settings-row label{display:block;color:#94a3b8;font-size:10px;font-weight:800;margin-bottom:6px}.settings-row input{width:100%;height:48px;border-radius:14px;border:1px solid var(--line);background:#0004;color:#fff;padding:0 13px;outline:0}
.footer{text-align:center;color:#475569;font-size:9px;margin-top:auto;padding-top:24px}
.toast{position:fixed;left:50%;bottom:22px;transform:translate(-50%,20px);opacity:0;background:#151b2a;border:1px solid var(--line);padding:11px 15px;border-radius:99px;font-size:11px;z-index:20;transition:.3s;pointer-events:none;white-space:nowrap}.toast.show{opacity:1;transform:translate(-50%,0)}
@media(max-height:700px){h1{font-size:29px}.hero{padding-top:4px}.qrwrap{width:235px;height:235px}.key{height:45px}}
</style>
</head>
<body>
<div class="app">
<header class="top">
<div class="brand"><div class="logo">◈</div><div><div class="name">SecurePay</div><div class="sub">Premium UPI terminal</div></div></div>
<div class="ready"><span class="dot"></span>READY</div>
</header>

<section id="home" class="screen active">
<div class="hero"><div class="eyebrow">FAST • SIMPLE • PRIVATE</div><h1>Accept payments<br>beautifully.</h1><p>Create a temporary UPI QR in seconds.</p></div>
<div class="card">
<div class="merchant"><div class="merchant-icon">🏪</div><div><div class="merchant-name">{{shop}}</div><div class="merchant-upi">{{upi}}</div></div></div>
<div class="label">PAYMENT AMOUNT</div>
<div class="amountbox"><span class="currency">₹</span><input id="amount" class="amount" inputmode="decimal" placeholder="0.00" readonly></div>
<div class="quick">
<button onclick="setAmount(50)">₹50</button><button onclick="setAmount(100)">₹100</button><button onclick="setAmount(200)">₹200</button><button onclick="setAmount(500)">₹500</button>
</div>
<div class="keypad">
<button class="key" onclick="key('1')">1</button><button class="key" onclick="key('2')">2</button><button class="key" onclick="key('3')">3</button>
<button class="key" onclick="key('4')">4</button><button class="key" onclick="key('5')">5</button><button class="key" onclick="key('6')">6</button>
<button class="key" onclick="key('7')">7</button><button class="key" onclick="key('8')">8</button><button class="key" onclick="key('9')">9</button>
<button class="key" onclick="key('.')">.</button><button class="key" onclick="key('0')">0</button><button class="key back" onclick="backspace()">⌫</button>
</div>
<button class="action" onclick="generateQR()">Generate Secure QR</button>
<div class="hint">🔒 Display automatically locks after 5 minutes</div>
</div>
</section>

<section id="qr" class="screen">
<div class="card">
<div class="qrhead"><div class="badge"><span class="dot"></span>QR ACTIVE</div><div class="qrtitle">Scan to Pay</div><div class="qrsub">{{shop}}</div></div>
<div id="qrAmount" class="qramount">₹0.00</div>
<div class="qrsub" style="text-align:center">{{upi}}</div>
<div class="qrwrap"><div class="glow"></div><div class="qrframe"><img id="qrImage"></div></div>
<div class="timer"><svg viewBox="0 0 112 112"><circle class="track" cx="56" cy="56" r="48"></circle><circle id="progress" class="progress" cx="56" cy="56" r="48"></circle></svg><div><div id="timer" class="tvalue">05:00</div><div class="tlabel">EXPIRES IN</div></div></div>
<button class="lock" onclick="lockQR()">🔒 Lock QR Now</button>
<div class="meta"><button onclick="copyUPI()">📋 Copy UPI ID</button><button onclick="sharePayment()">↗ Share</button></div>
</div>
</section>

<section id="locked" class="screen">
<div class="card center"><div class="lockicon">🔒</div><div class="lockedtitle">QR Locked</div><div class="lockedtext">This display session has ended. Create a fresh QR for the next payment.</div><button class="action" onclick="newPayment()">Generate New Payment</button></div>
</section>

<section id="settings" class="screen">
<div class="card">
<div class="qrtitle">Settings</div><div class="qrsub" style="margin-bottom:20px">Local terminal settings</div>
<div class="settings-row"><label>SHOP NAME</label><input id="shopInput" value="{{shop}}"></div>
<div class="settings-row"><label>UPI ID</label><input id="upiInput" value="{{upi}}"></div>
<button class="action" onclick="saveSettings()">Save Settings</button>
<button class="lock" style="margin-top:10px" onclick="show('home')">← Back</button>
</div>
</section>

<footer class="footer">{{shop}} • SecurePay local terminal</footer>
</div>
<div id="toast" class="toast"></div>

<script>
let remaining=300, timerInterval=null, sessionId=null;
const C=301.59;
const amountEl=()=>document.getElementById('amount');

function show(id){document.querySelectorAll('.screen').forEach(x=>x.classList.remove('active'));document.getElementById(id).classList.add('active')}
function buzz(ms=12){if(navigator.vibrate)navigator.vibrate(ms)}
function toast(t){const x=document.getElementById('toast');x.textContent=t;x.classList.add('show');setTimeout(()=>x.classList.remove('show'),1800)}
function key(v){
 let s=amountEl().value;
 if(v==='.'&&s.includes('.'))return;
 if(v==='.'&&s==='')s='0';
 if(s.includes('.')&&s.split('.')[1].length>=2)return;
 if(s==='0'&&v!==' .')s='';
 if(s.length>=8)return;
 amountEl().value=s+v;buzz(8);
}
function backspace(){amountEl().value=amountEl().value.slice(0,-1);buzz(8)}
function setAmount(n){amountEl().value=n.toFixed(2);buzz(15)}
async function generateQR(){
 const amount=Number(amountEl().value);
 if(!amount||amount<=0){toast('Enter an amount');buzz(40);return}
 const b=document.querySelector('#home .action');b.disabled=true;
 try{
  const r=await fetch('/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({amount})});
  const d=await r.json();
  if(!d.success){toast(d.error||'Unable to generate');return}
  sessionId=d.session_id;
  document.getElementById('qrImage').src='data:image/png;base64,'+d.qr;
  document.getElementById('qrAmount').textContent='₹'+amount.toFixed(2);
  show('qr');startTimer();buzz(25);
 }catch(e){toast('Server connection error')}finally{b.disabled=false}
}
function startTimer(){
 clearInterval(timerInterval);remaining=300;updateTimer();
 timerInterval=setInterval(()=>{remaining--;updateTimer();if(remaining<=0){clearInterval(timerInterval);lockQR(true)}},1000)
}
function updateTimer(){
 const m=String(Math.floor(remaining/60)).padStart(2,'0'),s=String(remaining%60).padStart(2,'0');
 document.getElementById('timer').textContent=m+':'+s;
 document.getElementById('progress').style.strokeDashoffset=C*(1-remaining/300);
 document.getElementById('progress').style.stroke=remaining<=30?'#ff6680':'#7785ff';
}
async function lockQR(expired=false){
 clearInterval(timerInterval);
 if(sessionId){try{await fetch('/lock',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({session_id:sessionId})})}catch(e){}}
 sessionId=null;show('locked');if(!expired)buzz(25)
}
function newPayment(){amountEl().value='';show('home');setTimeout(()=>amountEl().focus(),180)}
async function copyUPI(){try{await navigator.clipboard.writeText('{{upi}}');toast('UPI ID copied');buzz(10)}catch(e){toast('Copy unavailable')}}
async function sharePayment(){
 const amount=Number(amountEl().value||0);
 const text='Payment to {{shop}}\\nUPI: {{upi}}\\nAmount: ₹'+amount.toFixed(2);
 if(navigator.share){try{await navigator.share({title:'SecurePay Payment',text})}catch(e){}}
 else{try{await navigator.clipboard.writeText(text);toast('Payment details copied')}catch(e){toast('Share unavailable')}}
}
function saveSettings(){
 const shop=document.getElementById('shopInput').value.trim(),upi=document.getElementById('upiInput').value.trim();
 if(!shop||!upi){toast('Fill both fields');return}
 localStorage.setItem('securepay_shop',shop);localStorage.setItem('securepay_upi',upi);
 toast('Saved locally');setTimeout(()=>location.reload(),600)
}
(function loadLocal(){
 const s=localStorage.getItem('securepay_shop'),u=localStorage.getItem('securepay_upi');
 if(s||u){/* Local values are intentionally only UI convenience; server QR uses server config. */}
})();
document.addEventListener('keydown',e=>{if(e.key==='Escape')lockQR()});
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(PAGE, shop=SHOP_NAME, upi=UPI_ID)

@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json(silent=True) or {}
        amount = float(data.get("amount", 0))
        if not amount or amount <= 0 or amount > 10000000:
            return jsonify(success=False, error="Enter a valid amount.")

        params = {
            "pa": UPI_ID,
            "pn": SHOP_NAME,
            "am": f"{amount:.2f}",
            "cu": "INR"
        }
        uri = "upi://pay?" + urllib.parse.urlencode(params)

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4
        )
        qr.add_data(uri)
        qr.make(fit=True)
        image = qr.make_image(fill_color="black", back_color="white")

        buf = io.BytesIO()
        image.save(buf, format="PNG")
        encoded = base64.b64encode(buf.getvalue()).decode()

        session_id = secrets.token_urlsafe(18)
        sessions[session_id] = time.time() + SESSION_SECONDS

        # Clean expired sessions.
        now = time.time()
        for sid, expiry in list(sessions.items()):
            if expiry < now:
                sessions.pop(sid, None)

        return jsonify(success=True, qr=encoded, session_id=session_id, expires_in=SESSION_SECONDS)
    except Exception as e:
        return jsonify(success=False, error=str(e))

@app.route("/lock", methods=["POST"])
def lock():
    data = request.get_json(silent=True) or {}
    sid = data.get("session_id")
    if sid:
        sessions.pop(sid, None)
    return jsonify(success=True)

@app.route("/session/<sid>")
def session_status(sid):
    expiry = sessions.get(sid)
    if not expiry:
        return jsonify(active=False)
    left = max(0, int(expiry - time.time()))
    if left <= 0:
        sessions.pop(sid, None)
        return jsonify(active=False)
    return jsonify(active=True, remaining=left)

if __name__ == "__main__":
    print("\n=============================================")
    print("          SECUREPAY PREMIUM UPI")
    print("=============================================\n")
    print("Shop :", SHOP_NAME)
    print("UPI  :", UPI_ID)
    print("Open : http://127.0.0.1:5010")
    print("QR display session: 5 minutes")
    print("\nPress CTRL+C to stop\n")
    app.run(host=HOST, port=PORT, debug=False)

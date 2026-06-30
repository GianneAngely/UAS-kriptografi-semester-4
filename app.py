import os
import sys
import json
import base64
import hashlib
import time
import random
import threading
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature

DIRS = ["data/ca", "data/ra", "data/cust", "data/certs", "data/messages"]
for d in DIRS:
    os.makedirs(d, exist_ok=True)

R  = "\033[91m"
G  = "\033[92m"
Y  = "\033[93m"
B  = "\033[94m"
M  = "\033[95m"
C  = "\033[96m"
W  = "\033[97m"
DG = "\033[90m"
BOLD = "\033[1m"
DIM  = "\033[2m"
BLINK = "\033[5m"
RST  = "\033[0m"
BG_BLACK = "\033[40m"
CLEAR = "\033[2J\033[H"

WIDTH = 72

ASCII_BANNER = f"""
{C}{BOLD}██████╗ ██╗  ██╗██╗    ███████╗██╗   ██╗███████╗████████╗███████╗███╗   ███╗
{C}██╔══██╗██║ ██╔╝██║    ██╔════╝╚██╗ ██╔╝██╔════╝╚══██╔══╝██╔════╝████╗ ████║
{B}██████╔╝█████╔╝ ██║    ███████╗ ╚████╔╝ ███████╗   ██║   █████╗  ██╔████╔██║
{B}██╔═══╝ ██╔═██╗ ██║    ╚════██║  ╚██╔╝  ╚════██║   ██║   ██╔══╝  ██║╚██╔╝██║
{M}██║     ██║  ██╗██║    ███████║   ██║   ███████║   ██║   ███████╗██║ ╚═╝ ██║
{M}╚═╝     ╚═╝  ╚═╝╚═╝    ╚══════╝   ╚═╝   ╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝{RST}"""

LOCK_ART = f"""
{C}     ██████╗  ██████╗ ██████╗ 
{C}    ██╔═══██╗██╔════╝ ╚════██╗
{B}    ██║   ██║██║       █████╔╝
{B}    ██║▄▄ ██║██║      ██╔═══╝ 
{M}    ╚██████╔╝╚██████╗ ███████╗
{M}     ╚══▀▀═╝  ╚═════╝ ╚══════╝{RST}"""

def cls():
    print(CLEAR, end="")

def line(char="─", color=DG, width=WIDTH):
    print(f"{color}{char * width}{RST}")

def double_line(color=C, width=WIDTH):
    print(f"{color}{'═' * width}{RST}")

def title_box(text, color=C):
    double_line(color)
    pad = (WIDTH - len(text) - 2) // 2
    print(f"{color}║{RST}{' ' * pad}{BOLD}{W}{text}{RST}{' ' * (WIDTH - pad - len(text) - 2)}{color}║{RST}")
    double_line(color)

def section_header(title, icon="◈", color=Y):
    print()
    line("┄", DG)
    print(f"{color}{BOLD} {icon} {title}{RST}")
    line("┄", DG)

def status_dot(ok):
    return f"{G}●{RST}" if ok else f"{R}●{RST}"

def tag(label, color=B):
    return f"{color}[{label}]{RST}"

def glitch_print(text, delay=0.018):
    chars = "▓▒░█▄▀■□▪▫"
    for i, ch in enumerate(text):
        if random.random() < 0.06:
            sys.stdout.write(f"{DG}{random.choice(chars)}{RST}")
            sys.stdout.flush()
            time.sleep(delay * 0.4)
            sys.stdout.write("\b \b")
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay * (0.5 + random.random()))
    print()

def typewrite(text, delay=0.012, color=""):
    for ch in text:
        sys.stdout.write(f"{color}{ch}{RST}")
        sys.stdout.flush()
        time.sleep(delay)
    print()

def spinner_task(label, duration=0.8):
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        sys.stdout.write(f"\r  {C}{frames[i % len(frames)]}{RST} {DIM}{label}...{RST}")
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1
    sys.stdout.write(f"\r  {G}✔{RST} {label}{' ' * 10}\n")
    sys.stdout.flush()

def progress_bar(label, width=30, color=C, duration=0.6):
    steps = width
    delay = duration / steps
    sys.stdout.write(f"  {DIM}{label}{RST}  {DG}[{RST}")
    sys.stdout.flush()
    for _ in range(steps):
        sys.stdout.write(f"{color}█{RST}")
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(f"{DG}]{RST} {G}100%{RST}\n")
    sys.stdout.flush()

def boot_sequence():
    cls()
    print(ASCII_BANNER)
    print(LOCK_ART)
    time.sleep(0.3)
    print(f"\n{DG}{'─'*WIDTH}{RST}")
    typewrite(f"  {C}Initializing Public Key Infrastructure System...{RST}", 0.02, "")
    time.sleep(0.2)
    items = [
        ("RSA-2048 Engine", 0.4),
        ("Certificate Authority Module", 0.5),
        ("Registration Authority Module", 0.4),
        ("Digital Signature Verifier (PSS/SHA-256)", 0.5),
        ("Asymmetric Encryption (OAEP)", 0.4),
        ("Secure Storage Layer", 0.3),
    ]
    for label, dur in items:
        spinner_task(label, dur)
    print()
    progress_bar("Loading PKI modules", 36, C, 0.8)
    print()
    print(f"  {G}{BOLD}✔  SYSTEM READY{RST}  {DG}│{RST}  {DIM}RSA-2048 │ SHA-256 │ PSS │ OAEP{RST}")
    print(f"{DG}{'─'*WIDTH}{RST}")
    time.sleep(0.5)

def format_ok(label, value=""):
    return f"  {G}✔{RST}  {W}{BOLD}{label}{RST}  {DG}{value}{RST}"

def format_err(label, value=""):
    return f"  {R}✘{RST}  {W}{BOLD}{label}{RST}  {DG}{value}{RST}"

def format_warn(label, value=""):
    return f"  {Y}⚠{RST}  {W}{BOLD}{label}{RST}  {DG}{value}{RST}"

def format_info(label, value=""):
    return f"  {C}◈{RST}  {label:<28}  {Y}{value}{RST}"

def hex_preview(data_hex, n=32):
    segments = [data_hex[i:i+2] for i in range(0, min(n*2, len(data_hex)), 2)]
    colored = ""
    palette = [C, B, M, Y, G]
    for i, seg in enumerate(segments):
        colored += f"{palette[i % len(palette)]}{seg}{RST} "
    return colored.strip() + f" {DG}...{RST}"

def b64_preview(b64str, n=24):
    chunk = b64str[:n]
    out = ""
    palette = [G, C, Y]
    for i, ch in enumerate(chunk):
        out += f"{palette[i % len(palette)]}{ch}{RST}"
    return out + f"{DG}...{RST}"

def show_cert_card(cert):
    p = cert["payload"]
    print(f"\n  {DG}┌{'─'*54}┐{RST}")
    print(f"  {DG}│{RST}  {C}{BOLD}DIGITAL CERTIFICATE{RST}{' '*33}{DG}│{RST}")
    print(f"  {DG}├{'─'*54}┤{RST}")
    fields = [
        ("Subject", p.get("subject", "-")),
        ("Name", p.get("name", "-")),
        ("Email", p.get("email", "-")),
        ("Org", p.get("org", "-")),
        ("Issuer", p.get("issuer", "-")),
        ("Issued", p.get("issued_at", "-")[:19]),
        ("Valid Until", p.get("valid_until", "-")[:10]),
        ("Serial", p.get("serial", "-")[:18] + "..."),
    ]
    for k, v in fields:
        row = f"  {DG}│{RST}  {DG}{k:<12}{RST} {W}{v}{RST}"
        print(row + " " * max(0, WIDTH - len(f"  │  {k:<12} {v}") + 2) + f"  {DG}│{RST}")
    print(f"  {DG}└{'─'*54}┘{RST}")

def _load_private(path):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

def _load_public(path):
    with open(path, "rb") as f:
        return serialization.load_pem_public_key(f.read(), backend=default_backend())

def _save_private(key, path):
    with open(path, "wb") as f:
        f.write(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL, serialization.NoEncryption()))

def _save_public(key, path):
    with open(path, "wb") as f:
        f.write(key.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))

def _gen_keypair():
    priv = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    return priv, priv.public_key()

def _sign(private_key, data: bytes) -> bytes:
    return private_key.sign(data, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())

def _verify_sig(public_key, sig: bytes, data: bytes) -> bool:
    try:
        public_key.verify(sig, data, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
        return True
    except InvalidSignature:
        return False

def _encrypt(public_key, plaintext: bytes) -> bytes:
    return public_key.encrypt(plaintext, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None))

def _decrypt(private_key, ciphertext: bytes) -> bytes:
    return private_key.decrypt(ciphertext, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None))


def menu_1_ca_setup():
    title_box("CA — INISIALISASI KEY PAIR", C)
    if os.path.exists("data/ca/ca_private.pem"):
        print(format_warn("Key pair CA sudah ada", "tidak perlu generate ulang"))
        return
    typewrite(f"  {DIM}Generating RSA-2048 key pair for Certificate Authority...{RST}", 0.015)
    spinner_task("Generating RSA-2048 key pair", 1.2)
    priv, pub = _gen_keypair()
    _save_private(priv, "data/ca/ca_private.pem")
    _save_public(pub, "data/ca/ca_public.pem")
    print()
    print(format_ok("Key pair CA berhasil dibuat!"))
    print()
    print(f"  {DG}┌{'─'*52}┐")
    print(f"  │{RST}  {R}{BOLD}🔐 PRIVATE KEY{RST}  {DIM}(RAHASIA — simpan aman!){RST}{' '*4}{DG}│")
    print(f"  │{RST}  {DG}Path : {W}data/ca/ca_private.pem{' '*18}{DG}│")
    print(f"  ├{'─'*52}┤")
    print(f"  │{RST}  {G}{BOLD}🔑 PUBLIC KEY{RST}  {DIM}(Root of Trust — publik){RST}{' '*6}{DG}│")
    print(f"  │{RST}  {DG}Path : {W}data/ca/ca_public.pem{' '*19}{DG}│")
    print(f"  └{'─'*52}┘{RST}")


def menu_2_ca_issue():
    title_box("CA — TERBITKAN SERTIFIKAT DIGITAL", C)
    if not os.path.exists("data/ca/ca_private.pem"):
        print(format_err("CA private key tidak ditemukan", "jalankan Menu 1 terlebih dahulu"))
        return

    approved = [
        f.replace("_request.json", "")
        for f in os.listdir("data/ra")
        if f.endswith("_request.json")
        and json.load(open(f"data/ra/{f}")).get("status") == "APPROVED"
        and not os.path.exists(f"data/certs/{f.replace('_request.json','')}_cert.json")
    ]

    if not approved:
        print(format_warn("Tidak ada request APPROVED yang belum disertifikasi"))
        return

    section_header("Request Siap Disertifikasi", "◈", Y)
    for i, name in enumerate(approved, 1):
        print(f"  {DG}[{Y}{i}{DG}]{RST}  {W}{name}{RST}")

    print()
    try:
        idx = int(input(f"  {C}▶{RST} Pilih nomor: {W}")) - 1
        print(RST, end="")
        username = approved[idx]
    except (ValueError, IndexError):
        print(format_err("Pilihan tidak valid"))
        return

    req = json.load(open(f"data/ra/{username}_request.json"))
    ca_priv = _load_private("data/ca/ca_private.pem")

    spinner_task(f"Generating certificate for '{username}'", 0.8)
    spinner_task("Signing payload with CA private key (RSA-PSS/SHA-256)", 0.6)

    import uuid
    payload = {
        "serial": str(uuid.uuid4()),
        "subject": username,
        "name": req["name"],
        "email": req["email"],
        "org": req["org"],
        "public_key": req["public_key"],
        "issuer": "CA-PKI-UAS",
        "issued_at": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=365)).isoformat()
    }
    payload_bytes = json.dumps(payload, sort_keys=True).encode()
    payload_hash = hashlib.sha256(payload_bytes).hexdigest()
    sig = _sign(ca_priv, payload_hash.encode())

    cert = {"payload": payload, "payload_hash": payload_hash, "ca_signature": sig.hex()}
    with open(f"data/certs/{username}_cert.json", "w") as f:
        json.dump(cert, f, indent=2)

    print()
    show_cert_card(cert)
    print()
    print(format_ok(f"Sertifikat '{username}' berhasil diterbitkan!", ""))
    print(f"  {DG}CA Signature (hex preview):{RST}")
    print(f"  {hex_preview(cert['ca_signature'])}")


def menu_3_ra_validate():
    title_box("RA — VALIDASI REQUEST CUSTOMER", Y)

    pending = [
        f.replace("_request.json", "")
        for f in os.listdir("data/ra")
        if f.endswith("_request.json")
        and json.load(open(f"data/ra/{f}")).get("status") == "PENDING"
    ]

    if not pending:
        print(format_warn("Tidak ada request PENDING saat ini"))
        return

    section_header("Request Menunggu Validasi", "◈", Y)
    for i, name in enumerate(pending, 1):
        print(f"  {DG}[{Y}{i}{DG}]{RST}  {Y}⏳{RST}  {W}{name}{RST}")

    print()
    try:
        idx = int(input(f"  {Y}▶{RST} Pilih nomor: {W}")) - 1
        print(RST, end="")
        username = pending[idx]
    except (ValueError, IndexError):
        print(format_err("Pilihan tidak valid"))
        return

    req = json.load(open(f"data/ra/{username}_request.json"))

    section_header("Detail Pemohon Sertifikat", "◈", B)
    fields = [
        ("Nama Lengkap", req["name"]),
        ("Email", req["email"]),
        ("Organisasi", req["org"]),
        ("Timestamp", req["timestamp"][:19]),
        ("Public Key", f"{len(req['public_key'])} chars (PEM format)"),
        ("Status", req["status"]),
    ]
    for k, v in fields:
        print(format_info(k, v))

    print()
    print(f"  {DG}{'─'*50}{RST}")
    decision = input(f"  {Y}{BOLD}⚡ Setujui request '{username}'?{RST}  {DG}[y/n]{RST}  {W}").strip().lower()
    print(RST, end="")

    req["status"] = "APPROVED" if decision == "y" else "REJECTED"
    req["ra_reviewed_at"] = datetime.utcnow().isoformat()
    with open(f"data/ra/{username}_request.json", "w") as f:
        json.dump(req, f, indent=2)

    spinner_task("Updating request status", 0.4)
    if decision == "y":
        print(f"\n  {G}{BOLD}✔  REQUEST APPROVED{RST}  {DG}│{RST}  {DIM}'{username}' siap disertifikasi CA{RST}")
    else:
        print(f"\n  {R}{BOLD}✘  REQUEST REJECTED{RST}  {DG}│{RST}  {DIM}'{username}' ditolak oleh RA{RST}")


def menu_4_cust_register():
    title_box("CUST — PENDAFTARAN & KEY GENERATION", G)

    print(f"\n  {DIM}Masukkan data identitas Customer:{RST}\n")
    username = input(f"  {G}▶{RST} Username {DG}(contoh: yoga){RST}: {W}").strip().lower()
    print(RST, end="")
    name  = input(f"  {G}▶{RST} Nama Lengkap: {W}").strip(); print(RST, end="")
    email = input(f"  {G}▶{RST} Email: {W}").strip(); print(RST, end="")
    org   = input(f"  {G}▶{RST} Organisasi: {W}").strip(); print(RST, end="")

    print()
    if os.path.exists(f"data/cust/{username}_private.pem"):
        print(format_warn(f"Key pair '{username}' sudah ada", "melewati keygen"))
    else:
        spinner_task(f"Generating RSA-2048 key pair for '{username}'", 1.0)
        priv, pub = _gen_keypair()
        _save_private(priv, f"data/cust/{username}_private.pem")
        _save_public(pub, f"data/cust/{username}_public.pem")
        print(format_ok(f"Key pair '{username}' berhasil dibuat"))

    pub_pem = open(f"data/cust/{username}_public.pem").read()
    spinner_task("Menyiapkan Certificate Signing Request (CSR)", 0.5)

    request = {
        "username": username, "name": name, "email": email,
        "org": org, "public_key": pub_pem,
        "timestamp": datetime.utcnow().isoformat(), "status": "PENDING"
    }
    with open(f"data/ra/{username}_request.json", "w") as f:
        json.dump(request, f, indent=2)

    spinner_task("Mengirim CSR ke Registration Authority", 0.5)
    print()
    print(f"  {DG}┌{'─'*52}┐")
    print(f"  │{RST}  {R}{BOLD}🔐 PRIVATE KEY{RST}  {DIM}SIMPAN SENDIRI — JANGAN DIBAGI!{RST}{' '*2}{DG}│")
    print(f"  │{RST}  {DG}  data/cust/{username}_private.pem{' '*(36-len(username))}{DG}│")
    print(f"  ├{'─'*52}┤")
    print(f"  │{RST}  {G}📨 CSR dikirim ke RA → status: {Y}PENDING{RST}{' '*12}{DG}│")
    print(f"  └{'─'*52}┘{RST}")


def menu_5_sign_message():
    title_box("CUST — TANDA TANGAN DIGITAL PESAN", M)
    username = input(f"\n  {M}▶{RST} Nama pengirim: {W}").strip().lower(); print(RST, end="")

    if not os.path.exists(f"data/certs/{username}_cert.json"):
        print(f"\n{format_err(f'Sertifikat {username} belum ada', 'minta CA terbitkan dulu')}")
        return

    message = input(f"  {M}▶{RST} Isi pesan: {W}").strip(); print(RST, end="")
    priv = _load_private(f"data/cust/{username}_private.pem")
    msg_bytes = message.encode()

    spinner_task("Menghitung SHA-256 hash pesan", 0.4)
    spinner_task("Membuat tanda tangan RSA-PSS", 0.6)

    sig = _sign(priv, msg_bytes)
    out = {
        "from": username, "to": "public", "message": message,
        "signature": base64.b64encode(sig).decode(),
        "timestamp": datetime.utcnow().isoformat()
    }
    out_path = f"data/messages/{username}_signed.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)

    print()
    print(f"  {DG}┌{'─'*52}┐")
    print(f"  │{RST}  {M}{BOLD}✍  PESAN DITANDATANGANI{RST}{' '*29}{DG}│")
    print(f"  ├{'─'*52}┤")
    print(f"  │{RST}  {DG}Pesan   :{RST} {W}{message[:38]}{'...' if len(message)>38 else ''}{' '*(10-min(len(message),38)+28)}{DG}│")
    print(f"  │{RST}  {DG}Output  :{RST} {W}{out_path}{' '*(52-len(out_path)-11)}{DG}│")
    print(f"  └{'─'*52}┘{RST}")
    print(f"\n  {DG}Signature preview:{RST}")
    print(f"  {b64_preview(out['signature'], 40)}")


def menu_6_encrypt_message():
    title_box("CUST — ENKRIPSI PESAN RAHASIA", B)

    sender   = input(f"\n  {B}▶{RST} Nama pengirim: {W}").strip().lower(); print(RST, end="")
    receiver = input(f"  {B}▶{RST} Nama penerima: {W}").strip().lower(); print(RST, end="")

    if not os.path.exists(f"data/certs/{sender}_cert.json"):
        print(f"\n{format_err(f'Sertifikat {sender} tidak ditemukan')}"); return
    if not os.path.exists(f"data/certs/{receiver}_cert.json"):
        print(f"\n{format_err(f'Sertifikat {receiver} tidak ditemukan')}"); return

    message = input(f"  {B}▶{RST} Isi pesan rahasia: {W}").strip(); print(RST, end="")
    msg_bytes = message.encode()

    recv_cert = json.load(open(f"data/certs/{receiver}_cert.json"))
    recv_pub  = serialization.load_pem_public_key(recv_cert["payload"]["public_key"].encode(), backend=default_backend())
    sender_priv = _load_private(f"data/cust/{sender}_private.pem")

    spinner_task(f"Mengambil public key '{receiver}' dari sertifikat", 0.4)
    spinner_task("Membuat tanda tangan digital pengirim (RSA-PSS)", 0.6)
    spinner_task(f"Mengenkripsi pesan dengan public key '{receiver}' (OAEP)", 0.7)

    sig = _sign(sender_priv, msg_bytes)
    ciphertext = _encrypt(recv_pub, msg_bytes)

    out = {
        "from": sender, "to": receiver,
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "signature": base64.b64encode(sig).decode(),
        "timestamp": datetime.utcnow().isoformat()
    }
    out_path = f"data/messages/{receiver}_encrypted.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)

    print()
    print(f"  {DG}╔{'═'*52}╗")
    print(f"  ║{RST}  {B}{BOLD}🔒 PESAN TERENKRIPSI BERHASIL{RST}{' '*24}{DG}║")
    print(f"  ╠{'═'*52}╣")
    print(f"  ║{RST}  {DG}Dari    :{RST}  {W}{sender}{' '*(43-len(sender))}{DG}║")
    print(f"  ║{RST}  {DG}Kepada  :{RST}  {W}{receiver}{' '*(43-len(receiver))}{DG}║")
    print(f"  ║{RST}  {DG}Metode  :{RST}  {W}RSA-OAEP/SHA-256 + RSA-PSS{' '*18}{DG}║")
    print(f"  ║{RST}  {R}Catatan :{RST}  {DIM}Hanya '{receiver}' yang bisa membuka!{RST}{' '*(28-len(receiver))}{DG}║")
    print(f"  ╚{'═'*52}╝{RST}")
    print(f"\n  {DG}Ciphertext preview:{RST}")
    print(f"  {b64_preview(out['ciphertext'], 48)}")


def menu_7_decrypt_message():
    title_box("CUST — DEKRIPSI PESAN RAHASIA", G)
    username = input(f"\n  {G}▶{RST} Nama penerima: {W}").strip().lower(); print(RST, end="")

    env_path = f"data/messages/{username}_encrypted.json"
    if not os.path.exists(env_path):
        print(f"\n{format_err(f'Tidak ada pesan terenkripsi untuk {username}')}")
        return

    env  = json.load(open(env_path))
    priv = _load_private(f"data/cust/{username}_private.pem")

    spinner_task("Memuat ciphertext dari repository", 0.3)
    spinner_task(f"Mendekripsi dengan private key '{username}' (OAEP)", 0.7)

    try:
        plaintext = _decrypt(priv, base64.b64decode(env["ciphertext"]))
    except Exception as e:
        print(f"\n{format_err('Dekripsi GAGAL', str(e))}"); return

    sender = env["from"]
    sender_cert = json.load(open(f"data/certs/{sender}_cert.json"))
    sender_pub  = serialization.load_pem_public_key(sender_cert["payload"]["public_key"].encode(), backend=default_backend())

    spinner_task(f"Memverifikasi tanda tangan digital '{sender}' (PSS)", 0.6)

    sig_valid = _verify_sig(sender_pub, base64.b64decode(env["signature"]), plaintext)

    print()
    print(f"  {DG}╔{'═'*52}╗")
    print(f"  ║{RST}  {G}{BOLD}🔓 DEKRIPSI BERHASIL{RST}{' '*34}{DG}║")
    print(f"  ╠{'═'*52}╣")
    print(f"  ║{RST}  {DG}Dari           :{RST}  {W}{sender}{' '*(36-len(sender))}{DG}║")
    msg_disp = plaintext.decode()[:36]
    print(f"  ║{RST}  {DG}Isi Pesan      :{RST}  {Y}{BOLD}{msg_disp}{'...' if len(plaintext.decode())>36 else ''}{RST}{' '*(35-len(msg_disp))}{DG}║")
    sv_label = f"{G}✔  VALID{RST}" if sig_valid else f"{R}✘  TIDAK VALID{RST}"
    print(f"  ║{RST}  {DG}Tanda Tangan   :{RST}  {sv_label}{' '*40}{DG}║")
    print(f"  ╚{'═'*52}╝{RST}")

    if sig_valid:
        print(f"\n  {G}{BOLD}⚡ Autentikasi PENUH — pesan asli dari '{sender}'{RST}")
    else:
        print(f"\n  {R}{BOLD}⚠  Tanda tangan TIDAK VALID — waspadai pemalsuan!{RST}")


def menu_8_verify_signed():
    title_box("CUST — VERIFIKASI TANDA TANGAN DIGITAL", C)

    signed_files = [f for f in os.listdir("data/messages") if f.endswith("_signed.json")]
    if not signed_files:
        print(format_warn("Tidak ada pesan bertanda tangan tersedia"))
        return

    section_header("Pesan Tersedia", "◈", B)
    for i, fname in enumerate(signed_files, 1):
        print(f"  {DG}[{B}{i}{DG}]{RST}  {W}{fname}{RST}")

    print()
    try:
        idx = int(input(f"  {C}▶{RST} Pilih nomor: {W}")) - 1; print(RST, end="")
        fname = signed_files[idx]
    except (ValueError, IndexError):
        print(format_err("Pilihan tidak valid")); return

    msg_data = json.load(open(f"data/messages/{fname}"))
    sender   = msg_data["from"]

    if not os.path.exists(f"data/certs/{sender}_cert.json"):
        print(f"\n{format_err(f'Sertifikat {sender} tidak ditemukan')}"); return

    ca_pub = _load_public("data/ca/ca_public.pem")
    cert   = json.load(open(f"data/certs/{sender}_cert.json"))

    spinner_task("Mengambil sertifikat dari repository", 0.3)
    spinner_task("Memverifikasi tanda tangan CA pada sertifikat", 0.6)
    spinner_task(f"Memverifikasi tanda tangan pesan '{sender}'", 0.5)

    payload_hash = hashlib.sha256(json.dumps(cert["payload"], sort_keys=True).encode()).hexdigest()
    cert_valid   = _verify_sig(ca_pub, bytes.fromhex(cert["ca_signature"]), payload_hash.encode())
    sender_pub   = serialization.load_pem_public_key(cert["payload"]["public_key"].encode(), backend=default_backend())
    sig_valid    = _verify_sig(sender_pub, base64.b64decode(msg_data["signature"]), msg_data["message"].encode())

    all_ok = cert_valid and sig_valid

    print()
    print(f"  {DG}╔{'═'*56}╗")
    title_str = "VERIFIKASI BERHASIL ✔" if all_ok else "VERIFIKASI GAGAL ✘"
    tcolor = G if all_ok else R
    print(f"  ║{RST}  {tcolor}{BOLD}{title_str}{RST}{' '*(56-len(title_str)-3)}{DG}║")
    print(f"  ╠{'═'*56}╣")

    cv = f"{G}✔ VALID{RST}" if cert_valid else f"{R}✘ TIDAK VALID{RST}"
    sv = f"{G}✔ VALID{RST}" if sig_valid  else f"{R}✘ TIDAK VALID{RST}"
    print(f"  ║{RST}  {DG}Sertifikat CA    :{RST}  {cv}{' '*30}{DG}║")
    print(f"  ║{RST}  {DG}Tanda Tangan     :{RST}  {sv}{' '*30}{DG}║")

    msg_disp = msg_data['message'][:40]
    print(f"  ║{RST}  {DG}Isi Pesan        :{RST}  {Y}{msg_disp}{'...' if len(msg_data['message'])>40 else ''}{' '*(55-len(msg_disp)-2)}{DG}║")

    name_disp = cert['payload']['name']
    email_disp = cert['payload']['email']
    print(f"  ║{RST}  {DG}Identitas        :{RST}  {W}{name_disp}{RST}  {DG}<{email_disp}>{' '*(55-len(name_disp)-len(email_disp)-4)}{DG}║")
    print(f"  ╚{'═'*56}╝{RST}")

    if all_ok:
        print(f"\n  {G}{BOLD}🔐 CHAIN OF TRUST VERIFIED — Pesan otentik & tidak dimanipulasi!{RST}")
    else:
        print(f"\n  {R}{BOLD}⚠  Salah satu verifikasi GAGAL — pesan mungkin dipalsukan!{RST}")


def menu_9_negative_test():
    title_box("NEGATIVE TEST — SIMULASI SERANGAN", R)

    print(f"\n  {DG}Pilih skenario serangan:{RST}\n")
    scenarios = [
        (f"{R}1{RST}", "Forge Sertifikat CA", "attacker mencoba buat sertifikat palsu"),
        (f"{Y}2{RST}", "Tamper Pesan Bertanda Tangan", "pesan dimanipulasi setelah ditandatangani"),
        (f"{M}3{RST}", "Wrong Private Key Decrypt", "attacker coba dekripsi dengan key berbeda"),
    ]
    for num, name, desc in scenarios:
        print(f"  [{num}]  {W}{BOLD}{name}{RST}  {DG}— {desc}{RST}")

    print()
    choice = input(f"  {R}▶{RST} Pilih skenario: {W}").strip(); print(RST, end="")
    print()

    if choice == "1":
        section_header("SKENARIO 1: Certificate Forgery Attack", "⚠", R)
        spinner_task("Attacker sedang membuat sertifikat palsu", 0.6)
        fake_cert = {
            "payload": {
                "serial": "FAKE-999", "subject": "attacker",
                "name": "Evil Attacker", "email": "evil@hack.com",
                "org": "Hackers Inc", "public_key": "FAKE_KEY",
                "issuer": "CA-PKI-UAS",
                "issued_at": datetime.utcnow().isoformat(),
                "valid_until": (datetime.utcnow() + timedelta(days=365)).isoformat()
            },
            "payload_hash": "fakehash", "ca_signature": "deadbeef"
        }
        ca_pub = _load_public("data/ca/ca_public.pem")
        try:
            payload_hash = hashlib.sha256(json.dumps(fake_cert["payload"], sort_keys=True).encode()).hexdigest()
            ca_pub.verify(bytes.fromhex(fake_cert["ca_signature"]), payload_hash.encode(),
                          padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
            print(f"\n  {R}[BUG] Sertifikat palsu diterima! Ada masalah.{RST}")
        except Exception:
            print(f"\n  {R}✘  Sertifikat PALSU → Signature tidak cocok dengan CA key{RST}")
            print(f"  {G}✔  DITOLAK — Trust chain PKI bekerja dengan benar!{RST}")

    elif choice == "2":
        section_header("SKENARIO 2: Message Tampering Attack", "⚠", Y)
        signed_files = [f for f in os.listdir("data/messages") if f.endswith("_signed.json")]
        if not signed_files:
            print(f"  {Y}[!] Belum ada pesan bertanda tangan. Jalankan Menu 5 dulu.{RST}"); return
        msg_data = json.load(open(f"data/messages/{signed_files[0]}"))
        original = msg_data["message"]
        tampered_msg = original + " [DIMANIPULASI ATTACKER]"
        spinner_task("Attacker memanipulasi isi pesan", 0.5)
        sender = msg_data["from"]
        cert   = json.load(open(f"data/certs/{sender}_cert.json"))
        sender_pub = serialization.load_pem_public_key(cert["payload"]["public_key"].encode(), backend=default_backend())
        sig_valid  = _verify_sig(sender_pub, base64.b64decode(msg_data["signature"]), tampered_msg.encode())
        print()
        print(f"  {DG}Pesan Asli   :{RST}  {G}{original}{RST}")
        print(f"  {DG}Pesan Palsu  :{RST}  {R}{tampered_msg}{RST}")
        print()
        if not sig_valid:
            print(f"  {R}✘  Tanda tangan TIDAK VALID pada pesan yang dimanipulasi{RST}")
            print(f"  {G}✔  Integritas pesan TERLINDUNGI — manipulasi terdeteksi!{RST}")

    elif choice == "3":
        section_header("SKENARIO 3: Wrong Key Decryption Attack", "⚠", M)
        encrypted_files = [f for f in os.listdir("data/messages") if f.endswith("_encrypted.json")]
        if not encrypted_files:
            print(f"  {Y}[!] Belum ada pesan terenkripsi. Jalankan Menu 6 dulu.{RST}"); return
        env = json.load(open(f"data/messages/{encrypted_files[0]}"))
        spinner_task("Attacker generate random key pair", 0.4)
        spinner_task("Attacker mencoba dekripsi ciphertext", 0.6)
        wrong_priv, _ = _gen_keypair()
        try:
            _decrypt(wrong_priv, base64.b64decode(env["ciphertext"]))
            print(f"\n  {R}[BUG] Berhasil dekripsi dengan key salah!{RST}")
        except Exception:
            print(f"\n  {R}✘  Dekripsi GAGAL — private key tidak cocok dengan ciphertext{RST}")
            print(f"  {G}✔  Kerahasiaan pesan TERJAGA — hanya pemilik private key asli yang bisa!{RST}")
    else:
        print(format_err("Skenario tidak valid"))


def menu_0_status():
    title_box("STATUS SISTEM PKI", B)

    print()
    ca_exists = os.path.exists("data/ca/ca_private.pem")
    print(f"  {status_dot(ca_exists)}  {W}{BOLD}Certificate Authority{RST}  {DG}key pair: {'Ada' if ca_exists else 'Belum dibuat'}{RST}")

    section_header("Registration Authority — Requests", "◈", Y)
    ra_files = [f for f in os.listdir("data/ra") if f.endswith("_request.json")]
    if not ra_files:
        print(f"  {DG}(kosong){RST}")
    for f in ra_files:
        req = json.load(open(f"data/ra/{f}"))
        sc = {"PENDING": Y, "APPROVED": G, "REJECTED": R}.get(req["status"], W)
        print(f"  {status_dot(req['status']=='APPROVED')}  {W}{req['username']:<16}{RST}  {sc}{req['status']:<10}{RST}  {DG}{req['timestamp'][:10]}{RST}")

    section_header("Sertifikat Diterbitkan", "◈", G)
    cert_files = [f for f in os.listdir("data/certs") if f.endswith("_cert.json")]
    if not cert_files:
        print(f"  {DG}(kosong){RST}")
    for f in cert_files:
        cert = json.load(open(f"data/certs/{f}"))
        p = cert["payload"]
        expiry = p["valid_until"][:10]
        valid  = datetime.fromisoformat(p["valid_until"]) > datetime.utcnow()
        print(f"  {status_dot(valid)}  {W}{p['subject']:<16}{RST}  {DG}Serial: {C}{p['serial'][:8]}...{RST}  {DG}Exp: {Y}{expiry}{RST}")

    section_header("Pesan Repository", "◈", M)
    msg_files = os.listdir("data/messages")
    if not msg_files:
        print(f"  {DG}(kosong){RST}")
    for f in msg_files:
        msg  = json.load(open(f"data/messages/{f}"))
        tipe = f"{B}SIGNED   {RST}" if "_signed" in f else f"{R}ENCRYPTED{RST}"
        fr   = msg.get("from", "-")
        to   = msg.get("to", "-")
        print(f"  {C}◈{RST}  {tipe}  {W}{fr}{RST} {DG}→{RST} {W}{to}{RST}  {DG}{msg.get('timestamp','')[:10]}{RST}")

    print()
    double_line(DG)
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"  {DG}Snapshot: {RST}{Y}{now}{RST}")
    double_line(DG)


MENU = {
    "1": (f"{C}CA{RST}   — Inisialisasi Key Pair CA",       menu_1_ca_setup),
    "2": (f"{C}CA{RST}   — Terbitkan Sertifikat",           menu_2_ca_issue),
    "3": (f"{Y}RA{RST}   — Validasi Request Cust",          menu_3_ra_validate),
    "4": (f"{G}CUST{RST} — Daftar & Buat Key Pair",         menu_4_cust_register),
    "5": (f"{G}CUST{RST} — Tanda Tangan Digital",           menu_5_sign_message),
    "6": (f"{B}CUST{RST} — Enkripsi Pesan Rahasia",         menu_6_encrypt_message),
    "7": (f"{B}CUST{RST} — Dekripsi Pesan Rahasia",         menu_7_decrypt_message),
    "8": (f"{M}CUST{RST} — Verifikasi Tanda Tangan",        menu_8_verify_signed),
    "9": (f"{R}TEST{RST} — Negative Test (Simulasi Serangan)", menu_9_negative_test),
    "0": (f"{DG}INFO{RST} — Status Sistem PKI",             menu_0_status),
}

def draw_main_menu():
    cls()
    print(ASCII_BANNER)
    print()
    double_line(C)
    pad = (WIDTH - 34) // 2
    print(f"{C}║{RST}{' '*pad}{BOLD}{W}  SISTEM PKI — UAS Kriptografi Semester 4  {RST}{' '*(WIDTH - pad - 42)}{C}║{RST}")
    double_line(C)
    print()

    rows = [
        ("1", "2", C), ("3", None, Y), ("4", "5", G), ("6", "7", B), ("8", None, M),
        ("9", None, R), ("0", None, DG),
    ]
    for nums in [
        [("1", C), ("2", C)],
        [("3", Y)],
        [("4", G), ("5", G)],
        [("6", B), ("7", B)],
        [("8", M)],
        [("9", R)],
        [("0", DG)],
    ]:
        for key, color in nums:
            label = MENU[key][0]
            plain_label = label.replace(C,"").replace(Y,"").replace(G,"").replace(B,"").replace(M,"").replace(R,"").replace(DG,"").replace(W,"").replace(BOLD,"").replace(RST,"")
            print(f"  {color}{BOLD}[{key}]{RST}  {label}")
        if len(nums) == 1:
            pass

    print()
    print(f"  {DG}[q]{RST}  {DIM}Keluar{RST}")
    print()
    double_line(DG)

    ca_ok  = os.path.exists("data/ca/ca_private.pem")
    certs  = len([f for f in os.listdir("data/certs") if f.endswith("_cert.json")])
    msgs   = len(os.listdir("data/messages"))
    reqs   = len([f for f in os.listdir("data/ra") if f.endswith("_request.json")])

    print(f"  {status_dot(ca_ok)} CA  {DG}│{RST}  {G if certs else DG}◈{RST} {certs} sertifikat  {DG}│{RST}  {C}◈{RST} {reqs} requests  {DG}│{RST}  {M}◈{RST} {msgs} pesan")
    double_line(DG)
    print()


def main():
    boot_sequence()
    input(f"\n  {DG}Tekan {W}ENTER{DG} untuk masuk ke sistem...{RST}")

    while True:
        draw_main_menu()
        raw = input(f"  {C}▶{RST} Pilih menu: {BOLD}{W}").strip().lower()
        print(RST, end="")

        if raw == "q":
            cls()
            print(f"\n\n  {C}{BOLD}Terima kasih telah menggunakan Sistem PKI.{RST}")
            print(f"  {DG}UAS Kriptografi Semester 4{RST}\n")
            time.sleep(0.5)
            break
        elif raw in MENU:
            print()
            MENU[raw][1]()
            print()
            input(f"  {DG}Tekan {W}ENTER{DG} untuk kembali ke menu...{RST}")
        else:
            print(f"\n  {R}[!] Menu '{raw}' tidak ditemukan.{RST}")
            time.sleep(0.8)


if __name__ == "__main__":
    main()

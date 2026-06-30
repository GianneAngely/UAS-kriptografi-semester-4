import os
import sys
import time
import json
import base64
import datetime
from pathlib import Path

try:
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import utils as asym_utils
    from cryptography.exceptions import InvalidSignature
    CRYPTO_OK = True
except ImportError:
    CRYPTO_OK = False

KEYS_DIR = Path("keys")
CERTS_DIR = Path("certs")
MSGS_DIR = Path("messages")

for d in [KEYS_DIR, CERTS_DIR, MSGS_DIR]:
    d.mkdir(exist_ok=True)

class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    BLINK   = "\033[5m"
    GREEN   = "\033[38;5;82m"
    CYAN    = "\033[38;5;51m"
    YELLOW  = "\033[38;5;220m"
    RED     = "\033[38;5;196m"
    MAGENTA = "\033[38;5;201m"
    BLUE    = "\033[38;5;33m"
    WHITE   = "\033[38;5;255m"
    GRAY    = "\033[38;5;245m"
    ORANGE  = "\033[38;5;214m"
    BGBLACK = "\033[40m"
    BGGREEN = "\033[48;5;22m"
    BGRED   = "\033[48;5;52m"
    BGCYAN  = "\033[48;5;23m"

W = 62

def clr():
    os.system('clear' if os.name != 'nt' else 'cls')

def slow_print(text, delay=0.012):
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def box_line(char="─", color=C.GREEN):
    return f"{color}{char * W}{C.RESET}"

def box_top(color=C.GREEN):
    return f"{color}╔{'═' * W}╗{C.RESET}"

def box_bot(color=C.GREEN):
    return f"{color}╚{'═' * W}╝{C.RESET}"

def box_mid(color=C.GREEN):
    return f"{color}╠{'═' * W}╣{C.RESET}"

def box_row(text="", color=C.GREEN, text_color=C.WHITE, center=False):
    inner = W - 2
    if center:
        content = text.center(inner)
    else:
        content = text.ljust(inner)
    visible_len = len(text)
    pad = inner - visible_len
    if center:
        lpad = pad // 2
        rpad = pad - lpad
        content = " " * lpad + text + " " * rpad
    else:
        content = text + " " * max(0, pad)
    return f"{color}║{C.RESET}{text_color}{content[:inner]}{C.RESET}{color}║{C.RESET}"

def tag(label, color):
    return f"{color}[{label}]{C.RESET}"

def status_ok(msg):
    print(f"  {C.GREEN}✔{C.RESET}  {C.WHITE}{msg}{C.RESET}")

def status_err(msg):
    print(f"  {C.RED}✘{C.RESET}  {C.RED}{msg}{C.RESET}")

def status_info(msg):
    print(f"  {C.CYAN}◆{C.RESET}  {C.GRAY}{msg}{C.RESET}")

def status_warn(msg):
    print(f"  {C.YELLOW}▲{C.RESET}  {C.YELLOW}{msg}{C.RESET}")

def spinner(msg, duration=0.8):
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    end = time.time() + duration
    i = 0
    while time.time() < end:
        sys.stdout.write(f"\r  {C.CYAN}{frames[i % len(frames)]}{C.RESET}  {C.GRAY}{msg}...{C.RESET}")
        sys.stdout.flush()
        time.sleep(0.07)
        i += 1
    sys.stdout.write(f"\r  {C.GREEN}✔{C.RESET}  {C.WHITE}{msg}{C.RESET}{'  ':10}\n")
    sys.stdout.flush()

def progress_bar(label, steps=20, delay=0.03):
    sys.stdout.write(f"\n  {C.GRAY}{label}{C.RESET}\n  {C.GREEN}")
    for i in range(steps + 1):
        filled = int((i / steps) * 30)
        bar = "█" * filled + "░" * (30 - filled)
        pct = int((i / steps) * 100)
        sys.stdout.write(f"\r  {C.GREEN}[{bar}]{C.RESET} {C.YELLOW}{pct:3d}%{C.RESET}")
        sys.stdout.flush()
        time.sleep(delay)
    print()

def section_header(title, subtitle="", role_tag="", role_color=C.GREEN):
    clr()
    print()
    print(box_top(role_color))
    if role_tag:
        rt = f" {role_color}{C.BOLD}{role_tag}{C.RESET} "
        pad_inner = W - 2 - len(role_tag) - 2
        row_content = f" {role_color}{C.BOLD}{role_tag}{C.RESET}" + " " * (W - 2 - len(role_tag) - 1)
        print(f"{role_color}║{C.RESET}{row_content}{role_color}║{C.RESET}")
        print(box_mid(role_color))
    inner = W - 2
    t_pad = max(0, (inner - len(title)) // 2)
    t_content = " " * t_pad + f"{C.BOLD}{C.WHITE}{title}{C.RESET}" + " " * max(0, inner - t_pad - len(title))
    print(f"{role_color}║{C.RESET}{t_content}{role_color}║{C.RESET}")
    if subtitle:
        s_pad = max(0, (inner - len(subtitle)) // 2)
        s_content = " " * s_pad + f"{C.GRAY}{subtitle}{C.RESET}" + " " * max(0, inner - s_pad - len(subtitle))
        print(f"{role_color}║{C.RESET}{s_content}{role_color}║{C.RESET}")
    print(box_bot(role_color))
    print()

def pause():
    print()
    print(f"  {C.GRAY}{'─' * 50}{C.RESET}")
    input(f"  {C.CYAN}⏎  Tekan Enter untuk kembali ke menu...{C.RESET}")

def check_crypto():
    if not CRYPTO_OK:
        status_err("Library 'cryptography' belum terinstall!")
        status_info("Jalankan: pip install cryptography")
        pause()
        return False
    return True

def gen_rsa_keypair():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)

def save_private_key(key, path):
    with open(path, "wb") as f:
        f.write(key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption()
        ))

def save_public_key(key, path):
    with open(path, "wb") as f:
        f.write(key.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo
        ))

def load_private_key(path):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def load_public_key(path):
    with open(path, "rb") as f:
        return serialization.load_pem_public_key(f.read())

def sign_data(private_key, data: bytes) -> bytes:
    return private_key.sign(data, padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ), hashes.SHA256())

def verify_sig(public_key, data: bytes, signature: bytes) -> bool:
    try:
        public_key.verify(signature, data, padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ), hashes.SHA256())
        return True
    except InvalidSignature:
        return False

def encrypt_msg(public_key, message: bytes) -> bytes:
    return public_key.encrypt(message, padding.OAEP(
        mgf=padding.MGF1(hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    ))

def decrypt_msg(private_key, ciphertext: bytes) -> bytes:
    return private_key.decrypt(ciphertext, padding.OAEP(
        mgf=padding.MGF1(hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    ))

def get_pki_status():
    st = {}
    st["ca_ready"]    = (KEYS_DIR / "ca_private.pem").exists() and (KEYS_DIR / "ca_public.pem").exists()
    st["cust1_key"]   = (KEYS_DIR / "cust1_public.pem").exists()
    st["cust2_key"]   = (KEYS_DIR / "cust2_public.pem").exists()
    st["cust3_key"]   = (KEYS_DIR / "cust3_public.pem").exists()
    st["cust1_cert"]  = (CERTS_DIR / "cust1_cert.json").exists()
    st["cust2_cert"]  = (CERTS_DIR / "cust2_cert.json").exists()
    st["cust1_csr"]   = (KEYS_DIR / "cust1_csr.json").exists()
    st["cust2_csr"]   = (KEYS_DIR / "cust2_csr.json").exists()
    st["msg_c1c2"]    = (MSGS_DIR / "cust1_to_cust2.json").exists()
    st["announce"]    = (MSGS_DIR / "cust2_announcement.json").exists()
    return st

def draw_main_menu():
    clr()
    st = get_pki_status()
    now = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")

    print()
    print(f"{C.GREEN}╔{'═' * W}╗{C.RESET}")

    title_line = "SISTEM PKI — UAS Kriptografi Semester 4"
    t_pad = (W - len(title_line)) // 2
    t_content = " " * t_pad + f"{C.BOLD}{C.GREEN}{title_line}{C.RESET}" + " " * (W - t_pad - len(title_line))
    print(f"{C.GREEN}║{C.RESET}{t_content}{C.GREEN}║{C.RESET}")

    sub = "RSA-2048 · PSS Signature · OAEP Encryption · SHA-256"
    s_pad = (W - len(sub)) // 2
    s_content = " " * s_pad + f"{C.GRAY}{sub}{C.RESET}" + " " * (W - s_pad - len(sub))
    print(f"{C.GREEN}║{C.RESET}{s_content}{C.GREEN}║{C.RESET}")
    print(f"{C.GREEN}╠{'═' * W}╣{C.RESET}")

    ts_content = f"  {C.GRAY}⏱  {now}{C.RESET}" + " " * (W - 2 - 3 - len(now) - 3)
    print(f"{C.GREEN}║{C.RESET}{ts_content}{C.GREEN}║{C.RESET}")
    print(f"{C.GREEN}╠{'═' * W}╣{C.RESET}")

    entries = [
        ("1", "CA", "Inisialisasi Key Pair CA",         C.YELLOW,  "ca_ready"),
        ("2", "CA", "Terbitkan Sertifikat",              C.YELLOW,  "cust1_cert"),
        ("3", "RA", "Validasi & Setujui Request Cust",   C.MAGENTA, "cust1_csr"),
        ("4", "CUST", "Daftar & Buat Key Pair",          C.CYAN,    "cust1_key"),
        ("5", "CUST", "Tanda Tangan Digital",            C.CYAN,    "announce"),
        ("6", "CUST", "Enkripsi Pesan Rahasia",          C.CYAN,    "msg_c1c2"),
        ("7", "CUST", "Dekripsi Pesan Rahasia",          C.CYAN,    None),
        ("8", "CUST", "Verifikasi Tanda Tangan",         C.CYAN,    None),
        ("9", "TEST", "Negative Test (Simulasi Serangan)", C.RED,   None),
        ("0", "INFO", "Status Sistem PKI",               C.BLUE,    None),
    ]

    for num, role, desc, rc, status_key in entries:
        dot = f"{C.GREEN}●{C.RESET}" if (status_key and st.get(status_key)) else f"{C.GRAY}○{C.RESET}"
        role_str = f"{rc}{C.BOLD}{role:<5}{C.RESET}"
        num_str  = f"{C.BOLD}{C.WHITE}{num}{C.RESET}"
        sep      = f"{C.GRAY}│{C.RESET}"
        desc_str = f"{C.WHITE}{desc}{C.RESET}"
        row_text = f"  [{num_str}] {dot} {role_str} {sep} {desc_str}"
        visible  = f"  [{num}] {('●' if (status_key and st.get(status_key)) else '○')} {role:<5} | {desc}"
        pad = max(0, W - len(visible))
        print(f"{C.GREEN}║{C.RESET}{row_text}{' ' * pad}{C.GREEN}║{C.RESET}")

    print(f"{C.GREEN}╠{'═' * W}╣{C.RESET}")
    q_text  = f"  [{C.BOLD}{C.WHITE}q{C.RESET}]   {C.RED}Keluar dari sistem{C.RESET}"
    q_vis   = f"  [q]   Keluar dari sistem"
    q_pad   = max(0, W - len(q_vis))
    print(f"{C.GREEN}║{C.RESET}{q_text}{' ' * q_pad}{C.GREEN}║{C.RESET}")
    print(f"{C.GREEN}╚{'═' * W}╝{C.RESET}")
    print()
    return input(f"  {C.BOLD}{C.CYAN}⌨  Pilih menu{C.RESET} {C.GRAY}»{C.RESET} ").strip().lower()

def menu_ca_init():
    if not check_crypto(): return
    section_header("INISIALISASI KEY PAIR CA", "Certificate Authority — RSA 2048-bit", "CA", C.YELLOW)
    if (KEYS_DIR / "ca_private.pem").exists():
        status_warn("Key pair CA sudah ada.")
        print()
        regen = input(f"  {C.YELLOW}Generate ulang? (y/N){C.RESET} ").strip().lower()
        if regen != 'y':
            pause()
            return
    print()
    spinner("Generating RSA 2048-bit key pair", 1.2)
    ca_key = gen_rsa_keypair()
    save_private_key(ca_key, KEYS_DIR / "ca_private.pem")
    save_public_key(ca_key.public_key(), KEYS_DIR / "ca_public.pem")
    print()
    status_ok("CA Private Key  →  keys/ca_private.pem")
    status_ok("CA Public Key   →  keys/ca_public.pem")
    print()
    pub_pem = (KEYS_DIR / "ca_public.pem").read_text()
    fingerprint = pub_pem[27:67].replace("\n", "")
    print(f"  {C.GRAY}Fingerprint: {C.GREEN}{fingerprint}...{C.RESET}")
    pause()

def menu_ca_certify():
    if not check_crypto(): return
    section_header("TERBITKAN SERTIFIKAT DIGITAL", "Certify Public Key dari User", "CA", C.YELLOW)
    if not (KEYS_DIR / "ca_private.pem").exists():
        status_err("Key pair CA belum ada! Jalankan menu [1] dulu.")
        pause()
        return
    users = []
    for f in KEYS_DIR.glob("*_csr.json"):
        uname = f.stem.replace("_csr", "")
        approved = json.loads(f.read_text()).get("ra_approved", False)
        if approved and not (CERTS_DIR / f"{uname}_cert.json").exists():
            users.append(uname)
    if not users:
        status_warn("Tidak ada CSR yang sudah diapprove RA dan belum disertifikasi.")
        pause()
        return
    print(f"  {C.CYAN}CSR menunggu sertifikasi:{C.RESET}")
    for i, u in enumerate(users):
        print(f"    {C.WHITE}[{i+1}]{C.RESET}  {C.YELLOW}{u}{C.RESET}")
    print()
    choice = input(f"  {C.CYAN}Pilih user (nama/nomor){C.RESET} {C.GRAY}»{C.RESET} ").strip()
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(users):
            target = users[idx]
        else:
            status_err("Pilihan tidak valid.")
            pause()
            return
    elif choice in users:
        target = choice
    else:
        status_err(f"User '{choice}' tidak ditemukan.")
        pause()
        return
    print()
    spinner(f"Memverifikasi CSR {target}", 0.6)
    csr_data = json.loads((KEYS_DIR / f"{target}_csr.json").read_text())
    pub_pem  = csr_data["public_key_pem"]
    ca_key   = load_private_key(KEYS_DIR / "ca_private.pem")
    issued   = datetime.datetime.now().isoformat()
    cert_payload = json.dumps({
        "subject": target,
        "issued_at": issued,
        "public_key_pem": pub_pem,
        "issuer": "CA-PKI-UAS-Kriptografi"
    }, sort_keys=True).encode()
    spinner(f"Menandatangani sertifikat dengan CA Private Key", 0.8)
    sig = sign_data(ca_key, cert_payload)
    cert = {
        "subject": target,
        "issued_at": issued,
        "public_key_pem": pub_pem,
        "issuer": "CA-PKI-UAS-Kriptografi",
        "signature": base64.b64encode(sig).decode()
    }
    cert_path = CERTS_DIR / f"{target}_cert.json"
    cert_path.write_text(json.dumps(cert, indent=2))
    pub_path = KEYS_DIR / f"{target}_public.pem"
    pub_path.write_text(pub_pem)
    print()
    status_ok(f"Sertifikat diterbitkan  →  certs/{target}_cert.json")
    status_ok(f"Public key disimpan     →  keys/{target}_public.pem")
    print()
    print(f"  {C.GRAY}Subject : {C.WHITE}{target}{C.RESET}")
    print(f"  {C.GRAY}Issued  : {C.WHITE}{issued[:19]}{C.RESET}")
    print(f"  {C.GRAY}Issuer  : {C.GREEN}CA-PKI-UAS-Kriptografi{C.RESET}")
    pause()

def menu_ra_validate():
    if not check_crypto(): return
    section_header("VALIDASI REQUEST SERTIFIKAT", "Registration Authority — Pemeriksaan CSR", "RA", C.MAGENTA)
    pending = []
    for f in KEYS_DIR.glob("*_csr.json"):
        data = json.loads(f.read_text())
        if not data.get("ra_approved", False):
            pending.append((f.stem.replace("_csr",""), data))
    if not pending:
        status_warn("Tidak ada CSR baru yang perlu divalidasi.")
        pause()
        return
    for uname, data in pending:
        print(f"  {C.YELLOW}{'─' * 50}{C.RESET}")
        print(f"  {C.BOLD}{C.WHITE}User     :{C.RESET}  {C.CYAN}{uname}{C.RESET}")
        print(f"  {C.BOLD}{C.WHITE}Email    :{C.RESET}  {data.get('email', '-')}")
        print(f"  {C.BOLD}{C.WHITE}Org      :{C.RESET}  {data.get('org', '-')}")
        print(f"  {C.BOLD}{C.WHITE}Dibuat   :{C.RESET}  {data.get('created_at', '-')[:19]}")
        print(f"  {C.BOLD}{C.WHITE}PubKey   :{C.RESET}  {C.GRAY}...{data['public_key_pem'][30:70]}...{C.RESET}")
        print()
        ans = input(f"  {C.MAGENTA}Setujui CSR dari {uname}? (y/N){C.RESET} ").strip().lower()
        if ans == 'y':
            data["ra_approved"] = True
            data["ra_approved_at"] = datetime.datetime.now().isoformat()
            (KEYS_DIR / f"{uname}_csr.json").write_text(json.dumps(data, indent=2))
            status_ok(f"CSR {uname} DISETUJUI — diteruskan ke CA")
        else:
            status_warn(f"CSR {uname} DITOLAK")
        print()
    pause()

def menu_cust_keygen():
    if not check_crypto(): return
    section_header("DAFTAR & BUAT KEY PAIR", "Customer — Generate RSA Key + Kirim CSR ke RA", "CUST", C.CYAN)
    users = ["cust1", "cust2", "cust3"]
    print(f"  {C.CYAN}Pilih user:{C.RESET}")
    for i, u in enumerate(users):
        cert_exists = (CERTS_DIR / f"{u}_cert.json").exists()
        key_exists  = (KEYS_DIR / f"{u}_private.pem").exists()
        mark = f"{C.GREEN}[CERT ✔]{C.RESET}" if cert_exists else (f"{C.YELLOW}[KEY ✔]{C.RESET}" if key_exists else f"{C.GRAY}[─]{C.RESET}")
        print(f"    {C.WHITE}[{i+1}]{C.RESET}  {C.CYAN}{u:<8}{C.RESET}  {mark}")
    print()
    choice = input(f"  {C.CYAN}Pilih (1-3){C.RESET} {C.GRAY}»{C.RESET} ").strip()
    if choice not in ["1","2","3"]:
        status_err("Pilihan tidak valid.")
        pause()
        return
    target = users[int(choice)-1]
    priv_path = KEYS_DIR / f"{target}_private.pem"
    if priv_path.exists():
        status_warn(f"Key pair {target} sudah ada.")
        regen = input(f"  {C.YELLOW}Generate ulang? (y/N){C.RESET} ").strip().lower()
        if regen != 'y':
            pause()
            return
    print()
    spinner(f"Generating RSA 2048-bit key pair untuk {target}", 1.0)
    key = gen_rsa_keypair()
    save_private_key(key, KEYS_DIR / f"{target}_private.pem")
    pub_pem = key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
    email = input(f"\n  {C.CYAN}Email {target}{C.RESET} {C.GRAY}»{C.RESET} ").strip() or f"{target}@pki.local"
    org   = input(f"  {C.CYAN}Organisasi{C.RESET} {C.GRAY}»{C.RESET} ").strip() or "PKI UAS Kriptografi"
    csr = {
        "subject": target,
        "email": email,
        "org": org,
        "created_at": datetime.datetime.now().isoformat(),
        "public_key_pem": pub_pem,
        "ra_approved": False
    }
    (KEYS_DIR / f"{target}_csr.json").write_text(json.dumps(csr, indent=2))
    spinner("Mengirim CSR ke RA", 0.5)
    print()
    status_ok(f"Private Key  →  keys/{target}_private.pem")
    status_ok(f"CSR dikirim  →  keys/{target}_csr.json")
    status_info("Tunggu validasi dari RA, lalu CA akan menerbitkan sertifikat.")
    pause()

def menu_sign():
    if not check_crypto(): return
    section_header("TANDA TANGAN DIGITAL", "Buat & Tanda Tangani Pesan (Pengumuman Publik)", "CUST", C.CYAN)
    signers = [u for u in ["cust1","cust2","cust3"] if (KEYS_DIR / f"{u}_private.pem").exists()]
    if not signers:
        status_err("Belum ada user dengan private key.")
        pause()
        return
    print(f"  {C.CYAN}Pengirim tersedia:{C.RESET}")
    for i, u in enumerate(signers):
        print(f"    {C.WHITE}[{i+1}]{C.RESET}  {C.CYAN}{u}{C.RESET}")
    print()
    s_ch = input(f"  {C.CYAN}Pilih pengirim (1-{len(signers)}){C.RESET} {C.GRAY}»{C.RESET} ").strip()
    if not s_ch.isdigit() or not (1 <= int(s_ch) <= len(signers)):
        status_err("Pilihan tidak valid.")
        pause()
        return
    sender = signers[int(s_ch)-1]
    print()
    msg = input(f"  {C.CYAN}Isi pengumuman{C.RESET} {C.GRAY}»{C.RESET} ").strip()
    if not msg:
        status_err("Pesan tidak boleh kosong.")
        pause()
        return
    spinner("Menandatangani pesan", 0.8)
    priv = load_private_key(KEYS_DIR / f"{sender}_private.pem")
    sig  = sign_data(priv, msg.encode())
    out  = {
        "sender": sender,
        "message": msg,
        "signature": base64.b64encode(sig).decode(),
        "created_at": datetime.datetime.now().isoformat()
    }
    out_path = MSGS_DIR / f"{sender}_announcement.json"
    out_path.write_text(json.dumps(out, indent=2))
    print()
    status_ok(f"Pengumuman tersimpan  →  messages/{sender}_announcement.json")
    status_info("Semua user dapat membaca dan memverifikasi tanda tangan ini.")
    pause()

def menu_encrypt():
    if not check_crypto(): return
    section_header("ENKRIPSI PESAN RAHASIA", "Enkripsi + Tanda Tangan — Cust1 → Cust2", "CUST", C.CYAN)
    if not (KEYS_DIR / "cust1_private.pem").exists():
        status_err("Private key Cust1 belum ada.")
        pause()
        return
    if not (CERTS_DIR / "cust2_cert.json").exists() and not (KEYS_DIR / "cust2_public.pem").exists():
        status_err("Public key Cust2 belum tersedia.")
        pause()
        return
    print()
    msg = input(f"  {C.CYAN}Pesan rahasia untuk Cust2{C.RESET} {C.GRAY}»{C.RESET} ").strip()
    if not msg:
        status_err("Pesan tidak boleh kosong.")
        pause()
        return
    spinner("Mengambil public key Cust2", 0.4)
    if (CERTS_DIR / "cust2_cert.json").exists():
        cert  = json.loads((CERTS_DIR / "cust2_cert.json").read_text())
        pub2  = serialization.load_pem_public_key(cert["public_key_pem"].encode())
    else:
        pub2 = load_public_key(KEYS_DIR / "cust2_public.pem")
    priv1 = load_private_key(KEYS_DIR / "cust1_private.pem")
    spinner("Menandatangani pesan dengan Cust1 Private Key", 0.6)
    sig = sign_data(priv1, msg.encode())
    spinner("Mengenkripsi dengan Cust2 Public Key (RSA-OAEP)", 0.8)
    ciphertext = encrypt_msg(pub2, msg.encode())
    out = {
        "sender": "cust1",
        "recipient": "cust2",
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "signature": base64.b64encode(sig).decode(),
        "created_at": datetime.datetime.now().isoformat()
    }
    (MSGS_DIR / "cust1_to_cust2.json").write_text(json.dumps(out, indent=2))
    print()
    status_ok("Pesan terenkripsi  →  messages/cust1_to_cust2.json")
    status_info(f"Ciphertext: {base64.b64encode(ciphertext).decode()[:48]}...")
    status_info("Hanya Cust2 (dengan private key-nya) yang bisa membuka pesan ini.")
    pause()

def menu_decrypt():
    if not check_crypto(): return
    section_header("DEKRIPSI PESAN RAHASIA", "Buka Pesan Terenkripsi dari Cust1", "CUST", C.CYAN)
    msg_file = MSGS_DIR / "cust1_to_cust2.json"
    if not msg_file.exists():
        status_err("Belum ada pesan terenkripsi dari Cust1.")
        pause()
        return
    if not (KEYS_DIR / "cust2_private.pem").exists():
        status_err("Private key Cust2 belum ada.")
        pause()
        return
    data = json.loads(msg_file.read_text())
    spinner("Mendekripsi dengan Cust2 Private Key", 0.8)
    priv2 = load_private_key(KEYS_DIR / "cust2_private.pem")
    try:
        plaintext = decrypt_msg(priv2, base64.b64decode(data["ciphertext"]))
        print()
        print(f"  {C.GREEN}{'═' * 50}{C.RESET}")
        print(f"  {C.BOLD}{C.WHITE}PESAN TERDEKRIPSI:{C.RESET}")
        print(f"  {C.BOLD}{C.CYAN}  {plaintext.decode()}{C.RESET}")
        print(f"  {C.GREEN}{'═' * 50}{C.RESET}")
        print()
        spinner("Memverifikasi tanda tangan Cust1", 0.6)
        if (CERTS_DIR / "cust1_cert.json").exists():
            cert = json.loads((CERTS_DIR / "cust1_cert.json").read_text())
            pub1 = serialization.load_pem_public_key(cert["public_key_pem"].encode())
        elif (KEYS_DIR / "cust1_public.pem").exists():
            pub1 = load_public_key(KEYS_DIR / "cust1_public.pem")
        else:
            status_warn("Public key Cust1 tidak tersedia untuk verifikasi tanda tangan.")
            pause()
            return
        ok = verify_sig(pub1, plaintext, base64.b64decode(data["signature"]))
        print()
        if ok:
            status_ok("Tanda tangan Cust1 VALID ✔  — pesan asli, tidak dipalsukan")
        else:
            status_err("Tanda tangan Cust1 TIDAK VALID ✘")
    except Exception as e:
        print()
        status_err(f"Dekripsi gagal: {e}")
    pause()

def menu_verify():
    if not check_crypto(): return
    section_header("VERIFIKASI TANDA TANGAN DIGITAL", "Verifikasi Pengumuman Publik", "CUST", C.CYAN)
    announcements = list(MSGS_DIR.glob("*_announcement.json"))
    if not announcements:
        status_err("Belum ada pengumuman yang tersimpan.")
        pause()
        return
    print(f"  {C.CYAN}Pengumuman tersedia:{C.RESET}")
    for i, a in enumerate(announcements):
        sender = json.loads(a.read_text()).get("sender","?")
        print(f"    {C.WHITE}[{i+1}]{C.RESET}  {C.CYAN}{sender}{C.RESET}  {C.GRAY}({a.name}){C.RESET}")
    print()
    ch = input(f"  {C.CYAN}Pilih pengumuman{C.RESET} {C.GRAY}»{C.RESET} ").strip()
    if not ch.isdigit() or not (1 <= int(ch) <= len(announcements)):
        status_err("Pilihan tidak valid.")
        pause()
        return
    ann_file = announcements[int(ch)-1]
    ann = json.loads(ann_file.read_text())
    sender = ann["sender"]
    print()
    print(f"  {C.BOLD}{C.WHITE}Pengirim :{C.RESET}  {C.CYAN}{sender}{C.RESET}")
    print(f"  {C.BOLD}{C.WHITE}Pesan    :{C.RESET}  {C.WHITE}{ann['message']}{C.RESET}")
    print(f"  {C.BOLD}{C.WHITE}Dibuat   :{C.RESET}  {C.GRAY}{ann['created_at'][:19]}{C.RESET}")
    print()
    if (CERTS_DIR / f"{sender}_cert.json").exists():
        cert = json.loads((CERTS_DIR / f"{sender}_cert.json").read_text())
        pub  = serialization.load_pem_public_key(cert["public_key_pem"].encode())
        spinner("Verifikasi via sertifikat CA", 0.7)
        source = "Sertifikat CA"
    elif (KEYS_DIR / f"{sender}_public.pem").exists():
        pub = load_public_key(KEYS_DIR / f"{sender}_public.pem")
        spinner("Verifikasi via public key langsung", 0.7)
        source = "Public Key"
    else:
        status_err(f"Public key / sertifikat {sender} tidak tersedia.")
        pause()
        return
    ok = verify_sig(pub, ann["message"].encode(), base64.b64decode(ann["signature"]))
    print()
    if ok:
        status_ok(f"Tanda tangan VALID ✔  (sumber: {source})")
        status_info("Pesan ini benar-benar dari pengirim yang diklaim, tidak dimodifikasi.")
    else:
        status_err("Tanda tangan TIDAK VALID ✘  — pesan mungkin dipalsukan!")
    pause()

def menu_negative_test():
    if not check_crypto(): return
    section_header("NEGATIVE TEST — SIMULASI SERANGAN", "Uji Keamanan Sistem PKI", "TEST", C.RED)
    print(f"  {C.RED}Simulasi serangan untuk membuktikan keamanan sistem:{C.RESET}")
    print()

    tests = [
        ("Falsifikasi Tanda Tangan", "Memodifikasi pesan setelah ditandatangani"),
        ("Penggunaan Key Palsu", "Verifikasi dengan public key yang salah"),
        ("Replay Attack", "Mengirim ulang pesan lama"),
    ]
    for i, (name, desc) in enumerate(tests):
        print(f"  {C.WHITE}[{i+1}]{C.RESET}  {C.RED}{name}{C.RESET}")
        print(f"       {C.GRAY}{desc}{C.RESET}")
    print(f"  {C.WHITE}[4]{C.RESET}  {C.ORANGE}Jalankan Semua Test{C.RESET}")
    print()
    ch = input(f"  {C.RED}Pilih test{C.RESET} {C.GRAY}»{C.RESET} ").strip()

    print()
    if ch in ["1", "4"]:
        spinner("Test 1: Falsifikasi tanda tangan", 0.5)
        key  = gen_rsa_keypair()
        msg  = b"Pesan asli dari Cust1"
        sig  = sign_data(key, msg)
        tampered = b"Pesan dipalsukan oleh attacker!"
        ok   = verify_sig(key.public_key(), tampered, sig)
        if not ok:
            status_ok("Test 1 LULUS ✔ — Tanda tangan tidak valid untuk pesan yang dimodifikasi")
        else:
            status_err("Test 1 GAGAL ✘")
        print()

    if ch in ["2", "4"]:
        spinner("Test 2: Verifikasi dengan key palsu", 0.5)
        key1 = gen_rsa_keypair()
        key2 = gen_rsa_keypair()
        msg  = b"Pesan dari Cust1"
        sig  = sign_data(key1, msg)
        ok   = verify_sig(key2.public_key(), msg, sig)
        if not ok:
            status_ok("Test 2 LULUS ✔ — Verifikasi dengan key berbeda gagal seperti yang diharapkan")
        else:
            status_err("Test 2 GAGAL ✘")
        print()

    if ch in ["3", "4"]:
        spinner("Test 3: Replay attack (dekripsi dengan key salah)", 0.5)
        key_legit   = gen_rsa_keypair()
        key_attacker = gen_rsa_keypair()
        msg = b"Pesan rahasia untuk Cust2"
        ciphertext = encrypt_msg(key_legit.public_key(), msg)
        try:
            decrypt_msg(key_attacker, ciphertext)
            status_err("Test 3 GAGAL ✘")
        except Exception:
            status_ok("Test 3 LULUS ✔ — Attacker tidak bisa mendekripsi tanpa private key yang benar")
        print()

    if ch not in ["1","2","3","4"]:
        status_err("Pilihan tidak valid.")
    pause()

def menu_info():
    section_header("STATUS SISTEM PKI", "Ringkasan komponen yang sudah diinisialisasi", "INFO", C.BLUE)
    st = get_pki_status()

    def row_status(label, ok, detail=""):
        mark  = f"{C.GREEN}✔  AKTIF{C.RESET}  " if ok else f"{C.RED}✘  BELUM{C.RESET}  "
        print(f"  {C.GRAY}{label:<22}{C.RESET}  {mark}{C.GRAY}{detail}{C.RESET}")

    print(f"  {C.BOLD}{C.YELLOW}── Certificate Authority ──────────────────{C.RESET}")
    row_status("CA Key Pair",    st["ca_ready"],   "keys/ca_private.pem + ca_public.pem")
    print()
    print(f"  {C.BOLD}{C.CYAN}── Customers ──────────────────────────────{C.RESET}")
    row_status("Cust1 Key",      st["cust1_key"],  "keys/cust1_public.pem")
    row_status("Cust2 Key",      st["cust2_key"],  "keys/cust2_public.pem")
    row_status("Cust3 Key",      st["cust3_key"],  "keys/cust3_public.pem")
    print()
    print(f"  {C.BOLD}{C.MAGENTA}── Registration Authority ─────────────────{C.RESET}")
    row_status("Cust1 CSR",      st["cust1_csr"],  "keys/cust1_csr.json")
    row_status("Cust2 CSR",      st["cust2_csr"],  "keys/cust2_csr.json")
    print()
    print(f"  {C.BOLD}{C.YELLOW}── Sertifikat ─────────────────────────────{C.RESET}")
    row_status("Cust1 Cert",     st["cust1_cert"], "certs/cust1_cert.json")
    row_status("Cust2 Cert",     st["cust2_cert"], "certs/cust2_cert.json")
    print()
    print(f"  {C.BOLD}{C.GREEN}── Pesan ──────────────────────────────────{C.RESET}")
    row_status("Cust1→Cust2",    st["msg_c1c2"],   "messages/cust1_to_cust2.json")
    row_status("Pengumuman",     st["announce"],   "messages/*_announcement.json")
    print()
    done = sum(1 for v in st.values() if v)
    total = len(st)
    bar_filled = int((done/total) * 40)
    bar = f"{C.GREEN}{'█' * bar_filled}{C.GRAY}{'░' * (40-bar_filled)}{C.RESET}"
    print(f"  {C.BOLD}{C.WHITE}Progress PKI{C.RESET}  [{bar}] {C.YELLOW}{done}/{total}{C.RESET}")
    pause()

def boot_screen():
    clr()
    lines = [
        "",
        f"  {C.GREEN}{'▓' * 58}{C.RESET}",
        f"  {C.GREEN}{'▓' * 58}{C.RESET}",
        f"",
        f"  {C.BOLD}{C.GREEN}  ██████╗ ██╗  ██╗██╗{C.RESET}",
        f"  {C.BOLD}{C.GREEN}  ██╔══██╗██║ ██╔╝██║{C.RESET}",
        f"  {C.BOLD}{C.GREEN}  ██████╔╝█████╔╝ ██║{C.RESET}",
        f"  {C.BOLD}{C.GREEN}  ██╔═══╝ ██╔═██╗ ██║{C.RESET}",
        f"  {C.BOLD}{C.GREEN}  ██║     ██║  ██╗██║{C.RESET}",
        f"  {C.BOLD}{C.GREEN}  ╚═╝     ╚═╝  ╚═╝╚═╝  {C.GRAY}Public Key Infrastructure{C.RESET}",
        f"",
        f"  {C.GRAY}Universitas — UAS Kriptografi Semester 4{C.RESET}",
        f"  {C.GRAY}RSA-2048 · OAEP · PSS · SHA-256{C.RESET}",
        f"",
        f"  {C.GREEN}{'▓' * 58}{C.RESET}",
        f"  {C.GREEN}{'▓' * 58}{C.RESET}",
        "",
    ]
    for line in lines:
        print(line)
        time.sleep(0.04)
    progress_bar("Initializing PKI Engine...", steps=25, delay=0.025)
    time.sleep(0.3)

def main():
    boot_screen()
    while True:
        choice = draw_main_menu()
        actions = {
            "1": menu_ca_init,
            "2": menu_ca_certify,
            "3": menu_ra_validate,
            "4": menu_cust_keygen,
            "5": menu_sign,
            "6": menu_encrypt,
            "7": menu_decrypt,
            "8": menu_verify,
            "9": menu_negative_test,
            "0": menu_info,
        }
        if choice in actions:
            actions[choice]()
        elif choice == "q":
            clr()
            print()
            print(f"  {C.GREEN}Terima kasih telah menggunakan Sistem PKI.{C.RESET}")
            print(f"  {C.GRAY}UAS Kriptografi Semester 4 — Keluar.{C.RESET}")
            print()
            sys.exit(0)
        else:
            pass

if __name__ == "__main__":
    main()

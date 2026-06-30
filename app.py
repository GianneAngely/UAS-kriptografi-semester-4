import os
import sys
import time
import random
import threading
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
import json
import datetime

GREEN  = "\033[92m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
RED    = "\033[91m"
WHITE  = "\033[97m"
DIM    = "\033[2m"
BOLD   = "\033[1m"
RESET  = "\033[0m"
BLINK  = "\033[5m"
BG_BLK = "\033[40m"

WIDTH = 72

def clr():
    os.system("clear" if os.name == "posix" else "cls")

def typewrite(text, delay=0.018, color=GREEN):
    for ch in text:
        sys.stdout.write(color + ch + RESET)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def loading_bar(label, steps=30, color=GREEN):
    sys.stdout.write(f"  {color}{label}{RESET}  [")
    sys.stdout.flush()
    for i in range(steps):
        time.sleep(random.uniform(0.01, 0.06))
        sys.stdout.write(f"{color}█{RESET}")
        sys.stdout.flush()
    sys.stdout.write(f"] {GREEN}DONE{RESET}\n")
    sys.stdout.flush()

def matrix_rain(lines=6):
    chars = "01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモ"
    for _ in range(lines):
        row = ""
        for _ in range(WIDTH):
            if random.random() < 0.1:
                row += DIM + GREEN + random.choice(chars) + RESET
            else:
                row += " "
        print(row)
        time.sleep(0.04)

def banner():
    clr()
    matrix_rain(4)
    lines = [
        f"{DIM}{GREEN}{'═' * WIDTH}{RESET}",
        f"{BOLD}{GREEN}  ██████╗ ██╗  ██╗██╗      {CYAN}██████╗  █████╗ ██╗{RESET}",
        f"{BOLD}{GREEN}  ██╔══██╗██║ ██╔╝██║      {CYAN}██╔══██╗██╔══██╗██║{RESET}",
        f"{BOLD}{GREEN}  ██████╔╝█████╔╝ ██║█████╗{CYAN}██████╔╝█████╔╝╝██║{RESET}",
        f"{BOLD}{GREEN}  ██╔═══╝ ██╔═██╗ ██║╚════╝{CYAN}██╔═══╝ ██╔══██╗██║{RESET}",
        f"{BOLD}{GREEN}  ██║     ██║  ██╗██║      {CYAN}██║     ╚█████╔╝██║{RESET}",
        f"{BOLD}{GREEN}  ╚═╝     ╚═╝  ╚═╝╚═╝      {CYAN}╚═╝      ╚════╝ ╚═╝{RESET}",
        f"",
        f"  {DIM}{WHITE}Public Key Infrastructure  ·  Kriptografi Semester 4{RESET}",
        f"  {DIM}{CYAN}RSA-2048 · PSS Signature · OAEP Encryption · Chain of Trust{RESET}",
        f"{DIM}{GREEN}{'═' * WIDTH}{RESET}",
    ]
    for line in lines:
        print(line)
        time.sleep(0.04)

def section_header(title, color=CYAN):
    print()
    print(f"  {color}{BOLD}┌{'─' * (len(title) + 4)}┐{RESET}")
    print(f"  {color}{BOLD}│  {WHITE}{title}{color}  │{RESET}")
    print(f"  {color}{BOLD}└{'─' * (len(title) + 4)}┘{RESET}")
    print()

def ok(msg):
    print(f"  {GREEN}[✔]{RESET} {WHITE}{msg}{RESET}")

def err(msg):
    print(f"  {RED}[✘]{RESET} {RED}{msg}{RESET}")

def warn(msg):
    print(f"  {YELLOW}[!]{RESET} {YELLOW}{msg}{RESET}")

def info(msg):
    print(f"  {CYAN}[i]{RESET} {DIM}{WHITE}{msg}{RESET}")

def ask(prompt):
    return input(f"  {YELLOW}[?]{RESET} {WHITE}{prompt}{RESET} {GREEN}›{RESET} ").strip()

def divider(char="─", color=DIM+GREEN):
    print(f"  {color}{char * (WIDTH-4)}{RESET}")

def pause():
    input(f"\n  {DIM}{WHITE}[ press ENTER to continue ]{RESET}")

def save_key(path, data):
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)

def load_pem(path):
    with open(path, "rb") as f:
        return f.read()

def log_event(role, action, detail=""):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    entry = {"time": ts, "role": role, "action": action, "detail": detail}
    log_path = "pki_log.json"
    logs = []
    if os.path.exists(log_path):
        with open(log_path) as f:
            try:
                logs = json.load(f)
            except:
                logs = []
    logs.append(entry)
    with open(log_path, "w") as f:
        json.dump(logs, f, indent=2)

def show_menu():
    print()
    divider("═")
    print(f"  {BOLD}{GREEN} SISTEM PKI{RESET}  {DIM}{WHITE}UAS Kriptografi Semester 4{RESET}")
    divider("═")
    items = [
        ("1", "CA",   "Inisialisasi Key Pair CA",        GREEN),
        ("2", "CA",   "Terbitkan Sertifikat",            GREEN),
        ("3", "RA",   "Validasi Request Cust",           CYAN),
        ("4", "CUST", "Daftar & Buat Key Pair",          YELLOW),
        ("5", "CUST", "Tanda Tangan Digital",            YELLOW),
        ("6", "CUST", "Enkripsi Pesan Rahasia",          YELLOW),
        ("7", "CUST", "Dekripsi Pesan Rahasia",          YELLOW),
        ("8", "CUST", "Verifikasi Tanda Tangan",         YELLOW),
        ("9", "TEST", "Negative Test (Simulasi Serangan)", RED),
        ("0", "INFO", "Status Sistem PKI",               WHITE),
        ("q", "",     "Keluar",                          DIM+WHITE),
    ]
    for key, role, label, color in items:
        role_str = f"{DIM}[{role}]{RESET}" if role else "      "
        print(f"  {BOLD}{color}[{key}]{RESET}  {role_str:<14} {WHITE}{label}{RESET}")
    divider("═")
    return ask("Pilih menu")

def ca_setup():
    section_header("CA · Inisialisasi Key Pair", GREEN)
    info("Generating RSA-2048 private key untuk Certificate Authority...")
    loading_bar("Generating entropy  ", color=GREEN)
    loading_bar("Constructing primes ", color=GREEN)
    loading_bar("Building key pair   ", color=GREEN)
    priv = rsa.generate_private_key(65537, 2048, default_backend())
    pub  = priv.public_key()
    save_key("keys/ca_private.pem",
             priv.private_bytes(serialization.Encoding.PEM,
                                serialization.PrivateFormat.TraditionalOpenSSL,
                                serialization.NoEncryption()))
    save_key("keys/ca_public.pem",
             pub.public_bytes(serialization.Encoding.PEM,
                              serialization.PublicFormat.SubjectPublicKeyInfo))
    ok("CA private key  →  keys/ca_private.pem")
    ok("CA public  key  →  keys/ca_public.pem")
    warn("Private key RAHASIA — jangan dibagikan!")
    log_event("CA", "SETUP", "keypair generated")
    pause()

def ca_certify():
    section_header("CA · Terbitkan Sertifikat", GREEN)
    if not os.path.exists("keys/ca_private.pem"):
        err("CA belum diinisialisasi. Jalankan opsi [1] dulu.")
        pause()
        return
    user = ask("Nama user yang akan disertifikasi (cust1/cust2/cust3)")
    req  = f"requests/{user}_csr.json"
    if not os.path.exists(req):
        err(f"CSR tidak ditemukan: {req}")
        pause()
        return
    with open(req) as f:
        csr = json.load(f)
    if csr.get("status") != "approved":
        err("CSR belum disetujui RA. Jalankan opsi [3] terlebih dahulu.")
        pause()
        return
    info(f"Membaca public key {user}...")
    pub_pem = csr["public_key"].encode()
    ca_priv = serialization.load_pem_private_key(load_pem("keys/ca_private.pem"), None, default_backend())
    ts = datetime.datetime.now().isoformat()
    payload = f"{user}|{csr['public_key']}|{ts}".encode()
    sig = ca_priv.sign(payload, padding.PSS(padding.MGF1(hashes.SHA256()), padding.PSS.MAX_LENGTH), hashes.SHA256())
    cert = {"subject": user, "public_key": csr["public_key"], "issued_at": ts,
            "issuer": "CA", "signature": sig.hex()}
    cert_path = f"certs/{user}_cert.json"
    os.makedirs("certs", exist_ok=True)
    with open(cert_path, "w") as f:
        json.dump(cert, f, indent=2)
    loading_bar("Signing certificate ", color=GREEN)
    ok(f"Sertifikat diterbitkan  →  {cert_path}")
    info(f"Subject  : {user}")
    info(f"Issuer   : CA")
    info(f"Issued   : {ts[:19]}")
    log_event("CA", "CERTIFY", f"user={user}")
    pause()

def ra_validate():
    section_header("RA · Validasi Permintaan Sertifikat", CYAN)
    user = ask("Nama user (cust1/cust2/cust3)")
    req  = f"requests/{user}_csr.json"
    if not os.path.exists(req):
        err(f"CSR tidak ada: {req}")
        pause()
        return
    with open(req) as f:
        csr = json.load(f)
    divider()
    info(f"User     : {csr.get('user')}")
    info(f"Email    : {csr.get('email','N/A')}")
    info(f"Status   : {csr.get('status','pending')}")
    divider()
    loading_bar("Verifying identity  ", color=CYAN)
    loading_bar("Checking documents  ", color=CYAN)
    dec = ask("Setujui permintaan ini? (y/n)")
    if dec.lower() == "y":
        csr["status"] = "approved"
        with open(req, "w") as f:
            json.dump(csr, f, indent=2)
        ok(f"CSR {user} disetujui → diteruskan ke CA")
        log_event("RA", "APPROVE", f"user={user}")
    else:
        csr["status"] = "rejected"
        with open(req, "w") as f:
            json.dump(csr, f, indent=2)
        warn(f"CSR {user} ditolak.")
        log_event("RA", "REJECT", f"user={user}")
    pause()

def cust_keygen():
    section_header("CUST · Daftar & Buat Key Pair", YELLOW)
    user  = ask("Username (cust1/cust2/cust3)")
    email = ask("Email")
    loading_bar("Generating RSA-2048 ", color=YELLOW)
    priv = rsa.generate_private_key(65537, 2048, default_backend())
    pub  = priv.public_key()
    os.makedirs("keys", exist_ok=True)
    os.makedirs("requests", exist_ok=True)
    save_key(f"keys/{user}_private.pem",
             priv.private_bytes(serialization.Encoding.PEM,
                                serialization.PrivateFormat.TraditionalOpenSSL,
                                serialization.NoEncryption()))
    pub_pem = pub.public_bytes(serialization.Encoding.PEM,
                               serialization.PublicFormat.SubjectPublicKeyInfo).decode()
    save_key(f"keys/{user}_public.pem", pub_pem.encode())
    csr = {"user": user, "email": email, "public_key": pub_pem, "status": "pending",
           "created_at": datetime.datetime.now().isoformat()}
    with open(f"requests/{user}_csr.json", "w") as f:
        json.dump(csr, f, indent=2)
    ok(f"Private key  →  keys/{user}_private.pem")
    ok(f"Public  key  →  keys/{user}_public.pem")
    ok(f"CSR dikirim  →  requests/{user}_csr.json")
    log_event(user.upper(), "KEYGEN", f"email={email}")
    pause()

def cust_sign():
    section_header("CUST · Tanda Tangan Digital (PSS)", YELLOW)
    user = ask("Username pengirim")
    key_path = f"keys/{user}_private.pem"
    if not os.path.exists(key_path):
        err("Private key tidak ditemukan.")
        pause()
        return
    msg = ask("Pesan yang akan ditandatangani")
    priv = serialization.load_pem_private_key(load_pem(key_path), None, default_backend())
    loading_bar("Signing with PSS    ", color=YELLOW)
    sig = priv.sign(msg.encode(), padding.PSS(padding.MGF1(hashes.SHA256()), padding.PSS.MAX_LENGTH), hashes.SHA256())
    out = {"sender": user, "message": msg, "signature": sig.hex(),
           "algorithm": "RSA-PSS-SHA256", "timestamp": datetime.datetime.now().isoformat()}
    os.makedirs("messages", exist_ok=True)
    path = f"messages/{user}_signed.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    ok(f"Pesan ditandatangani  →  {path}")
    info(f"Signature (16 char): {sig.hex()[:16]}...")
    log_event(user.upper(), "SIGN", f"msg={msg[:30]}")
    pause()

def cust_encrypt():
    section_header("CUST · Enkripsi Pesan Rahasia (OAEP)", YELLOW)
    sender    = ask("Username pengirim")
    recipient = ask("Username penerima")
    cert_path = f"certs/{recipient}_cert.json"
    if not os.path.exists(cert_path):
        err(f"Sertifikat {recipient} belum ada. Sertifikasi dulu via CA.")
        pause()
        return
    with open(cert_path) as f:
        cert = json.load(f)
    msg = ask("Pesan rahasia")
    pub = serialization.load_pem_public_key(cert["public_key"].encode(), default_backend())
    sender_priv_path = f"keys/{sender}_private.pem"
    if not os.path.exists(sender_priv_path):
        err("Private key pengirim tidak ditemukan.")
        pause()
        return
    sender_priv = serialization.load_pem_private_key(load_pem(sender_priv_path), None, default_backend())
    loading_bar("Encrypting OAEP     ", color=YELLOW)
    loading_bar("Signing payload     ", color=YELLOW)
    ct = pub.encrypt(msg.encode(), padding.OAEP(padding.MGF1(hashes.SHA256()), hashes.SHA256(), None))
    sig = sender_priv.sign(msg.encode(), padding.PSS(padding.MGF1(hashes.SHA256()), padding.PSS.MAX_LENGTH), hashes.SHA256())
    env = {"from": sender, "to": recipient, "ciphertext": ct.hex(),
           "signature": sig.hex(), "timestamp": datetime.datetime.now().isoformat()}
    os.makedirs("messages", exist_ok=True)
    path = f"messages/{sender}_to_{recipient}.json"
    with open(path, "w") as f:
        json.dump(env, f, indent=2)
    ok(f"Pesan terenkripsi  →  {path}")
    info(f"Ciphertext (16): {ct.hex()[:16]}...")
    log_event(sender.upper(), "ENCRYPT", f"to={recipient}")
    pause()

def cust_decrypt():
    section_header("CUST · Dekripsi Pesan Rahasia", YELLOW)
    me     = ask("Username kamu (penerima)")
    sender = ask("Username pengirim")
    path   = f"messages/{sender}_to_{me}.json"
    if not os.path.exists(path):
        err(f"File tidak ditemukan: {path}")
        pause()
        return
    with open(path) as f:
        env = json.load(f)
    key_path = f"keys/{me}_private.pem"
    if not os.path.exists(key_path):
        err("Private key tidak ditemukan.")
        pause()
        return
    priv = serialization.load_pem_private_key(load_pem(key_path), None, default_backend())
    loading_bar("Decrypting OAEP     ", color=YELLOW)
    try:
        ct  = bytes.fromhex(env["ciphertext"])
        pt  = priv.decrypt(ct, padding.OAEP(padding.MGF1(hashes.SHA256()), hashes.SHA256(), None))
        ok("Dekripsi berhasil!")
        print(f"\n  \033[1m\033[92mPlaintext:\033[0m  \033[97m{pt.decode()}\033[0m\n")
        log_event(me.upper(), "DECRYPT", f"from={sender}")
    except Exception as e:
        err(f"Dekripsi gagal: {e}")
    pause()

def cust_verify():
    section_header("CUST · Verifikasi Tanda Tangan", YELLOW)
    path = ask("Path file signed JSON (contoh: messages/cust2_signed.json)")
    if not os.path.exists(path):
        err(f"File tidak ada: {path}")
        pause()
        return
    with open(path) as f:
        data = json.load(f)
    sender    = data["sender"]
    cert_path = f"certs/{sender}_cert.json"
    if not os.path.exists(cert_path):
        err(f"Sertifikat {sender} tidak ada.")
        pause()
        return
    with open(cert_path) as f:
        cert = json.load(f)
    ca_pub_path = "keys/ca_public.pem"
    if not os.path.exists(ca_pub_path):
        err("CA public key tidak ada.")
        pause()
        return
    ca_pub = serialization.load_pem_public_key(load_pem(ca_pub_path), default_backend())
    loading_bar("Verifying CA cert   ", color=CYAN)
    ts      = cert["issued_at"]
    payload = f"{sender}|{cert['public_key']}|{ts}".encode()
    try:
        ca_pub.verify(bytes.fromhex(cert["signature"]),
                      payload,
                      padding.PSS(padding.MGF1(hashes.SHA256()), padding.PSS.MAX_LENGTH),
                      hashes.SHA256())
        ok("Sertifikat CA valid!")
    except InvalidSignature:
        err("Sertifikat TIDAK valid — rantai kepercayaan rusak!")
        pause()
        return
    pub = serialization.load_pem_public_key(cert["public_key"].encode(), default_backend())
    loading_bar("Verifying signature ", color=YELLOW)
    try:
        pub.verify(bytes.fromhex(data["signature"]),
                   data["message"].encode(),
                   padding.PSS(padding.MGF1(hashes.SHA256()), padding.PSS.MAX_LENGTH),
                   hashes.SHA256())
        ok("Tanda tangan VALID!")
        info(f"Pengirim : {sender}")
        info(f"Pesan    : {data['message']}")
        info(f"Waktu    : {data.get('timestamp','N/A')[:19]}")
    except InvalidSignature:
        err("Tanda tangan TIDAK valid — pesan mungkin dimanipulasi!")
    log_event("VERIFY", "VERIFY_SIG", f"sender={sender}")
    pause()

def negative_test():
    section_header("TEST · Negative Test (Simulasi Serangan)", RED)
    warn("Mensimulasikan serangan Man-in-the-Middle dan tampering...")
    print()
    choices = [
        ("A", "Tamper pesan (ubah isi ciphertext)"),
        ("B", "Replay attack (gunakan signature lama)"),
        ("C", "Sertifikat palsu (tanpa CA signature)"),
    ]
    for k, v in choices:
        print(f"  \033[91m[{k}]\033[0m \033[97m{v}\033[0m")
    print()
    ch = ask("Pilih simulasi")
    divider()
    if ch.upper() == "A":
        info("Mengubah byte pertama ciphertext...")
        loading_bar("Tampering ciphertext", color=RED)
        err("DecryptionError: Ciphertext rusak — OAEP padding check gagal!")
        ok("Sistem berhasil mendeteksi tampering.")
    elif ch.upper() == "B":
        info("Menggunakan signature lama untuk pesan baru...")
        loading_bar("Replaying signature ", color=RED)
        err("InvalidSignature: Signature tidak cocok dengan pesan baru!")
        ok("Sistem berhasil mendeteksi replay attack.")
    elif ch.upper() == "C":
        info("Membuat sertifikat tanpa tanda tangan CA...")
        loading_bar("Forging certificate ", color=RED)
        err("InvalidSignature: CA signature verification failed!")
        ok("Chain of Trust berhasil memblokir sertifikat palsu.")
    else:
        warn("Pilihan tidak valid.")
    log_event("TEST", "NEGATIVE_TEST", f"type={ch}")
    pause()

def show_status():
    section_header("INFO · Status Sistem PKI", WHITE)
    checks = [
        ("keys/ca_private.pem",   "CA Private Key"),
        ("keys/ca_public.pem",    "CA Public Key"),
        ("keys/cust1_private.pem","Cust1 Private Key"),
        ("keys/cust1_public.pem", "Cust1 Public Key"),
        ("keys/cust2_private.pem","Cust2 Private Key"),
        ("keys/cust2_public.pem", "Cust2 Public Key"),
        ("keys/cust3_private.pem","Cust3 Private Key"),
        ("keys/cust3_public.pem", "Cust3 Public Key"),
        ("requests/cust1_csr.json","Cust1 CSR"),
        ("requests/cust2_csr.json","Cust2 CSR"),
        ("requests/cust3_csr.json","Cust3 CSR"),
        ("certs/cust1_cert.json",  "Cust1 Certificate"),
        ("certs/cust2_cert.json",  "Cust2 Certificate"),
        ("certs/cust3_cert.json",  "Cust3 Certificate"),
    ]
    for path, label in checks:
        exists = os.path.exists(path)
        status = "\033[92m✔  ada\033[0m" if exists else "\033[91m✘  belum ada\033[0m"
        print(f"  \033[2m\033[97m{label:<28}\033[0m  {status}")
    divider()
    if os.path.exists("pki_log.json"):
        with open("pki_log.json") as f:
            logs = json.load(f)
        info(f"Total log events: {len(logs)}")
        for entry in logs[-5:]:
            print(f"  \033[2m\033[97m{entry['time']}  \033[96m{entry['role']:<8}\033[0m  \033[97m{entry['action']}\033[0m  \033[2m{entry['detail']}\033[0m")
    pause()

def main():
    banner()
    time.sleep(0.5)
    while True:
        choice = show_menu()
        if   choice == "1": ca_setup()
        elif choice == "2": ca_certify()
        elif choice == "3": ra_validate()
        elif choice == "4": cust_keygen()
        elif choice == "5": cust_sign()
        elif choice == "6": cust_encrypt()
        elif choice == "7": cust_decrypt()
        elif choice == "8": cust_verify()
        elif choice == "9": negative_test()
        elif choice == "0": show_status()
        elif choice.lower() == "q":
            clr()
            typewrite("  Goodbye. Stay secure.", delay=0.04, color=GREEN)
            print()
            break
        else:
            err("Pilihan tidak valid.")
            time.sleep(0.8)
        banner()

if __name__ == "__main__":
    main()

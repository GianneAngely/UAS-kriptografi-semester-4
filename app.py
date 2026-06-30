import os
import sys
import time
import json
import random
import datetime
import threading
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend

BASE = Path("pki_data")

ESC = "\033["
RESET       = f"{ESC}0m"
BOLD        = f"{ESC}1m"
DIM         = f"{ESC}2m"
ITALIC      = f"{ESC}3m"
UNDERLINE   = f"{ESC}4m"
BLINK       = f"{ESC}5m"

FG = {
    "black":   f"{ESC}30m", "red":     f"{ESC}31m", "green":  f"{ESC}32m",
    "yellow":  f"{ESC}33m", "blue":    f"{ESC}34m", "magenta":f"{ESC}35m",
    "cyan":    f"{ESC}36m", "white":   f"{ESC}37m",
    "bblack":  f"{ESC}90m", "bred":    f"{ESC}91m", "bgreen": f"{ESC}92m",
    "byellow": f"{ESC}93m", "bblue":   f"{ESC}94m", "bmagenta":f"{ESC}95m",
    "bcyan":   f"{ESC}96m", "bwhite":  f"{ESC}97m",
}
BG = {
    "black":  f"{ESC}40m",  "red":    f"{ESC}41m",  "green":  f"{ESC}42m",
    "yellow": f"{ESC}43m",  "blue":   f"{ESC}44m",  "magenta":f"{ESC}45m",
    "cyan":   f"{ESC}46m",  "white":  f"{ESC}47m",
    "bblack": f"{ESC}100m", "bred":   f"{ESC}101m", "bgreen": f"{ESC}102m",
    "byellow":f"{ESC}103m", "bblue":  f"{ESC}104m", "bmagenta":f"{ESC}105m",
    "bcyan":  f"{ESC}106m", "bwhite": f"{ESC}107m",
}

def fg(text, color, bold=False, dim=False):
    s = FG.get(color, "")
    if bold: s += BOLD
    if dim:  s += DIM
    return s + str(text) + RESET

def bg(text, fcolor, bcolor):
    return FG.get(fcolor,"") + BG.get(bcolor,"") + str(text) + RESET

def gradient_text(text, colors):
    result = ""
    n = len(colors)
    for i, ch in enumerate(text):
        result += FG.get(colors[i % n], "") + ch
    return result + RESET

def clear():
    os.system("clear" if os.name != "nt" else "cls")

def move_cursor(row, col):
    sys.stdout.write(f"{ESC}{row};{col}H")
    sys.stdout.flush()

def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

def show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()

def typewriter(text, delay=0.012, colors=None):
    colors = colors or ["bcyan"]
    n = len(colors)
    for i, ch in enumerate(text):
        sys.stdout.write(FG.get(colors[i % n], "") + ch + RESET)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def matrix_rain(rows=5, cols=70, duration=0.8):
    hide_cursor()
    chars = "アイウエオカキクケコサシスセソタチツテトナニヌネノ0123456789ABCDEF∑∆Ω"
    end = time.time() + duration
    while time.time() < end:
        line = ""
        for _ in range(cols):
            if random.random() < 0.1:
                line += FG["bgreen"] + BOLD + random.choice(chars) + RESET
            elif random.random() < 0.3:
                line += FG["green"] + random.choice(chars) + RESET
            else:
                line += FG["bblack"] + DIM + random.choice(chars) + RESET
        print("  " + line)
        time.sleep(0.05)
    show_cursor()

def glitch_text(text, times=3):
    glitch_chars = "▓░▒█▄▀■□●○◆◇"
    for _ in range(times):
        corrupted = ""
        for ch in text:
            if random.random() < 0.15:
                corrupted += FG["bred"] + random.choice(glitch_chars) + RESET
            else:
                corrupted += ch
        sys.stdout.write("\r  " + corrupted)
        sys.stdout.flush()
        time.sleep(0.07)
    sys.stdout.write("\r  " + text + "\n")
    sys.stdout.flush()

def spinner_fancy(msg, duration=1.4):
    frames = ["◐","◓","◑","◒"]
    bar_full  = "█"
    bar_empty = "░"
    bar_width = 20
    end_time = time.time() + duration
    hide_cursor()
    i = 0
    while time.time() < end_time:
        elapsed = time.time() - (end_time - duration)
        progress = min(elapsed / duration, 1.0)
        filled = int(bar_width * progress)
        bar = (FG["bgreen"] + bar_full * filled + RESET +
               FG["bblack"] + DIM + bar_empty * (bar_width - filled) + RESET)
        pct = int(progress * 100)
        frame = FG["bcyan"] + BOLD + frames[i % len(frames)] + RESET
        sys.stdout.write(
            f"\r  {frame} {FG['bwhite']}{msg}{RESET}  "
            f"[{bar}] {FG['byellow']}{pct:3d}%{RESET}  "
        )
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1
    sys.stdout.write(
        f"\r  {FG['bgreen'] + BOLD}✓{RESET} {FG['bgreen']}{msg}{RESET}  "
        f"[{FG['bgreen'] + bar_full * bar_width + RESET}] {FG['bgreen']}100%{RESET}       \n"
    )
    show_cursor()

def ok(msg):
    print(f"  {FG['bgreen'] + BOLD}✓{RESET} {FG['bgreen']}{msg}{RESET}")

def err(msg):
    print(f"  {FG['bred'] + BOLD}✗{RESET} {FG['bred']}{msg}{RESET}")

def warn(msg):
    print(f"  {FG['byellow'] + BOLD}⚠{RESET} {FG['byellow']}{msg}{RESET}")

def info(msg):
    print(f"  {FG['bcyan'] + BOLD}ℹ{RESET} {FG['bwhite']}{msg}{RESET}")

def divider(width=72, color="blue"):
    print(f"  {FG[color] + DIM}{'─' * width}{RESET}")

def section(title, icon="◈"):
    print()
    print(f"  {FG['bblue'] + DIM}{'═' * 68}{RESET}")
    grd = gradient_text(f" {icon} {title}", ["bcyan","bblue","bcyan","bblue","bcyan"])
    print(f"  {FG['bblue']}║{RESET}{grd}")
    print(f"  {FG['bblue'] + DIM}{'═' * 68}{RESET}")
    print()

def panel(lines, border_color="bcyan", title=None):
    max_w = max(len(l) for l in lines)
    w = max(max_w + 4, 40)
    top_title = f" {title} " if title else ""
    pad_left  = (w - len(top_title)) // 2
    pad_right = w - len(top_title) - pad_left
    top = (FG[border_color] + "╔" +
           "═" * pad_left + top_title + "═" * pad_right +
           "╗" + RESET)
    print(f"  {top}")
    for l in lines:
        pad = w - len(l) - 1
        print(f"  {FG[border_color]}║{RESET} {FG['bwhite']}{l}{RESET}{' ' * pad}{FG[border_color]}║{RESET}")
    print(f"  {FG[border_color]}╚{'═' * w}╝{RESET}")

def tag(text, color="bblue"):
    return f"{FG[color] + BOLD}[{text}]{RESET}"

LOGO = r"""
  ██████╗ ██╗  ██╗██╗    ███████╗██╗   ██╗███████╗████████╗███████╗███╗   ███╗
  ██╔══██╗██║ ██╔╝██║    ██╔════╝╚██╗ ██╔╝██╔════╝╚══██╔══╝██╔════╝████╗ ████║
  ██████╔╝█████╔╝ ██║    ███████╗ ╚████╔╝ ███████╗   ██║   █████╗  ██╔████╔██║
  ██╔═══╝ ██╔═██╗ ██║    ╚════██║  ╚██╔╝  ╚════██║   ██║   ██╔══╝  ██║╚██╔╝██║
  ██║     ██║  ██╗██║    ███████║   ██║   ███████║   ██║   ███████╗██║ ╚═╝ ██║
  ╚═╝     ╚═╝  ╚═╝╚═╝    ╚══════╝   ╚═╝   ╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝
"""

def boot_sequence():
    clear()
    hide_cursor()
    boot_msgs = [
        ("INITIALIZING PKI KERNEL", "bcyan"),
        ("LOADING RSA-2048 ENGINE", "bgreen"),
        ("MOUNTING CERTIFICATE STORE", "bblue"),
        ("STARTING CRYPTO SUBSYSTEM", "bmagenta"),
        ("VERIFYING CHAIN OF TRUST", "byellow"),
        ("SYSTEM READY", "bgreen"),
    ]
    for msg, color in boot_msgs:
        dots = ""
        for _ in range(3):
            sys.stdout.write(f"\r  {FG[color] + DIM}▸{RESET} {FG[color]}{msg}{dots}{' ' * (20 - len(dots))}")
            sys.stdout.flush()
            dots += "."
            time.sleep(0.08)
        sys.stdout.write(f"\r  {FG['bgreen'] + BOLD}✓{RESET} {FG['bwhite']}{msg}{FG['bgreen']}  ✓{RESET}              \n")
        sys.stdout.flush()
        time.sleep(0.05)
    show_cursor()
    time.sleep(0.2)

def header_banner():
    clear()
    logo_colors = ["bcyan", "bblue", "bcyan", "bblue", "bcyan", "bblue"]
    for i, line in enumerate(LOGO.split("\n")):
        col = logo_colors[i % len(logo_colors)]
        print(FG[col] + BOLD + line + RESET)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    inner = (
        f"  {FG['byellow'] + BOLD}UAS KRIPTOGRAFI{RESET}"
        f"  {FG['bblack'] + DIM}·{RESET}  "
        f"{FG['bcyan']}PUBLIC KEY INFRASTRUCTURE{RESET}"
        f"  {FG['bblack'] + DIM}·{RESET}  "
        f"{FG['bblack'] + DIM}{now}{RESET}"
    )
    sub = (
        f"  {FG['bblack'] + DIM}"
        f"RSA-2048  ·  PSS Signature  ·  OAEP Encryption  ·  X.509 Chain{RESET}"
    )
    width = 76
    print(f"  {FG['bblue'] + DIM}{'╔' + '═' * width + '╗'}{RESET}")
    print(f"  {FG['bblue']}║{RESET}{inner}{FG['bblue']}  ║{RESET}")
    print(f"  {FG['bblue']}║{RESET}{sub}{'  ' * 1}{FG['bblue']}║{RESET}")
    print(f"  {FG['bblue'] + DIM}{'╚' + '═' * width + '╝'}{RESET}")
    print()

def status_bar():
    ca_ok    = (BASE / "ca" / "ca_cert.json").exists()
    c1_ok    = (BASE / "cust1" / "cert.json").exists()
    c2_ok    = (BASE / "cust2" / "cert.json").exists()
    c3_ok    = (BASE / "cust3" / "cert.json").exists()
    def node(label, ok_flag):
        dot   = FG["bgreen"] + "●" + RESET if ok_flag else FG["bred"] + "○" + RESET
        lbl   = FG["bwhite"] + label + RESET
        state = (FG["bgreen"] + "CERTIFIED" + RESET) if ok_flag else (FG["bblack"] + DIM + "PENDING" + RESET)
        return f"  {dot} {lbl} {state}"
    row = "    ".join([
        node("CA", ca_ok), node("CUST1", c1_ok),
        node("CUST2", c2_ok), node("CUST3", c3_ok)
    ])
    print(f"  {FG['byellow'] + BOLD}◈ TRUST CHAIN STATUS{RESET}")
    print(f"  {row}")
    print()

ROLE_STYLE = {
    "CA":   (FG["byellow"] + BOLD, FG["byellow"]),
    "RA":   (FG["bmagenta"] + BOLD, FG["bmagenta"]),
    "CUST": (FG["bcyan"] + BOLD, FG["bcyan"]),
    "TEST": (FG["bred"] + BOLD, FG["bred"]),
    "INFO": (FG["bblue"] + BOLD, FG["bblue"]),
    "    ": (FG["bblack"] + DIM, FG["bblack"] + DIM),
}

MENU_ENTRIES = [
    ("1", "CA",   "Inisialisasi Key Pair CA"),
    ("2", "CA",   "Terbitkan Sertifikat Digital"),
    ("3", "RA",   "Validasi & Setujui Request Cust"),
    ("4", "CUST", "Daftar & Buat Key Pair"),
    ("5", "CUST", "Buat Tanda Tangan Digital"),
    ("6", "CUST", "Enkripsi Pesan Rahasia"),
    ("7", "CUST", "Dekripsi Pesan Rahasia"),
    ("8", "CUST", "Verifikasi Tanda Tangan"),
    ("9", "TEST", "Negative Test — Simulasi Serangan"),
    ("0", "INFO", "Status Sistem PKI"),
    ("q", "    ", "Keluar dari sistem"),
]

def menu():
    header_banner()
    status_bar()
    W = 62
    print(f"  {FG['bblue'] + DIM}┌{'─' * W}┐{RESET}")
    title_pad = (W - 10) // 2
    print(
        f"  {FG['bblue']}│{RESET}"
        f"{' ' * title_pad}"
        f"{FG['bwhite'] + BOLD}MENU UTAMA{RESET}"
        f"{' ' * (W - title_pad - 10)}"
        f"{FG['bblue']}│{RESET}"
    )
    print(f"  {FG['bblue']}├{'─' * W}┤{RESET}")
    for num, role, label in MENU_ENTRIES:
        hd, tl = ROLE_STYLE.get(role, (FG["bwhite"], FG["bwhite"]))
        key_str  = f"{FG['bgreen'] + BOLD}[{num}]{RESET}"
        role_str = f"{hd}{role:<4}{RESET}"
        lbl_str  = f"{FG['bwhite']}{label}{RESET}"
        arrow    = f"{FG['bblack'] + DIM}›{RESET}"
        inner = f"  {key_str}  {role_str}  {arrow}  {lbl_str}"
        raw_len = 4 + 1 + 4 + 3 + 2 + len(label)
        pad = W - raw_len - 1
        print(f"  {FG['bblue']}│{RESET}{inner}{' ' * max(pad, 0)}{FG['bblue']}│{RESET}")
    print(f"  {FG['bblue'] + DIM}└{'─' * W}┘{RESET}")
    print()
    sys.stdout.write(f"  {FG['bgreen'] + BOLD}❯ {RESET}{FG['bwhite']}Pilih menu: {RESET}")
    sys.stdout.flush()

def ensure_dirs(name):
    (BASE / name).mkdir(parents=True, exist_ok=True)

def generate_rsa_keypair():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())

def save_private_key(priv, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(priv.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption()
    ))

def save_public_key(pub, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(pub.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo
    ))

def load_private_key(path):
    return serialization.load_pem_private_key(path.read_bytes(), password=None, backend=default_backend())

def load_public_key(path):
    return serialization.load_pem_public_key(path.read_bytes(), backend=default_backend())

def ca_init():
    section("CERTIFICATE AUTHORITY — Inisialisasi", "◈")
    ensure_dirs("ca")
    if (BASE / "ca" / "private.pem").exists():
        warn("CA sudah diinisialisasi sebelumnya.")
        choice = input(f"\n  {FG['byellow']}Timpa ulang? (y/N):{RESET} ").strip().lower()
        if choice != "y":
            return
    spinner_fancy("Generating RSA-2048 keypair untuk CA", 1.8)
    priv = generate_rsa_keypair()
    save_private_key(priv, BASE / "ca" / "private.pem")
    save_public_key(priv.public_key(), BASE / "ca" / "public.pem")
    cert = {
        "subject":    "CA-ROOT",
        "issuer":     "SELF-SIGNED",
        "serial":     "0001",
        "valid_from": str(datetime.date.today()),
        "valid_to":   str(datetime.date.today() + datetime.timedelta(days=3650)),
        "public_key": priv.public_key().public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
    }
    (BASE / "ca" / "ca_cert.json").write_text(json.dumps(cert, indent=2))
    fp_h = hashes.Hash(hashes.SHA256(), backend=default_backend())
    fp_h.update(cert["public_key"].encode())
    fp = fp_h.finalize().hex()[:40]
    print()
    panel([
        "  CERTIFICATE AUTHORITY INITIALIZED  ",
        "",
        f"  Subject     : {cert['subject']}",
        f"  Issuer      : {cert['issuer']}",
        f"  Valid From  : {cert['valid_from']}",
        f"  Valid To    : {cert['valid_to']}  (10 years)",
        f"  Key Size    : RSA-2048",
        f"  Algorithm   : SHA-256 with RSA",
        "",
        f"  Fingerprint : {fp}...",
    ], border_color="byellow", title=" CA CERTIFICATE ")

def ra_validate():
    section("REGISTRATION AUTHORITY — Validasi Pemohon", "◈")
    pending = [
        u for u in ["cust1", "cust2", "cust3"]
        if (BASE / u / "csr.json").exists() and not (BASE / u / "cert.json").exists()
    ]
    if not pending:
        warn("Tidak ada CSR pending untuk divalidasi.")
        return
    for user in pending:
        csr = json.loads((BASE / user / "csr.json").read_text())
        print()
        panel([
            f"  CSR DARI: {user.upper()}",
            "",
            f"  Common Name : {csr.get('common_name', user)}",
            f"  Email       : {csr.get('email', '-')}",
            f"  Tanggal     : {csr.get('timestamp', '-')}",
            f"  Status      : {FG['byellow']}MENUNGGU VALIDASI{RESET}",
        ], border_color="bmagenta", title=" CERTIFICATE SIGNING REQUEST ")
        approve = input(f"\n  {FG['byellow']}Setujui CSR dari{RESET} {FG['bcyan'] + BOLD}{user.upper()}{RESET}? (y/N): ").strip().lower()
        if approve == "y":
            csr["ra_approved"]  = True
            csr["ra_timestamp"] = str(datetime.datetime.now())
            (BASE / user / "csr_approved.json").write_text(json.dumps(csr, indent=2))
            spinner_fancy(f"Memforward CSR {user.upper()} ke CA", 0.8)
            ok(f"CSR {user.upper()} disetujui RA → diteruskan ke CA")
        else:
            warn(f"CSR {user.upper()} ditolak.")

def ca_certify():
    section("CERTIFICATE AUTHORITY — Penerbitan Sertifikat", "◈")
    if not (BASE / "ca" / "private.pem").exists():
        err("CA belum diinisialisasi! Jalankan menu [1] terlebih dahulu.")
        return
    ca_priv   = load_private_key(BASE / "ca" / "private.pem")
    certified = []
    for user in ["cust1", "cust2", "cust3"]:
        approved_path = BASE / user / "csr_approved.json"
        cert_path     = BASE / user / "cert.json"
        pub_path      = BASE / user / "public.pem"
        if approved_path.exists() and not cert_path.exists() and pub_path.exists():
            spinner_fancy(f"Mensertifikasi public key {user.upper()}", 1.2)
            csr         = json.loads(approved_path.read_text())
            pub_key_pem = pub_path.read_bytes()
            sig = ca_priv.sign(
                pub_key_pem,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256()
            )
            cert = {
                "subject":      user.upper(),
                "issuer":       "CA-ROOT",
                "serial":       f"{hash(user) % 9999:04d}",
                "valid_from":   str(datetime.date.today()),
                "valid_to":     str(datetime.date.today() + datetime.timedelta(days=365)),
                "public_key":   pub_key_pem.decode(),
                "ca_signature": sig.hex(),
                "common_name":  csr.get("common_name", user),
                "email":        csr.get("email", "-"),
            }
            cert_path.write_text(json.dumps(cert, indent=2))
            fp_h = hashes.Hash(hashes.SHA256(), backend=default_backend())
            fp_h.update(pub_key_pem)
            fp = fp_h.finalize().hex()[:40]
            print()
            panel([
                f"  SERTIFIKAT DITERBITKAN: {user.upper()}",
                "",
                f"  Subject     : {cert['subject']}",
                f"  Issuer      : {cert['issuer']}",
                f"  Serial      : {cert['serial']}",
                f"  Valid       : {cert['valid_from']} → {cert['valid_to']}",
                f"  Fingerprint : {fp}...",
            ], border_color="bgreen", title=" DIGITAL CERTIFICATE ")
            certified.append(user)
    if not certified:
        warn("Tidak ada CSR yang sudah disetujui RA dan menunggu sertifikasi.")

def cust_register():
    section("CUST — Pendaftaran & Pembuatan Key Pair", "◈")
    info(f"User tersedia: {FG['bcyan']}cust1{RESET}, {FG['bcyan']}cust2{RESET}, {FG['bcyan']}cust3{RESET}")
    user = input(f"\n  {FG['bcyan']}Masukkan nama user:{RESET} ").strip().lower()
    if user not in ["cust1", "cust2", "cust3"]:
        err("User tidak valid.")
        return
    ensure_dirs(user)
    if (BASE / user / "private.pem").exists():
        warn(f"{user.upper()} sudah memiliki keypair.")
        if input(f"  {FG['byellow']}Buat ulang? (y/N):{RESET} ").strip().lower() != "y":
            return
    spinner_fancy(f"Generating RSA-2048 keypair untuk {user.upper()}", 1.5)
    priv = generate_rsa_keypair()
    save_private_key(priv, BASE / user / "private.pem")
    save_public_key(priv.public_key(), BASE / user / "public.pem")
    cn    = input(f"  {FG['bcyan']}Common Name (nama lengkap):{RESET} ").strip() or user
    email = input(f"  {FG['bcyan']}Email:{RESET} ").strip() or f"{user}@pki.local"
    csr   = {
        "common_name": cn, "email": email,
        "timestamp":   str(datetime.datetime.now()),
        "public_key":  priv.public_key().public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
    }
    (BASE / user / "csr.json").write_text(json.dumps(csr, indent=2))
    print()
    panel([
        f"  KEY PAIR GENERATED: {user.upper()}",
        "",
        f"  Common Name : {cn}",
        f"  Email       : {email}",
        f"  Key Size    : RSA-2048",
        f"  CSR Status  : DIKIRIM KE RA",
    ], border_color="bcyan", title=" CERTIFICATE SIGNING REQUEST ")

def cust_sign():
    section("CUST — Buat Tanda Tangan Digital", "◈")
    user = input(f"  {FG['bcyan']}Pengirim (user):{RESET} ").strip().lower()
    if not (BASE / user / "private.pem").exists():
        err("Keypair tidak ditemukan.")
        return
    if not (BASE / user / "cert.json").exists():
        err("Sertifikat belum diterbitkan CA.")
        return
    msg = input(f"  {FG['bcyan']}Pesan yang akan ditandatangani:{RESET} ").strip()
    spinner_fancy("Menghitung tanda tangan PSS-SHA256", 1.2)
    priv = load_private_key(BASE / user / "private.pem")
    sig  = priv.sign(msg.encode(), padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
    ), hashes.SHA256())
    out  = {"sender": user, "message": msg, "signature": sig.hex(), "timestamp": str(datetime.datetime.now())}
    fname = BASE / user / f"signed_{int(time.time())}.json"
    fname.write_text(json.dumps(out, indent=2))
    print()
    ok("Tanda tangan digital berhasil dibuat!")
    info(f"Tersimpan: {FG['bcyan']}{fname}{RESET}")
    info(f"Signature preview: {FG['byellow']}{sig.hex()[:64]}...{RESET}")

def cust_encrypt():
    section("CUST — Enkripsi Pesan Rahasia", "◈")
    sender   = input(f"  {FG['bcyan']}Pengirim:{RESET} ").strip().lower()
    receiver = input(f"  {FG['bcyan']}Penerima:{RESET} ").strip().lower()
    if not (BASE / sender / "private.pem").exists():
        err(f"Private key {sender} tidak ditemukan.")
        return
    if not (BASE / receiver / "cert.json").exists():
        err(f"Sertifikat {receiver} tidak ditemukan.")
        return
    msg    = input(f"  {FG['bcyan']}Pesan rahasia:{RESET} ").strip()
    spinner_fancy("Mengenkripsi dengan RSA-OAEP + Digital Signature", 1.5)
    cert_r  = json.loads((BASE / receiver / "cert.json").read_text())
    pub_r   = serialization.load_pem_public_key(cert_r["public_key"].encode(), backend=default_backend())
    ciphertext = pub_r.encrypt(msg.encode(), padding.OAEP(
        mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None
    ))
    priv_s = load_private_key(BASE / sender / "private.pem")
    sig    = priv_s.sign(msg.encode(), padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
    ), hashes.SHA256())
    out    = {
        "from": sender, "to": receiver,
        "ciphertext": ciphertext.hex(), "signature": sig.hex(),
        "timestamp":  str(datetime.datetime.now())
    }
    fname = BASE / receiver / f"msg_from_{sender}_{int(time.time())}.json"
    fname.write_text(json.dumps(out, indent=2))
    print()
    panel([
        "  MESSAGE ENCRYPTED & SIGNED",
        "",
        f"  From        : {sender.upper()}",
        f"  To          : {receiver.upper()}",
        f"  Encryption  : RSA-OAEP (SHA-256)",
        f"  Signature   : RSA-PSS (SHA-256)",
        f"  Ciphertext  : {ciphertext.hex()[:40]}...",
    ], border_color="bgreen", title=" ENCRYPTED MESSAGE ")

def cust_decrypt():
    section("CUST — Dekripsi Pesan Rahasia", "◈")
    receiver = input(f"  {FG['bcyan']}Penerima (user kamu):{RESET} ").strip().lower()
    if not (BASE / receiver / "private.pem").exists():
        err("Private key tidak ditemukan.")
        return
    msgs = list((BASE / receiver).glob("msg_from_*.json"))
    if not msgs:
        warn("Tidak ada pesan masuk.")
        return
    info(f"Pesan masuk ({len(msgs)} pesan):")
    for i, m in enumerate(msgs):
        print(f"    {FG['bgreen'] + BOLD}[{i}]{RESET}  {FG['bwhite']}{m.name}{RESET}")
    idx = int(input(f"\n  {FG['bcyan']}Pilih nomor pesan:{RESET} "))
    data = json.loads(msgs[idx].read_text())
    spinner_fancy("Mendekripsi dengan RSA-OAEP private key", 1.3)
    priv_r = load_private_key(BASE / receiver / "private.pem")
    try:
        plaintext = priv_r.decrypt(bytes.fromhex(data["ciphertext"]), padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None
        ))
        ok("Dekripsi berhasil!")
        sender = data["from"]
        if (BASE / sender / "cert.json").exists():
            spinner_fancy(f"Memverifikasi tanda tangan {sender.upper()}", 0.9)
            cert_s = json.loads((BASE / sender / "cert.json").read_text())
            pub_s  = serialization.load_pem_public_key(cert_s["public_key"].encode(), backend=default_backend())
            try:
                pub_s.verify(bytes.fromhex(data["signature"]), plaintext, padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
                ), hashes.SHA256())
                ok(f"Tanda tangan {sender.upper()} VALID ✓")
            except InvalidSignature:
                err(f"Tanda tangan {sender.upper()} TIDAK VALID!")
        print()
        panel([
            "  MESSAGE DECRYPTED",
            "",
            f"  From      : {data['from'].upper()}",
            f"  To        : {receiver.upper()}",
            f"  Plaintext : {plaintext.decode()}",
            f"  Timestamp : {data['timestamp']}",
        ], border_color="bgreen", title=" DECRYPTED MESSAGE ")
    except Exception as e:
        err(f"Dekripsi gagal: {e}")

def cust_verify():
    section("CUST — Verifikasi Tanda Tangan Digital", "◈")
    user   = input(f"  {FG['bcyan']}User yang memverifikasi:{RESET} ").strip().lower()
    signer = input(f"  {FG['bcyan']}User yang menandatangani:{RESET} ").strip().lower()
    if not (BASE / signer / "cert.json").exists():
        err(f"Sertifikat {signer} tidak ditemukan.")
        return
    signed_files = list((BASE / signer).glob("signed_*.json"))
    if not signed_files:
        warn("Tidak ada file bertanda tangan.")
        return
    for i, f in enumerate(signed_files):
        print(f"    {FG['bgreen'] + BOLD}[{i}]{RESET}  {FG['bwhite']}{f.name}{RESET}")
    idx  = int(input(f"\n  {FG['bcyan']}Pilih file:{RESET} "))
    data = json.loads(signed_files[idx].read_text())
    spinner_fancy("Memverifikasi rantai sertifikat CA", 0.9)
    cert_s = json.loads((BASE / signer / "cert.json").read_text())
    pub_s  = serialization.load_pem_public_key(cert_s["public_key"].encode(), backend=default_backend())
    ca_cert = json.loads((BASE / "ca" / "ca_cert.json").read_text())
    ca_pub  = serialization.load_pem_public_key(ca_cert["public_key"].encode(), backend=default_backend())
    try:
        ca_pub.verify(
            bytes.fromhex(cert_s["ca_signature"]), cert_s["public_key"].encode(),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        ok(f"Sertifikat {signer.upper()} valid — ditandatangani CA ✓")
    except InvalidSignature:
        err("Sertifikat tidak valid! Chain of trust GAGAL.")
        return
    spinner_fancy(f"Memverifikasi tanda tangan {signer.upper()}", 0.9)
    try:
        pub_s.verify(
            bytes.fromhex(data["signature"]), data["message"].encode(),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        print()
        panel([
            "  SIGNATURE VERIFIED ✓",
            "",
            f"  Pesan       : {data['message']}",
            f"  Pengirim    : {signer.upper()} (CA cert valid)",
            f"  Verifikator : {user.upper()}",
            f"  Timestamp   : {data['timestamp']}",
        ], border_color="bgreen", title=" VERIFIED ")
    except InvalidSignature:
        print()
        panel([
            "  SIGNATURE INVALID ✗",
            "",
            "  Pesan mungkin telah dimanipulasi!",
            f"  Pengirim Klaim: {signer.upper()}",
            "  Chain of Trust: BROKEN",
        ], border_color="bred", title=" TAMPERED ")

def negative_test():
    section("NEGATIVE TEST — Simulasi Serangan", "⚠")
    scenarios = [
        ("1", "Man-in-the-Middle  — Pesan dimanipulasi, signature palsu"),
        ("2", "Wrong Key Attack   — Dekripsi dengan private key yang salah"),
        ("3", "Forged Certificate — Sertifikat dipalsukan tanpa CA"),
    ]
    for key, desc in scenarios:
        icon = FG["bred"] + "▸" + RESET
        print(f"    {icon} {FG['bwhite']}{FG['bred'] + BOLD}[{key}]{RESET}  {FG['bwhite']}{desc}{RESET}")
    print()
    choice = input(f"  {FG['bcyan']}Pilih skenario (1/2/3):{RESET} ").strip()
    print()
    if choice == "1":
        spinner_fancy("Mensimulasikan MITM attack...", 1.2)
        for user in ["cust1", "cust2"]:
            if (BASE / user / "cert.json").exists():
                cert     = json.loads((BASE / user / "cert.json").read_text())
                pub      = serialization.load_pem_public_key(cert["public_key"].encode(), backend=default_backend())
                fake_sig = os.urandom(256)
                try:
                    pub.verify(fake_sig, b"PESAN PALSU", padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
                    ), hashes.SHA256())
                    warn("Signature valid (unexpected!)")
                except InvalidSignature:
                    print()
                    panel([
                        "  [ATTACK BLOCKED] MITM FAILED",
                        "",
                        f"  Target     : {user.upper()}",
                        "  Fake sig   : os.urandom(256)",
                        "  Result     : InvalidSignature — REJECTED",
                        "  Reason     : Signature tidak cocok dengan public key CA",
                    ], border_color="bred", title=" ATTACK NEUTRALIZED ")
                break
    elif choice == "2":
        spinner_fancy("Mensimulasikan wrong-key decryption", 1.0)
        for user in ["cust1", "cust2"]:
            if (BASE / user / "cert.json").exists():
                cert  = json.loads((BASE / user / "cert.json").read_text())
                pub   = serialization.load_pem_public_key(cert["public_key"].encode(), backend=default_backend())
                ct    = pub.encrypt(b"PESAN RAHASIA", padding.OAEP(
                    mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None
                ))
                wrong = generate_rsa_keypair()
                try:
                    wrong.decrypt(ct, padding.OAEP(
                        mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None
                    ))
                except Exception:
                    print()
                    panel([
                        "  [ATTACK BLOCKED] WRONG KEY FAILED",
                        "",
                        f"  Target     : {user.upper()}",
                        "  Attacker   : random RSA-2048 key",
                        "  Result     : ValueError — REJECTED",
                        "  Reason     : Ciphertext hanya bisa dibuka kunci privat asli",
                    ], border_color="bred", title=" ATTACK NEUTRALIZED ")
                break
    elif choice == "3":
        spinner_fancy("Mensimulasikan forged certificate", 1.0)
        fake_priv = generate_rsa_keypair()
        fake_sig  = fake_priv.sign(b"fakepubkey", padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
        ), hashes.SHA256())
        if (BASE / "ca" / "ca_cert.json").exists():
            ca_cert = json.loads((BASE / "ca" / "ca_cert.json").read_text())
            ca_pub  = serialization.load_pem_public_key(ca_cert["public_key"].encode(), backend=default_backend())
            try:
                ca_pub.verify(fake_sig, b"fakepubkey", padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
                ), hashes.SHA256())
            except InvalidSignature:
                print()
                panel([
                    "  [ATTACK BLOCKED] FORGE FAILED",
                    "",
                    "  Attacker   : generated own RSA keypair",
                    "  Attempted  : sign certificate without CA private key",
                    "  Result     : InvalidSignature — REJECTED",
                    "  Reason     : Hanya CA-ROOT yang bisa menerbitkan sertifikat",
                ], border_color="bred", title=" ATTACK NEUTRALIZED ")
    else:
        warn("Pilihan tidak valid.")

def pki_status():
    section("STATUS SISTEM PKI", "◈")
    entities = ["ca", "cust1", "cust2", "cust3"]
    print(f"  {FG['bwhite'] + BOLD}{'Entity':<8}  {'KeyPair':<9}  {'CSR':<6}  {'Approved':<10}  {'Cert':<6}  Messages{RESET}")
    divider(60)
    for e in entities:
        d       = BASE / e
        has_kp  = (d / "private.pem").exists() and (d / "public.pem").exists()
        has_csr = (d / "csr.json").exists() if e != "ca" else False
        has_app = (d / "csr_approved.json").exists() if e != "ca" else False
        has_cert= (d / ("ca_cert.json" if e == "ca" else "cert.json")).exists()
        msgs    = len(list(d.glob("msg_from_*.json"))) if e != "ca" else 0
        def sym(flag): return f"{FG['bgreen']}✓{RESET}" if flag else f"{FG['bred']}✗{RESET}"
        label   = f"{FG['bcyan'] + BOLD}{e.upper():<8}{RESET}"
        kp      = sym(has_kp)
        csr_s   = sym(has_csr) if e != "ca" else f"{FG['bblack'] + DIM}N/A{RESET}"
        app_s   = sym(has_app) if e != "ca" else f"{FG['bblack'] + DIM}N/A{RESET}"
        cert_s  = sym(has_cert)
        msg_s   = f"{FG['byellow']}{msgs} msg{RESET}" if msgs else f"{FG['bblack'] + DIM}none{RESET}"
        print(f"  {label}  {kp}        {csr_s}      {app_s}          {cert_s}      {msg_s}")
    divider(60)
    total_msgs  = len(list(BASE.glob("*/msg_from_*.json")))
    total_signs = len(list(BASE.glob("*/signed_*.json")))
    print()
    info(f"Total pesan terenkripsi : {FG['byellow'] + BOLD}{total_msgs}{RESET}")
    info(f"Total file signed       : {FG['byellow'] + BOLD}{total_signs}{RESET}")

def main():
    BASE.mkdir(parents=True, exist_ok=True)
    boot_sequence()
    while True:
        menu()
        choice = input("").strip().lower()
        print()
        if   choice == "1": ca_init()
        elif choice == "2": ca_certify()
        elif choice == "3": ra_validate()
        elif choice == "4": cust_register()
        elif choice == "5": cust_sign()
        elif choice == "6": cust_encrypt()
        elif choice == "7": cust_decrypt()
        elif choice == "8": cust_verify()
        elif choice == "9": negative_test()
        elif choice == "0": pki_status()
        elif choice == "q":
            print()
            typewriter("  Keluar dari sistem PKI. Sampai jumpa!", 0.015, ["bcyan", "bblue", "bcyan"])
            print()
            break
        else:
            warn("Pilihan tidak valid.")
        print()
        input(f"  {FG['bblack'] + DIM}Tekan Enter untuk kembali ke menu...{RESET}")

if __name__ == "__main__":
    main()

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

ESC    = "\033["
RESET  = f"{ESC}0m"
BOLD   = f"{ESC}1m"
DIM    = f"{ESC}2m"
ITALIC = f"{ESC}3m"
BLINK  = f"{ESC}5m"
REV    = f"{ESC}7m"

FG = {
    "black":    f"{ESC}30m", "red":      f"{ESC}31m", "green":   f"{ESC}32m",
    "yellow":   f"{ESC}33m", "blue":     f"{ESC}34m", "magenta": f"{ESC}35m",
    "cyan":     f"{ESC}36m", "white":    f"{ESC}37m",
    "bblack":   f"{ESC}90m", "bred":     f"{ESC}91m", "bgreen":  f"{ESC}92m",
    "byellow":  f"{ESC}93m", "bblue":    f"{ESC}94m", "bmagenta":f"{ESC}95m",
    "bcyan":    f"{ESC}96m", "bwhite":   f"{ESC}97m",
}
BG = {
    "black":   f"{ESC}40m",  "red":     f"{ESC}41m",  "green":   f"{ESC}42m",
    "yellow":  f"{ESC}43m",  "blue":    f"{ESC}44m",  "magenta": f"{ESC}45m",
    "cyan":    f"{ESC}46m",  "white":   f"{ESC}47m",
    "bblack":  f"{ESC}100m", "bred":    f"{ESC}101m",  "bgreen":  f"{ESC}102m",
    "byellow": f"{ESC}103m", "bblue":   f"{ESC}104m",  "bmagenta":f"{ESC}105m",
    "bcyan":   f"{ESC}106m", "bwhite":  f"{ESC}107m",
}

def fg(text, color, bold=False, dim=False):
    s = FG.get(color, "")
    if bold: s += BOLD
    if dim:  s += DIM
    return s + str(text) + RESET

def gradient_text(text, colors):
    result = ""
    n = len(colors)
    for i, ch in enumerate(text):
        result += FG.get(colors[i % n], "") + ch
    return result + RESET

def clear():
    os.system("clear" if os.name != "nt" else "cls")

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

def matrix_rain(rows=4, cols=78, duration=1.0):
    hide_cursor()
    chars = "アイウエオカキクケコサシスセソタチツテトナニヌネノ0123456789ABCDEF∑∆Ωλψ"
    end = time.time() + duration
    while time.time() < end:
        line = ""
        for _ in range(cols):
            r = random.random()
            if r < 0.05:
                line += FG["bwhite"] + BOLD + random.choice(chars) + RESET
            elif r < 0.15:
                line += FG["bgreen"] + BOLD + random.choice(chars) + RESET
            elif r < 0.4:
                line += FG["green"] + random.choice(chars) + RESET
            else:
                line += FG["bblack"] + DIM + random.choice(chars) + RESET
        print(line)
        time.sleep(0.045)
    show_cursor()

def glitch_text(text, times=3):
    glitch_chars = "▓░▒█▄▀■□●○◆◇▪▫"
    for _ in range(times):
        corrupted = ""
        for ch in text:
            if random.random() < 0.18:
                corrupted += FG["bred"] + BOLD + random.choice(glitch_chars) + RESET
            else:
                corrupted += ch
        sys.stdout.write("\r" + corrupted)
        sys.stdout.flush()
        time.sleep(0.06)
    sys.stdout.write("\r" + text + "\n")
    sys.stdout.flush()

def spinner_fancy(msg, duration=1.4):
    frames  = ["⣾","⣽","⣻","⢿","⡿","⣟","⣯","⣷"]
    bar_w   = 22
    end_t   = time.time() + duration
    hide_cursor()
    i = 0
    while time.time() < end_t:
        elapsed  = time.time() - (end_t - duration)
        progress = min(elapsed / duration, 1.0)
        filled   = int(bar_w * progress)
        bar = (FG["bgreen"] + BOLD + "█" * filled + RESET +
               FG["bblack"] + DIM + "░" * (bar_w - filled) + RESET)
        pct   = int(progress * 100)
        frame = FG["bcyan"] + BOLD + frames[i % len(frames)] + RESET
        sys.stdout.write(
            f"\r  {frame} {FG['bwhite']}{BOLD}{msg}{RESET}  "
            f"{FG['bblack']}[{RESET}{bar}{FG['bblack']}]{RESET} "
            f"{FG['byellow']}{BOLD}{pct:3d}%{RESET}  "
        )
        sys.stdout.flush()
        time.sleep(0.06)
        i += 1
    sys.stdout.write(
        f"\r  {FG['bgreen'] + BOLD}✓{RESET} {FG['bgreen']}{BOLD}{msg}{RESET}  "
        f"{FG['bblack']}[{RESET}{FG['bgreen'] + BOLD}{'█' * bar_w}{RESET}{FG['bblack']}]{RESET} "
        f"{FG['bgreen']}{BOLD}100%{RESET}       \n"
    )
    show_cursor()

def ok(msg):
    print(f"  {FG['bgreen'] + BOLD}✓{RESET} {FG['bgreen']}{BOLD}{msg}{RESET}")

def err(msg):
    print(f"  {FG['bred'] + BOLD}✗{RESET} {FG['bred']}{BOLD}{msg}{RESET}")

def warn(msg):
    print(f"  {FG['byellow'] + BOLD}⚠{RESET} {FG['byellow']}{msg}{RESET}")

def info(msg):
    print(f"  {FG['bcyan'] + BOLD}ℹ{RESET} {FG['bwhite']}{msg}{RESET}")

def divider(width=74, color="bblue", style="thin"):
    char = "─" if style == "thin" else "═"
    print(f"  {FG[color] + DIM}{char * width}{RESET}")

def section(title, icon="◈", color="bcyan"):
    w = 70
    print()
    top = f"{FG['bblue'] + DIM}╔{'═' * w}╗{RESET}"
    mid_icon = f"{FG[color] + BOLD}{icon}{RESET}"
    mid_text = gradient_text(f" {title}", ["bcyan", "bblue", "bcyan", "bblue", "bcyan"])
    pad = w - len(title) - 3
    mid = f"{FG['bblue']}║{RESET} {mid_icon}{mid_text}{' ' * max(pad, 0)}{FG['bblue']}║{RESET}"
    bot = f"{FG['bblue'] + DIM}╚{'═' * w}╝{RESET}"
    print(f"  {top}")
    print(f"  {mid}")
    print(f"  {bot}")
    print()

def panel(lines, border_color="bcyan", title=None, accent=None):
    raw_lens  = [len(l) for l in lines]
    inner_w   = max(max(raw_lens) + 4, 46) if raw_lens else 46
    top_title = f" {title} " if title else ""
    pad_l     = (inner_w - len(top_title)) // 2
    pad_r     = inner_w - len(top_title) - pad_l
    tl_color  = FG.get(accent or border_color, "")
    top  = (FG[border_color] + "╔" + "═" * pad_l + tl_color + top_title +
            FG[border_color] + "═" * pad_r + "╗" + RESET)
    print(f"  {top}")
    for l in lines:
        pad = inner_w - len(l) - 1
        if l.strip() == "":
            print(f"  {FG[border_color]}║{RESET}{' ' * (inner_w + 1)}{FG[border_color]}║{RESET}")
        else:
            print(f"  {FG[border_color]}║{RESET} {FG['bwhite']}{l}{RESET}{' ' * max(pad, 0)}{FG[border_color]}║{RESET}")
    print(f"  {FG[border_color]}╚{'═' * (inner_w + 1)}╝{RESET}")

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

LOGO_SMALL = r"""
  ██████╗ ██╗  ██╗██╗    ███████╗██╗   ██╗███████╗████████╗███████╗███╗   ███╗
"""

def boot_sequence():
    clear()
    hide_cursor()
    matrix_rain(rows=6, cols=80, duration=0.7)
    print()
    boot_msgs = [
        ("BIOS PKI v2.4.1 …………………………… OK",     "bgreen"),
        ("Loading RSA-2048 crypto engine ……… OK", "bgreen"),
        ("Mounting certificate store ………… OK",   "bcyan"),
        ("Starting X.509 chain validator …… OK",  "bblue"),
        ("Initializing PSS/OAEP modules …… OK",   "bmagenta"),
        ("Verifying chain of trust ………………… OK",  "byellow"),
        ("",                                        "bblack"),
        ("[ ALL SYSTEMS OPERATIONAL ]",             "bgreen"),
    ]
    for msg, color in boot_msgs:
        if msg == "":
            print()
            continue
        sys.stdout.write(f"  {FG['bblack'] + DIM}▸{RESET} ")
        sys.stdout.flush()
        for ch in msg:
            sys.stdout.write(FG[color] + ch + RESET)
            sys.stdout.flush()
            time.sleep(0.006)
        print()
        time.sleep(0.04)
    show_cursor()
    time.sleep(0.3)

def _logo_gradient_line(line, tick):
    palettes = [
        ["bcyan", "bblue", "bcyan", "bblue"],
        ["bblue", "bcyan", "bblue", "bcyan"],
        ["bmagenta", "bcyan", "bblue", "bcyan"],
        ["bcyan", "bmagenta", "bcyan", "bblue"],
    ]
    pal = palettes[tick % len(palettes)]
    result = ""
    n = len(pal)
    for i, ch in enumerate(line):
        result += FG.get(pal[(i + tick) % n], "") + ch
    return result + RESET

def header_banner():
    clear()
    logo_lines = LOGO.split("\n")
    for i, line in enumerate(logo_lines):
        pal = ["bcyan", "bblue", "bcyan", "bblue", "bcyan", "bmagenta"]
        col = pal[i % len(pal)]
        print(FG[col] + BOLD + line + RESET)
    now = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    W   = 78
    print(f"  {FG['bblue'] + DIM}{'▄' * W}{RESET}")
    inner = (
        f" {FG['byellow'] + BOLD}◈ UAS KRIPTOGRAFI{RESET}"
        f"  {FG['bblack'] + DIM}│{RESET}  "
        f"{FG['bcyan'] + BOLD}PUBLIC KEY INFRASTRUCTURE{RESET}"
        f"  {FG['bblack'] + DIM}│{RESET}  "
        f"{FG['bblack'] + DIM}{now}{RESET} "
    )
    sub = (
        f" {FG['bblack'] + DIM}"
        f"RSA-2048  ·  PSS Signature  ·  OAEP Encryption  ·  X.509 Chain  ·  Semester 4{RESET}"
    )
    print(f"  {FG['bblue']}▌{RESET}{inner}{FG['bblue']}▐{RESET}")
    print(f"  {FG['bblue']}▌{RESET}{sub}{FG['bblue']}▐{RESET}")
    print(f"  {FG['bblue'] + DIM}{'▀' * W}{RESET}")
    print()

def status_bar():
    ca_ok = (BASE / "ca" / "ca_cert.json").exists()
    c1_ok = (BASE / "cust1" / "cert.json").exists()
    c2_ok = (BASE / "cust2" / "cert.json").exists()
    c3_ok = (BASE / "cust3" / "cert.json").exists()

    def node_badge(label, ok_flag):
        if ok_flag:
            return (f"{FG['bgreen'] + BOLD}▐{BG['green'] + FG['black'] + BOLD} {label} {RESET}"
                    f"{FG['bgreen'] + DIM}▌ {FG['bgreen']}LIVE{RESET}")
        else:
            return (f"{FG['bblack'] + BOLD}▐{BG['bblack'] + FG['bwhite'] + DIM} {label} {RESET}"
                    f"{FG['bblack'] + DIM}▌ {FG['bblack'] + DIM}PEND{RESET}")

    badges = "    ".join([
        node_badge("CA", ca_ok),
        node_badge("CUST1", c1_ok),
        node_badge("CUST2", c2_ok),
        node_badge("CUST3", c3_ok),
    ])
    divider(76, "bblue", "thin")
    print(f"  {FG['byellow'] + BOLD}TRUST CHAIN{RESET}  {badges}")
    divider(76, "bblue", "thin")
    print()

ROLE_META = {
    "CA":   ("byellow",  "●", "AUTHORITY"),
    "RA":   ("bmagenta", "●", "REGISTRAR"),
    "CUST": ("bcyan",    "●", "USER"),
    "TEST": ("bred",     "▲", "ATTACK"),
    "INFO": ("bblue",    "◆", "SYSTEM"),
    "    ": ("bblack",   "·", ""),
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
    ("0", "INFO", "Status & Info Sistem PKI"),
    ("q", "    ", "Keluar dari sistem"),
]

def menu():
    header_banner()
    status_bar()
    W = 68
    border = FG["bblue"]
    dim    = FG["bblue"] + DIM
    print(f"  {dim}┏{'━' * W}┓{RESET}")
    title_s = "  MENU UTAMA  "
    pad_l   = (W - len(title_s)) // 2
    pad_r   = W - len(title_s) - pad_l
    print(
        f"  {border}┃{RESET}"
        f"{'─' * pad_l}"
        f"{FG['bwhite'] + BOLD}{title_s}{RESET}"
        f"{'─' * pad_r}"
        f"{border}┃{RESET}"
    )
    print(f"  {dim}┣{'━' * W}┫{RESET}")
    print(f"  {border}┃{RESET}{'  ' + FG['bblack'] + DIM + 'KEY  ROLE        DESC' + RESET:<{W-1}}{border}┃{RESET}")
    print(f"  {dim}┠{'─' * W}┨{RESET}")
    for num, role, label in MENU_ENTRIES:
        color, dot, badge = ROLE_META.get(role, ("bwhite", "·", ""))
        key_s  = f"{FG['bgreen'] + BOLD} {num} {RESET}"
        dot_s  = f"{FG[color] + BOLD}{dot}{RESET}"
        role_s = f"{FG[color] + BOLD}{role:<4}{RESET}"
        sep    = f"{FG['bblack'] + DIM}│{RESET}"
        lbl_s  = f"{FG['bwhite']}{label}{RESET}"
        badge_s = f"{FG[color] + DIM}[{badge}]{RESET}" if badge else ""
        inner  = f" {key_s} {sep} {dot_s} {role_s} {sep} {lbl_s}  {badge_s}"
        vis_len = 3 + 3 + 3 + 1 + len(role) + 3 + len(label) + 2 + (len(badge) + 2 if badge else 0)
        pad    = max(W - vis_len, 0)
        print(f"  {border}┃{RESET}{inner}{' ' * pad}{border}┃{RESET}")
    print(f"  {dim}┗{'━' * W}┛{RESET}")
    print()
    sys.stdout.write(
        f"  {FG['bgreen'] + BOLD}❯❯{RESET} "
        f"{FG['bwhite'] + BOLD}Pilih menu:{RESET} "
        f"{FG['bcyan']}"
    )
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
    section("CERTIFICATE AUTHORITY — Inisialisasi", "◈", "byellow")
    ensure_dirs("ca")
    if (BASE / "ca" / "private.pem").exists():
        warn("CA sudah diinisialisasi sebelumnya.")
        choice = input(f"\n  {FG['byellow']}Timpa ulang? (y/N):{RESET} {FG['bcyan']}").strip().lower()
        print(RESET, end="")
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
        f"  Subject     : {cert['subject']}",
        f"  Issuer      : {cert['issuer']}",
        f"  Serial No   : {cert['serial']}",
        "",
        f"  Valid From  : {cert['valid_from']}",
        f"  Valid To    : {cert['valid_to']}  (10 years)",
        f"  Key Size    : RSA-2048",
        f"  Signature   : SHA-256 with RSA",
        "",
        f"  Fingerprint : {fp}...",
    ], border_color="byellow", title=" ◈ CA CERTIFICATE ", accent="byellow")

def ra_validate():
    section("REGISTRATION AUTHORITY — Validasi Pemohon", "◈", "bmagenta")
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
            f"  Common Name : {csr.get('common_name', user)}",
            f"  Email       : {csr.get('email', '-')}",
            f"  Timestamp   : {csr.get('timestamp', '-')}",
            "",
            f"  Status      : MENUNGGU VALIDASI RA",
        ], border_color="bmagenta", title=f" ◈ CSR DARI {user.upper()} ", accent="bmagenta")
        approve = input(f"\n  {FG['bmagenta']}Setujui CSR {FG['bcyan'] + BOLD}{user.upper()}{RESET}{FG['bmagenta']}?{RESET} (y/N): {FG['bcyan']}").strip().lower()
        print(RESET, end="")
        if approve == "y":
            csr["ra_approved"]  = True
            csr["ra_timestamp"] = str(datetime.datetime.now())
            (BASE / user / "csr_approved.json").write_text(json.dumps(csr, indent=2))
            spinner_fancy(f"Memforward CSR {user.upper()} ke CA", 0.9)
            ok(f"CSR {user.upper()} disetujui RA → diteruskan ke CA")
        else:
            warn(f"CSR {user.upper()} ditolak.")

def ca_certify():
    section("CERTIFICATE AUTHORITY — Penerbitan Sertifikat", "◈", "byellow")
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
            spinner_fancy(f"Mensertifikasi public key {user.upper()}", 1.3)
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
                f"  Subject     : {cert['subject']}",
                f"  Issuer      : {cert['issuer']}",
                f"  Serial No   : {cert['serial']}",
                "",
                f"  Valid       : {cert['valid_from']} → {cert['valid_to']}",
                f"  Common Name : {cert['common_name']}",
                f"  Email       : {cert['email']}",
                "",
                f"  Fingerprint : {fp}...",
            ], border_color="bgreen", title=f" ◈ CERT ISSUED: {user.upper()} ", accent="bgreen")
            certified.append(user)
    if not certified:
        warn("Tidak ada CSR yang sudah disetujui RA dan menunggu sertifikasi.")

def cust_register():
    section("CUST — Pendaftaran & Pembuatan Key Pair", "◈", "bcyan")
    info(f"User tersedia: {FG['bcyan'] + BOLD}cust1{RESET}  {FG['bcyan'] + BOLD}cust2{RESET}  {FG['bcyan'] + BOLD}cust3{RESET}")
    user = input(f"\n  {FG['bcyan']}Masukkan nama user:{RESET} {FG['bcyan']}").strip().lower()
    print(RESET, end="")
    if user not in ["cust1", "cust2", "cust3"]:
        err("User tidak valid.")
        return
    ensure_dirs(user)
    if (BASE / user / "private.pem").exists():
        warn(f"{user.upper()} sudah memiliki keypair.")
        if input(f"  {FG['byellow']}Buat ulang? (y/N):{RESET} {FG['bcyan']}").strip().lower() != "y":
            print(RESET, end="")
            return
        print(RESET, end="")
    spinner_fancy(f"Generating RSA-2048 keypair untuk {user.upper()}", 1.6)
    priv  = generate_rsa_keypair()
    save_private_key(priv, BASE / user / "private.pem")
    save_public_key(priv.public_key(), BASE / user / "public.pem")
    cn    = input(f"  {FG['bcyan']}Common Name (nama lengkap):{RESET} {FG['bwhite']}").strip() or user
    print(RESET, end="")
    email = input(f"  {FG['bcyan']}Email:{RESET} {FG['bwhite']}").strip() or f"{user}@pki.local"
    print(RESET, end="")
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
        f"  User        : {user.upper()}",
        f"  Common Name : {cn}",
        f"  Email       : {email}",
        f"  Key Size    : RSA-2048",
        "",
        f"  CSR Status  : DIKIRIM KE RA →",
    ], border_color="bcyan", title=" ◈ KEYPAIR GENERATED ", accent="bcyan")

def cust_sign():
    section("CUST — Buat Tanda Tangan Digital", "◈", "bcyan")
    user = input(f"  {FG['bcyan']}Pengirim (user):{RESET} {FG['bcyan']}").strip().lower()
    print(RESET, end="")
    if not (BASE / user / "private.pem").exists():
        err("Keypair tidak ditemukan.")
        return
    if not (BASE / user / "cert.json").exists():
        err("Sertifikat belum diterbitkan CA.")
        return
    msg  = input(f"  {FG['bcyan']}Pesan yang akan ditandatangani:{RESET} {FG['bwhite']}").strip()
    print(RESET, end="")
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
    info(f"Disimpan   : {FG['bcyan']}{fname}{RESET}")
    info(f"Sig (hex)  : {FG['byellow']}{sig.hex()[:64]}…{RESET}")

def cust_encrypt():
    section("CUST — Enkripsi Pesan Rahasia", "◈", "bgreen")
    sender   = input(f"  {FG['bcyan']}Pengirim:{RESET} {FG['bcyan']}").strip().lower()
    print(RESET, end="")
    receiver = input(f"  {FG['bcyan']}Penerima:{RESET} {FG['bcyan']}").strip().lower()
    print(RESET, end="")
    if not (BASE / sender / "private.pem").exists():
        err(f"Private key {sender} tidak ditemukan.")
        return
    if not (BASE / receiver / "cert.json").exists():
        err(f"Sertifikat {receiver} tidak ditemukan.")
        return
    msg = input(f"  {FG['bcyan']}Pesan rahasia:{RESET} {FG['bwhite']}").strip()
    print(RESET, end="")
    spinner_fancy("Mengenkripsi dengan RSA-OAEP + Digital Signature", 1.6)
    cert_r     = json.loads((BASE / receiver / "cert.json").read_text())
    pub_r      = serialization.load_pem_public_key(cert_r["public_key"].encode(), backend=default_backend())
    ciphertext = pub_r.encrypt(msg.encode(), padding.OAEP(
        mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None
    ))
    priv_s = load_private_key(BASE / sender / "private.pem")
    sig    = priv_s.sign(msg.encode(), padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
    ), hashes.SHA256())
    out   = {
        "from": sender, "to": receiver,
        "ciphertext": ciphertext.hex(), "signature": sig.hex(),
        "timestamp":  str(datetime.datetime.now())
    }
    fname = BASE / receiver / f"msg_from_{sender}_{int(time.time())}.json"
    fname.write_text(json.dumps(out, indent=2))
    print()
    panel([
        f"  From        : {sender.upper()}",
        f"  To          : {receiver.upper()}",
        f"  Encryption  : RSA-OAEP (SHA-256)",
        f"  Signature   : RSA-PSS (SHA-256)",
        "",
        f"  Ciphertext  : {ciphertext.hex()[:48]}…",
    ], border_color="bgreen", title=" ◈ ENCRYPTED & SIGNED ", accent="bgreen")

def cust_decrypt():
    section("CUST — Dekripsi Pesan Rahasia", "◈", "bcyan")
    receiver = input(f"  {FG['bcyan']}Penerima (user kamu):{RESET} {FG['bcyan']}").strip().lower()
    print(RESET, end="")
    if not (BASE / receiver / "private.pem").exists():
        err("Private key tidak ditemukan.")
        return
    msgs = list((BASE / receiver).glob("msg_from_*.json"))
    if not msgs:
        warn("Tidak ada pesan masuk.")
        return
    print(f"\n  {FG['bwhite'] + BOLD}Pesan masuk{RESET}  {FG['bblack'] + DIM}({len(msgs)} pesan){RESET}")
    divider(50, "bblue")
    for i, m in enumerate(msgs):
        data = json.loads(m.read_text())
        ts   = data.get("timestamp", "")[:16]
        print(f"  {FG['bgreen'] + BOLD}[{i}]{RESET}  {FG['bcyan']}{m.name}{RESET}  {FG['bblack'] + DIM}{ts}{RESET}")
    divider(50, "bblue")
    idx  = int(input(f"\n  {FG['bcyan']}Pilih nomor pesan:{RESET} {FG['bcyan']}"))
    print(RESET, end="")
    data = json.loads(msgs[idx].read_text())
    spinner_fancy("Mendekripsi dengan RSA-OAEP private key", 1.4)
    priv_r = load_private_key(BASE / receiver / "private.pem")
    try:
        plaintext = priv_r.decrypt(bytes.fromhex(data["ciphertext"]), padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None
        ))
        ok("Dekripsi berhasil!")
        sender = data["from"]
        if (BASE / sender / "cert.json").exists():
            spinner_fancy(f"Memverifikasi tanda tangan {sender.upper()}", 1.0)
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
            f"  From        : {data['from'].upper()}",
            f"  To          : {receiver.upper()}",
            f"  Timestamp   : {data['timestamp']}",
            "",
            f"  Plaintext   : {plaintext.decode()}",
        ], border_color="bgreen", title=" ◈ MESSAGE DECRYPTED ", accent="bgreen")
    except Exception as e:
        err(f"Dekripsi gagal: {e}")

def cust_verify():
    section("CUST — Verifikasi Tanda Tangan Digital", "◈", "bcyan")
    user   = input(f"  {FG['bcyan']}User yang memverifikasi:{RESET} {FG['bcyan']}").strip().lower()
    print(RESET, end="")
    signer = input(f"  {FG['bcyan']}User yang menandatangani:{RESET} {FG['bcyan']}").strip().lower()
    print(RESET, end="")
    if not (BASE / signer / "cert.json").exists():
        err(f"Sertifikat {signer} tidak ditemukan.")
        return
    signed_files = list((BASE / signer).glob("signed_*.json"))
    if not signed_files:
        warn("Tidak ada file bertanda tangan.")
        return
    divider(50, "bblue")
    for i, f in enumerate(signed_files):
        data = json.loads(f.read_text())
        ts   = data.get("timestamp", "")[:16]
        print(f"  {FG['bgreen'] + BOLD}[{i}]{RESET}  {FG['bwhite']}{f.name}{RESET}  {FG['bblack'] + DIM}{ts}{RESET}")
    divider(50, "bblue")
    idx  = int(input(f"\n  {FG['bcyan']}Pilih file:{RESET} {FG['bcyan']}"))
    print(RESET, end="")
    data = json.loads(signed_files[idx].read_text())
    spinner_fancy("Memverifikasi rantai sertifikat CA", 1.0)
    cert_s  = json.loads((BASE / signer / "cert.json").read_text())
    pub_s   = serialization.load_pem_public_key(cert_s["public_key"].encode(), backend=default_backend())
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
    spinner_fancy(f"Memverifikasi tanda tangan {signer.upper()}", 1.0)
    try:
        pub_s.verify(
            bytes.fromhex(data["signature"]), data["message"].encode(),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        print()
        panel([
            f"  Pesan       : {data['message']}",
            f"  Pengirim    : {signer.upper()}  (cert valid ✓)",
            f"  Verifikator : {user.upper()}",
            f"  Timestamp   : {data['timestamp']}",
            "",
            f"  Signature   : VALID ✓",
        ], border_color="bgreen", title=" ◈ SIGNATURE VERIFIED ", accent="bgreen")
    except InvalidSignature:
        print()
        panel([
            f"  Pesan       : {data['message']}",
            f"  Pengirim    : {signer.upper()}",
            "",
            f"  PESAN MUNGKIN TELAH DIMANIPULASI!",
            f"  Chain of Trust : BROKEN",
        ], border_color="bred", title=" ◈ SIGNATURE INVALID ✗ ", accent="bred")

def negative_test():
    section("NEGATIVE TEST — Simulasi Serangan", "⚠", "bred")
    scenarios = [
        ("1", "Man-in-the-Middle", "Pesan dimanipulasi, tanda tangan dipalsukan"),
        ("2", "Wrong Key Attack",  "Dekripsi dengan private key yang salah"),
        ("3", "Forged Certificate","Sertifikat dibuat tanpa private key CA"),
    ]
    print(f"  {FG['bred'] + BOLD}⚠  ATTACK SIMULATION LAB{RESET}")
    print()
    for key, name, desc in scenarios:
        print(f"  {FG['bred'] + BOLD}[{key}]{RESET}  {FG['bwhite'] + BOLD}{name:<22}{RESET}  {FG['bblack'] + DIM}{desc}{RESET}")
    print()
    choice = input(f"  {FG['bcyan']}Pilih skenario (1/2/3):{RESET} {FG['bcyan']}").strip()
    print(RESET + "")
    if choice == "1":
        spinner_fancy("Mensimulasikan MITM attack…", 1.3)
        for user in ["cust1", "cust2"]:
            if (BASE / user / "cert.json").exists():
                cert     = json.loads((BASE / user / "cert.json").read_text())
                pub      = serialization.load_pem_public_key(cert["public_key"].encode(), backend=default_backend())
                fake_sig = os.urandom(256)
                try:
                    pub.verify(fake_sig, b"PESAN PALSU", padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
                    ), hashes.SHA256())
                except InvalidSignature:
                    print()
                    panel([
                        f"  Target      : {user.upper()}",
                        f"  Fake Sig    : os.urandom(256)",
                        f"  Result      : InvalidSignature",
                        "",
                        f"  Reason      : Sig tidak cocok public key CA",
                        f"  VERDICT     : ATTACK BLOCKED ✓",
                    ], border_color="bred", title=" ⚠ MITM — NEUTRALIZED ", accent="bred")
                break
    elif choice == "2":
        spinner_fancy("Mensimulasikan wrong-key decryption", 1.1)
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
                        f"  Target      : {user.upper()}",
                        f"  Attacker    : random RSA-2048 key",
                        f"  Result      : ValueError — REJECTED",
                        "",
                        f"  Reason      : Hanya private key asli yang bisa dekripsi",
                        f"  VERDICT     : ATTACK BLOCKED ✓",
                    ], border_color="bred", title=" ⚠ WRONG KEY — NEUTRALIZED ", accent="bred")
                break
    elif choice == "3":
        spinner_fancy("Mensimulasikan certificate forgery", 1.1)
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
                    f"  Attacker    : own RSA-2048 keypair",
                    f"  Attempted   : sign cert without CA private key",
                    f"  Result      : InvalidSignature",
                    "",
                    f"  Reason      : Hanya CA-ROOT yang bisa terbitkan cert",
                    f"  VERDICT     : ATTACK BLOCKED ✓",
                ], border_color="bred", title=" ⚠ FORGE CERT — NEUTRALIZED ", accent="bred")
    else:
        warn("Pilihan tidak valid.")

def pki_status():
    section("STATUS & INFO SISTEM PKI", "◈", "bblue")
    entities = ["ca", "cust1", "cust2", "cust3"]
    header = (
        f"  {FG['bwhite'] + BOLD}{'Entity':<8}  {'KeyPair':<9}  {'CSR':<6}  {'Approved':<10}  {'Cert':<8}  {'Messages'}{RESET}"
    )
    divider(64, "bblue")
    print(header)
    divider(64, "bblue")
    for e in entities:
        d        = BASE / e
        has_kp   = (d / "private.pem").exists() and (d / "public.pem").exists()
        has_csr  = (d / "csr.json").exists() if e != "ca" else False
        has_app  = (d / "csr_approved.json").exists() if e != "ca" else False
        has_cert = (d / ("ca_cert.json" if e == "ca" else "cert.json")).exists()
        msgs     = len(list(d.glob("msg_from_*.json"))) if e != "ca" else 0

        def sym(flag, na=False):
            if na:  return f"{FG['bblack'] + DIM} N/A {RESET}"
            return f"{FG['bgreen'] + BOLD} ✓  {RESET}" if flag else f"{FG['bred'] + DIM} ✗  {RESET}"

        label  = f"{FG['bcyan'] + BOLD}{e.upper():<8}{RESET}"
        msg_s  = f"{FG['byellow']}{msgs} msg{RESET}" if msgs else f"{FG['bblack'] + DIM}none{RESET}"
        print(
            f"  {label}  {sym(has_kp)}      {sym(has_csr, e=='ca')}    "
            f"{sym(has_app, e=='ca')}        {sym(has_cert)}      {msg_s}"
        )
    divider(64, "bblue")
    total_msgs  = len(list(BASE.glob("*/msg_from_*.json")))
    total_signs = len(list(BASE.glob("*/signed_*.json")))
    print()
    info(f"Pesan terenkripsi  : {FG['byellow'] + BOLD}{total_msgs}{RESET}")
    info(f"File ditandatangani: {FG['byellow'] + BOLD}{total_signs}{RESET}")
    print()
    panel([
        "  ALGORITMA YANG DIGUNAKAN",
        "",
        "  Enkripsi   : RSA-OAEP (SHA-256, MGF1)",
        "  Signature  : RSA-PSS (SHA-256, MAX_SALT)",
        "  Key Size   : RSA-2048 bit",
        "  Cert Format: JSON (simplified X.509)",
        "  CA Model   : Hierarchical PKI (Root CA)",
    ], border_color="bblue", title=" ◈ CRYPTO SPEC ", accent="bcyan")

def main():
    BASE.mkdir(parents=True, exist_ok=True)
    boot_sequence()
    while True:
        menu()
        choice = sys.stdin.readline().strip().lower()
        print(RESET)
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
            print(f"  {FG['bblue'] + DIM}{'▄' * 72}{RESET}")
            typewriter("  ◈  Terima kasih. PKI System offline.", 0.013, ["bcyan", "bblue", "bcyan", "bblue"])
            typewriter("  ◈  Sampai jumpa!", 0.015, ["bblue", "bcyan"])
            print(f"  {FG['bblue'] + DIM}{'▀' * 72}{RESET}")
            print(RESET)
            break
        else:
            warn("Pilihan tidak valid.")
        print()
        input(f"  {FG['bblack'] + DIM}[ tekan Enter untuk kembali ke menu ] {RESET}")

if __name__ == "__main__":
    main()

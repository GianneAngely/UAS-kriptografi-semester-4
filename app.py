import os
import sys
import time
import json
import datetime
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend

BASE = Path("pki_data")

C = {
    "reset": "\033[0m", "bold": "\033[1m", "dim": "\033[2m",
    "green": "\033[92m", "cyan": "\033[96m", "yellow": "\033[93m",
    "red": "\033[91m", "magenta": "\033[95m", "blue": "\033[94m",
    "white": "\033[97m",
}

ASCII_LOGO = """
 ██████╗ ██╗  ██╗██╗    ███████╗██╗   ██╗███████╗████████╗███████╗███╗   ███╗
 ██╔══██╗██║ ██╔╝██║    ██╔════╝╚██╗ ██╔╝██╔════╝╚══██╔══╝██╔════╝████╗ ████║
 ██████╔╝█████╔╝ ██║    ███████╗ ╚████╔╝ ███████╗   ██║   █████╗  ██╔████╔██║
 ██╔═══╝ ██╔═██╗ ██║    ╚════██║  ╚██╔╝  ╚════██║   ██║   ██╔══╝  ██║╚██╔╝██║
 ██║     ██║  ██╗██║    ███████║   ██║   ███████║   ██║   ███████╗██║ ╚═╝ ██║
 ╚═╝     ╚═╝  ╚═╝╚═╝    ╚══════╝   ╚═╝   ╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝
"""


def c(text, *codes):
    return "".join(C.get(code, "") for code in codes) + str(text) + C["reset"]


def clear():
    os.system("clear" if os.name != "nt" else "cls")


def typewriter(text, delay=0.018, color="cyan"):
    for ch in text:
        sys.stdout.write(c(ch, color))
        sys.stdout.flush()
        time.sleep(delay)
    print()


def spinner(msg, duration=1.2):
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    end = time.time() + duration
    i = 0
    while time.time() < end:
        sys.stdout.write(f"\r  {c(frames[i % len(frames)], 'cyan', 'bold')} {c(msg, 'white')}  ")
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1
    sys.stdout.write(f"\r  {c('✓', 'green', 'bold')} {c(msg, 'green')}       \n")


def ok(msg):
    print(f"  {c('✓', 'green', 'bold')} {c(msg, 'green')}")


def err(msg):
    print(f"  {c('✗', 'red', 'bold')} {c(msg, 'red')}")


def warn(msg):
    print(f"  {c('⚠', 'yellow', 'bold')} {c(msg, 'yellow')}")


def info(msg):
    print(f"  {c('ℹ', 'cyan', 'bold')} {c(msg, 'white')}")


def section(title):
    width = 60
    line = c("─" * width, "blue", "dim")
    print()
    print(f"  {line}")
    print(f"  {c('│', 'blue', 'dim')} {c(title, 'cyan', 'bold')}")
    print(f"  {line}")


def box_print(lines, color="cyan"):
    width = max(len(l) for l in lines) + 4
    print(f"  {c('╔' + '═'*width + '╗', color)}")
    for l in lines:
        pad = width - len(l) - 2
        print(f"  {c('║', color)} {c(l, 'white')} {' '*pad}{c('║', color)}")
    print(f"  {c('╚' + '═'*width + '╝', color)}")


def header_banner():
    clear()
    for line in ASCII_LOGO.split("\n"):
        print(c(line, "cyan", "bold"))
    print(c("  ╔══════════════════════════════════════════════════════════════════════════╗", "blue"))
    print(c("  ║  ", "blue") + c("UAS KRIPTOGRAFI SEMESTER 4", "yellow", "bold") + c("  ·  ", "blue") + c("PUBLIC KEY INFRASTRUCTURE", "cyan") + c("  ║", "blue"))
    print(c("  ║  ", "blue") + c("RSA-2048 · PSS Signature · OAEP Encryption · X.509 Certificate Chain", "dim") + c("        ║", "blue"))
    print(c("  ╚══════════════════════════════════════════════════════════════════════════╝", "blue"))
    print()


def status_bar():
    ca_ok = (BASE / "ca" / "ca_cert.json").exists()
    cust1_ok = (BASE / "cust1" / "cert.json").exists()
    cust2_ok = (BASE / "cust2" / "cert.json").exists()
    items = [("CA", ca_ok), ("CUST1", cust1_ok), ("CUST2", cust2_ok)]
    parts = []
    for name, status in items:
        dot = c("●", "green") if status else c("●", "red")
        parts.append(f"  {dot} {c(name, 'white', 'dim')}")
    ts = c(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "dim")
    print("  " + c("STATUS:", "yellow", "bold") + "  " + "  ".join(parts) + "     " + ts)
    print()


def menu():
    header_banner()
    status_bar()
    entries = [
        ("1", "CA", "Inisialisasi Key Pair CA"),
        ("2", "CA", "Terbitkan Sertifikat"),
        ("3", "RA", "Validasi Request Cust"),
        ("4", "CUST", "Daftar & Buat Key Pair"),
        ("5", "CUST", "Tanda Tangan Digital"),
        ("6", "CUST", "Enkripsi Pesan Rahasia"),
        ("7", "CUST", "Dekripsi Pesan Rahasia"),
        ("8", "CUST", "Verifikasi Tanda Tangan"),
        ("9", "TEST", "Negative Test (Simulasi Serangan)"),
        ("0", "INFO", "Status Sistem PKI"),
        ("q", "    ", "Keluar"),
    ]
    role_colors = {"CA": "yellow", "RA": "magenta", "CUST": "cyan", "TEST": "red", "INFO": "blue", "    ": "dim"}
    print(c("  ┌─────────────────────────────────────────────────────┐", "blue"))
    print(c("  │  ", "blue") + c("MENU UTAMA", "white", "bold") + c("                                          │", "blue"))
    print(c("  ├─────────────────────────────────────────────────────┤", "blue"))
    for num, role, label in entries:
        rc = role_colors.get(role, "white")
        n = c(f"[{num}]", "green", "bold")
        r = c(f"{role:<4}", rc, "bold")
        l = c(label, "white")
        print(f"  {c('│', 'blue')}  {n}  {r}  {l:<35}{c('│', 'blue')}")
    print(c("  └─────────────────────────────────────────────────────┘", "blue"))
    print()


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
    section("INISIALISASI CA — Certificate Authority")
    ensure_dirs("ca")
    if (BASE / "ca" / "private.pem").exists():
        warn("CA sudah diinisialisasi sebelumnya.")
        choice = input(f"  {c('Timpa ulang?', 'yellow')} (y/N): ").strip().lower()
        if choice != "y":
            return
    spinner("Membuat RSA-2048 keypair untuk CA...", 1.5)
    priv = generate_rsa_keypair()
    save_private_key(priv, BASE / "ca" / "private.pem")
    save_public_key(priv.public_key(), BASE / "ca" / "public.pem")
    cert = {
        "subject": "CA-ROOT",
        "issuer": "SELF-SIGNED",
        "serial": "0001",
        "valid_from": str(datetime.date.today()),
        "valid_to": str(datetime.date.today() + datetime.timedelta(days=3650)),
        "public_key": priv.public_key().public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
    }
    (BASE / "ca" / "ca_cert.json").write_text(json.dumps(cert, indent=2))
    fingerprint = hashes.Hash(hashes.SHA256(), backend=default_backend())
    fingerprint.update(cert["public_key"].encode())
    fp = fingerprint.finalize().hex()[:32]
    ok("Keypair CA berhasil dibuat!")
    box_print([
        "CERTIFICATE AUTHORITY INITIALIZED",
        "",
        f"Subject  : {cert['subject']}",
        f"Valid    : {cert['valid_from']} → {cert['valid_to']}",
        f"Key Size : RSA-2048",
        f"Fingerprint: {fp}...",
    ], "yellow")


def ra_validate():
    section("RA — Registration Authority: Validasi Pemohon")
    pending = []
    for user in ["cust1", "cust2", "cust3"]:
        csr_path = BASE / user / "csr.json"
        cert_path = BASE / user / "cert.json"
        if csr_path.exists() and not cert_path.exists():
            pending.append(user)
    if not pending:
        warn("Tidak ada CSR pending untuk divalidasi.")
        return
    for user in pending:
        csr = json.loads((BASE / user / "csr.json").read_text())
        print()
        box_print([
            f"CSR DARI: {user.upper()}",
            "",
            f"Common Name : {csr.get('common_name', user)}",
            f"Email       : {csr.get('email', '-')}",
            f"Tanggal     : {csr.get('timestamp', '-')}",
            f"Status      : MENUNGGU VALIDASI",
        ], "magenta")
        approve = input(f"  {c('Setujui CSR dari', 'yellow')} {c(user.upper(), 'cyan', 'bold')}? (y/N): ").strip().lower()
        if approve == "y":
            csr["ra_approved"] = True
            csr["ra_timestamp"] = str(datetime.datetime.now())
            (BASE / user / "csr_approved.json").write_text(json.dumps(csr, indent=2))
            ok(f"CSR {user.upper()} disetujui oleh RA → diteruskan ke CA")
        else:
            warn(f"CSR {user.upper()} ditolak.")


def ca_certify():
    section("CA — Penerbitan Sertifikat Digital")
    if not (BASE / "ca" / "private.pem").exists():
        err("CA belum diinisialisasi! Jalankan menu [1] terlebih dahulu.")
        return
    ca_priv = load_private_key(BASE / "ca" / "private.pem")
    certified = []
    for user in ["cust1", "cust2", "cust3"]:
        approved_path = BASE / user / "csr_approved.json"
        cert_path = BASE / user / "cert.json"
        pub_path = BASE / user / "public.pem"
        if approved_path.exists() and not cert_path.exists() and pub_path.exists():
            spinner(f"Mensertifikasi kunci publik {user.upper()}...", 1.0)
            csr = json.loads(approved_path.read_text())
            pub_key_pem = pub_path.read_bytes()
            sig = ca_priv.sign(pub_key_pem, padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ), hashes.SHA256())
            cert = {
                "subject": user.upper(),
                "issuer": "CA-ROOT",
                "serial": f"{hash(user) % 9999:04d}",
                "valid_from": str(datetime.date.today()),
                "valid_to": str(datetime.date.today() + datetime.timedelta(days=365)),
                "public_key": pub_key_pem.decode(),
                "ca_signature": sig.hex(),
                "common_name": csr.get("common_name", user),
                "email": csr.get("email", "-"),
            }
            cert_path.write_text(json.dumps(cert, indent=2))
            fp_h = hashes.Hash(hashes.SHA256(), backend=default_backend())
            fp_h.update(pub_key_pem)
            fp = fp_h.finalize().hex()[:32]
            ok(f"Sertifikat {user.upper()} diterbitkan!")
            print(f"     {c('Serial:', 'dim')} {c(cert['serial'], 'cyan')}")
            print(f"     {c('Fingerprint:', 'dim')} {c(fp + '...', 'cyan')}")
            certified.append(user)
    if not certified:
        warn("Tidak ada CSR yang sudah disetujui RA dan menunggu sertifikasi.")


def cust_register():
    section("CUST — Pendaftaran & Pembuatan Key Pair")
    print(f"  {c('User tersedia:', 'yellow')} cust1, cust2, cust3")
    user = input(f"  {c('Masukkan nama user:', 'cyan')} ").strip().lower()
    if user not in ["cust1", "cust2", "cust3"]:
        err("User tidak valid.")
        return
    ensure_dirs(user)
    if (BASE / user / "private.pem").exists():
        warn(f"{user.upper()} sudah memiliki keypair.")
        if input(f"  {c('Buat ulang?', 'yellow')} (y/N): ").strip().lower() != "y":
            return
    spinner(f"Membuat RSA-2048 keypair untuk {user.upper()}...", 1.3)
    priv = generate_rsa_keypair()
    save_private_key(priv, BASE / user / "private.pem")
    save_public_key(priv.public_key(), BASE / user / "public.pem")
    cn = input(f"  {c('Common Name (nama lengkap):', 'cyan')} ").strip() or user
    email = input(f"  {c('Email:', 'cyan')} ").strip() or f"{user}@pki.local"
    csr = {
        "common_name": cn, "email": email,
        "timestamp": str(datetime.datetime.now()),
        "public_key": priv.public_key().public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
    }
    (BASE / user / "csr.json").write_text(json.dumps(csr, indent=2))
    ok(f"Keypair {user.upper()} dibuat & CSR dikirim ke RA")
    box_print([
        f"KEY PAIR GENERATED: {user.upper()}",
        "",
        f"Common Name : {cn}",
        f"Email       : {email}",
        f"Key Size    : RSA-2048",
        f"CSR Status  : DIKIRIM KE RA",
    ], "cyan")


def cust_sign():
    section("CUST — Buat Tanda Tangan Digital")
    user = input(f"  {c('Pengirim (user):', 'cyan')} ").strip().lower()
    if not (BASE / user / "private.pem").exists():
        err("Keypair tidak ditemukan.")
        return
    if not (BASE / user / "cert.json").exists():
        err("Sertifikat belum diterbitkan CA. Selesaikan alur CA→RA terlebih dahulu.")
        return
    msg = input(f"  {c('Pesan yang akan ditandatangani:', 'cyan')} ").strip()
    spinner("Menghitung tanda tangan digital PSS-SHA256...", 1.0)
    priv = load_private_key(BASE / user / "private.pem")
    sig = priv.sign(msg.encode(), padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
    ), hashes.SHA256())
    out = {"sender": user, "message": msg, "signature": sig.hex(), "timestamp": str(datetime.datetime.now())}
    fname = BASE / user / f"signed_{int(time.time())}.json"
    fname.write_text(json.dumps(out, indent=2))
    ok("Tanda tangan digital berhasil dibuat!")
    print(f"  {c('Tersimpan:', 'dim')} {c(str(fname), 'cyan')}")
    print(f"  {c('Signature (64-char preview):', 'dim')} {c(sig.hex()[:64] + '...', 'yellow')}")


def cust_encrypt():
    section("CUST — Enkripsi Pesan Rahasia")
    sender = input(f"  {c('Pengirim:', 'cyan')} ").strip().lower()
    receiver = input(f"  {c('Penerima:', 'cyan')} ").strip().lower()
    if not (BASE / sender / "private.pem").exists():
        err(f"Private key {sender} tidak ditemukan.")
        return
    if not (BASE / receiver / "cert.json").exists():
        err(f"Sertifikat {receiver} tidak ditemukan. Sertifikasi dulu via CA.")
        return
    msg = input(f"  {c('Pesan rahasia:', 'cyan')} ").strip()
    spinner("Mengenkripsi dengan RSA-OAEP + tanda tangan digital...", 1.2)
    cert_r = json.loads((BASE / receiver / "cert.json").read_text())
    pub_r = serialization.load_pem_public_key(cert_r["public_key"].encode(), backend=default_backend())
    ciphertext = pub_r.encrypt(msg.encode(), padding.OAEP(
        mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None
    ))
    priv_s = load_private_key(BASE / sender / "private.pem")
    sig = priv_s.sign(msg.encode(), padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
    ), hashes.SHA256())
    out = {
        "from": sender, "to": receiver,
        "ciphertext": ciphertext.hex(), "signature": sig.hex(),
        "timestamp": str(datetime.datetime.now())
    }
    fname = BASE / receiver / f"msg_from_{sender}_{int(time.time())}.json"
    fname.write_text(json.dumps(out, indent=2))
    ok(f"Pesan terenkripsi dikirim ke {receiver.upper()}!")
    box_print([
        "MESSAGE ENCRYPTED & SIGNED",
        "",
        f"From      : {sender.upper()}",
        f"To        : {receiver.upper()}",
        f"Algorithm : RSA-OAEP (SHA-256)",
        f"Signature : PSS-SHA256",
        f"Ciphertext: {ciphertext.hex()[:32]}...",
    ], "green")


def cust_decrypt():
    section("CUST — Dekripsi Pesan Rahasia")
    receiver = input(f"  {c('Penerima (user kamu):', 'cyan')} ").strip().lower()
    if not (BASE / receiver / "private.pem").exists():
        err("Private key tidak ditemukan.")
        return
    msgs = list((BASE / receiver).glob("msg_from_*.json"))
    if not msgs:
        warn("Tidak ada pesan masuk.")
        return
    print(f"  {c('Pesan masuk:', 'yellow')}")
    for i, m in enumerate(msgs):
        print(f"    {c(f'[{i}]', 'green')} {c(m.name, 'white')}")
    idx = int(input(f"  {c('Pilih nomor pesan:', 'cyan')} "))
    data = json.loads(msgs[idx].read_text())
    spinner("Mendekripsi pesan dengan private key RSA-OAEP...", 1.0)
    priv_r = load_private_key(BASE / receiver / "private.pem")
    try:
        plaintext = priv_r.decrypt(bytes.fromhex(data["ciphertext"]), padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None
        ))
        ok("Dekripsi berhasil!")
        sender = data["from"]
        if (BASE / sender / "cert.json").exists():
            spinner("Memverifikasi tanda tangan digital pengirim...", 0.8)
            cert_s = json.loads((BASE / sender / "cert.json").read_text())
            pub_s = serialization.load_pem_public_key(cert_s["public_key"].encode(), backend=default_backend())
            try:
                pub_s.verify(bytes.fromhex(data["signature"]), plaintext, padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
                ), hashes.SHA256())
                ok(f"Tanda tangan {sender.upper()} VALID ✓")
            except InvalidSignature:
                err(f"Tanda tangan {sender.upper()} TIDAK VALID!")
        box_print([
            "MESSAGE DECRYPTED",
            "",
            f"From    : {data['from'].upper()}",
            f"To      : {receiver.upper()}",
            f"Plaintext: {plaintext.decode()}",
            f"Sent    : {data['timestamp']}",
        ], "green")
    except Exception as e:
        err(f"Dekripsi gagal: {e}")


def cust_verify():
    section("CUST — Verifikasi Tanda Tangan Digital")
    user = input(f"  {c('User yang memverifikasi:', 'cyan')} ").strip().lower()
    signer = input(f"  {c('User yang menandatangani (pengirim):', 'cyan')} ").strip().lower()
    if not (BASE / signer / "cert.json").exists():
        err(f"Sertifikat {signer} tidak ditemukan.")
        return
    signed_files = list((BASE / signer).glob("signed_*.json"))
    if not signed_files:
        warn("Tidak ada file bertanda tangan.")
        return
    for i, f in enumerate(signed_files):
        print(f"    {c(f'[{i}]', 'green')} {c(f.name, 'white')}")
    idx = int(input(f"  {c('Pilih file:', 'cyan')} "))
    data = json.loads(signed_files[idx].read_text())
    spinner("Memverifikasi tanda tangan...", 0.9)
    cert_s = json.loads((BASE / signer / "cert.json").read_text())
    pub_s = serialization.load_pem_public_key(cert_s["public_key"].encode(), backend=default_backend())
    ca_cert = json.loads((BASE / "ca" / "ca_cert.json").read_text())
    ca_pub = serialization.load_pem_public_key(ca_cert["public_key"].encode(), backend=default_backend())
    try:
        ca_pub.verify(bytes.fromhex(cert_s["ca_signature"]), cert_s["public_key"].encode(),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
        ok(f"Sertifikat {signer.upper()} valid (ditandatangani CA)")
    except InvalidSignature:
        err("Sertifikat tidak valid!")
        return
    try:
        pub_s.verify(bytes.fromhex(data["signature"]), data["message"].encode(),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
        ok(f"Tanda tangan {signer.upper()} VALID!")
        box_print([
            "SIGNATURE VERIFIED ✓",
            "",
            f"Pesan    : {data['message']}",
            f"Pengirim : {signer.upper()} (sertifikat CA valid)",
            f"Verifikator: {user.upper()}",
            f"Timestamp: {data['timestamp']}",
        ], "green")
    except InvalidSignature:
        err("Tanda tangan TIDAK VALID!")
        box_print(["SIGNATURE INVALID ✗", "", "Pesan mungkin telah diubah!", f"Pengirim: {signer.upper()}"], "red")


def negative_test():
    section("TEST — Negative Test: Simulasi Serangan")
    print(f"  {c('Skenario serangan yang diuji:', 'yellow', 'bold')}")
    tests = [
        "1. Verifikasi pesan yang telah dimanipulasi (man-in-the-middle)",
        "2. Dekripsi dengan private key yang salah",
        "3. Verifikasi sertifikat palsu (forged certificate)",
    ]
    for t in tests:
        print(f"    {c('·', 'red')} {c(t, 'white')}")
    print()
    choice = input(f"  {c('Pilih skenario (1/2/3):', 'cyan')} ").strip()
    if choice == "1":
        spinner("Mensimulasikan MITM attack...", 1.0)
        warn("Pesan dimanipulasi! Verifikasi tanda tangan...")
        for user in ["cust1", "cust2"]:
            if (BASE / user / "cert.json").exists():
                cert = json.loads((BASE / user / "cert.json").read_text())
                pub = serialization.load_pem_public_key(cert["public_key"].encode(), backend=default_backend())
                fake_msg = b"PESAN PALSU DARI ATTACKER"
                fake_sig = os.urandom(256)
                try:
                    pub.verify(fake_sig, fake_msg, padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
                    ), hashes.SHA256())
                    warn("Signature valid (unexpected!)")
                except InvalidSignature:
                    err(f"[ATTACK BLOCKED] Tanda tangan palsu untuk {user.upper()} ditolak sistem!")
                break
    elif choice == "2":
        spinner("Mensimulasikan wrong-key decryption...", 1.0)
        for user in ["cust1", "cust2"]:
            if (BASE / user / "cert.json").exists():
                cert = json.loads((BASE / user / "cert.json").read_text())
                pub = serialization.load_pem_public_key(cert["public_key"].encode(), backend=default_backend())
                ct = pub.encrypt(b"PESAN RAHASIA", padding.OAEP(
                    mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None
                ))
                wrong_priv = generate_rsa_keypair()
                try:
                    wrong_priv.decrypt(ct, padding.OAEP(
                        mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None
                    ))
                except Exception:
                    err(f"[ATTACK BLOCKED] Dekripsi dengan private key salah gagal untuk {user.upper()}!")
                break
    elif choice == "3":
        spinner("Mensimulasikan forged certificate...", 1.0)
        fake_priv = generate_rsa_keypair()
        fake_sig = fake_priv.sign(b"fakepubkey", padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
        ), hashes.SHA256())
        if (BASE / "ca" / "ca_cert.json").exists():
            ca_cert = json.loads((BASE / "ca" / "ca_cert.json").read_text())
            ca_pub = serialization.load_pem_public_key(ca_cert["public_key"].encode(), backend=default_backend())
            try:
                ca_pub.verify(fake_sig, b"fakepubkey", padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
                ), hashes.SHA256())
            except InvalidSignature:
                err("[ATTACK BLOCKED] Sertifikat palsu tidak diakui CA!")
    else:
        warn("Pilihan tidak valid.")


def pki_status():
    section("STATUS SISTEM PKI")
    entities = ["ca", "cust1", "cust2", "cust3"]
    for e in entities:
        d = BASE / e
        if e == "ca":
            has_priv = (d / "private.pem").exists()
            has_pub = (d / "public.pem").exists()
            has_cert = (d / "ca_cert.json").exists()
            has_csr = False
            has_approved = False
        else:
            has_priv = (d / "private.pem").exists()
            has_pub = (d / "public.pem").exists()
            has_csr = (d / "csr.json").exists()
            has_approved = (d / "csr_approved.json").exists()
            has_cert = (d / "cert.json").exists()
        label = e.upper()
        kp = c("✓", "green") if (has_priv and has_pub) else c("✗", "red")
        cs = c("✓", "green") if has_csr else c("·", "dim")
        ap = c("✓", "green") if has_approved else c("·", "dim")
        ct = c("✓", "green") if has_cert else c("·", "dim")
        print(f"  {c(label+' '*(6-len(label)), 'cyan', 'bold')} KeyPair:{kp}  CSR:{cs}  Approved:{ap}  Cert:{ct}")
    print()
    msgs = list(BASE.glob("*/msg_from_*.json"))
    signs = list(BASE.glob("*/signed_*.json"))
    info(f"Pesan terenkripsi tersimpan: {c(str(len(msgs)), 'yellow', 'bold')}")
    info(f"File bertanda tangan       : {c(str(len(signs)), 'yellow', 'bold')}")


def main():
    BASE.mkdir(parents=True, exist_ok=True)
    while True:
        menu()
        choice = input(c("  Pilih menu: ", "green", "bold")).strip().lower()
        print()
        if choice == "1":
            ca_init()
        elif choice == "2":
            ca_certify()
        elif choice == "3":
            ra_validate()
        elif choice == "4":
            cust_register()
        elif choice == "5":
            cust_sign()
        elif choice == "6":
            cust_encrypt()
        elif choice == "7":
            cust_decrypt()
        elif choice == "8":
            cust_verify()
        elif choice == "9":
            negative_test()
        elif choice == "0":
            pki_status()
        elif choice == "q":
            typewriter("  Keluar dari sistem PKI. Sampai jumpa!", 0.015, "cyan")
            print()
            break
        else:
            warn("Pilihan tidak valid.")
        input(f"\n  {c('Tekan Enter untuk kembali ke menu...', 'dim')}")


if __name__ == "__main__":
    main()

import os
import sys
import json
import base64
import hashlib
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature

DIRS = ["data/ca", "data/ra", "data/cust", "data/certs", "data/messages"]
for d in DIRS:
    os.makedirs(d, exist_ok=True)


def _load_private(path):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

def _load_public(path):
    with open(path, "rb") as f:
        return serialization.load_pem_public_key(f.read(), backend=default_backend())

def _save_private(key, path):
    with open(path, "wb") as f:
        f.write(key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption()
        ))

def _save_public(key, path):
    with open(path, "wb") as f:
        f.write(key.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo
        ))

def _gen_keypair():
    priv = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    return priv, priv.public_key()

def _sign(private_key, data: bytes) -> bytes:
    return private_key.sign(
        data,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )

def _verify_sig(public_key, sig: bytes, data: bytes) -> bool:
    try:
        public_key.verify(
            sig,
            data,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False

def _encrypt(public_key, plaintext: bytes) -> bytes:
    return public_key.encrypt(
        plaintext,
        padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )

def _decrypt(private_key, ciphertext: bytes) -> bytes:
    return private_key.decrypt(
        ciphertext,
        padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )


def menu_1_ca_setup():
    print("\n[MENU 1] CA — Inisialisasi Key Pair")
    if os.path.exists("data/ca/ca_private.pem"):
        print("[CA] Key pair sudah ada. Skip.")
        return
    priv, pub = _gen_keypair()
    _save_private(priv, "data/ca/ca_private.pem")
    _save_public(pub, "data/ca/ca_public.pem")
    print("[CA] Key pair RSA-2048 berhasil dibuat.")
    print("     Private key : data/ca/ca_private.pem  (RAHASIA)")
    print("     Public key  : data/ca/ca_public.pem   (Publik — root of trust)")


def menu_2_ca_issue():
    print("\n[MENU 2] CA — Terbitkan Sertifikat")
    if not os.path.exists("data/ca/ca_private.pem"):
        print("[CA] ERROR: Jalankan Menu 1 dulu.")
        return

    approved = [
        f.replace("_request.json", "")
        for f in os.listdir("data/ra")
        if f.endswith("_request.json")
        and json.load(open(f"data/ra/{f}")).get("status") == "APPROVED"
        and not os.path.exists(f"data/certs/{f.replace('_request.json', '')}_cert.json")
    ]

    if not approved:
        print("[CA] Tidak ada request APPROVED yang belum disertifikasi.")
        return

    print("[CA] Request APPROVED tersedia:")
    for i, name in enumerate(approved, 1):
        print(f"     {i}. {name}")

    try:
        idx = int(input("Pilih nomor: ")) - 1
        username = approved[idx]
    except (ValueError, IndexError):
        print("[CA] Pilihan tidak valid.")
        return

    req = json.load(open(f"data/ra/{username}_request.json"))
    ca_priv = _load_private("data/ca/ca_private.pem")

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

    print(f"[CA] Sertifikat untuk '{username}' berhasil diterbitkan.")
    print(f"     File: data/certs/{username}_cert.json")
    print(f"     Serial   : {payload['serial']}")
    print(f"     Issuer   : {payload['issuer']}")
    print(f"     Valid s/d: {payload['valid_until']}")


def menu_3_ra_validate():
    print("\n[MENU 3] RA — Validasi Request Cust")

    pending = [
        f.replace("_request.json", "")
        for f in os.listdir("data/ra")
        if f.endswith("_request.json")
        and json.load(open(f"data/ra/{f}")).get("status") == "PENDING"
    ]

    if not pending:
        print("[RA] Tidak ada request PENDING.")
        return

    print("[RA] Request PENDING:")
    for i, name in enumerate(pending, 1):
        print(f"     {i}. {name}")

    try:
        idx = int(input("Pilih nomor: ")) - 1
        username = pending[idx]
    except (ValueError, IndexError):
        print("[RA] Pilihan tidak valid.")
        return

    req = json.load(open(f"data/ra/{username}_request.json"))
    print(f"\n[RA] Detail pemohon:")
    print(f"     Nama         : {req['name']}")
    print(f"     Email        : {req['email']}")
    print(f"     Organisasi   : {req['org']}")
    print(f"     Timestamp    : {req['timestamp']}")
    print(f"     Public Key   : (ada, {len(req['public_key'])} karakter)")

    decision = input("\n[RA] Setujui request ini? (y/n): ").strip().lower()
    req["status"] = "APPROVED" if decision == "y" else "REJECTED"
    req["ra_reviewed_at"] = datetime.utcnow().isoformat()

    with open(f"data/ra/{username}_request.json", "w") as f:
        json.dump(req, f, indent=2)

    status_label = "DISETUJUI ✓" if decision == "y" else "DITOLAK ✗"
    print(f"[RA] Request '{username}' {status_label}")


def menu_4_cust_register():
    print("\n[MENU 4] CUST — Daftar & Buat Key Pair")
    username = input("Masukkan nama (contoh: yoga): ").strip().lower()
    name = input("Nama lengkap: ").strip()
    email = input("Email: ").strip()
    org = input("Organisasi: ").strip()

    if os.path.exists(f"data/cust/{username}_private.pem"):
        print(f"[CUST] Key pair untuk '{username}' sudah ada. Skip keygen.")
    else:
        priv, pub = _gen_keypair()
        _save_private(priv, f"data/cust/{username}_private.pem")
        _save_public(pub, f"data/cust/{username}_public.pem")
        print(f"[CUST] Key pair RSA-2048 untuk '{username}' dibuat.")

    pub_pem = open(f"data/cust/{username}_public.pem").read()

    request = {
        "username": username,
        "name": name,
        "email": email,
        "org": org,
        "public_key": pub_pem,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "PENDING"
    }
    with open(f"data/ra/{username}_request.json", "w") as f:
        json.dump(request, f, indent=2)

    print(f"[CUST] Request dikirim ke RA.")
    print(f"       Private key HANYA ada di: data/cust/{username}_private.pem")
    print(f"       Public key dikirim ke RA bersama data identitas.")


def menu_5_sign_message():
    print("\n[MENU 5] CUST — Tanda Tangan Digital Pesan")
    username = input("Nama pengirim: ").strip().lower()

    if not os.path.exists(f"data/certs/{username}_cert.json"):
        print(f"[CUST] ERROR: Sertifikat '{username}' belum ada. Minta CA terbitkan dulu.")
        return

    message = input("Isi pesan: ").strip()
    priv = _load_private(f"data/cust/{username}_private.pem")
    msg_bytes = message.encode()
    sig = _sign(priv, msg_bytes)

    out = {
        "from": username,
        "to": "public",
        "message": message,
        "signature": base64.b64encode(sig).decode(),
        "timestamp": datetime.utcnow().isoformat()
    }
    out_path = f"data/messages/{username}_signed.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)

    print(f"[CUST] Pesan berhasil ditandatangani.")
    print(f"       File: {out_path}")
    print(f"       Signature: {base64.b64encode(sig).decode()[:40]}...")


def menu_6_encrypt_message():
    print("\n[MENU 6] CUST — Enkripsi Pesan Rahasia")
    sender = input("Nama pengirim: ").strip().lower()
    receiver = input("Nama penerima: ").strip().lower()

    if not os.path.exists(f"data/certs/{sender}_cert.json"):
        print(f"[CUST] ERROR: Sertifikat '{sender}' belum ada.")
        return
    if not os.path.exists(f"data/certs/{receiver}_cert.json"):
        print(f"[CUST] ERROR: Sertifikat '{receiver}' belum ada.")
        return

    message = input("Isi pesan rahasia: ").strip()
    msg_bytes = message.encode()

    recv_cert = json.load(open(f"data/certs/{receiver}_cert.json"))
    recv_pub = serialization.load_pem_public_key(recv_cert["payload"]["public_key"].encode(), backend=default_backend())

    sender_priv = _load_private(f"data/cust/{sender}_private.pem")
    sig = _sign(sender_priv, msg_bytes)
    ciphertext = _encrypt(recv_pub, msg_bytes)

    out = {
        "from": sender,
        "to": receiver,
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "signature": base64.b64encode(sig).decode(),
        "timestamp": datetime.utcnow().isoformat()
    }
    out_path = f"data/messages/{receiver}_encrypted.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)

    print(f"[CUST] Pesan terenkripsi + ditandatangani oleh '{sender}'.")
    print(f"       Ciphertext (preview): {base64.b64encode(ciphertext).decode()[:40]}...")
    print(f"       Hanya '{receiver}' yang bisa membuka ini.")
    print(f"       File: {out_path}")


def menu_7_decrypt_message():
    print("\n[MENU 7] CUST — Dekripsi Pesan Rahasia")
    username = input("Nama penerima: ").strip().lower()

    env_path = f"data/messages/{username}_encrypted.json"
    if not os.path.exists(env_path):
        print(f"[CUST] ERROR: Tidak ada pesan terenkripsi untuk '{username}'.")
        return

    env = json.load(open(env_path))
    priv = _load_private(f"data/cust/{username}_private.pem")

    try:
        plaintext = _decrypt(priv, base64.b64decode(env["ciphertext"]))
    except Exception as e:
        print(f"[CUST] GAGAL dekripsi: {e}")
        return

    sender = env["from"]
    sender_cert = json.load(open(f"data/certs/{sender}_cert.json"))
    sender_pub = serialization.load_pem_public_key(sender_cert["payload"]["public_key"].encode(), backend=default_backend())
    sig_valid = _verify_sig(sender_pub, base64.b64decode(env["signature"]), plaintext)

    print(f"[CUST] Dekripsi BERHASIL ✓")
    print(f"       Dari           : {sender}")
    print(f"       Isi pesan      : '{plaintext.decode()}'")
    print(f"       Tanda tangan   : {'VALID ✓' if sig_valid else 'TIDAK VALID ✗'}")


def menu_8_verify_signed():
    print("\n[MENU 8] CUST — Verifikasi Tanda Tangan Digital")

    signed_files = [f for f in os.listdir("data/messages") if f.endswith("_signed.json")]
    if not signed_files:
        print("[CUST] Tidak ada pesan bertanda tangan.")
        return

    print("[CUST] Pesan tersedia:")
    for i, fname in enumerate(signed_files, 1):
        print(f"       {i}. {fname}")

    try:
        idx = int(input("Pilih nomor: ")) - 1
        fname = signed_files[idx]
    except (ValueError, IndexError):
        print("[CUST] Pilihan tidak valid.")
        return

    msg_data = json.load(open(f"data/messages/{fname}"))
    sender = msg_data["from"]

    if not os.path.exists(f"data/certs/{sender}_cert.json"):
        print(f"[CUST] ERROR: Sertifikat '{sender}' tidak ditemukan.")
        return

    ca_pub = _load_public("data/ca/ca_public.pem")
    cert = json.load(open(f"data/certs/{sender}_cert.json"))
    payload_hash = hashlib.sha256(json.dumps(cert["payload"], sort_keys=True).encode()).hexdigest()
    cert_valid = _verify_sig(ca_pub, bytes.fromhex(cert["ca_signature"]), payload_hash.encode())

    sender_pub = serialization.load_pem_public_key(cert["payload"]["public_key"].encode(), backend=default_backend())
    sig_valid = _verify_sig(sender_pub, base64.b64decode(msg_data["signature"]), msg_data["message"].encode())

    print(f"\n[CUST] Hasil Verifikasi:")
    print(f"       Sertifikat CA  : {'VALID ✓' if cert_valid else 'TIDAK VALID ✗'}")
    print(f"       Tanda Tangan   : {'VALID ✓' if sig_valid else 'TIDAK VALID ✗'}")
    print(f"       Isi pesan      : '{msg_data['message']}'")
    print(f"       Dari           : {cert['payload']['name']} ({cert['payload']['email']})")
    print(f"       Organisasi     : {cert['payload']['org']}")
    if cert_valid and sig_valid:
        print(f"       [✓] Pesan ASLI dan benar-benar dari '{sender}'!")
    else:
        print(f"       [✗] Verifikasi GAGAL — pesan mungkin dipalsukan!")


def menu_9_negative_test():
    print("\n[MENU 9] NEGATIVE TEST — Simulasi Serangan")
    print("       1. Sertifikat Palsu (forge CA signature)")
    print("       2. Pesan Dimanipulasi (tamper signed message)")
    print("       3. Private Key Salah (wrong key decrypt)")

    choice = input("Pilih skenario (1/2/3): ").strip()

    if choice == "1":
        print("\n[TEST 1] Attacker membuat sertifikat palsu...")
        fake_cert = {
            "payload": {
                "serial": "FAKE-999",
                "subject": "attacker",
                "name": "Evil Attacker",
                "email": "evil@hack.com",
                "org": "Hackers Inc",
                "public_key": "FAKE_KEY",
                "issuer": "CA-PKI-UAS",
                "issued_at": datetime.utcnow().isoformat(),
                "valid_until": (datetime.utcnow() + timedelta(days=365)).isoformat()
            },
            "payload_hash": "fakehash",
            "ca_signature": "deadbeef"
        }
        ca_pub = _load_public("data/ca/ca_public.pem")
        try:
            payload_hash = hashlib.sha256(json.dumps(fake_cert["payload"], sort_keys=True).encode()).hexdigest()
            ca_pub.verify(
                bytes.fromhex(fake_cert["ca_signature"]),
                payload_hash.encode(),
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256()
            )
            print("       [✗] BUG: Sertifikat palsu diterima! Ada masalah.")
        except Exception:
            print("       [✗] Sertifikat PALSU berhasil DITOLAK")
            print("       [✓] Trust chain bekerja dengan benar!")

    elif choice == "2":
        signed_files = [f for f in os.listdir("data/messages") if f.endswith("_signed.json")]
        if not signed_files:
            print("       [!] Belum ada pesan bertanda tangan. Jalankan Menu 5 dulu.")
            return
        msg_data = json.load(open(f"data/messages/{signed_files[0]}"))
        original = msg_data["message"]
        tampered = msg_data.copy()
        tampered["message"] = original + " [DIMANIPULASI ATTACKER]"

        sender = msg_data["from"]
        cert = json.load(open(f"data/certs/{sender}_cert.json"))
        sender_pub = serialization.load_pem_public_key(cert["payload"]["public_key"].encode(), backend=default_backend())
        sig_valid = _verify_sig(sender_pub, base64.b64decode(tampered["signature"]), tampered["message"].encode())

        print(f"\n[TEST 2] Pesan asli    : '{original}'")
        print(f"         Pesan diubah  : '{tampered['message']}'")
        print(f"         Tanda tangan  : {'VALID' if sig_valid else '[✗] TIDAK VALID — pesan telah dimanipulasi'}")
        if not sig_valid:
            print("         [✓] Integritas pesan terlindungi!")

    elif choice == "3":
        encrypted_files = [f for f in os.listdir("data/messages") if f.endswith("_encrypted.json")]
        if not encrypted_files:
            print("       [!] Belum ada pesan terenkripsi. Jalankan Menu 6 dulu.")
            return
        env = json.load(open(f"data/messages/{encrypted_files[0]}"))
        wrong_priv, _ = _gen_keypair()
        try:
            _decrypt(wrong_priv, base64.b64decode(env["ciphertext"]))
            print("       [✗] BUG: Berhasil dekripsi dengan key salah!")
        except Exception:
            print("\n[TEST 3] Attacker coba dekripsi dengan private key berbeda...")
            print("         [✗] Dekripsi GAGAL — private key salah")
            print("         [✓] Kerahasiaan pesan terjaga!")
    else:
        print("[TEST] Pilihan tidak valid.")


def menu_0_status():
    print("\n[MENU 0] STATUS SISTEM PKI")
    print("=" * 50)

    print("\n[CA]")
    ca_exists = os.path.exists("data/ca/ca_private.pem")
    print(f"  Key Pair CA : {'Ada ✓' if ca_exists else 'Belum dibuat ✗'}")

    print("\n[RA — Requests]")
    ra_files = [f for f in os.listdir("data/ra") if f.endswith("_request.json")]
    if not ra_files:
        print("  (kosong)")
    for f in ra_files:
        req = json.load(open(f"data/ra/{f}"))
        print(f"  {req['username']:15} | {req['status']}")

    print("\n[Sertifikat Diterbitkan]")
    cert_files = [f for f in os.listdir("data/certs") if f.endswith("_cert.json")]
    if not cert_files:
        print("  (kosong)")
    for f in cert_files:
        cert = json.load(open(f"data/certs/{f}"))
        print(f"  {cert['payload']['subject']:15} | Serial: {cert['payload']['serial'][:8]}... | Valid s/d: {cert['payload']['valid_until'][:10]}")

    print("\n[Pesan]")
    msg_files = os.listdir("data/messages")
    if not msg_files:
        print("  (kosong)")
    for f in msg_files:
        msg = json.load(open(f"data/messages/{f}"))
        tipe = "SIGNED" if "_signed" in f else "ENCRYPTED"
        print(f"  {f:35} | {tipe} | dari: {msg.get('from', '-')} → {msg.get('to', '-')}")

    print("\n" + "=" * 50)


def main():
    MENU = {
        "1": ("CA   — Inisialisasi Key Pair CA", menu_1_ca_setup),
        "2": ("CA   — Terbitkan Sertifikat", menu_2_ca_issue),
        "3": ("RA   — Validasi Request Cust", menu_3_ra_validate),
        "4": ("CUST — Daftar & Buat Key Pair", menu_4_cust_register),
        "5": ("CUST — Tanda Tangan Digital", menu_5_sign_message),
        "6": ("CUST — Enkripsi Pesan Rahasia", menu_6_encrypt_message),
        "7": ("CUST — Dekripsi Pesan Rahasia", menu_7_decrypt_message),
        "8": ("CUST — Verifikasi Tanda Tangan", menu_8_verify_signed),
        "9": ("TEST — Negative Test (Simulasi Serangan)", menu_9_negative_test),
        "0": ("INFO — Status Sistem PKI", menu_0_status),
    }

    while True:
        print("\n" + "=" * 50)
        print(" SISTEM PKI — UAS Kriptografi Semester 4")
        print("=" * 50)
        for k, (label, _) in MENU.items():
            print(f"  [{k}] {label}")
        print("  [q] Keluar")
        print("=" * 50)

        choice = input("Pilih menu: ").strip().lower()
        if choice == "q":
            print("Terima kasih. Sampai jumpa!")
            break
        elif choice in MENU:
            MENU[choice][1]()
        else:
            print("[!] Menu tidak ditemukan.")


if __name__ == "__main__":
    main()

import sys
import os
import json
import base64
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature

KEYS_DIR = "keys"
CERTS_DIR = "certs"
MSG_DIR = "messages"
USERNAME = "cust2"

os.makedirs(MSG_DIR, exist_ok=True)

def keygen():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    with open(f"{KEYS_DIR}/{USERNAME}_private.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    pub_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

    with open(f"{KEYS_DIR}/{USERNAME}_public.pem", "w") as f:
        f.write(pub_pem)

    csr = {
        "username": USERNAME,
        "name": "Cust2 User",
        "email": "cust2@example.com",
        "public_key": pub_pem,
        "timestamp": datetime.utcnow().isoformat(),
        "ra_approved": False
    }
    with open(f"{KEYS_DIR}/{USERNAME}_csr.json", "w") as f:
        json.dump(csr, f, indent=2)

    print(f"[{USERNAME.upper()}] Keypair berhasil dibuat.")
    print(f"[{USERNAME.upper()}] CSR dikirim ke RA: {KEYS_DIR}/{USERNAME}_csr.json")

def announce():
    cert_path = f"{CERTS_DIR}/{USERNAME}_cert.json"
    if not os.path.exists(cert_path):
        print(f"[{USERNAME.upper()}] ERROR: Sertifikat belum ada.")
        sys.exit(1)

    with open(f"{KEYS_DIR}/{USERNAME}_private.pem", "rb") as f:
        my_private = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

    announcement = "PENGUMUMAN dari Cust2: Sistem PKI kelompok kami telah berjalan dengan sukses! Semua user (Cust1 dan Cust3) dapat membaca pesan ini dan memverifikasi tanda tangan digital saya."
    msg_bytes = announcement.encode()

    signature = my_private.sign(
        msg_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    out = {
        "from": USERNAME,
        "to": "public",
        "message": announcement,
        "signature": base64.b64encode(signature).decode(),
        "timestamp": datetime.utcnow().isoformat()
    }

    out_path = f"{MSG_DIR}/cust2_announcement.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)

    print(f"[{USERNAME.upper()}] Pengumuman publik + tanda tangan digital dibuat.")
    print(f"[{USERNAME.upper()}] File: {out_path}")
    print(f"[{USERNAME.upper()}] Isi: '{announcement}'")

def receive():
    envelope_path = f"{MSG_DIR}/cust1_to_cust2.json"
    if not os.path.exists(envelope_path):
        print(f"[{USERNAME.upper()}] ERROR: Pesan dari Cust1 belum ada.")
        sys.exit(1)

    with open(envelope_path, "r") as f:
        envelope = json.load(f)

    with open(f"{KEYS_DIR}/{USERNAME}_private.pem", "rb") as f:
        my_private = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

    ciphertext = base64.b64decode(envelope["ciphertext"])
    plaintext = my_private.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    with open(f"{KEYS_DIR}/cust1_public.pem", "rb") as f:
        cust1_public = serialization.load_pem_public_key(f.read(), backend=default_backend())

    sig = base64.b64decode(envelope["signature"])
    try:
        cust1_public.verify(
            sig,
            plaintext,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        verified = True
    except InvalidSignature:
        verified = False

    print(f"[{USERNAME.upper()}] Pesan dari Cust1 berhasil didekripsi.")
    print(f"[{USERNAME.upper()}] Isi pesan  : '{plaintext.decode()}'")
    print(f"[{USERNAME.upper()}] Tanda tangan Cust1: {'VALID ✓' if verified else 'TIDAK VALID ✗'}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python cust2.py [keygen|announce|receive]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "keygen":
        keygen()
    elif cmd == "announce":
        announce()
    elif cmd == "receive":
        receive()
    else:
        print("Usage: python cust2.py [keygen|announce|receive]")

if __name__ == "__main__":
    main()

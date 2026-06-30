import sys
import os
import json
import base64
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend

KEYS_DIR = "keys"
CERTS_DIR = "certs"
MSG_DIR = "messages"
USERNAME = "cust1"

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
        "name": "Cust1 User",
        "email": "cust1@example.com",
        "public_key": pub_pem,
        "timestamp": datetime.utcnow().isoformat(),
        "ra_approved": False
    }
    with open(f"{KEYS_DIR}/{USERNAME}_csr.json", "w") as f:
        json.dump(csr, f, indent=2)

    print(f"[{USERNAME.upper()}] Keypair berhasil dibuat.")
    print(f"[{USERNAME.upper()}] CSR dikirim ke RA: {KEYS_DIR}/{USERNAME}_csr.json")

def send():
    cert_path = f"{CERTS_DIR}/{USERNAME}_cert.json"
    if not os.path.exists(cert_path):
        print(f"[{USERNAME.upper()}] ERROR: Sertifikat belum ada. Minta CA untuk mensertifikasi dulu.")
        sys.exit(1)

    with open(f"{KEYS_DIR}/{USERNAME}_private.pem", "rb") as f:
        my_private = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

    with open(f"{KEYS_DIR}/cust2_public.pem", "rb") as f:
        cust2_public = serialization.load_pem_public_key(f.read(), backend=default_backend())

    message = "Halo Cust2! Ini pesan rahasia dari Cust1. Semoga PKI kita bekerja dengan baik!"
    message_bytes = message.encode()

    signature = my_private.sign(
        message_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    ciphertext = cust2_public.encrypt(
        message_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    envelope = {
        "from": USERNAME,
        "to": "cust2",
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "signature": base64.b64encode(signature).decode(),
        "timestamp": datetime.utcnow().isoformat()
    }

    out_path = f"{MSG_DIR}/cust1_to_cust2.json"
    with open(out_path, "w") as f:
        json.dump(envelope, f, indent=2)

    print(f"[{USERNAME.upper()}] Pesan rahasia terenkripsi + tanda tangan digital dikirim ke Cust2.")
    print(f"[{USERNAME.upper()}] File: {out_path}")
    print(f"[{USERNAME.upper()}] Pesan asli: '{message}'")

def main():
    if len(sys.argv) < 2:
        print("Usage: python cust1.py [keygen|send]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "keygen":
        keygen()
    elif cmd == "send":
        send()
    else:
        print("Usage: python cust1.py [keygen|send]")

if __name__ == "__main__":
    main()

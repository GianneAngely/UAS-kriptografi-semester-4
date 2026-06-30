import sys
import os
import json
import hashlib
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend

KEYS_DIR = "keys"
CERTS_DIR = "certs"

os.makedirs(KEYS_DIR, exist_ok=True)
os.makedirs(CERTS_DIR, exist_ok=True)

def setup():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    with open(f"{KEYS_DIR}/ca_private.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open(f"{KEYS_DIR}/ca_public.pem", "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    print("[CA] Keypair berhasil dibuat.")
    print(f"[CA] Private key: {KEYS_DIR}/ca_private.pem  (RAHASIA - jangan dibagikan)")
    print(f"[CA] Public key : {KEYS_DIR}/ca_public.pem   (Publik - bisa diakses siapa saja)")

def certify(username):
    csr_path = f"{KEYS_DIR}/{username}_csr.json"
    if not os.path.exists(csr_path):
        print(f"[CA] ERROR: CSR untuk {username} tidak ditemukan. Pastikan RA sudah memvalidasi.")
        sys.exit(1)

    with open(csr_path, "r") as f:
        csr_data = json.load(f)

    if not csr_data.get("ra_approved"):
        print(f"[CA] ERROR: CSR {username} belum disetujui RA.")
        sys.exit(1)

    with open(f"{KEYS_DIR}/ca_private.pem", "rb") as f:
        ca_private = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

    cert_payload = {
        "subject": username,
        "public_key": csr_data["public_key"],
        "issued_by": "CA",
        "issued_at": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=365)).isoformat()
    }

    payload_bytes = json.dumps(cert_payload, sort_keys=True).encode()
    payload_hash = hashlib.sha256(payload_bytes).hexdigest()

    signature = ca_private.sign(
        payload_hash.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    cert = {
        "payload": cert_payload,
        "payload_hash": payload_hash,
        "ca_signature": signature.hex()
    }

    cert_path = f"{CERTS_DIR}/{username}_cert.json"
    with open(cert_path, "w") as f:
        json.dump(cert, f, indent=2)

    print(f"[CA] Sertifikat untuk {username} berhasil diterbitkan.")
    print(f"[CA] Sertifikat disimpan di: {cert_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python ca.py [setup|certify <username>]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "setup":
        setup()
    elif cmd == "certify" and len(sys.argv) == 3:
        certify(sys.argv[2])
    else:
        print("Usage: python ca.py [setup|certify <username>]")

if __name__ == "__main__":
    main()

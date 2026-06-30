import sys
import os
import json
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature

KEYS_DIR = "keys"
CERTS_DIR = "certs"
MSG_DIR = "messages"
USERNAME = "cust3"

def verify():
    ann_path = f"{MSG_DIR}/cust2_announcement.json"
    if not os.path.exists(ann_path):
        print(f"[{USERNAME.upper()}] ERROR: Pengumuman Cust2 belum ada.")
        sys.exit(1)

    with open(ann_path, "r") as f:
        ann = json.load(f)

    cert_path = f"{CERTS_DIR}/cust2_cert.json"
    if not os.path.exists(cert_path):
        print(f"[{USERNAME.upper()}] ERROR: Sertifikat Cust2 tidak ditemukan di repository.")
        sys.exit(1)

    with open(cert_path, "r") as f:
        cert = json.load(f)

    with open(f"{KEYS_DIR}/ca_public.pem", "rb") as f:
        ca_public = serialization.load_pem_public_key(f.read(), backend=default_backend())

    import hashlib
    payload_bytes = json.dumps(cert["payload"], sort_keys=True).encode()
    payload_hash = hashlib.sha256(payload_bytes).hexdigest()

    try:
        ca_public.verify(
            bytes.fromhex(cert["ca_signature"]),
            payload_hash.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        cert_valid = True
    except InvalidSignature:
        cert_valid = False

    cust2_pub_pem = cert["payload"]["public_key"].encode()
    cust2_public = serialization.load_pem_public_key(cust2_pub_pem, backend=default_backend())

    sig = base64.b64decode(ann["signature"])
    msg_bytes = ann["message"].encode()

    try:
        cust2_public.verify(
            sig,
            msg_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        sig_valid = True
    except InvalidSignature:
        sig_valid = False

    print(f"[{USERNAME.upper()}] Pengumuman publik dari Cust2 diterima.")
    print(f"[{USERNAME.upper()}] Isi pesan       : '{ann['message']}'")
    print(f"[{USERNAME.upper()}] Sertifikat CA   : {'VALID ✓' if cert_valid else 'TIDAK VALID ✗'}")
    print(f"[{USERNAME.upper()}] Tanda tangan    : {'VALID ✓' if sig_valid else 'TIDAK VALID ✗'}")
    if cert_valid and sig_valid:
        print(f"[{USERNAME.upper()}] ✓ Pesan benar-benar dari Cust2 yang sudah tersertifikasi CA!")
    else:
        print(f"[{USERNAME.upper()}] ✗ Verifikasi GAGAL — pesan mungkin dimanipulasi!")

def main():
    if len(sys.argv) < 2 or sys.argv[1] != "verify":
        print("Usage: python cust3.py verify")
        sys.exit(1)
    verify()

if __name__ == "__main__":
    main()

import sys
import os
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

KEYS_DIR = "keys"

def validate(username):
    csr_path = f"{KEYS_DIR}/{username}_csr.json"
    if not os.path.exists(csr_path):
        print(f"[RA] ERROR: CSR untuk {username} tidak ditemukan.")
        print(f"[RA] Pastikan {username} sudah menjalankan keygen terlebih dahulu.")
        sys.exit(1)

    with open(csr_path, "r") as f:
        csr_data = json.load(f)

    print(f"[RA] Memeriksa CSR dari: {username}")
    print(f"[RA] Nama       : {csr_data.get('name', '-')}")
    print(f"[RA] Email      : {csr_data.get('email', '-')}")
    print(f"[RA] Timestamp  : {csr_data.get('timestamp', '-')}")
    print(f"[RA] Public Key : (ada, {len(csr_data.get('public_key', ''))} karakter)")

    confirm = input(f"[RA] Setujui dan teruskan ke CA? (y/n): ").strip().lower()
    if confirm != "y":
        print(f"[RA] Permohonan {username} DITOLAK.")
        sys.exit(0)

    csr_data["ra_approved"] = True
    csr_data["ra_approved_at"] = __import__('datetime').datetime.utcnow().isoformat()

    with open(csr_path, "w") as f:
        json.dump(csr_data, f, indent=2)

    print(f"[RA] Data {username} telah DIVALIDASI dan diteruskan ke CA.")

def main():
    if len(sys.argv) != 3 or sys.argv[1] != "validate":
        print("Usage: python ra.py validate <username>")
        sys.exit(1)
    validate(sys.argv[2])

if __name__ == "__main__":
    main()

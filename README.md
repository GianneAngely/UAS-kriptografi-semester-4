# UAS Kriptografi Semester 4 — Public Key Infrastructure (PKI) Simulation

## Struktur Role

| Role | File | Deskripsi |
|------|------|----------|
| CA (Certificate Authority) | `ca.py` | Membuat pasangan kunci, mensertifikasi kunci publik User |
| RA (Registration Authority) | `ra.py` | Memvalidasi dan menyetujui data User sebelum dikirim ke CA |
| Cust1 | `cust1.py` | Membuat pesan rahasia terenkripsi + tanda tangan digital untuk Cust2 |
| Cust2 | `cust2.py` | Membuat pengumuman publik + membuka pesan dari Cust1 |
| Cust3 | `cust3.py` | Memverifikasi pengumuman publik dari Cust2 |

## Alur PKI

```
Cust1/Cust2 → (kirim public key) → RA → (validasi) → CA → (sertifikasi) → Repository Publik
```

## Cara Menjalankan (Arch Linux / Terminal)

### 1. Install dependencies
```bash
pip install cryptography
```

### 2. Jalankan sesuai urutan alur PKI

```bash
# Step 1: CA setup — buat keypair CA & simpan ke keys/
python ca.py setup

# Step 2: Cust1 & Cust2 buat keypair dan kirim CSR ke RA
python cust1.py keygen
python cust2.py keygen

# Step 3: RA validasi dan teruskan ke CA
python ra.py validate cust1
python ra.py validate cust2

# Step 4: CA sertifikasi
python ca.py certify cust1
python ca.py certify cust2

# Step 5: Cust1 kirim pesan rahasia ke Cust2
python cust1.py send

# Step 6: Cust2 buat pengumuman publik
python cust2.py announce

# Step 7: Cust2 buka pesan dari Cust1
python cust2.py receive

# Step 8: Cust3 verifikasi pengumuman Cust2
python cust3.py verify
```

## Direktori Output

```
keys/           — kunci publik & privat semua user
certs/          — sertifikat digital yang diterbitkan CA
messages/       — pesan terenkripsi & pengumuman
```

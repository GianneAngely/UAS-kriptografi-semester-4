# UAS Kriptografi Semester 4 — Public Key Infrastructure (PKI) Simulation

## Cara Clone & Jalankan (dari Nol)

```bash
git clone https://github.com/GianneAngely/UAS-kriptografi-semester-4.git
cd UAS-kriptografi-semester-4
pip install -r requirements.txt
python app.py
```

## Pembagian Role

| Orang | Role | Menu yang Dijalankan |
|-------|------|---------------------|
| Angel | CA + RA | 1 → 3 → 3 → 2 → 2 → 0 |
| Yoga  | Cust A (Pengirim) | 4 → 5 → 6 |
| Agus  | Cust B (Penerima + Verifier) | 4 → 8 → 7 → 9 |

## Reset Data (sebelum demo)

```bash
rm -rf data/
python app.py
```

## Alur Menu

```
[1] CA setup keypair
[2] CA terbitkan sertifikat
[3] RA validasi request
[4] Cust daftar & buat keypair
[5] Cust tanda tangan pesan
[6] Cust enkripsi pesan rahasia
[7] Cust dekripsi pesan
[8] Cust verifikasi tanda tangan
[9] Negative test (simulasi serangan)
[0] Status sistem
```

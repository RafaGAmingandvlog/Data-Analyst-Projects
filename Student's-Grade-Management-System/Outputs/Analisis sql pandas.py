import sqlite3
import pandas as pd

conn = sqlite3.connect(r"C:\Users\R4Fa\Python Projects\Data Analyst Journey\SQL\latihan.db")

cursor = conn.cursor()

# Buat ulang tabel
cursor.execute("""
CREATE TABLE IF NOT EXISTS siswa (
    id INTEGER PRIMARY KEY,
    nama TEXT,
    kelas TEXT,
    nilai INTEGER
)
""")

# Hapus isi lama supaya tidak double
cursor.execute("DELETE FROM siswa")

# Insert data
cursor.executemany("""
INSERT INTO siswa (nama, kelas, nilai) VALUES (?, ?, ?)
""", [
    ("Andi", "A", 85),
    ("Budi", "B", 90),
    ("Citra", "A", 88)
])

conn.commit()

# Sekarang baca dengan pandas
df = pd.read_sql_query("SELECT * FROM siswa", conn)

# Tutup koneksi ke database
conn.close()

# Tampilkan DataFrame
print("Data siswa dari database:")
print(df)

# Analisis sederhana menggunakan pandas
print("Rata-rata nilai siswa: ")
print(df['nilai'].mean())

print("Nilai tertinggi siswa: ")
print(df['nilai'].max())

print('Rata rata nilai siswa berdasarkan kelas:')
print(df.groupby('kelas')['nilai'].mean())
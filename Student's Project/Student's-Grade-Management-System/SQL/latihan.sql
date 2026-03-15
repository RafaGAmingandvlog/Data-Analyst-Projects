DROP TABLE IF EXISTS siswa;

CREATE TABLE siswa (
    id INTEGER PRIMARY KEY,
    nama TEXT,
    kelas TEXT,
    nilai INTEGER
);

INSERT INTO siswa (nama, kelas, nilai) VALUES
('Andi', 'A', 85),
('Budi', 'B', 90),
('Citra', 'A', 88);

SELECT * FROM siswa
WHERE nilai > 85
ORDER BY nilai DESC;
SELECT kelas, AVG(nilai) AS rata_rata
FROM siswa
GROUP BY kelas
ORDER BY rata_rata DESC;

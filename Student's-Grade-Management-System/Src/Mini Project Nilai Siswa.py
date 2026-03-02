"""
Mini Project: Nilai Siswa - Fixed Version
Sistem Manajemen Nilai Siswa dengan Analisis Data Lengkap
"""

# =============================================================================
# 1. IMPORT LIBRARY
# =============================================================================

import time
import csv
import json
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Union, Tuple, Any
from language import Translator  # Import Translator dari file language.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Konfigurasi matplotlib
plt.rcParams['font.family'] = 'DejaVu Sans'

# =============================================================================
# 2. KONFIGURASI DAN CONSTANT
# =============================================================================

DB_FILE = 'students.db'
CSV_FILE = 'student_scores.csv'
EXCEL_FILE = 'student_scores.xlsx'
JSON_FILE = 'students.json'

# Grade boundaries sesuai standar Indonesia
GRADE_BOUNDARIES = {
    'A': (85, 100, 'Istimewa'),
    'B': (70, 84, 'Baik'),
    'C': (55, 69, 'Cukup'),
    'D': (40, 54, 'Kurang'),
    'E': (0, 39, 'Gagal')
}

# =============================================================================
# 3. CLASS UNTUK DATA MANAGEMENT (FIXED)
# =============================================================================

class StudentDatabase:
    """
    Class untuk mengelola data siswa dengan SQLite backend.
    """
    
    def __init__(self, translator: Translator, db_file: str = DB_FILE ):
        self.translator = translator
        self.db_file = db_file
        self.conn = None
        self.cursor = None
        self._connect()  # Panggil method dengan underscore
        self._create_table()
    
    def _connect(self):
        """Membuat koneksi ke database SQLite."""
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.cursor = self.conn.cursor()
            print(self.translator.t("db_connected", db=self.db_file))
        except sqlite3.Error as e:
            print(f"❌ Error koneksi database: {e}")
            raise
    
    def _create_table(self):
        """Membuat tabel students jika belum ada."""
        query = """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            score INTEGER NOT NULL,
            grade TEXT,
            class_name TEXT DEFAULT 'Umum',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        try:
            self.cursor.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"❌ Error membuat tabel: {e}")
            raise
    
    def add_student(self, name: str, score: int, class_name: str = 'Umum') -> bool:
        """Menambahkan siswa baru ke database."""
        grade = self._calculate_grade(score)
        try:
            self.cursor.execute("""
                INSERT INTO students (name, score, grade, class_name)
                VALUES (?, ?, ?, ?)
            """, (name, score, grade, class_name))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            print(f"⚠️  Siswa dengan nama '{name}' sudah ada!")
            return False
        except sqlite3.Error as e:
            print(f"❌ Error menambahkan siswa: {e}")
            return False
    
    def get_all_students(self) -> pd.DataFrame:
        """Mengambil semua data siswa sebagai DataFrame."""
        try:
            query = "SELECT * FROM students ORDER BY created_at DESC"
            return pd.read_sql_query(query, self.conn)
        except Exception as e:
            print(f"❌ Error mengambil data: {e}")
            return pd.DataFrame()
    
    def get_student_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Mencari siswa berdasarkan nama."""
        try:
            self.cursor.execute(
                "SELECT * FROM students WHERE name = ?", (name,)
            )
            row = self.cursor.fetchone()
            if row:
                columns = [desc[0] for desc in self.cursor.description]
                return dict(zip(columns, row))
            return None
        except sqlite3.Error as e:
            print(f"❌ Error mencari siswa: {e}")
            return None
    
    def update_student(self, name: str, new_score: int) -> bool:
        """Update nilai siswa."""
        grade = self._calculate_grade(new_score)
        try:
            self.cursor.execute("""
                UPDATE students 
                SET score = ?, grade = ?, updated_at = CURRENT_TIMESTAMP
                WHERE name = ?
            """, (new_score, grade, name))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"❌ Error update siswa: {e}")
            return False
    
    def delete_student(self, name: str) -> bool:
        """Menghapus siswa dari database."""
        try:
            self.cursor.execute("DELETE FROM students WHERE name = ?", (name,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"❌ Error menghapus siswa: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, float]:
        """Menghitung statistik deskriptif."""
        df = self.get_all_students()
        if df.empty:
            return {}
        
        return {
            'total_students': len(df),
            'average_score': float(df['score'].mean()),
            'median_score': float(df['score'].median()),
            'std_deviation': float(df['score'].std()),
            'min_score': int(df['score'].min()),
            'max_score': int(df['score'].max()),
            'q1': float(df['score'].quantile(0.25)),
            'q3': float(df['score'].quantile(0.75))
        }
    
    def get_grade_distribution(self) -> pd.DataFrame:
        """Distribusi grade siswa."""
        df = self.get_all_students()
        if df.empty:
            return pd.DataFrame()
        return df['grade'].value_counts().sort_index()
    
    def get_class_statistics(self) -> pd.DataFrame:
        """Statistik per kelas menggunakan GROUP BY."""
        try:
            query = """
            SELECT 
                class_name,
                COUNT(*) as total_students,
                ROUND(AVG(score), 2) as average_score,
                MAX(score) as highest_score,
                MIN(score) as lowest_score
            FROM students
            GROUP BY class_name
            ORDER BY average_score DESC
            """
            return pd.read_sql_query(query, self.conn)
        except sqlite3.Error as e:
            print(f"❌ Error GROUP BY: {e}")
            return pd.DataFrame()
    
    def export_to_csv(self, filename: str = CSV_FILE) -> bool:
        """Export data ke CSV."""
        try:
            df = self.get_all_students()
            if df.empty:
                print("⚠️  Tidak ada data untuk diexport!")
                return False
            df.to_csv(filename, index=False)
            return True
        except Exception as e:
            print(f"❌ Error export CSV: {e}")
            return False
    
    def export_to_excel(self, filename: str = EXCEL_FILE) -> bool:
        """Export data ke Excel dengan multiple sheets."""
        try:
            df = self.get_all_students()
            stats = self.get_class_statistics()
            
            if df.empty:
                print("⚠️  Tidak ada data untuk diexport!")
                return False
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Data Siswa', index=False)
                if not stats.empty:
                    stats.to_excel(writer, sheet_name='Statistik Kelas', index=False)
            return True
        except Exception as e:
            print(f"❌ Error export Excel: {e}")
            return False
    
    def export_to_json(self, filename: str = JSON_FILE) -> bool:
        """Export data ke JSON."""
        try:
            df = self.get_all_students()
            if df.empty:
                print("⚠️  Tidak ada data untuk diexport!")
                return False
            df.to_json(filename, orient='records', indent=4, force_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error export JSON: {e}")
            return False
    
    @staticmethod
    def _calculate_grade(score: int) -> str:
        """Menghitung grade berdasarkan nilai."""
        for grade, (min_val, max_val, _) in GRADE_BOUNDARIES.items():
            if min_val <= score <= max_val:
                return grade
        return 'E'
    
    def close(self):
        """Menutup koneksi database."""
        if self.conn:
            self.conn.close()
            print(self.translator.t("db_closed"))


# =============================================================================
# 4. FUNGSI VALIDASI INPUT
# =============================================================================

def get_valid_string(prompt: str, min_length: int = 1, max_length: int = 100) -> str:
    """Meminta input string dengan validasi panjang."""
    while True:
        try:
            value = input(prompt).strip()
            if len(value) < min_length:
                print(f"⚠️  Input minimal {min_length} karakter!")
            elif len(value) > max_length:
                print(f"⚠️  Input maksimal {max_length} karakter!")
            elif not value.replace(" ", "").isalnum():
                print("⚠️  Nama hanya boleh mengandung huruf, angka, dan spasi!")
            else:
                return value
        except KeyboardInterrupt:
            print("\n⚠️  Input dibatalkan.")
            raise

def get_valid_integer(prompt: str, min_val: int = 0, max_val: int = 100) -> int:
    """Meminta input integer dengan validasi range."""
    while True:
        try:
            value = input(prompt).strip()
            if not value:
                print("⚠️  Input tidak boleh kosong!")
                continue
            
            if not value.isdigit():
                print("⚠️  Input harus berupa angka bulat positif!")
                continue
            
            num = int(value)
            
            if num < min_val:
                print(f"⚠️  Nilai minimal adalah {min_val}!")
            elif num > max_val:
                print(f"⚠️  Nilai maksimal adalah {max_val}!")
            else:
                return num
                
        except ValueError:
            print("⚠️  Input tidak valid. Masukkan angka!")
        except KeyboardInterrupt:
            print("\n⚠️  Input dibatalkan.")
            raise

def get_valid_choice(prompt: str, valid_options: List[str]) -> str:
    """Meminta pilihan dari daftar opsi yang valid."""
    while True:
        choice = input(prompt).strip()
        if choice in valid_options:
            return choice
        print(f"⚠️  Pilihan tidak valid. Pilih salah satu: {', '.join(valid_options)}")


# =============================================================================
# 5. CLASS VISUALISASI
# =============================================================================

class StudentVisualizer:
    """Class untuk menangani semua visualisasi data."""
    
    def __init__(self, db: StudentDatabase, translator: Translator):
        self.db = db
        self.translator = translator
    
    def _check_data(self) -> bool:
        """Cek apakah ada data untuk divisualisasikan."""
        df = self.db.get_all_students()
        if df.empty:
            print(self.translator.t("no_data"))
            return False
        return True
    
    def plot_score_distribution(self):
        """Histogram distribusi nilai."""
        if not self._check_data():
            return
        
        df = self.db.get_all_students()
        plt.figure(figsize=(10, 6))
        plt.hist(df['score'], bins=10, color='skyblue', edgecolor='black', alpha=0.7)
        plt.axvline(df['score'].mean(), color='red', linestyle='--', 
                   label=f'Rata-rata: {df["score"].mean():.1f}')
        plt.xlabel('Nilai')
        plt.ylabel('Frekuensi')
        plt.title('Distribusi Nilai Siswa')
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def plot_grade_distribution(self):
        """Pie chart distribusi grade."""
        grade_dist = self.db.get_grade_distribution()
        if grade_dist.empty:
            print("⚠️  Tidak ada data grade.")
            return
        
        colors = {'A': '#2ecc71', 'B': '#3498db', 'C': '#f1c40f', 
                 'D': '#e67e22', 'E': '#e74c3c'}
        
        plt.figure(figsize=(8, 8))
        plt.pie(grade_dist.values, labels=grade_dist.index, autopct='%1.1f%%',
                colors=[colors.get(g, 'gray') for g in grade_dist.index],
                startangle=90)
        plt.title('Distribusi Grade Siswa')
        plt.axis('equal')
        plt.show()
    
    def plot_class_comparison(self):
        """Bar chart perbandingan nilai antar kelas."""
        class_stats = self.db.get_class_statistics()
        if class_stats.empty:
            print("⚠️  Tidak ada data kelas.")
            return
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(class_stats['class_name'], class_stats['average_score'],
                      color='lightcoral')
        
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom')
        
        plt.xlabel('Kelas')
        plt.ylabel('Rata-rata Nilai')
        plt.title('Perbandingan Rata-rata Nilai per Kelas')
        plt.ylim(0, 100)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def plot_student_ranking(self, top_n: int = 10):
        """Horizontal bar chart ranking siswa."""
        df = self.db.get_all_students()
        if df.empty:
            return
        
        top_students = df.nlargest(top_n, 'score')
        
        plt.figure(figsize=(10, 8))
        colors = plt.cm.viridis(np.linspace(0, 1, len(top_students)))
        bars = plt.barh(top_students['name'], top_students['score'], color=colors)
        
        plt.xlabel('Nilai')
        plt.ylabel('Nama Siswa')
        plt.title(f'Top {top_n} Siswa dengan Nilai Tertinggi')
        plt.gca().invert_yaxis()
        
        for i, (bar, score) in enumerate(zip(bars, top_students['score'])):
            plt.text(score + 1, bar.get_y() + bar.get_height()/2,
                    f'{score}', va='center', fontsize=9)
        
        plt.xlim(0, 105)
        plt.tight_layout()
        plt.show()
    
    def plot_comprehensive_dashboard(self):
        """Dashboard lengkap dengan 4 subplot."""
        df = self.db.get_all_students()
        if df.empty:
            print("⚠️  Tidak ada data untuk dashboard.")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. Histogram
        axes[0, 0].hist(df['score'], bins=10, color='skyblue', edgecolor='black')
        axes[0, 0].set_title('Distribusi Nilai')
        axes[0, 0].set_xlabel('Nilai')
        axes[0, 0].set_ylabel('Frekuensi')
        
        # 2. Box plot
        axes[0, 1].boxplot(df['score'], vert=True)
        axes[0, 1].set_title('Box Plot Nilai')
        axes[0, 1].set_ylabel('Nilai')
        
        # 3. Grade distribution
        grade_counts = df['grade'].value_counts().sort_index()
        axes[1, 0].bar(grade_counts.index, grade_counts.values, color='lightgreen')
        axes[1, 0].set_title('Distribusi Grade')
        axes[1, 0].set_xlabel('Grade')
        axes[1, 0].set_ylabel('Jumlah Siswa')
        
        # 4. Trend (jika ada timestamp)
        df['created_at'] = pd.to_datetime(df['created_at'])
        daily_avg = df.groupby(df['created_at'].dt.date)['score'].mean()
        axes[1, 1].plot(daily_avg.index, daily_avg.values, marker='o')
        axes[1, 1].set_title('Tren Rata-rata Nilai per Hari')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.show()


# =============================================================================
# 6. FUNGSI UTILITAS
# =============================================================================

def print_statistics(db: StudentDatabase, translator):
    """Menampilkan statistik deskriptif lengkap."""
    stats = db.get_statistics()
    if not stats:
        print(translator.t("no_data"))
        return
    
    print("\n" + "="*50)
    print("📊 STATISTIK DESKRIPTIF LENGKAP")
    print("="*50)
    print(f"Total Siswa:          {int(stats['total_students'])}")
    print(f"Rata-rata Nilai:      {stats['average_score']:.2f}")
    print(f"Median Nilai:         {stats['median_score']:.2f}")
    print(f"Standar Deviasi:      {stats['std_deviation']:.2f}")
    print(f"Nilai Minimum:        {stats['min_score']}")
    print(f"Nilai Maksimum:       {stats['max_score']}")
    print(f"Kuartil 1 (Q1):       {stats['q1']:.2f}")
    print(f"Kuartil 3 (Q3):       {stats['q3']:.2f}")
    print(f"Rentang Interkuartil: {stats['q3'] - stats['q1']:.2f}")
    print("="*50)

def print_grade_info():
    """Menampilkan informasi kriteria penilaian."""
    print("\n📋 KRITERIA PENILAIAN:")
    print("-" * 40)
    for grade, (min_val, max_val, desc) in GRADE_BOUNDARIES.items():
        print(f"  Grade {grade}: {min_val:3d}-{max_val:3d} ({desc})")
    print("-" * 40)

def search_and_filter(db: StudentDatabase):
    """Fitur pencarian dan filter lanjutan."""
    print("\n🔍 FITUR PENCARIAN & FILTER")
    print("1. Cari siswa berdasarkan nama")
    print("2. Filter siswa dengan nilai di atas X")
    print("3. Filter siswa dengan nilai di bawah X")
    print("4. Filter berdasarkan grade")
    
    choice = get_valid_choice("Pilih opsi (1-4): ", ['1', '2', '3', '4'])
    df = db.get_all_students()
    
    if df.empty:
        print("📭 Tidak ada data untuk difilter.")
        return
    
    if choice == '1':
        name = get_valid_string("Masukkan nama siswa: ")
        student = db.get_student_by_name(name)
        if student:
            print(f"\n✅ Ditemukan: {student['name']}")
            print(f"   Nilai: {student['score']} (Grade {student['grade']})")
            print(f"   Kelas: {student['class_name']}")
        else:
            print("❌ Siswa tidak ditemukan.")
    
    elif choice == '2':
        threshold = get_valid_integer("Nilai minimum: ", 0, 100)
        filtered = df[df['score'] > threshold]
        print(f"\n📊 Siswa dengan nilai > {threshold} ({len(filtered)} orang):")
        if not filtered.empty:
            print(filtered[['name', 'score', 'grade']].to_string(index=False))
    
    elif choice == '3':
        threshold = get_valid_integer("Nilai maksimum: ", 0, 100)
        filtered = df[df['score'] < threshold]
        print(f"\n📊 Siswa dengan nilai < {threshold} ({len(filtered)} orang):")
        if not filtered.empty:
            print(filtered[['name', 'score', 'grade']].to_string(index=False))
    
    elif choice == '4':
        grade = get_valid_choice("Pilih grade (A/B/C/D/E): ", ['A', 'B', 'C', 'D', 'E'])
        filtered = df[df['grade'] == grade]
        print(f"\n📊 Siswa dengan grade {grade} ({len(filtered)} orang):")
        if not filtered.empty:
            print(filtered[['name', 'score', 'class_name']].to_string(index=False))


# =============================================================================
# 7. MAIN APPLICATION
# =============================================================================

def display_menu(translator: Translator):

    """Menampilkan menu utama."""
    print("\n" + "="*50)
    print(translator.t("menu_title"))
    print("="*50)
    print(" 1.", translator.t("add_student"))
    print(" 2.", translator.t("view_students"))
    print(" 3.", translator.t("search_filter"))
    print(" 4.", translator.t("update_score"))
    print(" 5.", translator.t("delete_student"))
    print(" 6.", translator.t("statistics"))
    print(" 7.", translator.t("class_analysis"))
    print(" 8.", translator.t("score_distribution"))
    print(" 9.", translator.t("grade_distribution"))
    print("10.", translator.t("ranking"))
    print("11.", translator.t("class_comparison"))
    print("12.", translator.t("dashboard"))
    print("13.", translator.t("export_csv"))
    print("14.", translator.t("export_excel"))
    print("15.", translator.t("export_json"))
    print("16.", translator.t("criteria_info"))
    print("17.", translator.t("exit"))
    print("18.", translator.t("language_changed"))
    print("="*50)

def main():
    """Fungsi utama aplikasi."""
    # =============================
    # PILIH BAHASA DULU
    # =============================

    print("Pilih bahasa / Choose language:")
    print("1. 🇮🇩 Bahasa Indonesia")
    print("2. 🇬🇧 English")

    lang_choice = get_valid_choice("Masukkan pilihan (1/2): ", ['1', '2'])

    if lang_choice == '2':
        translator = Translator("en")
    else:
        translator = Translator("id")

    # =============================
    # BARU BUAT DATABASE
    # =============================

    try:
        db = StudentDatabase(translator)
    except Exception as e:
        print(f"❌ Gagal inisialisasi database: {e}")
        return

    visualizer = StudentVisualizer(db, translator)

    # =============================
    # WELCOME SCREEN
    # =============================

    print("\n" + "="*50)
    print(translator.t("welcome"))
    print("="*50)
    
    try:
        while True:
            display_menu(translator)
            choice = get_valid_choice(translator.t("choose_menu"), 
                                    [str(i) for i in range(1, 19)])
            
            # MENU 1: Tambah Siswa
            if choice == '1':
                print("\n➕ TAMBAH SISWA BARU")
                name = get_valid_string("Nama siswa: ")
                
                # Cek duplikat
                existing = db.get_student_by_name(name)
                if existing:
                    print(f"⚠️  Siswa '{name}' sudah ada dengan nilai {existing['score']}")
                    update = get_valid_choice("Update nilai? (y/n): ", ['y', 'n'])
                    if update == 'y':
                        score = get_valid_integer("Nilai baru (0-100): ")
                        if db.update_student(name, score):
                            print(f"✅ Nilai {name} berhasil diupdate menjadi {score}")
                    continue
                
                score = get_valid_integer("Nilai (0-100): ")
                class_name = input("Nama Kelas (default: Umum): ").strip()
                if not class_name:
                    class_name = 'Umum'
                
                if db.add_student(name, score, class_name):
                    grade = db._calculate_grade(score)
                    print(f"✅ Siswa {name} (Kelas {class_name}) berhasil ditambahkan!")
                    print(f"   Nilai: {score} | Grade: {grade}")
                else:
                    print("❌ Gagal menambahkan siswa.")
            
            # MENU 2: Lihat Semua Siswa
            elif choice == '2':
                df = db.get_all_students()
                if df.empty:
                    print(translator.t("no_data"))
                else:
                    print(f"\n📋 DAFTAR SEMUA SISWA ({len(df)} orang)")
                    print("-" * 60)
                    display_df = df[['name', 'score', 'grade', 'class_name', 'created_at']]
                    print(display_df.to_string(index=False))
            
            # MENU 3: Cari & Filter
            elif choice == '3':
                search_and_filter(db)
            
            # MENU 4: Update Nilai
            elif choice == '4':
                name = get_valid_string("Nama siswa yang akan diupdate: ")
                existing = db.get_student_by_name(name)
                if not existing:
                    print("❌ Siswa tidak ditemukan.")
                    continue
                
                print(f"Nilai saat ini: {existing['score']} (Grade {existing['grade']})")
                new_score = get_valid_integer("Nilai baru (0-100): ")
                
                if db.update_student(name, new_score):
                    new_grade = db._calculate_grade(new_score)
                    print(f"✅ Berhasil update! {name}: {new_score} (Grade {new_grade})")
                else:
                    print("❌ Gagal mengupdate.")
            
            # MENU 5: Hapus Siswa
            elif choice == '5':
                name = get_valid_string("Nama siswa yang akan dihapus: ")
                confirm = get_valid_choice(f"Yakin hapus {name}? (y/n): ", ['y', 'n'])
                if confirm == 'y':
                    if db.delete_student(name):
                        print(f"✅ Siswa {name} berhasil dihapus.")
                    else:
                        print("❌ Siswa tidak ditemukan.")
            
            # MENU 6: Statistik Deskriptif
            elif choice == '6':
                print_statistics(db)
            
            # MENU 7: Analisis per Kelas (GroupBy)
            elif choice == '7':
                class_stats = db.get_class_statistics()
                if class_stats.empty:
                    print("📭 Belum ada data kelas.")
                else:
                    print("\n📊 STATISTIK PER KELAS (GROUP BY):")
                    print(class_stats.to_string(index=False))
            
            # MENU 8-12: Visualisasi
            elif choice == '8':
                visualizer.plot_score_distribution()
            elif choice == '9':
                visualizer.plot_grade_distribution()
            elif choice == '10':
                n = get_valid_integer("Jumlah top siswa (1-50): ", 1, 50)
                visualizer.plot_student_ranking(n)
            elif choice == '11':
                visualizer.plot_class_comparison()
            elif choice == '12':
                visualizer.plot_comprehensive_dashboard()
            
            # MENU 13-15: Export Data
            elif choice == '13':
                if db.export_to_csv():
                    print(f"✅ Data berhasil diekspor ke {CSV_FILE}")
                else:
                    print("❌ Gagal export CSV.")
            
            elif choice == '14':
                if db.export_to_excel():
                    print(f"✅ Data berhasil diekspor ke {EXCEL_FILE}")
                else:
                    print("❌ Gagal export Excel. Pastikan 'openpyxl' terinstall:")
                    print("   pip install openpyxl")
            
            elif choice == '15':
                if db.export_to_json():
                    print(f"✅ Data berhasil diekspor ke {JSON_FILE}")
                else:
                    print("❌ Gagal export JSON.")
            
            # MENU 16: Info Kriteria
            elif choice == '16':
                print_grade_info()
            
            # MENU 17: Keluar
            elif choice == '17':
                print(translator.t("goodbye"))
                print("Data tersimpan secara permanen di database SQLite.")
                break
                
            #MENU 18: Pilih bahasa
            elif choice == '18':
                new_lang = "en" if translator.get_language() == "id" else "id"
                translator.set_language(new_lang)

                lang_name = "Bahasa Indonesia" if new_lang == "id" else "English"
                print(translator.t("language_changed", lang=lang_name))
            
            if choice not in ['8', '9', '10', '11', '12']:  # Skip pause untuk plot
                input(translator.t("press_enter"))
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Program dihentikan oleh user.")
    except Exception as e:
        print(f"\n❌ Error tidak terduga: {e}")
    finally:
        db.close()
        print("💾 Sampai jumpa!")

if __name__ == "__main__":

    main()

"""
language.py
Professional Multilingual Translation System
"""

from typing import Dict, Optional
import json
import os


class Translator:
    """
    Universal Translator Class
    - Support multiple languages
    - Support fallback language
    - Support placeholder formatting
    - Can load external JSON language files
    """

    DEFAULT_LANGUAGE = "id"

    def __init__(self, lang: str = DEFAULT_LANGUAGE):
        self._languages: Dict[str, Dict[str, str]] = {}
        self._current_lang: str = lang
        self._fallback_lang: str = self.DEFAULT_LANGUAGE

        self._load_builtin_languages()

        if lang not in self._languages:
            self._current_lang = self._fallback_lang

    # ==========================================================
    # BUILTIN LANGUAGES
    # ==========================================================

    def _load_builtin_languages(self):
        """Load default built-in languages."""
        self._languages = {
            "id": {
                "welcome": "🎉 Selamat Datang di Sistem Manajemen Nilai Siswa!",
                "menu_title": "🎓 SISTEM MANAJEMEN NILAI SISWA",
                "add_student": "➕ Tambah Siswa Baru",
                "view_students": "📋 Lihat Semua Siswa",
                "exit": "🚪 Keluar",
                "choose_menu": "Pilih menu (1-17): ",
                "no_data": "📭 Belum ada data siswa.",
                "goodbye": "👋 Terima kasih telah menggunakan sistem ini!",
                "search_filter": "🔍  Cari & Filter Siswa",
                "update_score": "✏️   Update Nilai Siswa",
                "delete_student": "🗑️   Hapus Siswa",
                "statistics": "📊  Statistik Deskriptif",
                "class_analysis": "📈  Analisis per Kelas (GroupBy)",
                "score_distribution": "📉  Visualisasi: Distribusi Nilai",
                "grade_distribution": "🥧  Visualisasi: Distribusi Grade",
                "ranking": "🏆  Visualisasi: Ranking Siswa",
                "class_comparison": "📊  Visualisasi: Perbandingan Kelas",
                "dashboard": "🖥️   Dashboard Komprehensif",
                "export_csv": "💾  Export ke CSV",
                "export_excel": "📗  Export ke Excel",
                "export_json": "📝  Export ke JSON",
                "criteria_info": "ℹ️   Info Kriteria Penilaian",
                "db_connected": "✅ Terhubung ke database: {db}",
                "db_closed": "🔒 Koneksi database ditutup.",
                "invalid_choice": "⚠️ Pilihan tidak valid.",
                "press_enter": "Tekan Enter untuk melanjutkan..."
            },
            "en": {
                "welcome": "🎉 Welcome to Student Grade Management System!",
                "menu_title": "🎓 STUDENT GRADE MANAGEMENT SYSTEM",
                "add_student": "➕ Add New Student",
                "view_students": "📋 View All Students",
                "exit": "🚪 Exit",
                "choose_menu": "Choose menu (1-17): ",
                "no_data": "📭 No student data available.",
                "goodbye": "👋 Thank you for using this system!",
                "search_filter": "🔍  Search & Filter Students",
                "update_score": "✏️   Update Student Score",
                "delete_student": "🗑️   Delete Student",
                "statistics": "📊  Descriptive Statistics",
                "class_analysis": "📈  Class Analysis (GroupBy)",
                "score_distribution": "📉  Visualization: Score Distribution",
                "grade_distribution": "🥧  Visualization: Grade Distribution",
                "ranking": "🏆  Visualization: Student Ranking",
                "class_comparison": "📊  Visualization: Class Comparison",
                "dashboard": "🖥️   Comprehensive Dashboard",
                "export_csv": "💾  Export to CSV",
                "export_excel": "📗  Export to Excel",
                "export_json": "📝  Export to JSON",
                "criteria_info": "ℹ️   Grading Criteria Info",
                "db_connected": "✅ Connected to database: {db}",
                "db_closed": "🔒 Database connection closed.",
                "invalid_choice": "⚠️ Invalid choice.",
                "press_enter": "Press Enter to continue..."
            }
        }

    # ==========================================================
    # PUBLIC METHODS
    # ==========================================================

    def set_language(self, lang: str) -> None:
        """Change active language."""
        if lang in self._languages:
            self._current_lang = lang
        else:
            print(f"Language '{lang}' not available. Using fallback.")

    def get_language(self) -> str:
        """Return current active language."""
        return self._current_lang

    def available_languages(self):
        """Return list of available languages."""
        return list(self._languages.keys())

    def add_language(self, lang_code: str, translations: Dict[str, str]):
        """Add new language programmatically."""
        self._languages[lang_code] = translations

    def load_from_json(self, filepath: str):
        """
        Load language file from JSON.
        Format:
        {
            "en": { "welcome": "..." },
            "fr": { "welcome": "..." }
        }
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"{filepath} not found")

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        for lang, translations in data.items():
            self._languages[lang] = translations

    def t(self, key: str, **kwargs) -> str:
        """
        Translate text by key.
        Supports formatting placeholders.

        Example:
            translator.t("db_connected", db="students.db")
        """
        lang_dict = self._languages.get(self._current_lang, {})
        fallback_dict = self._languages.get(self._fallback_lang, {})

        text = lang_dict.get(key) or fallback_dict.get(key) or key

        try:
            return text.format(**kwargs)
        except Exception:
            return text
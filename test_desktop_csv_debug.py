#!/usr/bin/env python3
"""
Skrypt testowy do sprawdzenia wczytywania plików CSV/TSV z debugowaniem
"""

import sys
import os
import logging
sys.path.append('.')

# Włącz debugowanie
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from data_processor import DataProcessor

def test_desktop_csv_loading_debug():
    """Testuje wczytywanie plików CSV/TSV z debugowaniem"""
    
    # Inicjalizuj DataProcessor
    processor = DataProcessor()
    
    # Testuj plik "Brak płatności - sms 12.08.csv"
    file_path = "Brak płatności - sms 12.08.csv"
    
    if not os.path.exists(file_path):
        print(f"❌ Plik {file_path} nie istnieje!")
        return
    
    print(f"🔍 Testuję wczytywanie pliku z debugowaniem: {file_path}")
    print("=" * 70)
    
    # Testuj wykrywanie separatora
    print("📊 Test wykrywania separatora:")
    detected_sep = processor._detect_file_separator(file_path)
    print(f"   Wykryty separator: '{repr(detected_sep)}'")
    
    # Testuj wykrywanie kodowania
    print("\n📝 Test wykrywania kodowania:")
    detected_encoding = processor._detect_file_encoding(file_path)
    print(f"   Wykryte kodowanie: {detected_encoding}")
    
    # Testuj wczytywanie pliku
    print("\n📁 Test wczytywania pliku:")
    success = processor.load_excel_file(file_path)
    
    if success:
        print("   ✅ Plik został wczytany pomyślnie!")
        print(f"   📊 Liczba wierszy: {processor.get_row_count()}")
        print(f"   🔗 Kolumny: {processor.get_columns()}")
        print(f"   🎯 Mapowanie: {processor.column_mapping}")
    else:
        print("   ❌ Błąd wczytywania pliku!")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_desktop_csv_loading_debug() 
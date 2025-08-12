#!/usr/bin/env python3
"""
Skrypt testowy do sprawdzenia wykrywania separatorów w plikach CSV/TSV
"""

import sys
import os
sys.path.append('.')

from data_processor import DataProcessor

def test_separator_detection():
    """Testuje wykrywanie separatorów w pliku CSV/TSV"""
    
    # Inicjalizuj DataProcessor
    processor = DataProcessor()
    
    # Testuj plik "Brak płatności - sms 12.08.csv"
    file_path = "Brak płatności - sms 12.08.csv"
    
    if not os.path.exists(file_path):
        print(f"❌ Plik {file_path} nie istnieje!")
        return
    
    print(f"🔍 Testuję plik: {file_path}")
    print("=" * 60)
    
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
        
        # Pokaż pierwsze 3 wiersze
        print("\n📋 Pierwsze 3 wiersze:")
        preview = processor.get_preview_data(3)
        for i, row in enumerate(preview):
            print(f"   Wiersz {i+1}: {dict(list(row.items())[:5])}...")
    else:
        print("   ❌ Błąd wczytywania pliku!")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_separator_detection() 
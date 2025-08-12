#!/usr/bin/env python3
"""
Prosty test wczytywania CSV
"""

import sys
import os
sys.path.append('.')

from data_processor import DataProcessor

def test_simple_csv():
    """Testuje proste wczytywanie CSV"""
    
    # Inicjalizuj DataProcessor
    processor = DataProcessor()
    
    # Testuj plik "Brak płatności - sms 12.08.csv"
    file_path = "Brak płatności - sms 12.08.csv"
    
    if not os.path.exists(file_path):
        print(f"❌ Plik {file_path} nie istnieje!")
        return
    
    print(f"🔍 Testuję proste wczytywanie pliku: {file_path}")
    print("=" * 50)
    
    # Testuj wczytywanie pliku
    print("📁 Test wczytywania pliku:")
    success = processor.load_excel_file(file_path)
    
    if success:
        print("   ✅ Plik został wczytany pomyślnie!")
        print(f"   📊 Liczba wierszy: {processor.get_row_count()}")
        print(f"   🔗 Kolumny: {processor.get_columns()}")
        print(f"   🎯 Mapowanie: {processor.column_mapping}")
    else:
        print("   ❌ Błąd wczytywania pliku!")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_simple_csv() 
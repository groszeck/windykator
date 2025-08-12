#!/usr/bin/env python3
"""
Skrypt testowy do sprawdzenia wczytywania plików CSV/TSV w aplikacji desktopowej
"""

import sys
import os
sys.path.append('.')

from data_processor import DataProcessor

def test_desktop_csv_loading():
    """Testuje wczytywanie plików CSV/TSV w aplikacji desktopowej"""
    
    # Inicjalizuj DataProcessor
    processor = DataProcessor()
    
    # Testuj plik "Brak płatności - sms 12.08.csv"
    file_path = "Brak płatności - sms 12.08.csv"
    
    if not os.path.exists(file_path):
        print(f"❌ Plik {file_path} nie istnieje!")
        return
    
    print(f"🔍 Testuję wczytywanie pliku w aplikacji desktopowej: {file_path}")
    print("=" * 70)
    
    # Testuj wczytywanie pliku
    print("📁 Test wczytywania pliku:")
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
        
        # Sprawdź czy mapowanie jest poprawne
        print("\n🎯 Sprawdzenie mapowania:")
        required_fields = ['kontrahent', 'nip', 'nr_faktury', 'email', 'telefon', 'kwota', 'data_faktury']
        missing_fields = processor.validate_mapping(required_fields)
        
        if missing_fields:
            print(f"   ⚠️  Brakujące pola: {missing_fields}")
        else:
            print("   ✅ Wszystkie wymagane pola są zmapowane!")
        
    else:
        print("   ❌ Błąd wczytywania pliku!")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_desktop_csv_loading() 
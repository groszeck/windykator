#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test funkcji usuwania pozycji rozliczonych i odświeżania podglądu
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_processor import DataProcessor
import pandas as pd

def test_remove_settled_and_preview():
    """Testuje usuwanie pozycji rozliczonych i generowanie podglądu"""
    print("🧪 Test usuwania pozycji rozliczonych i odświeżania podglądu")
    print("=" * 60)
    
    # Utwórz procesor danych
    processor = DataProcessor()
    
    # Wczytaj plik
    file_path = "Brak płatności 08.08.csv"
    if not os.path.exists(file_path):
        print(f"❌ Plik {file_path} nie istnieje!")
        return
    
    print(f"📁 Wczytuję plik: {file_path}")
    success = processor.load_excel_file(file_path)
    
    if not success:
        print("❌ Nie udało się wczytać pliku!")
        return
    
    print(f"✅ Plik wczytany pomyślnie!")
    print(f"📊 Początkowa liczba wierszy: {len(processor.excel_data)}")
    
    # Sprawdź mapowanie kolumn
    print(f"🔍 Mapowanie kolumn: {processor.column_mapping}")
    
    # Generuj podgląd przed usunięciem
    print("\n🔍 Generuję podgląd PRZED usunięciem pozycji rozliczonych...")
    preview_before = processor.get_preview_data()
    print(f"📊 Liczba wierszy w podglądzie PRZED: {len(preview_before)}")
    
    # Usuń pozycje rozliczone
    print("\n🗑️ Usuwam pozycje rozliczone...")
    removed_count = processor.remove_settled_items()
    print(f"🗑️ Usunięto {removed_count} pozycji rozliczonych")
    print(f"📊 Liczba wierszy PO usunięciu: {len(processor.excel_data)}")
    
    # Generuj podgląd po usunięciu
    print("\n🔍 Generuję podgląd PO usunięciu pozycji rozliczonych...")
    preview_after = processor.get_preview_data()
    print(f"📊 Liczba wierszy w podglądzie PO: {len(preview_after)}")
    
    # Sprawdź czy liczby się zgadzają
    print("\n🔍 Sprawdzam spójność danych...")
    if len(preview_after) == len(processor.excel_data):
        print("✅ Spójność OK: podgląd zawiera wszystkie wiersze")
    else:
        print(f"❌ Błąd spójności: podgląd {len(preview_after)} vs dane {len(processor.excel_data)}")
    
    # Sprawdź czy usunięte pozycje rzeczywiście miały kwotę ≤ 0
    if 'kwota' in processor.column_mapping:
        kwota_col = processor.column_mapping['kwota']
        print(f"\n🔍 Sprawdzam kolumnę kwoty: {kwota_col}")
        
        # Sprawdź czy wszystkie pozostałe kwoty są > 0
        all_positive = True
        for idx, row in processor.excel_data.iterrows():
            try:
                kwota_str = str(row[kwota_col]).replace(',', '.').strip()
                kwota_num = float(kwota_str) if kwota_str else 0
                if kwota_num <= 0:
                    print(f"❌ Znaleziono kwotę ≤ 0 w wierszu {idx}: {kwota_num}")
                    all_positive = False
            except (ValueError, TypeError):
                print(f"⚠️ Nie można przekonwertować kwoty w wierszu {idx}: {row[kwota_col]}")
        
        if all_positive:
            print("✅ Wszystkie pozostałe kwoty są > 0")
        else:
            print("❌ Znaleziono kwoty ≤ 0 w pozostałych wierszach")
    
    print("\n" + "=" * 60)
    print("🏁 Test zakończony")

if __name__ == "__main__":
    test_remove_settled_and_preview() 
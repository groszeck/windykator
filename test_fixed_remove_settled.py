#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test poprawionej funkcji remove_settled_items
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_processor import DataProcessor
import pandas as pd

def test_fixed_remove_settled():
    """Testuje poprawioną funkcję remove_settled_items"""
    print("🧪 Test poprawionej funkcji remove_settled_items")
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
    
    # Sprawdź czy kolumna kwota jest zmapowana
    if 'kwota' in processor.column_mapping:
        kwota_col = processor.column_mapping['kwota']
        print(f"✅ Kolumna kwota jest zmapowana na: {kwota_col}")
        
        # Sprawdź kilka wartości w tej kolumnie
        print(f"🔍 Przykładowe wartości w kolumnie {kwota_col}:")
        for i in range(min(5, len(processor.excel_data))):
            value = processor.excel_data.iloc[i][kwota_col]
            print(f"   Wiersz {i}: {value}")
    else:
        print("❌ Kolumna kwota nie jest zmapowana!")
        return
    
    # Sprawdź ile wierszy ma kwotę = 0
    print(f"\n🔍 Sprawdzam ile wierszy ma kwotę = 0...")
    zero_count = 0
    for idx, row in processor.excel_data.iterrows():
        try:
            kwota_str = str(row[kwota_col]).replace(',', '.').strip()
            kwota_num = float(kwota_str) if kwota_str else 0
            if kwota_num == 0:
                zero_count += 1
        except (ValueError, TypeError):
            pass
    
    print(f"📊 Znaleziono {zero_count} wierszy z kwotą = 0")
    
    # Usuń pozycje rozliczone
    print(f"\n🗑️ Usuwam pozycje rozliczone...")
    removed_count = processor.remove_settled_items()
    print(f"🗑️ Usunięto {removed_count} pozycji rozliczonych")
    print(f"📊 Liczba wierszy PO usunięciu: {len(processor.excel_data)}")
    
    # Sprawdź czy wszystkie pozostałe kwoty są > 0
    print(f"\n🔍 Sprawdzam czy wszystkie pozostałe kwoty są > 0...")
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
    test_fixed_remove_settled() 
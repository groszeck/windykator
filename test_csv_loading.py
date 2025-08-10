#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_processor import DataProcessor
import logging

# Ustawienie logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_csv_loading():
    """Testuje wczytywanie pliku CSV"""
    processor = DataProcessor()
    
    # Ścieżka do pliku CSV
    csv_file = "Brak płatności 08.08.csv"
    
    if not os.path.exists(csv_file):
        print(f"Plik {csv_file} nie istnieje!")
        return
    
    print(f"Testuję wczytywanie pliku: {csv_file}")
    print("=" * 50)
    
    # Wczytaj plik
    success = processor.load_excel_file(csv_file)
    
    if success:
        print("✅ Plik został wczytany pomyślnie!")
        print(f"Liczba wierszy: {processor.get_row_count()}")
        print(f"Kolumny: {processor.get_columns()}")
        print()
        
        # Pokaż mapowanie kolumn
        print("Mapowanie kolumn:")
        print(processor.get_mapping_summary())
        print()
        
        # Pokaż przykładowe dane
        print("Przykładowe dane (pierwsze 3 wiersze):")
        preview = processor.get_preview_data(3)
        for i, row in enumerate(preview):
            print(f"Wiersz {i+1}: {row}")
        print()
        
        # Pokaż pokrycie mapowania
        coverage = processor.get_mapping_coverage()
        print(f"Pokrycie mapowania: {coverage:.1f}%")
        
        # Pokaż niezmapowane kolumny
        unmapped = processor.get_unmapped_columns()
        if unmapped:
            print(f"Niezmapowane kolumny: {unmapped}")
        
    else:
        print("❌ Błąd podczas wczytywania pliku!")
        
        # Spróbuj pobrać informacje o pliku
        try:
            info = processor.get_file_info(csv_file)
            print(f"Informacje o pliku: {info}")
        except Exception as e:
            print(f"Nie można pobrać informacji o pliku: {e}")

if __name__ == "__main__":
    test_csv_loading() 
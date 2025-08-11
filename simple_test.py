#!/usr/bin/env python3
"""
Prosty test wczytywania pliku CSV z poprawioną obsługą cudzysłowów
"""

from data_processor import DataProcessor
import logging
import os

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_csv_loading():
    """Testuje wczytywanie pliku CSV i mapowanie kolumn"""
    print("=== TEST WCZYTYWANIA CSV I MAPOWANIA KOLUMN ===")
    
    # Konfiguracja logowania
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Ścieżka do pliku CSV
    csv_file = "Brak płatności 08.08.csv"
    
    # Sprawdź czy plik istnieje
    if not os.path.exists(csv_file):
        print(f"❌ Plik {csv_file} nie istnieje!")
        return
    
    print(f"📁 Wczytywanie pliku: {csv_file}")
    
    # Utwórz instancję DataProcessor
    processor = DataProcessor()
    
    # Wczytaj plik
    if processor.load_excel_file(csv_file):
        print("✅ Plik został wczytany pomyślnie!")
        
        # Pokaż informacje o danych
        print(f"📊 Liczba wierszy: {processor.get_row_count()}")
        print(f"📋 Kolumny: {processor.get_columns()}")
        
        # Sprawdź mapowanie kolumn
        print("\n🔍 SPRAWDZANIE MAPOWANIA KOLUMN:")
        mapping_summary = processor.get_mapping_summary()
        for field, info in mapping_summary.items():
            print(f"  {field}: {info['mapped_to']} (pokrycie: {info['coverage']:.1f}%)")
        
        # Sprawdź problemy z kodowaniem
        print("\n🔍 SPRAWDZANIE PROBLEMÓW Z KODOWANIEM:")
        try:
            encoding_issues = processor.check_encoding_issues()
            if encoding_issues:
                for col, issues in encoding_issues.items():
                    print(f"  ❌ {col}: {issues['total_problematic']} problematycznych wartości")
                    print(f"     Przykłady: {issues['sample_problematic']}")
            else:
                print("  ✅ Nie znaleziono problemów z kodowaniem")
        except Exception as e:
            print(f"  ⚠️ Błąd podczas sprawdzania kodowania: {e}")
        
        # Sprawdź konkretne wiersze
        print("\n🔍 SPRAWDZANIE KONKRETNYCH WIERSZY:")
        search_terms = ["KOSSOWSKI", "SADOWSKI", "BEST", "ELECTRO"]
        try:
            specific_rows = processor.diagnose_specific_rows(search_terms)
            for term, rows in specific_rows.items():
                if rows:
                    print(f"  ✅ Znaleziono {len(rows)} wierszy dla '{term}':")
                    for i, row in enumerate(rows[:3]):  # Pokaż pierwsze 3
                        print(f"     Wiersz {i+1}: {row}")
                else:
                    print(f"  ❌ Nie znaleziono wierszy dla '{term}'")
        except Exception as e:
            print(f"  ⚠️ Błąd podczas diagnozowania wierszy: {e}")
        
        # Sprawdź mapowanie kolumn
        print("\n🔍 SZCZEGÓŁOWE MAPOWANIE KOLUMN:")
        try:
            unmapped = processor.get_unmapped_columns()
            if unmapped:
                print(f"  ⚠️ Niemapowane kolumny: {unmapped}")
            else:
                print("  ✅ Wszystkie kolumny są zmapowane")
        except Exception as e:
            print(f"  ⚠️ Błąd podczas sprawdzania mapowania: {e}")
        
        # Pokaż podgląd danych
        print("\n📋 PODGLĄD DANYCH:")
        try:
            preview = processor.get_preview_data(5)
            if preview:
                for i, row in enumerate(preview):
                    print(f"  Wiersz {i+1}: {row}")
        except Exception as e:
            print(f"  ⚠️ Błąd podczas pobierania podglądu: {e}")
        
        # Sprawdź surowe dane
        print("\n🔍 SUROWE DANE Z DATAFRAME:")
        try:
            if processor.excel_data is not None:
                print(f"  📊 Rozmiar DataFrame: {processor.excel_data.shape}")
                print(f"  📋 Nazwy kolumn: {list(processor.excel_data.columns)}")
                
                # Sprawdź konkretnie "Andrzej KOSSOWSKI" i "BEST Sadowski"
                print("\n  🔍 SZUKANIE KONKRETNYCH FIRM:")
                
                # Szukaj "Andrzej KOSSOWSKI"
                for i, row in processor.excel_data.iterrows():
                    for col in processor.excel_data.columns:
                        if isinstance(row[col], str) and "KOSSOWSKI" in row[col].upper():
                            print(f"    ✅ Znaleziono 'KOSSOWSKI' w wierszu {i+1}, kolumna '{col}': {row[col]}")
                
                # Szukaj "BEST Sadowski"
                for i, row in processor.excel_data.iterrows():
                    for col in processor.excel_data.columns:
                        if isinstance(row[col], str) and "BEST" in row[col].upper() and "SADOWSKI" in row[col].upper():
                            print(f"    ✅ Znaleziono 'BEST Sadowski' w wierszu {i+1}, kolumna '{col}': {row[col]}")
                
                # Dodaj szczegółowe sprawdzenie wiersza z datą 25.07.2025
                print("\n🔍 SZCZEGÓŁOWE SPRAWDZENIE WIERSZA Z DATĄ 25.07.2025:")
                if processor.excel_data is not None:
                    # Znajdź wiersz z datą 25.07.2025
                    data_mask = processor.excel_data['Data'] == '25.07.2025'
                    if data_mask.any():
                        row_index = data_mask.idxmax()
                        row_data = processor.excel_data.loc[row_index]
                        print(f"    📅 Wiersz z datą 25.07.2025 (indeks: {row_index}):")
                        print(f"      Data: {row_data['Data']}")
                        print(f"      Kontrahent: {row_data['Kontrahent']}")
                        print(f"      dni_po_terminie: {row_data['dni_po_terminie']}")
                        
                        # Sprawdź mapowanie kolumn
                        print(f"      Mapowanie kolumn: {processor.column_mapping}")
                        
                        # Sprawdź czy data_faktury jest zmapowane
                        if 'data_faktury' in processor.column_mapping:
                            mapped_col = processor.column_mapping['data_faktury']
                            print(f"      Kolumna 'data_faktury' zmapowana na: {mapped_col}")
                            print(f"      Wartość w zmapowanej kolumnie: {row_data[mapped_col]}")
                            
                            # Przetestuj funkcję calculate_days_overdue bezpośrednio
                            dni = processor.calculate_days_overdue(row_data)
                            print(f"      Wynik calculate_days_overdue: {dni}")
                        else:
                            print(f"      ❌ Brak mapowania dla 'data_faktury'")
                    else:
                        print("    ❌ Nie znaleziono wiersza z datą 25.07.2025")

                # Pokaż pierwsze kilka wierszy
                print("\n📋 PIERWSZE 3 WIERSZE:")
                for i in range(min(3, len(processor.excel_data))):
                    row = processor.excel_data.iloc[i]
                    print(f"    Wiersz {i+1}:")
                    for col in processor.excel_data.columns:
                        print(f"      {col}: {row[col]}")
                        
        except Exception as e:
            print(f"  ⚠️ Błąd podczas sprawdzania surowych danych: {e}")
        
    else:
        print("❌ Nie udało się wczytać pliku!")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    test_csv_loading() 
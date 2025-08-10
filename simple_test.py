#!/usr/bin/env python3
"""
Prosty test modułu DataProcessor
"""
import logging
from data_processor import DataProcessor

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_data_processor():
    """Testuje główne funkcje DataProcessor"""
    processor = DataProcessor()
    
    print("Testuję wczytywanie pliku: Brak płatności 08.08.csv")
    print("=" * 50)
    
    # Wczytaj plik
    success = processor.load_excel_file("Brak płatności 08.08.csv")
    
    if success:
        print("✅ Plik został wczytany pomyślnie!")
        print(f"Liczba wierszy: {processor.get_row_count()}")
        print(f"Kolumny: {processor.get_columns()}")
        print(f"\nMapowanie kolumn:")
        for field, column in processor.column_mapping.items():
            print(f"  {field} -> {column}")
        
        # Test podglądu wszystkich wierszy
        print(f"\n🔍 Test podglądu wszystkich wierszy:")
        preview_data = processor.get_preview_data()  # Bez parametru = wszystkie wiersze
        print(f"Liczba wierszy w podglądzie: {len(preview_data)}")
        
        if preview_data:
            print(f"Pierwszy wiersz:")
            first_row = preview_data[0]
            for key, value in first_row.items():
                print(f"  {key}: {value}")
        
        # Test usuwania pozycji rozliczonych
        print(f"\n🗑️ Test usuwania pozycji rozliczonych:")
        initial_count = processor.get_row_count()
        removed_count = processor.remove_settled_items()
        final_count = processor.get_row_count()
        
        print(f"Początkowa liczba wierszy: {initial_count}")
        print(f"Usunięto pozycji rozliczonych: {removed_count}")
        print(f"Końcowa liczba wierszy: {final_count}")
        
        # Sprawdź podgląd po usunięciu
        preview_after = processor.get_preview_data()
        print(f"Liczba wierszy w podglądzie po usunięciu: {len(preview_after)}")
        
    else:
        print("❌ Błąd wczytywania pliku")

if __name__ == "__main__":
    test_data_processor() 
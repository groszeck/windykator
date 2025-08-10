"""
Moduł do przetwarzania danych Excel/CSV
"""
import pandas as pd
from datetime import datetime
import logging

class DataProcessor:
    """Klasa do przetwarzania danych z plików Excel/CSV"""
    
    def __init__(self):
        self.excel_data = None
        self.column_mapping = {}
        self.logger = logging.getLogger(__name__)
    
    def load_excel_file(self, file_path):
        """Wczytuje plik Excel/CSV"""
        try:
            if file_path.endswith(('.xlsx', '.xls')):
                self.excel_data = pd.read_excel(file_path)
            elif file_path.endswith('.csv'):
                self.excel_data = pd.read_csv(file_path, encoding='utf-8')
            else:
                raise ValueError("Nieobsługiwany format pliku")
            
            self.logger.info(f"Wczytano plik: {file_path}")
            self.logger.info(f"Liczba wierszy: {len(self.excel_data)}")
            self.logger.info(f"Kolumny: {list(self.excel_data.columns)}")
            
            return True
        except Exception as e:
            self.logger.error(f"Błąd wczytywania pliku: {e}")
            return False
    
    def get_columns(self):
        """Zwraca listę kolumn z wczytanych danych"""
        if self.excel_data is not None:
            return list(self.excel_data.columns)
        return []
    
    def get_row_count(self):
        """Zwraca liczbę wierszy"""
        if self.excel_data is not None:
            return len(self.excel_data)
        return 0
    
    def set_column_mapping(self, mapping):
        """Ustawia mapowanie kolumn"""
        self.column_mapping = mapping
    
    def process_row(self, index):
        """Przetwarza pojedynczy wiersz danych"""
        if self.excel_data is None or index >= len(self.excel_data):
            return None
        
        row = self.excel_data.iloc[index]
        template_data = {}
        
        # Przygotuj dane do szablonów
        for field, col_name in self.column_mapping.items():
            if col_name in row:
                if field == 'kwota':
                    try:
                        kwota_value = float(str(row[col_name]).replace(',', '.'))
                        template_data[field] = f"{kwota_value:.2f}".replace('.', ',')
                    except (ValueError, TypeError):
                        template_data[field] = str(row[col_name])
                else:
                    template_data[field] = str(row[col_name])
            else:
                template_data[field] = ""
        
        # Dodaj data_faktury do template_data (nawet jeśli nie jest zmapowane)
        if 'data_faktury' in self.column_mapping:
            data_faktury_col = self.column_mapping['data_faktury']
            if data_faktury_col in row:
                template_data['data_faktury'] = str(row[data_faktury_col])
            else:
                template_data['data_faktury'] = ""
        else:
            template_data['data_faktury'] = ""
        
        # Oblicz dni po terminie
        template_data['dni_po_terminie'] = self.calculate_days_overdue(row)
        
        return template_data
    
    def calculate_days_overdue(self, row):
        """Oblicza dni po terminie na podstawie daty faktury"""
        if 'data_faktury' not in self.column_mapping:
            return ""
        
        data_faktury_col = self.column_mapping['data_faktury']
        if data_faktury_col not in row:
            return ""
        
        try:
            data_faktury_str = str(row[data_faktury_col])
            for fmt in ['%Y-%m-%d', '%d.%m.%Y', '%Y/%m/%d', '%d/%m/%Y']:
                try:
                    data_faktury = datetime.strptime(data_faktury_str, fmt)
                    return str((datetime.now() - data_faktury).days)
                except ValueError:
                    continue
            return "Błąd daty"
        except Exception:
            return "Błąd daty"
    
    def get_preview_data(self):
        """Zwraca dane do podglądu"""
        if self.excel_data is None:
            return []
        
        preview_data = []
        for index, row in self.excel_data.iterrows():
            try:
                template_data = self.process_row(index)
                if template_data:
                    values = (
                        template_data.get('kontrahent', ''),
                        template_data.get('nip', ''),
                        template_data.get('nr_faktury', ''),
                        template_data.get('email', ''),
                        template_data.get('telefon', ''),
                        template_data.get('kwota', ''),
                        template_data.get('dni_po_terminie', '')
                    )
                    preview_data.append((values, index))
            except Exception as e:
                self.logger.error(f"Błąd przetwarzania wiersza {index}: {e}")
        
        return preview_data
    
    def validate_mapping(self, required_fields):
        """Sprawdza czy mapowanie zawiera wymagane pola"""
        missing_fields = []
        for field in required_fields:
            if field not in self.column_mapping or not self.column_mapping[field]:
                missing_fields.append(field)
        return missing_fields
    
    def get_row_by_index(self, index):
        """Zwraca wiersz danych po indeksie"""
        if self.excel_data is not None and 0 <= index < len(self.excel_data):
            return self.excel_data.iloc[index]
        return None
    
    def search_rows(self, search_term, column_name):
        """Wyszukuje wiersze zawierające określony termin"""
        if self.excel_data is None or column_name not in self.excel_data.columns:
            return []
        
        matching_rows = []
        for index, row in self.excel_data.iterrows():
            if search_term.lower() in str(row[column_name]).lower():
                matching_rows.append(index)
        
        return matching_rows 
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
        """Wczytuje plik Excel/CSV - maksymalnie elastycznie"""
        try:
            if file_path.endswith(('.xlsx', '.xls')):
                # Excel - próbuj różne opcje
                try:
                    # Najpierw spróbuj z openpyxl (nowsze pliki)
                    self.excel_data = pd.read_excel(file_path, engine='openpyxl')
                    self.logger.info("Wczytano Excel z silnikiem openpyxl")
                except Exception as e:
                    self.logger.debug(f"openpyxl nie zadziałał: {e}")
                    try:
                        # Spróbuj z xlrd (starsze pliki)
                        self.excel_data = pd.read_excel(file_path, engine='xlrd')
                        self.logger.info("Wczytano Excel z silnikiem xlrd")
                    except Exception as e:
                        self.logger.debug(f"xlrd nie zadziałał: {e}")
                        try:
                            # Spróbuj bez określania engine
                            self.excel_data = pd.read_excel(file_path)
                            self.logger.info("Wczytano Excel z domyślnym silnikiem")
                        except Exception as e:
                            self.logger.debug(f"Domyślny silnik nie zadziałał: {e}")
                            
                            # Ostateczna próba - wczytaj pierwszy arkusz
                            try:
                                excel_file = pd.ExcelFile(file_path)
                                sheet_names = excel_file.sheet_names
                                if sheet_names:
                                    self.excel_data = pd.read_excel(file_path, sheet_name=sheet_names[0])
                                    self.logger.info(f"Wczytano Excel z arkusza: {sheet_names[0]}")
                                else:
                                    raise Exception("Brak arkuszy w pliku Excel")
                            except Exception as e:
                                self.logger.error(f"Wszystkie próby wczytania Excel nie powiodły się: {e}")
                                return False
                        
            elif file_path.endswith('.csv'):
                # CSV - maksymalnie elastyczne wczytywanie
                # Próbuj różne kombinacje parametrów
                success = False
                
                # Kombinacja 1: Standardowe ustawienia
                try:
                    self.excel_data = pd.read_csv(
                        file_path, 
                        encoding='utf-8',
                        on_bad_lines='skip',
                        error_bad_lines=False,
                        engine='python'
                    )
                    success = True
                    self.logger.info("Wczytano CSV z domyślnymi ustawieniami")
                except Exception as e:
                    self.logger.debug(f"Standardowe ustawienia nie zadziałały: {e}")
                
                # Kombinacja 2: Różne kodowania
                if not success:
                    encodings = ['windows-1250', 'cp1250', 'latin-1', 'iso-8859-2']
                    for encoding in encodings:
                        try:
                            self.excel_data = pd.read_csv(
                                file_path, 
                                encoding=encoding,
                                on_bad_lines='skip',
                                error_bad_lines=False,
                                engine='python'
                            )
                            success = True
                            self.logger.info(f"Wczytano CSV z kodowaniem {encoding}")
                            break
                        except Exception as e:
                            self.logger.debug(f"Kodowanie {encoding} nie zadziałało: {e}")
                
                # Kombinacja 3: Różne separatory
                if not success:
                    separators = [';', '\t', '|', ' ']
                    for sep in separators:
                        try:
                            self.excel_data = pd.read_csv(
                                file_path, 
                                encoding='utf-8',
                                sep=sep,
                                on_bad_lines='skip',
                                error_bad_lines=False,
                                engine='python'
                            )
                            success = True
                            self.logger.info(f"Wczytano CSV z separatorem '{sep}'")
                            break
                        except Exception as e:
                            self.logger.debug(f"Separator '{sep}' nie zadziałał: {e}")
                
                # Kombinacja 3b: Średnik z polskim kodowaniem (najczęstszy przypadek)
                if not success:
                    try:
                        self.excel_data = pd.read_csv(
                            file_path, 
                            encoding='windows-1250',
                            sep=';',
                            on_bad_lines='skip',
                            error_bad_lines=False,
                            engine='python',
                            quotechar=None,  # Ignoruj cudzysłowy
                            quoting=3  # QUOTE_NONE
                        )
                        success = True
                        self.logger.info("Wczytano CSV z polskim kodowaniem i separatorem średnika")
                    except Exception as e:
                        self.logger.debug(f"Polskie kodowanie ze średnikiem nie zadziałało: {e}")
                
                # Kombinacja 4: Ostatnia szansa - wszystko razem
                if not success:
                    try:
                        self.excel_data = pd.read_csv(
                            file_path, 
                            encoding='latin-1',
                            sep=';',
                            on_bad_lines='skip',
                            error_bad_lines=False,
                            engine='python',
                            quoting=3  # QUOTE_NONE
                        )
                        success = True
                        self.logger.info("Wczytano CSV z ostatecznymi ustawieniami")
                    except Exception as e:
                        self.logger.debug(f"Ostateczne ustawienia nie zadziałały: {e}")
                
                # Kombinacja 5: Ostateczna próba - wczytaj jako tekst i przetwórz
                if not success:
                    try:
                        with open(file_path, 'r', encoding='windows-1250', errors='ignore') as f:
                            lines = f.readlines()
                        
                        if len(lines) > 0:
                            # Podziel pierwszy wiersz na kolumny
                            header = lines[0].strip().split(';')
                            
                            # Utwórz DataFrame z wierszami
                            data_rows = []
                            for line in lines[1:]:
                                if line.strip():
                                    # Usuń cudzysłowy i podziel na kolumny
                                    clean_line = line.strip().replace('"', '').replace('"', '')
                                    row_data = clean_line.split(';')
                                    
                                    # Uzupełnij brakujące kolumny
                                    while len(row_data) < len(header):
                                        row_data.append('')
                                    # Skróć jeśli za dużo kolumn
                                    row_data = row_data[:len(header)]
                                    
                                    # Sprawdź czy kwota nie jest 0 (pomiń wiersze z zerową kwotą)
                                    try:
                                        # Szukaj kolumny z kwotą (Netto, Kwota płatności, itp.)
                                        kwota_kol = None
                                        for i, col_name in enumerate(header):
                                            if any(keyword in col_name.lower() for keyword in ['netto', 'kwota', 'wartość', 'brutto']):
                                                kwota_kol = i
                                                break
                                        
                                        if kwota_kol is not None and kwota_kol < len(row_data):
                                            kwota_str = str(row_data[kwota_kol]).replace(',', '.').replace(' ', '')
                                            if kwota_str and kwota_str != '0' and kwota_str != '0.0':
                                                data_rows.append(row_data)
                                            else:
                                                self.logger.debug(f"Pominięto wiersz z zerową kwotą: {row_data[kwota_kol]}")
                                        else:
                                            # Jeśli nie ma kolumny kwoty, dodaj wiersz
                                            data_rows.append(row_data)
                                    except:
                                        # W przypadku błędu, dodaj wiersz
                                        data_rows.append(row_data)
                            
                            # Utwórz DataFrame
                            self.excel_data = pd.DataFrame(data_rows, columns=header)
                            success = True
                            self.logger.info(f"Wczytano CSV jako tekst: {len(self.excel_data)} wierszy, {len(header)} kolumn")
                    except Exception as e:
                        self.logger.debug(f"Wczytywanie jako tekst nie zadziałało: {e}")
                
                if not success:
                    self.logger.error("Wszystkie próby wczytania CSV nie powiodły się")
                    return False
                
            else:
                raise ValueError("Nieobsługiwany format pliku")
            
            # Sprawdź czy dane zostały wczytane
            if self.excel_data is None or len(self.excel_data) == 0:
                self.logger.error("Plik został wczytany, ale nie zawiera danych")
                return False
            
            # Usuń wiersze z zerową kwotą
            self.filter_zero_amount_rows()
            
            # Wyczyść dane - usuń puste wiersze i kolumny
            self.clean_data()
            
            # Automatycznie spróbuj zmapować kolumny
            if self.apply_smart_mapping():
                self.logger.info("Automatycznie zmapowano kolumny")
                # Normalizuj dane po mapowaniu
                self.normalize_data()
            else:
                self.logger.info("Nie udało się automatycznie zmapować kolumn - wymagane ręczne mapowanie")
            
            self.logger.info(f"Wczytano plik: {file_path}")
            self.logger.info(f"Liczba wierszy: {len(self.excel_data)}")
            self.logger.info(f"Kolumny: {list(self.excel_data.columns)}")
            self.logger.info(f"Mapowanie kolumn: {self.column_mapping}")
            
            return True
        except Exception as e:
            self.logger.error(f"Błąd wczytywania pliku: {e}")
            return False
    
    def filter_zero_amount_rows(self):
        """Usuwa wiersze z zerową kwotą"""
        if self.excel_data is None:
            return
        
        try:
            initial_count = len(self.excel_data)
            
            # Znajdź kolumnę z kwotą
            kwota_column = None
            for col in self.excel_data.columns:
                if any(keyword in col.lower() for keyword in ['netto', 'kwota', 'wartość', 'brutto']):
                    kwota_column = col
                    break
            
            if kwota_column:
                # Usuń wiersze z zerową kwotą
                self.excel_data = self.excel_data[
                    (self.excel_data[kwota_column].astype(str).str.replace(',', '.').str.replace(' ', '') != '0') &
                    (self.excel_data[kwota_column].astype(str).str.replace(',', '.').str.replace(' ', '') != '0.0') &
                    (self.excel_data[kwota_column].astype(str).str.strip() != '')
                ]
                
                # Resetuj indeksy
                self.excel_data = self.excel_data.reset_index(drop=True)
                
                removed_count = initial_count - len(self.excel_data)
                if removed_count > 0:
                    self.logger.info(f"Usunięto {removed_count} wierszy z zerową kwotą")
            
        except Exception as e:
            self.logger.error(f"Błąd podczas filtrowania wierszy z zerową kwotą: {e}")
    
    def clean_data(self):
        """Czyści wczytane dane - usuwa puste wiersze i kolumny"""
        if self.excel_data is None:
            return
        
        try:
            # Usuń kolumny, które są całkowicie puste
            self.excel_data = self.excel_data.dropna(axis=1, how='all')
            
            # Usuń wiersze, które są całkowicie puste
            self.excel_data = self.excel_data.dropna(axis=0, how='all')
            
            # Usuń kolumny z samymi pustymi stringami
            for col in self.excel_data.columns:
                if self.excel_data[col].astype(str).str.strip().eq('').all():
                    self.excel_data = self.excel_data.drop(columns=[col])
            
            # Resetuj indeksy po usunięciu wierszy
            self.excel_data = self.excel_data.reset_index(drop=True)
            
            # Wyczyść nazwy kolumn - usuń białe znaki
            self.excel_data.columns = self.excel_data.columns.str.strip()
            
            self.logger.info(f"Wyczyszczono dane: {len(self.excel_data)} wierszy, {len(self.excel_data.columns)} kolumn")
        except Exception as e:
            self.logger.error(f"Błąd podczas czyszczenia danych: {e}")
    
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
    
    def auto_map_columns(self):
        """Automatycznie mapuje kolumny na podstawie nazw"""
        if self.excel_data is None:
            return {}
        
        auto_mapping = {}
        columns = [col.lower().strip() for col in self.excel_data.columns]
        
        # Słownik mapowań nazw kolumn
        field_mappings = {
                             'kontrahent': ['kontrahent', 'nazwa', 'nazwa firmy', 'firma', 'klient', 'odbiorca', 'odbiorca płatności', 'kontrahent'],
            'nip': ['nip', 'numer nip', 'tax id', 'identyfikator podatkowy'],
            'nr_faktury': ['nr faktury', 'numer faktury', 'faktura', 'nr', 'numer', 'invoice', 'invoice number'],
                             'email': ['email', 'e-mail', 'adres email', 'mail', 'e-mail adres', 'EMAIL'],
                             'telefon': ['telefon', 'phone', 'tel', 'numer telefonu', 'phone number', 'telefon komórkowy', 'telefon komorkowy'],
                             'kwota': ['kwota', 'amount', 'suma', 'wartość', 'kwota brutto', 'brutto', 'netto', 'kwota netto', 'kwota płatności'],
                 'data_faktury': ['data faktury', 'data', 'data wystawienia', 'data utworzenia', 'date', 'invoice date', 'wystawienia', 'data'],
                 'nr_faktury': ['nr faktury', 'numer faktury', 'faktura', 'nr', 'numer', 'invoice', 'invoice number', 'numer']
        }
        
        # Mapuj każdą kolumnę
        for field, possible_names in field_mappings.items():
            for col_name in possible_names:
                if col_name in columns:
                    # Znajdź oryginalną nazwę kolumny (z zachowaniem wielkości liter)
                    for orig_col in self.excel_data.columns:
                        if orig_col.lower().strip() == col_name:
                            auto_mapping[field] = orig_col
                            break
                    if field in auto_mapping:
                        break
        
        self.logger.info(f"Automatyczne mapowanie kolumn: {auto_mapping}")
        return auto_mapping
    
    def suggest_column_mapping(self):
        """Sugeruje mapowanie kolumn na podstawie zawartości"""
        if self.excel_data is None:
            return {}
        
        suggestions = {}
        
        # Analizuj zawartość kolumn
        for col in self.excel_data.columns:
            col_lower = col.lower()
            
            # Sprawdź czy kolumna zawiera NIP (10 cyfr)
            if self.excel_data[col].astype(str).str.match(r'^\d{10}$').any():
                suggestions['nip'] = col
                continue
            
            # Sprawdź czy kolumna zawiera emaile
            if self.excel_data[col].astype(str).str.contains(r'@').any():
                suggestions['email'] = col
                continue
            
            # Sprawdź czy kolumna zawiera telefony
            if self.excel_data[col].astype(str).str.match(r'[\d\s\+\-\(\)]+').any():
                suggestions['telefon'] = col
                continue
            
            # Sprawdź czy kolumna zawiera kwoty
            if self.excel_data[col].astype(str).str.match(r'[\d\.,]+').any():
                suggestions['kwota'] = col
                continue
        
        self.logger.info(f"Sugestie mapowania kolumn: {suggestions}")
        return suggestions
    
    def get_smart_column_mapping(self):
        """Łączy automatyczne mapowanie z sugestiami na podstawie zawartości"""
        if self.excel_data is None:
            return {}
        
        # Najpierw automatyczne mapowanie na podstawie nazw
        auto_mapping = self.auto_map_columns()
        
        # Dodaj sugestie na podstawie zawartości dla brakujących pól
        suggestions = self.suggest_column_mapping()
        
        # Połącz mapowania
        final_mapping = auto_mapping.copy()
        
        for field, col in suggestions.items():
            if field not in final_mapping:
                final_mapping[field] = col
        
        self.logger.info(f"Inteligentne mapowanie kolumn: {final_mapping}")
        return final_mapping
    
    def apply_smart_mapping(self):
        """Automatycznie aplikuje inteligentne mapowanie kolumn"""
        smart_mapping = self.get_smart_column_mapping()
        if smart_mapping:
            self.set_column_mapping(smart_mapping)
            return True
        return False
    
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
            
            # Rozszerzone formaty dat
            date_formats = [
                '%Y-%m-%d', '%d.%m.%Y', '%Y/%m/%d', '%d/%m/%Y',
                '%d-%m-%Y', '%Y.%m.%d', '%d/%m/%y', '%y/%m/%d',
                '%d.%m.%y', '%y.%m.%d', '%d-%m-%y', '%y-%m-%d',
                '%Y.%m.%d', '%d.%m.%Y', '%Y-%m-%d %H:%M:%S',
                '%d.%m.%Y %H:%M:%S', '%Y/%m/%d %H:%M:%S'
            ]
            
            for fmt in date_formats:
                try:
                    data_faktury = datetime.strptime(data_faktury_str.strip(), fmt)
                    return str((datetime.now() - data_faktury).days)
                except ValueError:
                    continue
            
            # Jeśli żaden format nie zadziałał, spróbuj pandas
            try:
                import pandas as pd
                data_faktury = pd.to_datetime(data_faktury_str, errors='coerce')
                if pd.notna(data_faktury):
                    return str((datetime.now() - data_faktury.to_pydatetime()).days)
            except:
                pass
            
            return "Błąd daty"
        except Exception:
            return "Błąd daty"
    
    def get_preview_data(self, rows=None):
        """Zwraca dane do podglądu (domyślnie wszystkie wiersze)"""
        if self.excel_data is None:
            return []
        
        try:
            # Jeśli rows nie jest podane, zwróć wszystkie wiersze
            if rows is None:
                rows = len(self.excel_data)
            
            # Zwróć przetworzone dane z mapowaniem
            preview_data = []
            for i in range(min(rows, len(self.excel_data))):
                template_data = self.process_row(i)
                if template_data:
                    preview_data.append(template_data)
            return preview_data
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania podglądu: {e}")
            return []
    
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
    
    def diagnose_csv_file(self, file_path):
        """Diagnozuje problemy z plikiem CSV"""
        try:
            # Spróbuj różne kodowania
            lines = None
            encodings_to_try = ['windows-1250', 'cp1250', 'utf-8', 'latin-1']
            
            for encoding in encodings_to_try:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        lines = f.readlines()
                    self.logger.info(f"Pomyślnie odczytano plik z kodowaniem: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            
            if lines is None:
                self.logger.error("Nie udało się odczytać pliku z żadnym kodowaniem")
                return None
            
            diagnosis = {
                'total_lines': len(lines),
                'line_lengths': [],
                'encoding_issues': [],
                'separator_issues': []
            }
            
            for i, line in enumerate(lines[:10]):  # Sprawdź pierwsze 10 linii
                line = line.strip()
                diagnosis['line_lengths'].append(len(line))
                
                # Sprawdź różne separatory
                comma_count = line.count(',')
                semicolon_count = line.count(';')
                tab_count = line.count('\t')
                
                if i == 0:  # Nagłówek
                    diagnosis['header_separators'] = {
                        'comma': comma_count,
                        'semicolon': semicolon_count,
                        'tab': tab_count
                    }
                
                # Sprawdź czy liczba kolumn jest spójna
                if i > 0:  # Pomijamy nagłówek
                    expected_columns = diagnosis['line_lengths'][0]
                    if abs(len(line) - expected_columns) > 5:  # Tolerancja
                        diagnosis['separator_issues'].append(f"Linia {i+1}: różna liczba kolumn")
            
            self.logger.info(f"Diagnoza pliku CSV: {diagnosis}")
            return diagnosis
            
        except Exception as e:
            self.logger.error(f"Błąd podczas diagnozy pliku: {e}")
            return None
    
    def normalize_data(self):
        """Normalizuje dane po mapowaniu kolumn"""
        if self.excel_data is None or not self.column_mapping:
            return
        
        try:
            # Normalizuj kwoty
            if 'kwota' in self.column_mapping:
                kwota_col = self.column_mapping['kwota']
                if kwota_col in self.excel_data.columns:
                    # Usuń spacje, waluty i inne znaki
                    self.excel_data[kwota_col] = self.excel_data[kwota_col].astype(str).str.replace(' ', '')
                    self.excel_data[kwota_col] = self.excel_data[kwota_col].str.replace('zł', '').str.replace('PLN', '')
                    self.excel_data[kwota_col] = self.excel_data[kwota_col].str.replace('€', '').str.replace('EUR', '')
                    self.excel_data[kwota_col] = self.excel_data[kwota_col].str.replace('$', '').str.replace('USD', '')
                    
                    # Obsłuż różne separatory dziesiętne
                    # Sprawdź czy używa przecinka czy kropki jako separatora dziesiętnego
                    sample_values = self.excel_data[kwota_col].dropna().astype(str)
                    if len(sample_values) > 0:
                        # Jeśli większość wartości ma przecinek, to prawdopodobnie przecinek to separator dziesiętny
                        comma_count = sample_values.str.count(',').sum()
                        dot_count = sample_values.str.count('.').sum()
                        
                        if comma_count > dot_count:
                            # Przecinek to separator dziesiętny, zamień na kropkę
                            self.excel_data[kwota_col] = self.excel_data[kwota_col].str.replace(',', '.')
                        else:
                            # Kropka to separator dziesiętny, usuń przecinki (separatory tysięcy)
                            self.excel_data[kwota_col] = self.excel_data[kwota_col].str.replace(',', '')
                    
                    # Konwertuj na liczby
                    self.excel_data[kwota_col] = pd.to_numeric(self.excel_data[kwota_col], errors='coerce')
            
            # Normalizuj NIP
            if 'nip' in self.column_mapping:
                nip_col = self.column_mapping['nip']
                if nip_col in self.excel_data.columns:
                    # Usuń spacje i myślniki
                    self.excel_data[nip_col] = self.excel_data[nip_col].astype(str).str.replace(' ', '').str.replace('-', '')
            
            # Normalizuj telefony
            if 'telefon' in self.column_mapping:
                tel_col = self.column_mapping['telefon']
                if tel_col in self.excel_data.columns:
                    # Usuń spacje i dodaj +48 jeśli brak kodu kraju
                    self.excel_data[tel_col] = self.excel_data[tel_col].astype(str).str.replace(' ', '')
                    # Dodaj +48 jeśli numer zaczyna się od 0
                    self.excel_data[tel_col] = self.excel_data[tel_col].apply(
                        lambda x: '+48' + x[1:] if str(x).startswith('0') and len(str(x)) == 9 else x
                    )
            
            # Normalizuj emaile
            if 'email' in self.column_mapping:
                email_col = self.column_mapping['email']
                if email_col in self.excel_data.columns:
                    # Konwertuj na małe litery
                    self.excel_data[email_col] = self.excel_data[email_col].astype(str).str.lower()
            
            self.logger.info("Dane zostały znormalizowane")
            
        except Exception as e:
            self.logger.error(f"Błąd podczas normalizacji danych: {e}")
    
    def get_mapping_summary(self):
        """Zwraca podsumowanie mapowania kolumn"""
        if not self.column_mapping:
            return "Brak mapowania kolumn"
        
        summary = "Mapowanie kolumn:\n"
        for field, col in self.column_mapping.items():
            summary += f"  {field} -> {col}\n"
        
        return summary
    
    def get_excel_sheets(self, file_path):
        """Zwraca listę dostępnych arkuszy w pliku Excel"""
        try:
            if file_path.endswith(('.xlsx', '.xls')):
                excel_file = pd.ExcelFile(file_path)
                return excel_file.sheet_names
            return []
        except Exception as e:
            self.logger.error(f"Błąd podczas odczytu arkuszy Excel: {e}")
            return []
    
    def load_excel_sheet(self, file_path, sheet_name):
        """Wczytuje konkretny arkusz z pliku Excel"""
        try:
            if file_path.endswith(('.xlsx', '.xls')):
                self.excel_data = pd.read_excel(file_path, sheet_name=sheet_name)
                self.clean_data()
                
                # Automatycznie spróbuj zmapować kolumny
                if self.apply_smart_mapping():
                    self.logger.info(f"Automatycznie zmapowano kolumny dla arkusza: {sheet_name}")
                    self.normalize_data()
                
                self.logger.info(f"Wczytano arkusz Excel: {sheet_name}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Błąd podczas wczytywania arkusza {sheet_name}: {e}")
            return False
    
    def get_file_info(self, file_path):
        """Zwraca informacje o pliku"""
        info = {
            'file_type': 'unknown',
            'sheets': [],
            'columns': [],
            'rows': 0,
            'encoding': 'unknown',
            'separator': 'unknown'
        }
        
        try:
            if file_path.endswith(('.xlsx', '.xls')):
                info['file_type'] = 'excel'
                info['sheets'] = self.get_excel_sheets(file_path)
                if info['sheets']:
                    # Wczytaj pierwszy arkusz dla informacji
                    self.load_excel_sheet(file_path, info['sheets'][0])
                    info['columns'] = list(self.excel_data.columns) if self.excel_data is not None else []
                    info['rows'] = len(self.excel_data) if self.excel_data is not None else 0
                    
            elif file_path.endswith('.csv'):
                info['file_type'] = 'csv'
                # Wczytaj plik dla informacji
                if self.load_excel_file(file_path):
                    info['columns'] = list(self.excel_data.columns) if self.excel_data is not None else []
                    info['rows'] = len(self.excel_data) if self.excel_data is not None else 0
                    
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania informacji o pliku: {e}")
        
        return info
    
    def reset_mapping(self):
        """Resetuje mapowanie kolumn"""
        self.column_mapping = {}
        self.logger.info("Mapowanie kolumn zostało zresetowane")
    
    def reload_file(self, file_path):
        """Ponownie wczytuje plik z resetowaniem mapowania"""
        self.reset_mapping()
        return self.load_excel_file(file_path)
    
    def force_column_mapping(self, field, column_name):
        """Wymusza mapowanie konkretnej kolumny"""
        if self.excel_data is not None and column_name in self.excel_data.columns:
            self.column_mapping[field] = column_name
            self.logger.info(f"Wymuszone mapowanie: {field} -> {column_name}")
            return True
        else:
            self.logger.warning(f"Nie można zmapować {field} na {column_name} - kolumna nie istnieje")
            return False
    
    def get_unmapped_columns(self):
        """Zwraca kolumny, które nie są zmapowane"""
        if self.excel_data is None:
            return []
        
        mapped_columns = set(self.column_mapping.values())
        all_columns = set(self.excel_data.columns)
        return list(all_columns - mapped_columns)
    
    def get_mapping_coverage(self):
        """Zwraca procent pokrycia mapowania kolumn"""
        if self.excel_data is None or len(self.excel_data.columns) == 0:
            return 0.0
        
        mapped_count = len(self.column_mapping)
        total_count = len(self.excel_data.columns)
        return (mapped_count / total_count) * 100.0
    
    def remove_settled_items(self):
        """Usuwa pozycje z kwotą równą lub mniejszą od zera (rozliczone)"""
        if self.excel_data is None:
            return 0
        
        try:
            initial_count = len(self.excel_data)
            
            # Użyj zmapowanej kolumny kwota, jeśli istnieje
            kwota_column = None
            if 'kwota' in self.column_mapping:
                kwota_column = self.column_mapping['kwota']
                self.logger.info(f"Używam zmapowanej kolumny kwoty: {kwota_column}")
            else:
                # Fallback: znajdź kolumnę z kwotą po słowach kluczowych
                for col in self.excel_data.columns:
                    if any(keyword in col.lower() for keyword in ['netto', 'kwota', 'wartość', 'brutto']):
                        kwota_column = col
                        break
                if kwota_column:
                    self.logger.info(f"Znaleziono kolumnę kwoty (fallback): {kwota_column}")
            
            if kwota_column:
                # Przygotuj dane do filtrowania - usuń białe znaki i zamień przecinki na kropki
                cleaned_values = self.excel_data[kwota_column].astype(str).str.strip().str.replace(',', '.')
                
                # Usuń wiersze z kwotą ≤ 0
                # Najpierw spróbuj przekonwertować na liczby
                numeric_values = pd.to_numeric(cleaned_values, errors='coerce')
                
                # Filtruj wiersze gdzie kwota > 0 (nie NaN i > 0)
                self.excel_data = self.excel_data[
                    (numeric_values > 0) & (numeric_values.notna())
                ]
                
                # Resetuj indeksy
                self.excel_data = self.excel_data.reset_index(drop=True)
                
                removed_count = initial_count - len(self.excel_data)
                if removed_count > 0:
                    self.logger.info(f"Usunięto {removed_count} pozycji rozliczonych (kwota ≤ 0)")
                    self.logger.info(f"Pozostało {len(self.excel_data)} pozycji")
                else:
                    self.logger.info("Nie znaleziono pozycji rozliczonych do usunięcia")
                
                return removed_count
            else:
                self.logger.warning("Nie znaleziono kolumny z kwotą do usunięcia pozycji rozliczonych")
                return 0
            
        except Exception as e:
            self.logger.error(f"Błąd podczas usuwania pozycji rozliczonych: {e}")
            return 0
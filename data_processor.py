"""
Moduł do przetwarzania danych Excel/CSV
"""
import pandas as pd
from datetime import datetime
import logging

class DataProcessor:
    """Klasa do przetwarzania danych z plików Excel/CSV"""
    
    def __init__(self):
        """Inicjalizuje DataProcessor"""
        self.excel_data = None
        self.column_mapping = {}  # Inicjalizuj mapowanie kolumn
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
                        
                # Wyczyść dane po wczytaniu
                self.clean_data()
                
                # Wymuś inteligentne mapowanie kolumn
                self.force_smart_mapping_for_specific_data()
                
                return True
            
            elif file_path.endswith('.csv'):
                # CSV - maksymalnie elastyczne wczytywanie
                # Próbuj różne kombinacje parametrów
                success = False
                
                # Próba 1: Standardowe wczytywanie CSV z UTF-8
                try:
                    self.excel_data = pd.read_csv(
                        file_path, 
                        encoding='utf-8', 
                        sep=';',  # Użyj średnika jako separatora
                        on_bad_lines='skip',
                        engine='python'
                    )
                    success = True
                    self.logger.info("Wczytano CSV z UTF-8 i separatorem ';'")
                except Exception as e:
                    self.logger.debug(f"Wczytywanie z UTF-8 i ';' nie zadziałało: {e}")
                
                # Próba 2: CSV z Windows-1250 i separatorem ';'
                if not success:
                    try:
                        self.excel_data = pd.read_csv(
                            file_path, 
                            encoding='windows-1250', 
                            sep=';',
                            on_bad_lines='skip',
                            engine='python'
                        )
                        success = True
                        self.logger.info("Wczytano CSV z Windows-1250 i separatorem ';'")
                    except Exception as e:
                        self.logger.debug(f"Wczytywanie z Windows-1250 i ';' nie zadziałało: {e}")
                
                # Próba 3: CSV z ISO-8859-2 i separatorem ';'
                if not success:
                    try:
                        self.excel_data = pd.read_csv(
                            file_path, 
                            encoding='iso-8859-2', 
                            sep=';',
                            on_bad_lines='skip',
                            engine='python'
                        )
                        success = True
                        self.logger.info("Wczytano CSV z ISO-8859-2 i separatorem ';'")
                    except Exception as e:
                        self.logger.debug(f"Wczytywanie z ISO-8859-2 i ';' nie zadziałało: {e}")
                
                # Próba 4: CSV z Latin-1 i separatorem ';'
                if not success:
                    try:
                        self.excel_data = pd.read_csv(
                            file_path, 
                            encoding='latin-1', 
                            sep=';',
                            on_bad_lines='skip',
                            engine='python'
                        )
                        success = True
                        self.logger.info("Wczytano CSV z Latin-1 i separatorem ';'")
                    except Exception as e:
                        self.logger.debug(f"Wczytywanie z Latin-1 i ';' nie zadziałało: {e}")
                
                # Próba 5: CSV z ignorowaniem cudzysłowów i separatorem ';'
                if not success:
                    try:
                        self.excel_data = pd.read_csv(
                            file_path, 
                            encoding='utf-8', 
                            sep=';',
                            quotechar=None,  # Ignoruj cudzysłowy
                            quoting=3,  # QUOTE_NONE
                            on_bad_lines='skip',
                            engine='python'
                        )
                        success = True
                        self.logger.info("Wczytano CSV z ignorowaniem cudzysłowów i separatorem ';'")
                    except Exception as e:
                        self.logger.debug(f"Wczytywanie z ignorowaniem cudzysłowów i ';' nie zadziałało: {e}")
                
                # Próba 6: CSV z automatycznym wykrywaniem kodowania i separatorem ';'
                if not success:
                    try:
                        self.excel_data = pd.read_csv(
                            file_path, 
                            encoding=None,  # Automatyczne wykrywanie
                            sep=';',
                            on_bad_lines='skip',
                            engine='python'
                        )
                        success = True
                        self.logger.info("Wczytano CSV z automatycznym kodowaniem i separatorem ';'")
                    except Exception as e:
                        self.logger.debug(f"Wczytywanie z automatycznym kodowaniem i ';' nie zadziałało: {e}")
                
                # Próba 7: CSV z różnymi separatorami (fallback)
                if not success:
                    try:
                        # Spróbuj automatycznie wykryć separator
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            first_line = f.readline()
                        
                        if ';' in first_line:
                            sep = ';'
                        elif ',' in first_line:
                            sep = ','
                        elif '\t' in first_line:
                            sep = '\t'
                        else:
                            sep = ';'  # Domyślny
                        
                        self.excel_data = pd.read_csv(
                            file_path, 
                            encoding='utf-8', 
                            sep=sep,
                            on_bad_lines='skip',
                            engine='python'
                        )
                        success = True
                        self.logger.info(f"Wczytano CSV z automatycznym separatorem '{sep}'")
                    except Exception as e:
                        self.logger.debug(f"Wczytywanie z automatycznym separatorem nie zadziałało: {e}")
                
                # Próba 8: Wczytywanie jako tekst i ręczne parsowanie
                if not success:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                        
                        # Ręczne parsowanie CSV
                        if lines:
                            headers = lines[0].strip().split(';')
                            data = []
                            for line in lines[1:]:
                                if line.strip():
                                    # Podziel linię na kolumny, ale uwzględnij cudzysłowy
                                    row_data = []
                                    current_field = ""
                                    in_quotes = False
                                    
                                    for char in line:
                                        if char == '"':
                                            in_quotes = not in_quotes
                                        elif char == ';' and not in_quotes:
                                            row_data.append(current_field.strip())
                                            current_field = ""
                                        else:
                                            current_field += char
                                    
                                    # Dodaj ostatnie pole
                                    row_data.append(current_field.strip())
                                    
                                    # Uzułnij brakujące kolumny
                                    while len(row_data) < len(headers):
                                        row_data.append("")
                                    
                                    data.append(row_data[:len(headers)])
                            
                            self.excel_data = pd.DataFrame(data, columns=headers)
                            success = True
                            self.logger.info("Wczytano CSV ręcznym parsowaniem")
                    except Exception as e:
                        self.logger.debug(f"Ręczne parsowanie nie zadziałało: {e}")
                
                if not success:
                    self.logger.error("Wszystkie próby wczytania CSV nie powiodły się")
                    return False
                
                # Wyczyść dane po wczytaniu
                self.clean_data()
                
                return True
            
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
            
            # Wymuś inteligentne mapowanie kolumn
            self.force_smart_mapping_for_specific_data()
            
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
            
            # Usuń pozostałe cudzysłowy ze wszystkich kolumn tekstowych
            for col in self.excel_data.columns:
                if self.excel_data[col].dtype == 'object':  # Kolumny tekstowe
                    self.excel_data[col] = self.excel_data[col].astype(str).str.replace('"', '').str.replace('"', '')
            
            # Napraw problemy z kodowaniem
            self.fix_encoding_issues()
            
            # Sprawdź i popraw mapowanie kolumn
            self.check_and_fix_column_mapping()
            
            # Dodaj kolumnę z dniami po terminie (po ustawieniu mapowania)
            self.add_days_overdue_column()
            
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
            'kontrahent': ['kontrahent', 'nazwa', 'nazwa firmy', 'firma', 'klient', 'odbiorca', 'odbiorca płatności'],
            'nip': ['nip', 'numer nip', 'tax id', 'identyfikator podatkowy'],
            'nr_faktury': ['nr faktury', 'numer faktury', 'faktura', 'nr', 'numer', 'invoice', 'invoice number'],
            'email': ['email', 'e-mail', 'adres email', 'mail', 'e-mail adres', 'EMAIL'],
            'telefon': ['telefon', 'phone', 'tel', 'numer telefonu', 'phone number', 'telefon komórkowy', 'telefon komorkowy'],
            'kwota': ['kwota', 'amount', 'suma', 'wartość', 'kwota brutto', 'brutto', 'netto', 'kwota netto', 'kwota płatności'],
            'data_faktury': ['data faktury', 'data', 'data wystawienia', 'data utworzenia', 'date', 'invoice date', 'wystawienia'],
            'dni_po_terminie': ['dni po terminie', 'dni po', 'dni', 'termin', 'opóźnienie', 'dni opóźnienia']
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
            
            # Sprawdź czy kolumna zawiera telefony (9 cyfr)
            if self.excel_data[col].astype(str).str.match(r'^\d{9}$').any():
                suggestions['telefon'] = col
                continue
            
            # Sprawdź czy kolumna zawiera kwoty (liczby z przecinkami)
            if self.excel_data[col].astype(str).str.match(r'^\d+[,\.]\d{2}$').any():
                suggestions['kwota'] = col
                continue
            
            # Sprawdź czy kolumna zawiera daty (format DD.MM.YYYY)
            if self.excel_data[col].astype(str).str.match(r'^\d{2}\.\d{2}\.\d{4}$').any():
                suggestions['data_faktury'] = col
                continue
            
            # Sprawdź czy kolumna zawiera numery faktur (format XXX/XX/XXXX)
            if self.excel_data[col].astype(str).str.match(r'^\d+/\d+/\d{4}$').any():
                suggestions['nr_faktury'] = col
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
        """Oblicza dni po terminie płatności"""
        self.logger.info(f"=== WYWOŁANO calculate_days_overdue ===")
        self.logger.info(f"Typ row: {type(row)}")
        self.logger.info(f"Zawartość row: {row}")
        
        try:
            # Pobierz datę faktury - sprawdź typ i pobierz odpowiednio
            if isinstance(row, dict):
                # Jeśli row to słownik
                data_faktury = row.get('data_faktury', '')
                self.logger.info(f"Pobrano datę z dict['data_faktury']: '{data_faktury}'")
            elif hasattr(row, 'get') and hasattr(row, 'index'):
                # Jeśli row to pandas.Series, spróbuj pobrać z zmapowanej kolumny
                if 'data_faktury' in self.column_mapping:
                    col_name = self.column_mapping['data_faktury']
                    if col_name in row.index:
                        data_faktury = row[col_name]
                        self.logger.info(f"Pobrano datę z pandas.Series[{col_name}]: '{data_faktury}'")
                    else:
                        data_faktury = ''
                        self.logger.info(f"Kolumna {col_name} nie istnieje w pandas.Series")
                else:
                    data_faktury = ''
                    self.logger.info("Brak mapowania dla 'data_faktury'")
            else:
                # Nieznany typ
                data_faktury = ''
                self.logger.info(f"Nieznany typ row: {type(row)}")
            
            if not data_faktury or str(data_faktury).strip() == '' or str(data_faktury).lower() == 'nan':
                self.logger.info(f"Pusta data faktury: '{data_faktury}'")
                return 0
            
            # Konwertuj datę z formatu DD.MM.YYYY
            try:
                from datetime import datetime, timedelta
                data_obj = datetime.strptime(str(data_faktury).strip(), '%d.%m.%Y')
                
                # Dodaj 7 dni (termin płatności zgodnie z wymaganiami użytkownika)
                termin_platnosci = data_obj + timedelta(days=7)
                
                # Oblicz różnicę dni od dzisiaj
                dzisiaj = datetime.now()
                roznica = (dzisiaj - termin_platnosci).days
                
                # Dodaj debugowanie
                self.logger.info(f"Data faktury: {data_faktury} -> {data_obj}")
                self.logger.info(f"Termin płatności: {termin_platnosci}")
                self.logger.info(f"Dzisiaj: {dzisiaj}")
                self.logger.info(f"Różnica dni: {roznica}")
                
                return max(0, roznica)  # Zwróć 0 jeśli nie minął termin
                
            except ValueError:
                # Jeśli data jest w innym formacie, spróbuj inne formaty
                try:
                    data_obj = datetime.strptime(str(data_faktury).strip(), '%Y-%m-%d')
                    termin_platnosci = data_obj + timedelta(days=7)
                    dzisiaj = datetime.now()
                    roznica = (dzisiaj - termin_platnosci).days
                    return max(0, roznica)
                except ValueError:
                    self.logger.debug(f"Nie można sparsować daty: {data_faktury}")
                    return 0
                    
        except Exception as e:
            self.logger.debug(f"Błąd obliczania dni po terminie: {e}")
            return 0
    
    def add_days_overdue_column(self):
        """Dodaje kolumnę z dniami po terminie"""
        if self.excel_data is None:
            return False
        
        try:
            # Sprawdź czy kolumna już istnieje
            if 'dni_po_terminie' in self.excel_data.columns:
                self.logger.info("Kolumna dni_po_terminie już istnieje")
                return True
            
            # Dodaj kolumnę z dniami po terminie
            self.excel_data['dni_po_terminie'] = 0
            self.logger.info(f"Rozpoczynam obliczanie dni po terminie dla {len(self.excel_data)} wierszy")
            
            # Oblicz dni po terminie dla każdego wiersza
            for i in range(len(self.excel_data)):
                row_data = self.get_row_by_index(i)
                if row_data is not None:
                    self.logger.info(f"Przetwarzam wiersz {i}: {row_data.get('Data', 'BRAK DATY') if hasattr(row_data, 'get') else 'pandas.Series'}")
                    dni = self.calculate_days_overdue(row_data)
                    self.excel_data.at[i, 'dni_po_terminie'] = dni
                    self.logger.info(f"Wiersz {i}: dni_po_terminie = {dni}")
                else:
                    self.logger.warning(f"Wiersz {i}: row_data jest None")
            
            self.logger.info("Dodano kolumnę z dniami po terminie")
            return True
            
        except Exception as e:
            self.logger.error(f"Błąd podczas dodawania kolumny dni po terminie: {e}")
            return False
    
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
    
    def diagnose_specific_rows(self, search_terms):
        """Diagnozuje konkretne wiersze na podstawie nazw firm"""
        if self.excel_data is None:
            return {}
        
        results = {}
        for term in search_terms:
            mask = self.excel_data.astype(str).apply(lambda x: x.str.contains(term, case=False, na=False)).any(axis=1)
            matching_rows = self.excel_data[mask]
            results[term] = matching_rows.to_dict('records')
        
        return results
    
    def check_encoding_issues(self):
        """Sprawdza problemy z kodowaniem w danych"""
        if self.excel_data is None:
            return {}
        
        issues = {}
        
        # Sprawdź kolumny tekstowe pod kątem problemów z kodowaniem
        for col in self.excel_data.columns:
            if self.excel_data[col].dtype == 'object':
                # Sprawdź czy są jakieś dziwne znaki
                sample_values = self.excel_data[col].dropna().astype(str).head(20)
                problematic_chars = []
                
                for val in sample_values:
                    # Sprawdź czy są znaki, które mogą wskazywać na problemy z kodowaniem
                    if any(ord(char) > 127 for char in val):
                        # Znaki spoza ASCII - mogą być problematyczne
                        problematic_chars.append(val)
                
                if problematic_chars:
                    issues[col] = {
                        'sample_problematic': problematic_chars[:5],
                        'total_problematic': len(problematic_chars)
                    }
        
        return issues
    
    def fix_encoding_issues(self):
        """Naprawia problemy z kodowaniem w danych"""
        if self.excel_data is None:
            return False
        
        try:
            fixed = False
            
            # Napraw problemy z cudzysłowami i innymi znakami
            for col in self.excel_data.columns:
                if self.excel_data[col].dtype == 'object':
                    # Usuń problematyczne znaki
                    original_col = self.excel_data[col].copy()
                    
                    # Usuń cudzysłowy i inne problematyczne znaki
                    cleaned_col = self.excel_data[col].astype(str).str.replace('"', '').str.replace('"', '')
                    cleaned_col = cleaned_col.str.replace('', '')  # Usuń znaki zastępcze
                    cleaned_col = cleaned_col.str.replace('?', '')  # Usuń znaki zapytania
                    
                    # Sprawdź czy coś się zmieniło
                    if not (original_col == cleaned_col).all():
                        self.excel_data[col] = cleaned_col
                        fixed = True
                        self.logger.info(f"Naprawiono problemy z kodowaniem w kolumnie: {col}")
            
            if fixed:
                self.logger.info("Naprawiono problemy z kodowaniem w danych")
            else:
                self.logger.info("Nie znaleziono problemów z kodowaniem do naprawienia")
            
            return fixed
            
        except Exception as e:
            self.logger.error(f"Błąd podczas naprawiania problemów z kodowaniem: {e}")
            return False
    
    def get_mapping_summary(self):
        """Zwraca podsumowanie mapowania kolumn jako słownik"""
        if not hasattr(self, 'column_mapping') or not self.column_mapping:
            return {}
        
        summary = {}
        for field, col in self.column_mapping.items():
            # Oblicz pokrycie danych dla tej kolumny
            if self.excel_data is not None and col in self.excel_data.columns:
                non_empty_count = self.excel_data[col].notna().sum()
                total_count = len(self.excel_data)
                coverage = (non_empty_count / total_count) * 100 if total_count > 0 else 0
            else:
                coverage = 0
            
            summary[field] = {
                'mapped_to': col,
                'coverage': coverage
            }
        
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
        """Wymusza mapowanie konkretnego pola na konkretną kolumnę"""
        if self.excel_data is None or column_name not in self.excel_data.columns:
            return False
        
        if not hasattr(self, 'column_mapping'):
            self.column_mapping = {}
        
        self.column_mapping[field] = column_name
        self.logger.info(f"Wymuszone mapowanie: {field} -> {column_name}")
        return True
    
    def force_smart_mapping_for_specific_data(self):
        """Wymusza inteligentne mapowanie na podstawie analizy konkretnych danych"""
        if self.excel_data is None:
            return False
        
        # Analizuj dane i wymuś mapowanie
        forced_mapping = {}
        
        # Sprawdź każdą kolumnę
        for col in self.excel_data.columns:
            col_lower = col.lower()
            
            # Kontrahent - kolumna z nazwami firm
            if 'kontrahent' in col_lower:
                forced_mapping['kontrahent'] = col
                continue
            
            # NIP - kolumna z 10-cyfrowymi numerami
            if self.excel_data[col].astype(str).str.match(r'^\d{10}$').any():
                forced_mapping['nip'] = col
                continue
            
            # Email - kolumna z adresami email
            if self.excel_data[col].astype(str).str.contains(r'@').any():
                forced_mapping['email'] = col
                continue
            
            # Telefon - kolumna z 9-cyfrowymi numerami
            if self.excel_data[col].astype(str).str.match(r'^\d{9}$').any():
                forced_mapping['telefon'] = col
                continue
            
            # Kwota - kolumna z kwotami (liczby z przecinkami)
            if self.excel_data[col].astype(str).str.match(r'^\d+[,\.]\d{2}$').any():
                forced_mapping['kwota'] = col
                continue
            
            # Data - kolumna z datami w formacie DD.MM.YYYY
            if self.excel_data[col].astype(str).str.match(r'^\d{2}\.\d{2}\.\d{4}$').any():
                forced_mapping['data_faktury'] = col
                continue
            
            # Numer faktury - kolumna z numerami w formacie XXX/XX/XXXX
            if self.excel_data[col].astype(str).str.match(r'^\d+/\d+/\d{4}$').any():
                forced_mapping['nr_faktury'] = col
                continue
            
            # Sprawdź czy kolumna zawiera daty w różnych formatach
            if self.excel_data[col].astype(str).str.contains(r'\d{2}\.\d{2}\.\d{4}').any():
                forced_mapping['data_faktury'] = col
                continue
        
        # Aplikuj wymuszone mapowanie
        if forced_mapping:
            self.set_column_mapping(forced_mapping)
            self.logger.info(f"Wymuszone mapowanie kolumn: {forced_mapping}")
            
            # Sprawdź i popraw mapowanie kolumn
            self.check_and_fix_column_mapping()
            
            return True
        
        return False
    
    def check_and_fix_column_mapping(self):
        """Sprawdza i poprawia mapowanie kolumn"""
        if self.excel_data is None:
            return False
        
        try:
            # Sprawdź czy kolumna 'Data' jest zmapowana jako 'data_faktury'
            if 'Data' in self.excel_data.columns and 'data_faktury' not in self.column_mapping:
                self.force_column_mapping('data_faktury', 'Data')
                self.logger.info("Zmapowano kolumnę 'Data' jako 'data_faktury'")
            
            # Sprawdź czy kolumna 'Kontrahent' jest zmapowana
            if 'Kontrahent' in self.excel_data.columns and 'kontrahent' not in self.column_mapping:
                self.force_column_mapping('kontrahent', 'Kontrahent')
                self.logger.info("Zmapowano kolumnę 'Kontrahent' jako 'kontrahent'")
            
            # Sprawdź czy kolumna 'NIP' jest zmapowana
            if 'NIP' in self.excel_data.columns and 'nip' not in self.column_mapping:
                self.force_column_mapping('nip', 'NIP')
                self.logger.info("Zmapowano kolumnę 'NIP' jako 'nip'")
            
            # Sprawdź czy kolumna 'EMAIL' jest zmapowana
            if 'EMAIL' in self.excel_data.columns and 'email' not in self.column_mapping:
                self.force_column_mapping('email', 'EMAIL')
                self.logger.info("Zmapowano kolumnę 'EMAIL' jako 'email'")
            
            # Sprawdź czy kolumna 'Telefon komorkowy' jest zmapowana
            if 'Telefon komorkowy' in self.excel_data.columns and 'telefon' not in self.column_mapping:
                self.force_column_mapping('telefon', 'Telefon komorkowy')
                self.logger.info("Zmapowano kolumnę 'Telefon komorkowy' jako 'telefon'")
            
            # Sprawdź czy kolumna 'Netto' jest zmapowana jako 'kwota'
            if 'Netto' in self.excel_data.columns and 'kwota' not in self.column_mapping:
                self.force_column_mapping('kwota', 'Netto')
                self.logger.info("Zmapowano kolumnę 'Netto' jako 'kwota'")
            
            # Sprawdź czy kolumna 'Numer' jest zmapowana jako 'nr_faktury'
            if 'Numer' in self.excel_data.columns and 'nr_faktury' not in self.column_mapping:
                self.force_column_mapping('nr_faktury', 'Numer')
                self.logger.info("Zmapowano kolumnę 'Numer' jako 'nr_faktury'")
            
            # Sprawdź czy kolumna 'Kwota p?atno?ci' jest zmapowana jako 'kwota_platnosci'
            if 'Kwota p?atno?ci' in self.excel_data.columns and 'kwota_platnosci' not in self.column_mapping:
                self.force_column_mapping('kwota_platnosci', 'Kwota p?atno?ci')
                self.logger.info("Zmapowano kolumnę 'Kwota p?atno?ci' jako 'kwota_platnosci'")
            
            # Sprawdź czy kolumna 'VAT' jest zmapowana
            if 'VAT' in self.excel_data.columns and 'vat' not in self.column_mapping:
                self.force_column_mapping('vat', 'VAT')
                self.logger.info("Zmapowano kolumnę 'VAT' jako 'vat'")
            
            # Sprawdź czy kolumna 'Warto??/B' jest zmapowana jako 'wartosc_brutto'
            if 'Warto??/B' in self.excel_data.columns and 'wartosc_brutto' not in self.column_mapping:
                self.force_column_mapping('wartosc_brutto', 'Warto??/B')
                self.logger.info("Zmapowano kolumnę 'Warto??/B' jako 'wartosc_brutto'")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Błąd podczas sprawdzania i poprawiania mapowania: {e}")
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
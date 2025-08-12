"""
Moduł do przetwarzania danych Excel/CSV/TSV
"""
import pandas as pd
from datetime import datetime
import logging

class DataProcessor:
    """Klasa do przetwarzania danych z plików Excel/CSV/TSV"""
    
    def __init__(self):
        """Inicjalizuje DataProcessor"""
        self.excel_data = None
        self.column_mapping = {}  # Inicjalizuj mapowanie kolumn
        self.logger = logging.getLogger(__name__)
    
    def load_excel_file(self, file_path):
        """Wczytuje plik Excel/CSV/TSV - maksymalnie elastycznie"""
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
            
            elif file_path.endswith(('.csv', '.tsv')):
                # CSV/TSV - maksymalnie elastyczne wczytywanie z automatycznym wykrywaniem separatorów
                success = False
                
                # Najpierw spróbuj automatycznie wykryć separator i kodowanie
                detected_sep = self._detect_file_separator(file_path)
                detected_encoding = self._detect_file_encoding(file_path)
                
                self.logger.info(f"Wykryto separator: '{repr(detected_sep)}', kodowanie: {detected_encoding}")
                
                # Próba 1: Z wykrytymi parametrami
                try:
                    self.excel_data = pd.read_csv(
                        file_path, 
                        encoding=detected_encoding, 
                        sep=detected_sep,
                        on_bad_lines='skip',
                        engine='python'
                    )
                    success = True
                    self.logger.info(f"Wczytano plik z wykrytymi parametrami: separator='{detected_sep}', kodowanie={detected_encoding}")
                except Exception as e:
                    self.logger.debug(f"Wczytywanie z wykrytymi parametrami nie zadziałało: {e}")
                
                # Próba 1b: Z wykrytymi parametrami i obsługą BOM
                if not success and detected_encoding.startswith('utf-16'):
                    try:
                        self.excel_data = pd.read_csv(
                            file_path, 
                            encoding=detected_encoding, 
                            sep=detected_sep,
                            on_bad_lines='skip',
                            engine='python',
                            skiprows=1  # Pomiń pierwszą linię (może mieć BOM)
                        )
                        success = True
                        self.logger.info(f"Wczytano plik z wykrytymi parametrami i pominięciem BOM: separator='{detected_sep}', kodowanie={detected_encoding}")
                    except Exception as e:
                        self.logger.debug(f"Wczytywanie z pominięciem BOM nie zadziałało: {e}")
                
                # Próba 2: Z różnymi kodowaniami i wykrytym separatorem
                if not success:
                    encodings_to_try = ['utf-16-le', 'utf-16-be', 'utf-8', 'windows-1250', 'iso-8859-2', 'latin-1', 'cp1250']
                    for encoding in encodings_to_try:
                        try:
                            self.excel_data = pd.read_csv(
                                file_path, 
                                encoding=encoding, 
                                sep=detected_sep,
                                on_bad_lines='skip',
                                engine='python'
                            )
                            success = True
                            self.logger.info(f"Wczytano plik z kodowaniem {encoding} i separatorem '{detected_sep}'")
                            break
                        except Exception as e:
                            self.logger.debug(f"Wczytywanie z {encoding} i '{detected_sep}' nie zadziałało: {e}")
                
                # Próba 3: Z różnymi separatorami i UTF-8
                if not success:
                    separators_to_try = [';', ',', '\t', '|']
                    for sep in separators_to_try:
                        try:
                            self.excel_data = pd.read_csv(
                                file_path, 
                                encoding='utf-8', 
                                sep=sep,
                                on_bad_lines='skip',
                                engine='python'
                            )
                            success = True
                            self.logger.info(f"Wczytano plik z separatorem '{sep}' i UTF-8")
                            break
                        except Exception as e:
                            self.logger.debug(f"Wczytywanie z separatorem '{sep}' i UTF-8 nie zadziałało: {e}")
                
                # Próba 4: Ostateczna próba z automatycznym wykrywaniem
                if not success:
                    try:
                        self.excel_data = pd.read_csv(
                            file_path, 
                            encoding=None,  # Automatyczne wykrywanie kodowania
                            sep=None,       # Automatyczne wykrywanie separatora
                            on_bad_lines='skip',
                            engine='python'
                        )
                        success = True
                        self.logger.info("Wczytano plik z automatycznym wykrywaniem parametrów")
                    except Exception as e:
                        self.logger.debug(f"Automatyczne wykrywanie nie zadziałało: {e}")
                
                # Próba 5: Z ignorowaniem cudzysłowów
                if not success:
                    try:
                        self.excel_data = pd.read_csv(
                            file_path, 
                            encoding='utf-8', 
                            sep=detected_sep,
                            quotechar=None,  # Ignoruj cudzysłowy
                            quoting=3,       # QUOTE_NONE
                            on_bad_lines='skip',
                            engine='python'
                        )
                        success = True
                        self.logger.info(f"Wczytano plik z ignorowaniem cudzysłowów i separatorem '{detected_sep}'")
                    except Exception as e:
                        self.logger.debug(f"Wczytywanie z ignorowaniem cudzysłowów nie zadziałało: {e}")
                
                if not success:
                    self.logger.error("Wszystkie próby wczytania pliku CSV/TSV nie powiodły się")
                    return False
                
                # Wyczyść dane po wczytaniu
                self.clean_data()
                
                # Wymuś inteligentne mapowanie kolumn
                self.force_smart_mapping_for_specific_data()
                
                return True
            
            else:
                raise ValueError("Nieobsługiwany format pliku")
            
            # Sprawdź czy dane zostały wczytane
            if self.excel_data is None or len(self.excel_data) == 0:
                self.logger.error("Plik został wczytany, ale nie zawiera danych")
                return False
            
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
            
            # Usuń wiersze z zerową kwotą - PO mapowaniu kolumn!
            self.filter_zero_amount_rows()
            
            self.logger.info(f"Wczytano plik: {file_path}")
            self.logger.info(f"Liczba wierszy: {len(self.excel_data)}")
            self.logger.info(f"Kolumny: {list(self.excel_data.columns)}")
            self.logger.info(f"Mapowanie kolumn: {self.column_mapping}")
            
            return True
        except Exception as e:
            self.logger.error(f"Błąd wczytywania pliku: {e}")
            return False
    
    def _detect_file_separator(self, file_path):
        """Wykrywa separator używany w pliku CSV/TSV"""
        try:
            # Najpierw spróbuj UTF-16 (Little Endian) - najczęstsze kodowanie UTF-16
            try:
                with open(file_path, 'r', encoding='utf-16-le') as f:
                    first_line = f.readline()
                    if first_line and len(first_line.strip()) > 0:
                        # Sprawdź różne separatory w kolejności priorytetu
                        self.logger.debug(f"Pierwsza linia (repr): {repr(first_line)}")
                        
                        # Sprawdź tabulatory (najpierw, bo mogą być mylone ze spacjami)
                        if '\t' in first_line:
                            self.logger.info("Wykryto separator: tabulator (\\t)")
                            return '\t'
                        
                        # Sprawdź średniki
                        if ';' in first_line:
                            self.logger.info("Wykryto separator: średnik (;)")
                            return ';'
                        
                        # Sprawdź przecinki
                        if ',' in first_line:
                            self.logger.info("Wykryto separator: przecinek (,)")
                            return ','
                        
                        # Sprawdź pionowe kreski
                        if '|' in first_line:
                            self.logger.info("Wykryto separator: pionowa kreska (|)")
                            return '|'
                        
                        # Jeśli nie znaleziono, spróbuj wykryć po liczbie kolumn
                        best_sep = ';'  # domyślny
                        max_columns = 0
                        
                        for sep in ['\t', ';', ',', '|']:
                            columns = first_line.split(sep)
                            if len(columns) > max_columns:
                                max_columns = len(columns)
                                best_sep = sep
                        
                        self.logger.info(f"Wybrano separator '{best_sep}' na podstawie liczby kolumn: {max_columns}")
                        return best_sep
            except Exception as e:
                self.logger.debug(f"UTF-16-LE nie zadziałało podczas wykrywania separatora: {e}")
            
            # Fallback: spróbuj UTF-8
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    first_line = f.readline()
                
                # Sprawdź różne separatory
                if '\t' in first_line:
                    return '\t'
                elif ';' in first_line:
                    return ';'
                elif ',' in first_line:
                    return ','
                elif '|' in first_line:
                    return '|'
                else:
                    return ';'  # domyślny
            except Exception as e:
                self.logger.debug(f"UTF-8 nie zadziałało podczas wykrywania separatora: {e}")
                return ';'  # Domyślny separator
            
        except Exception as e:
            self.logger.debug(f"Błąd podczas wykrywania separatora: {e}")
            return ';'  # Domyślny separator
    
    def _detect_file_encoding(self, file_path):
        """Wykrywa kodowanie pliku CSV/TSV"""
        try:
            # Najpierw spróbuj UTF-16 (Little Endian) - najczęstsze kodowanie UTF-16
            try:
                with open(file_path, 'r', encoding='utf-16-le') as f:
                    first_line = f.readline()
                    # Sprawdź czy linia ma sens (nie zawiera tylko \x00)
                    if first_line and len(first_line.strip()) > 0:
                        self.logger.info("Wykryto kodowanie: utf-16-le")
                        return 'utf-16-le'
            except Exception as e:
                self.logger.debug(f"UTF-16-LE nie zadziałało: {e}")
            
            # Spróbuj UTF-16 (Big Endian)
            try:
                with open(file_path, 'r', encoding='utf-16-be') as f:
                    first_line = f.readline()
                    if first_line and len(first_line.strip()) > 0:
                        self.logger.info("Wykryto kodowanie: utf-16-be")
                        return 'utf-16-be'
            except Exception as e:
                self.logger.debug(f"UTF-16-BE nie zadziałało: {e}")
            
            # Lista innych kodowań do sprawdzenia
            encodings = ['utf-8', 'windows-1250', 'iso-8859-2', 'latin-1', 'cp1250']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        f.readline()  # Próbuj przeczytać pierwszą linię
                    self.logger.info(f"Wykryto kodowanie: {encoding}")
                    return encoding
                except UnicodeDecodeError:
                    continue
            
            # Jeśli żadne nie zadziałało, użyj UTF-8 z obsługą błędów
            self.logger.warning("Nie udało się wykryć kodowania, używam UTF-8")
            return 'utf-8'
        except Exception as e:
            self.logger.debug(f"Błąd podczas wykrywania kodowania: {e}")
            return 'utf-8'  # Domyślne kodowanie
    
    def clean_data(self):
        """Czyści dane - usuwa puste wiersze i kolumny"""
        if self.excel_data is None:
            return
        
        try:
            # Usuń puste wiersze
            initial_rows = len(self.excel_data)
            self.excel_data = self.excel_data.dropna(how='all')
            if len(self.excel_data) < initial_rows:
                self.logger.info(f"Usunięto {initial_rows - len(self.excel_data)} pustych wierszy")
            
            # Usuń puste kolumny
            initial_cols = len(self.excel_data.columns)
            self.excel_data = self.excel_data.dropna(axis=1, how='all')
            if len(self.excel_data.columns) < initial_cols:
                self.logger.info(f"Usunięto {initial_cols - len(self.excel_data.columns)} pustych kolumn")
            
            # Resetuj indeksy
            self.excel_data = self.excel_data.reset_index(drop=True)
            
        except Exception as e:
            self.logger.error(f"Błąd podczas czyszczenia danych: {e}")
    
    def filter_zero_amount_rows(self):
        """Usuwa wiersze z zerową kwotą"""
        if self.excel_data is None:
            return
        
        try:
            initial_count = len(self.excel_data)
            self.logger.info(f"Rozpoczynam filtrowanie pozycji z kwotą ≤ 0. Początkowa liczba wierszy: {initial_count}")
            
            # Użyj zmapowanej kolumny kwota, jeśli istnieje
            kwota_column = None
            if 'kwota' in self.column_mapping:
                kwota_column = self.column_mapping['kwota']
                self.logger.info(f"✅ Używam zmapowanej kolumny kwoty: '{kwota_column}'")
            else:
                # Fallback: znajdź kolumnę z kwotą po słowach kluczowych
                for col in self.excel_data.columns:
                    if any(keyword in col.lower() for keyword in ['netto', 'kwota', 'wartość', 'brutto', 'do rozliczenia']):
                        kwota_column = col
                        break
                if kwota_column:
                    self.logger.info(f"🔍 Znaleziono kolumnę kwoty (fallback): '{kwota_column}'")
                else:
                    self.logger.warning("❌ Nie znaleziono kolumny z kwotą - dostępne kolumny: " + str(list(self.excel_data.columns)))
            
            if kwota_column:
                # Pokaż przykładowe wartości z kolumny kwoty
                sample_values = self.excel_data[kwota_column].head(5).tolist()
                self.logger.info(f"📊 Przykładowe wartości z kolumny '{kwota_column}': {sample_values}")
                
                # Przygotuj dane do filtrowania - usuń białe znaki i zamień przecinki na kropki
                cleaned_values = self.excel_data[kwota_column].astype(str).str.strip().str.replace(',', '.')
                
                # Usuń wiersze z kwotą ≤ 0
                # Najpierw spróbuj przekonwertować na liczby
                numeric_values = pd.to_numeric(cleaned_values, errors='coerce')
                
                # Pokaż statystyki przed filtrowaniem
                zero_count = (numeric_values <= 0).sum()
                nan_count = numeric_values.isna().sum()
                positive_count = (numeric_values > 0).sum()
                self.logger.info(f"📈 Statystyki kwot: ≤0: {zero_count}, NaN: {nan_count}, >0: {positive_count}")
                
                # Filtruj wiersze gdzie kwota > 0 (nie NaN i > 0)
                self.excel_data = self.excel_data[
                    (numeric_values > 0) & (numeric_values.notna())
                ]
                
                # Resetuj indeksy
                self.excel_data = self.excel_data.reset_index(drop=True)
                
                removed_count = initial_count - len(self.excel_data)
                if removed_count > 0:
                    self.logger.info(f"✅ Usunięto {removed_count} pozycji rozliczonych (kwota ≤ 0)")
                    self.logger.info(f"✅ Pozostało {len(self.excel_data)} pozycji")
                else:
                    self.logger.info("ℹ️ Nie znaleziono pozycji rozliczonych do usunięcia")
                
                return removed_count
            else:
                self.logger.warning("❌ Nie znaleziono kolumny z kwotą do usunięcia pozycji rozliczonych")
                return 0
            
        except Exception as e:
            self.logger.error(f"❌ Błąd podczas usuwania pozycji rozliczonych: {e}")
            return 0
    
    def force_smart_mapping_for_specific_data(self):
        """Wymusza mapowanie kolumn dla konkretnych danych"""
        try:
            if self.excel_data is None:
                return False
            
            # Sprawdź czy kolumna 'Kontrahent' jest zmapowana
            if 'Kontrahent' in self.excel_data.columns and 'kontrahent' not in self.column_mapping:
                self.force_column_mapping('kontrahent', 'Kontrahent')
                self.logger.info("Zmapowano kolumnę 'Kontrahent' jako 'kontrahent'")
            
            # Sprawdź czy kolumna 'NIP' jest zmapowana
            if 'NIP' in self.excel_data.columns and 'nip' not in self.column_mapping:
                self.force_column_mapping('nip', 'NIP')
                self.logger.info("Zmapowano kolumnę 'NIP' jako 'nip'")
            
            # Sprawdź czy kolumna 'EMAIL' jest zmapowana jako 'email'
            if 'EMAIL' in self.excel_data.columns and 'email' not in self.column_mapping:
                self.force_column_mapping('email', 'EMAIL')
                self.logger.info("Zmapowano kolumnę 'EMAIL' jako 'email'")
            
            # Sprawdź czy kolumna 'Telefon komorkowy' jest zmapowana jako 'telefon'
            if 'Telefon komorkowy' in self.excel_data.columns and 'telefon' not in self.column_mapping:
                self.force_column_mapping('telefon', 'Telefon komorkowy')
                self.logger.info("Zmapowano kolumnę 'Telefon komorkowy' jako 'telefon'")
            
            # Sprawdź czy kolumna 'Data' jest zmapowana jako 'data_faktury'
            if 'Data' in self.excel_data.columns and 'data_faktury' not in self.column_mapping:
                self.force_column_mapping('data_faktury', 'Data')
                self.logger.info("Zmapowano kolumnę 'Data' jako 'data_faktury'")
            
            # Sprawdź czy kolumna 'Netto' jest zmapowana jako 'kwota'
            if 'Netto' in self.excel_data.columns and 'kwota' not in self.column_mapping:
                self.force_column_mapping('kwota', 'Netto')
                self.logger.info("Zmapowano kolumnę 'Netto' jako 'kwota'")
            
            # Sprawdź czy kolumna 'Numer' jest zmapowana jako 'nr_faktury'
            if 'Numer' in self.excel_data.columns and 'nr_faktury' not in self.column_mapping:
                self.force_column_mapping('nr_faktury', 'Numer')
                self.logger.info("Zmapowano kolumnę 'Numer' jako 'nr_faktury'")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Błąd podczas sprawdzania i poprawiania mapowania: {e}")
            return False
    
    def force_column_mapping(self, target_name, source_name):
        """Wymusza mapowanie kolumny"""
        if source_name in self.excel_data.columns:
            self.column_mapping[target_name] = source_name
            return True
        return False
    
    def apply_smart_mapping(self):
        """Automatycznie mapuje kolumny na podstawie nazw"""
        try:
            if self.excel_data is None:
                return False
            
            # Mapowanie na podstawie słów kluczowych
            mappings = {
                'kontrahent': ['kontrahent', 'nazwa', 'firma', 'company'],
                'nip': ['nip', 'tax_id', 'regon'],
                'nr_faktury': ['numer', 'nr', 'faktura', 'invoice'],
                'email': ['email', 'e-mail', 'mail'],
                'telefon': ['telefon', 'phone', 'tel', 'komórkowy'],
                'kwota': ['kwota', 'netto', 'brutto', 'wartość', 'amount'],
                'data_faktury': ['data', 'date', 'termin'],
                'dni_po_terminie': ['dni', 'po', 'terminie', 'overdue']
            }
            
            for target, keywords in mappings.items():
                if target not in self.column_mapping:
                    for col in self.excel_data.columns:
                        if any(keyword.lower() in col.lower() for keyword in keywords):
                            self.column_mapping[target] = col
                            self.logger.info(f"Automatycznie zmapowano '{col}' -> '{target}'")
                            break
            
            return len(self.column_mapping) > 0
            
        except Exception as e:
            self.logger.error(f"Błąd podczas automatycznego mapowania: {e}")
            return False
    
    def normalize_data(self):
        """Normalizuje dane po mapowaniu"""
        try:
            if self.excel_data is None:
                return
            
            # Dodaj brakujące kolumny z wartościami domyślnymi
            required_columns = ['kontrahent', 'nip', 'nr_faktury', 'email', 'telefon', 'kwota', 'data_faktury', 'dni_po_terminie']
            
            for col in required_columns:
                if col not in self.column_mapping:
                    self.excel_data[col] = ''
                elif self.column_mapping[col] not in self.excel_data.columns:
                    self.excel_data[col] = ''
            
        except Exception as e:
            self.logger.error(f"Błąd podczas normalizacji danych: {e}")
    
    def get_columns(self):
        """Zwraca listę dostępnych kolumn"""
        if self.excel_data is None:
            return []
        return list(self.excel_data.columns)
    
    def get_row_count(self):
        """Zwraca liczbę wierszy"""
        if self.excel_data is None:
            return 0
        return len(self.excel_data)
    
    def get_preview_data(self, max_rows=10):
        """Zwraca dane do podglądu w oryginalnych kolumnach"""
        if self.excel_data is None:
            return []
        
        try:
            preview_data = []
            for idx, row in self.excel_data.head(max_rows).iterrows():
                item = {}
                for col in self.excel_data.columns:
                    item[col] = str(row[col]) if pd.notna(row[col]) else ''
                preview_data.append(item)
            
            return preview_data
        except Exception as e:
            self.logger.error(f"Błąd podczas generowania podglądu: {e}")
            return []
    
    def get_preview_data_mapped(self, max_rows=10):
        """Zwraca dane do podglądu w zmapowanym formacie"""
        if self.excel_data is None:
            return []
        
        try:
            preview_data = []
            self.logger.info(f"Generuję zmapowany podgląd dla {min(max_rows, len(self.excel_data))} wierszy")
            self.logger.info(f"Mapowanie kolumn: {self.column_mapping}")
            
            for idx, row in self.excel_data.head(max_rows).iterrows():
                item = {}
                # Dodaj wszystkie wymagane pola z mapowania
                required_fields = ['kontrahent', 'nip', 'nr_faktury', 'email', 'telefon', 'kwota', 'data_faktury', 'dni_po_terminie']
                
                for field in required_fields:
                    if field in self.column_mapping and self.column_mapping[field] in self.excel_data.columns:
                        # Pobierz wartość z zmapowanej kolumny
                        source_col = self.column_mapping[field]
                        value = str(row[source_col]) if pd.notna(row[source_col]) else ''
                        item[field] = value
                        
                        # Debug: loguj pierwsze kilka wierszy
                        if idx < 3:
                            self.logger.debug(f"Wiersz {idx}, pole {field}: '{source_col}' -> '{value}'")
                    else:
                        # Pole nie jest zmapowane
                        item[field] = ''
                        if idx < 3:
                            self.logger.debug(f"Wiersz {idx}, pole {field}: NIE ZMAPOWANE")
                
                preview_data.append(item)
            
            self.logger.info(f"Wygenerowano zmapowany podgląd: {len(preview_data)} wierszy")
            return preview_data
        except Exception as e:
            self.logger.error(f"Błąd podczas generowania zmapowanego podglądu: {e}")
            return []
    
    def get_mapped_data(self):
        """Zwraca dane z zmapowanymi kolumnami"""
        if self.excel_data is None:
            return []
        
        try:
            mapped_data = []
            for idx, row in self.excel_data.iterrows():
                item = {}
                for target, source in self.column_mapping.items():
                    if source in self.excel_data.columns:
                        item[target] = str(row[source]) if pd.notna(row[source]) else ''
                    else:
                        item[target] = ''
                mapped_data.append(item)
            
            return mapped_data
        except Exception as e:
            self.logger.error(f"Błąd podczas generowania zmapowanych danych: {e}")
            return []
    
    def set_column_mapping(self, mapping):
        """Ustawia mapowanie kolumn"""
        self.column_mapping = mapping
    
    def validate_mapping(self, required_fields):
        """Sprawdza czy wszystkie wymagane pola są zmapowane"""
        missing_fields = []
        for field in required_fields:
            if field not in self.column_mapping or not self.column_mapping[field]:
                missing_fields.append(field)
        return missing_fields 
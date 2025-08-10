"""
Moduł konfiguracji aplikacji Windykator
"""
import json
import os
from datetime import datetime

class Config:
    """Klasa zarządzająca konfiguracją aplikacji"""
    
    def __init__(self):
        # Katalog konfiguracji - używaj bieżącego katalogu roboczego
        self.config_dir = os.getcwd()
        
        self.config_file = 'api_config.json'
        self.mapping_file = 'column_mapping.json'
        self.email_template_file = 'email_template.txt'
        self.sms_template_file = 'sms_template.txt'
        
        # Kolory aplikacji
        self.primary_color = '#002999'  # Granatowy
        self.secondary_color = '#f3f2f1'  # Light gray
        self.accent_color = '#002999'  # Granatowy
        self.text_color = '#323130'  # Dark gray
        self.white_color = '#ffffff'  # White
        self.success_color = '#28a745'  # Zielony
        self.warning_color = '#ffc107'  # Żółty
        self.danger_color = '#dc3545'  # Czerwony
    
    def load_api_config(self):
        """Wczytuje konfigurację API z pliku"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("ℹ️ Nie znaleziono pliku konfiguracji API - użyj domyślnych ustawień")
            return self.get_default_api_config()
        except Exception as e:
            print(f"⚠️ Błąd wczytywania konfiguracji API: {str(e)}")
            return self.get_default_api_config()
    
    def save_api_config(self, config):
        """Zapisuje konfigurację API do pliku"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print("✅ Konfiguracja API została zapisana")
        except Exception as e:
            print(f"❌ Błąd zapisywania konfiguracji API: {str(e)}")
    
    def get_default_api_config(self):
        """Zwraca domyślną konfigurację API"""
        return {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": "587",
            "email": "",
            "password": "",
            "sms_url": "https://api.smsapi.pl/sms.do",
            "sms_token": "",
            "sms_sender": "Windykacja",
            "sms_test_number": "48500123456"
        }
    
    def load_mapping(self):
        """Wczytuje mapowanie kolumn z pliku"""
        try:
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("ℹ️ Nie znaleziono pliku mapowania kolumn")
            return {}
        except Exception as e:
            print(f"⚠️ Błąd wczytywania mapowania: {str(e)}")
            return {}
    
    def save_mapping(self, mapping):
        """Zapisuje mapowanie kolumn do pliku"""
        try:
            with open(self.mapping_file, 'w', encoding='utf-8') as f:
                json.dump(mapping, f, indent=2, ensure_ascii=False)
            print("✅ Mapowanie kolumn zostało zapisane")
        except Exception as e:
            print(f"❌ Błąd zapisywania mapowania: {str(e)}")
    
    def load_template(self, template_type):
        """Wczytuje szablon email lub SMS z pliku"""
        try:
            filename = self.email_template_file if template_type == 'email' else self.sms_template_file
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return self.get_default_template(template_type)
        except Exception as e:
            print(f"⚠️ Błąd wczytywania szablonu {template_type}: {str(e)}")
            return self.get_default_template(template_type)
    
    def save_template(self, template_type, content):
        """Zapisuje szablon email lub SMS do pliku"""
        try:
            filename = self.email_template_file if template_type == 'email' else self.sms_template_file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Szablon {template_type} został zapisany")
        except Exception as e:
            print(f"❌ Błąd zapisywania szablonu {template_type}: {str(e)}")
    
    def get_default_template(self, template_type):
        """Zwraca domyślny szablon email lub SMS"""
        if template_type == 'email':
            return """Przypomnienie o płatności

Szanowny/a {kontrahent},

Informujemy, że faktura nr {nr_faktury} w wysokości {kwota} PLN z dnia {data_faktury} jest przeterminowana. 

Od dnia wystawienia faktury minęło już {dni_po_terminie} dni.

Prosimy o niezwłoczne uregulowanie zaległej płatności.

W przypadku pytań prosimy o kontakt.

Z poważaniem,
Dział Windykacji"""
        else:
            return """Przypomnienie: Faktura {nr_faktury} na kwotę {kwota} zł z dnia {data_faktury} jest przeterminowana o {dni_po_terminie} dni. Prosimy o pilne uregulowanie."""
    
    def get_mapping_fields(self):
        """Zwraca listę pól do mapowania"""
        return [
            ('kontrahent', 'Nazwa Kontrahenta'),
            ('nip', 'NIP'),
            ('nr_faktury', 'Numer Faktury'),
            ('email', 'Email'),
            ('telefon', 'Telefon'),
            ('kwota', 'Kwota'),
            ('data_faktury', 'Data Faktury')
        ]
    
    def get_required_fields(self):
        """Zwraca listę wymaganych pól"""
        return ['kontrahent', 'nr_faktury', 'email', 'telefon', 'kwota'] 
    
    def load_placeholders(self):
        """Wczytuje placeholdery stałe z pliku"""
        try:
            placeholders_file = os.path.join(self.config_dir, 'placeholders.json')
            if os.path.exists(placeholders_file):
                with open(placeholders_file, 'r', encoding='utf-8') as f:
                    placeholders = json.load(f)
                return placeholders
            else:
                # Zwróć domyślne placeholdery jeśli plik nie istnieje
                return self.get_default_placeholders()
        except Exception as e:
            print(f"Błąd wczytywania placeholders: {e}")
            return self.get_default_placeholders()
    
    def save_placeholders(self, placeholders):
        """Zapisuje placeholdery stałe do pliku"""
        try:
            placeholders_file = os.path.join(self.config_dir, 'placeholders.json')
            with open(placeholders_file, 'w', encoding='utf-8') as f:
                json.dump(placeholders, f, ensure_ascii=False, indent=2)
            print("✅ Placeholdery zostały zapisane")
        except Exception as e:
            print(f"Błąd zapisywania placeholders: {e}")
            raise e
    
    def get_default_placeholders(self):
        """Zwraca domyślne placeholdery"""
        return [
            {
                'name': 'numer_konta',
                'value': 'PL12345678901234567890123456',
                'description': 'Numer konta bankowego'
            },
            {
                'name': 'data_wymagalnosci',
                'value': '31.12.2024',
                'description': 'Data wymagalności płatności'
            },
            {
                'name': 'kwota_zadluzenia',
                'value': '0.00 PLN',
                'description': 'Kwota zadłużenia'
            },
            {
                'name': 'nazwa_firmy',
                'value': 'KPJ.PL Sp. z o.o.',
                'description': 'Nazwa firmy windykacyjnej'
            },
            {
                'name': 'email_kontaktowy',
                'value': 'windykacja@kpj.pl',
                'description': 'Email kontaktowy'
            },
            {
                'name': 'telefon_kontaktowy',
                'value': '+48 123 456 789',
                'description': 'Telefon kontaktowy'
            }
        ] 
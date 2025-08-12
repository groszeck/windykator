# 🚨 Windykator - System Windykacji

**Profesjonalny system do zarządzania procesami windykacyjnymi z automatycznym wysyłaniem przypomnień email i SMS.**

## ✨ Funkcje

### 📊 **Zarządzanie danymi**
- Import plików Excel/CSV z danymi windykacyjnymi
- Mapowanie kolumn z plików źródłowych
- Podgląd i edycja danych przed wysyłką
- Eksport statusów do CSV

### 🌐 **Interfejs webowy (NOWOŚĆ!)**
- **Aplikacja Flask** dostępna w przeglądarce
- **Responsywny design** - działa na wszystkich urządzeniach
- **Współdzielone moduły** - używa tej samej logiki co desktop
- **Tryb testowy** - symulacja wysyłki przed rzeczywistą
- **Zarządzanie szablonami** - edycja email i SMS przez web

### 📧 **Edytor szablonów WYSIWYG**
- **Edytor email WYSIWYG** z pełnym formatowaniem:
  - Czcionki i rozmiary tekstu
  - Formatowanie (pogrubienie, kursywa, podkreślenie)
  - Kolory tekstu
  - Funkcje Cofnij/Ponów
  - Dodawanie stopek HTML i tekstowych
- **Edytor SMS** z podglądem
- **Placeholdery stałe** - edytor stałych wartości:
  - Numer konta bankowego
  - Data wymagalności
  - Kwota zadłużenia
  - Dane kontaktowe firmy

### 📤 **Automatyzacja wysyłki**
- Masowe wysyłanie przypomnień email
- Masowe wysyłanie SMS
- Śledzenie statusów wysyłki
- Obsługa błędów i ponownych prób

### ⚙️ **Konfiguracja**
- Konfiguracja serwera SMTP (Gmail, Outlook, etc.)
- Konfiguracja API SMS (SMSAPI.pl)
- Testowanie połączeń
- Zapisywanie ustawień

## 🚀 Instalacja

### Wymagania
- Python 3.7+
- Windows 10/11 (z Azure ttk theme) - **Desktop**
- Dowolna przeglądarka - **Web**

### Instalacja
```bash
# Sklonuj repozytorium
git clone https://github.com/twoja-nazwa/windykator.git
cd windykator

# Zainstaluj zależności
pip install -r requirements.txt

# Uruchom aplikację desktop
python main.py

# LUB uruchom aplikację web
python web_app.py
```

## 📋 Zależności

Główne biblioteki używane w projekcie:
- `tkinter` - interfejs graficzny
- `pandas` - przetwarzanie danych Excel/CSV
- `openpyxl` - obsługa plików Excel
- `requests` - komunikacja HTTP (SMS API)
- `smtplib` - wysyłanie emaili

## 🎨 Motywy

Aplikacja obsługuje:
- **Azure Light** - jasny motyw (domyślny)
- **Azure Dark** - ciemny motyw
- Przełączanie motywów w czasie rzeczywistym

## 📁 Struktura projektu

```
windykator/
├── main.py                 # Główna aplikacja desktop
├── web_app.py             # Aplikacja webowa Flask
├── ui_components.py        # Komponenty interfejsu desktop
├── config.py              # Zarządzanie konfiguracją
├── data_processor.py      # Przetwarzanie danych
├── email_sender.py        # Wysyłanie emaili
├── sms_sender.py          # Wysyłanie SMS
├── requirements.txt       # Zależności Python (desktop + web)
├── theme/                 # Motywy Azure (desktop)
│   ├── azure.tcl
│   ├── light/
│   └── dark/
├── templates/             # Szablony HTML (web)
│   ├── base.html
│   ├── index.html
│   └── ...
├── static/                # Pliki statyczne (web)
│   ├── css/
│   └── js/
└── README.md
```

## 🔧 Konfiguracja

### Email (SMTP)
1. Przejdź do zakładki "Konfiguracja"
2. Wprowadź dane serwera SMTP:
   - **Gmail**: `smtp.gmail.com:587`
   - **Outlook**: `smtp-mail.outlook.com:587`
3. Wprowadź email i hasło
4. Kliknij "Testuj połączenie"

### SMS (SMSAPI.pl)
1. Zarejestruj się na [smsapi.pl](https://smsapi.pl)
2. Wygeneruj token API
3. Wprowadź token i numer nadawcy
4. Testuj połączenie

## 📱 Placeholdery

System obsługuje placeholdery stałe:
- `{numer_konta}` - numer konta bankowego
- `{data_wymagalnosci}` - data wymagalności
- `{kwota_zadluzenia}` - kwota zadłużenia
- `{nazwa_firmy}` - nazwa firmy
- `{email_kontaktowy}` - email kontaktowy
- `{telefon_kontaktowy}` - telefon kontaktowy

## 🎯 Użycie

### 🖥️ **Aplikacja Desktop**
1. **Import danych**
   - Wybierz plik Excel/CSV z danymi
   - Zmapuj kolumny na pola systemu
   - Sprawdź podgląd danych

2. **Edycja szablonów**
   - Użyj edytora WYSIWYG do emaili
   - Dostosuj placeholdery stałe
   - Zapisz zmiany

3. **Wysyłka**
   - Wybierz elementy do wysłania
   - Uruchom proces wysyłki
   - Śledź statusy

### 🌐 **Aplikacja Web**
1. **Otwórz przeglądarkę**: `http://localhost:5000`
2. **Wczytaj plik**: przeciągnij i upuść lub wybierz z dysku
3. **Mapowanie**: przypisz kolumny do pól systemowych
4. **Podgląd**: sprawdź dane przed wysyłką
5. **Szablony**: edytuj email i SMS przez web
6. **Wysyłka**: użyj trybu testowego, a następnie rzeczywistej wysyłki

## 🐛 Rozwiązywanie problemów

### Błąd połączenia SMTP
- Sprawdź ustawienia serwera
- Włącz "Mniej bezpieczne aplikacje" (Gmail)
- Sprawdź firewall

### Błąd SMS API
- Sprawdź token API
- Sprawdź saldo konta
- Sprawdź numer nadawcy

## 🤝 Współpraca

1. Fork projektu
2. Utwórz branch (`git checkout -b feature/AmazingFeature`)
3. Commit zmiany (`git commit -m 'Add some AmazingFeature'`)
4. Push do branch (`git push origin feature/AmazingFeature`)
5. Otwórz Pull Request

## 📄 Licencja

Ten projekt jest objęty licencją MIT. Zobacz plik `LICENSE` dla szczegółów.

## 👨‍💻 Autor

**Zbigniew Grochowski**
- Email: [twój-email@example.com]
- GitHub: [@twoja-nazwa]

## 🙏 Podziękowania

- [Azure ttk theme](https://github.com/rdbende/Azure-ttk-theme) - piękne motywy
- [SMSAPI.pl](https://smsapi.pl) - API do wysyłania SMS
- [Flask](https://flask.palletsprojects.com/) - framework webowy
- Społeczność Python za wspaniałe biblioteki

---

⭐ **Jeśli projekt Ci się podoba, daj gwiazdkę na GitHub!**

## 🌐 **Aplikacja Web - Szczegóły**

Aplikacja webowa Flask jest dostępna pod adresem `http://localhost:5000` po uruchomieniu `python web_app.py`.

**Dokumentacja webowa**: Zobacz `README_WEB.md` dla szczegółowych informacji o interfejsie webowym. 
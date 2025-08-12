# 🌐 Windykator Web Interface

Interfejs przeglądarkowy dla systemu windykacji **Windykator**, działający równolegle z aplikacją desktopową.

## ✨ Funkcje

- **Wczytywanie plików** CSV/Excel z drag & drop
- **Mapowanie kolumn** z intuicyjnym interfejsem
- **Podgląd danych** w formie tabeli
- **Zarządzanie szablonami** email i SMS
- **Tryb testowy** wysyłki bez rzeczywistego wysłania
- **Rzeczywista wysyłka** email i SMS
- **Eksport danych** do CSV
- **Responsywny design** dla wszystkich urządzeń

## 🚀 Szybki start

### 1. Instalacja zależności

```bash
pip install -r requirements.txt
```

### 2. Uruchomienie aplikacji

```bash
python web_app.py
```

### 3. Otwórz przeglądarkę

Przejdź do: `http://localhost:5000`

## 📁 Struktura projektu

```
windykator/
├── web_app.py              # Główna aplikacja Flask
├── templates/              # Szablony HTML
│   ├── base.html          # Główny szablon
│   ├── index.html         # Strona główna
│   ├── upload.html        # Wczytywanie plików
│   ├── mapping.html       # Mapowanie kolumn
│   ├── preview.html       # Podgląd danych
│   ├── templates.html     # Zarządzanie szablonami
│   ├── sending.html       # Wysyłka
│   └── config.html        # Konfiguracja
├── static/                 # Pliki statyczne
│   ├── css/
│   │   └── style.css      # Style CSS
│   └── js/
│       └── app.js         # JavaScript
├── requirements.txt        # Zależności (desktop + web)
└── README_WEB.md          # Ten plik
```

## 🔧 Konfiguracja

### Zmienne środowiskowe

Utwórz plik `.env` w głównym katalogu:

```env
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your_secret_key_here
```

### Port i host

Domyślnie aplikacja działa na:
- **Host**: `0.0.0.0` (dostępna z zewnątrz)
- **Port**: `5000`

Możesz zmienić w `web_app.py`:

```python
app.run(debug=True, host='127.0.0.1', port=8080)
```

## 📱 Użytkowanie

### 1. Wczytywanie pliku

1. Przejdź do **"Wczytaj plik"**
2. Wybierz plik CSV/Excel lub przeciągnij i upuść
3. Kliknij **"Wczytaj plik"**

### 2. Mapowanie kolumn

1. Po wczytaniu pliku przejdź do **"Mapowanie kolumn"**
2. Przypisz kolumny z pliku do pól systemowych
3. Kliknij **"Zapisz mapowanie"**

### 3. Podgląd danych

1. Przejdź do **"Podgląd danych"**
2. Sprawdź czy dane są poprawnie zmapowane
3. W razie potrzeby wróć do mapowania

### 4. Szablony

1. Przejdź do **"Szablony"**
2. Edytuj szablony email i SMS
3. Użyj placeholderów: `{kontrahent}`, `{nip}`, `{kwota}`, etc.

### 5. Wysyłka

1. Przejdź do **"Wysyłka"**
2. Wybierz typy wiadomości (email/SMS)
3. Użyj **trybu testowego** przed rzeczywistą wysyłką
4. Kliknij **"Rozpocznij wysyłkę"**

## 🧪 Tryb testowy

Tryb testowy pozwala na:
- Symulację wysyłki bez rzeczywistego wysłania
- Sprawdzenie poprawności szablonów
- Weryfikację danych odbiorców
- Testowanie różnych scenariuszy

**Ważne**: Zawsze testuj przed rzeczywistą wysyłką!

## 🔒 Bezpieczeństwo

- **Secret Key**: Zmień domyślny klucz w produkcji
- **Upload Limits**: Maksymalny rozmiar pliku: 16MB
- **File Validation**: Sprawdzanie typów plików
- **Session Management**: Bezpieczne zarządzanie sesjami

## 🚀 Produkcja

### Gunicorn (Linux/macOS)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app
```

### Windows

```bash
pip install waitress
python -m waitress --host=0.0.0.0 --port=5000 web_app:app
```

### Docker (opcjonalnie)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "web_app.py"]
```

## 🔧 Rozwiązywanie problemów

### Błąd: "Module not found"

```bash
pip install -r requirements.txt
```

### Błąd: "Port already in use"

```bash
# Sprawdź co używa portu 5000
netstat -ano | findstr :5000

# Zmień port w web_app.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Błąd: "Permission denied"

```bash
# Windows: Uruchom jako administrator
# Linux/macOS: Sprawdź uprawnienia
chmod +x web_app.py
```

### Błąd: "Template not found"

Sprawdź czy folder `templates/` istnieje i zawiera pliki HTML.

## 📊 Monitoring

### Logi aplikacji

Logi są wyświetlane w konsoli. W produkcji przekieruj do pliku:

```bash
python web_app.py > app.log 2>&1
```

### Status aplikacji

Sprawdź status pod adresem: `http://localhost:5000/`

## 🤝 Integracja z desktop

Aplikacja webowa:
- ✅ **Używa tych samych modułów** (`data_processor.py`, `email_sender.py`, etc.)
- ✅ **Ma dostęp do tej samej konfiguracji**
- ✅ **Nie wpływa na działanie desktop**
- ✅ **Działa równolegle**

## 🔄 Aktualizacje

1. Pobierz najnowszą wersję z Git
2. Zaktualizuj zależności: `pip install -r requirements.txt`
3. Uruchom ponownie: `python web_app.py`

## 📞 Wsparcie

- **Dokumentacja**: Ten plik README
- **Kod źródłowy**: Sprawdź komentarze w kodzie
- **Logi**: Sprawdź konsolę aplikacji
- **GitHub**: Issues i Pull Requests

## 📝 Licencja

Ten projekt jest częścią systemu Windykator i podlega tej samej licencji.

---

**🌐 Windykator Web Interface** - Nowoczesny interfejs przeglądarkowy dla systemu windykacji! 
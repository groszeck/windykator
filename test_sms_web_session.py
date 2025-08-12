#!/usr/bin/env python3
"""
Test wysyłania SMS-ów w aplikacji webowej z obsługą sesji
"""
import requests
import json
import os

def test_sms_sending_with_session():
    """Testuje wysyłanie SMS-ów przez API aplikacji webowej z obsługą sesji"""
    
    # URL aplikacji webowej
    base_url = "http://localhost:5000"
    
    print("🧪 Test wysyłania SMS-ów w aplikacji webowej z sesją")
    print(f"🌐 URL: {base_url}")
    
    # Utwórz sesję
    session = requests.Session()
    
    # Krok 1: Wczytaj plik CSV
    print("\n📁 Krok 1: Wczytywanie pliku CSV...")
    
    csv_file_path = "testowy.csv"
    if not os.path.exists(csv_file_path):
        print(f"❌ Plik {csv_file_path} nie istnieje")
        return
    
    try:
        with open(csv_file_path, 'rb') as f:
            files = {'file': (csv_file_path, f, 'text/csv')}
            response = session.post(f"{base_url}/upload", files=files, timeout=30)
        
        print(f"📡 Status wczytywania: {response.status_code}")
        print(f"📄 Odpowiedź: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ Plik CSV wczytany pomyślnie")
        else:
            print(f"❌ Błąd wczytywania: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Błąd wczytywania pliku: {e}")
        return
    
    # Krok 2: Sprawdź mapowanie kolumn
    print("\n🗺️ Krok 2: Sprawdzanie mapowania kolumn...")
    
    try:
        response = session.get(f"{base_url}/mapping")
        print(f"📡 Status mapowania: {response.status_code}")
        if response.status_code == 200:
            print("✅ Mapowanie kolumn dostępne")
        else:
            print(f"❌ Błąd mapowania: {response.text}")
            
    except Exception as e:
        print(f"❌ Błąd mapowania: {e}")
    
    # Krok 3: Sprawdź podgląd danych
    print("\n👁️ Krok 3: Sprawdzanie podglądu danych...")
    
    try:
        response = session.get(f"{base_url}/preview")
        print(f"📡 Status podglądu: {response.status_code}")
        if response.status_code == 200:
            print("✅ Podgląd danych dostępny")
            # Sprawdź czy są dane w sesji
            if "Brak danych" in response.text:
                print("⚠️ Brak danych w podglądzie")
            else:
                print("✅ Dane są dostępne w podglądzie")
        else:
            print(f"❌ Błąd podglądu: {response.text}")
            
    except Exception as e:
        print(f"❌ Błąd podglądu: {e}")
    
    # Krok 4: Test wysyłania SMS-ów
    print("\n📱 Krok 4: Test wysyłania SMS-ów...")
    
    test_data = {
        "send_email": False,
        "send_sms": True,
        "selected_rows": [0]  # Testuj pierwszy wiersz
    }
    
    print(f"📤 Dane testowe: {json.dumps(test_data, indent=2)}")
    
    try:
        # Wywołaj API testowego wysyłania
        response = session.post(
            f"{base_url}/api/test_sending",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📡 Status HTTP: {response.status_code}")
        print(f"📄 Odpowiedź: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sukces: {result.get('success')}")
            if result.get('results'):
                for i, res in enumerate(result['results']):
                    print(f"📋 Wynik {i}:")
                    if res.get('sms_test'):
                        sms_test = res['sms_test']
                        print(f"  📱 SMS: {sms_test.get('success')} - {sms_test.get('message')}")
                        if sms_test.get('to'):
                            print(f"  📞 Do: {sms_test.get('to')}")
                        if sms_test.get('content'):
                            print(f"  📝 Treść: {sms_test.get('content')}")
            else:
                print("📋 Brak wyników")
        else:
            print(f"❌ Błąd HTTP: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Błąd połączenia - aplikacja webowa nie jest uruchomiona")
    except Exception as e:
        print(f"❌ Błąd: {e}")
    
    # Krok 5: Sprawdź sesję
    print("\n🔍 Krok 5: Sprawdzenie sesji...")
    print(f"🍪 Cookies: {dict(session.cookies)}")
    print(f"📋 Headers: {dict(session.headers)}")

if __name__ == "__main__":
    test_sms_sending_with_session() 
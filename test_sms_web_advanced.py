#!/usr/bin/env python3
"""
Zaawansowany test wysyłania SMS-ów w aplikacji webowej
"""
import requests
import json
import os

def test_sms_sending_advanced():
    """Testuje wysyłanie SMS-ów przez API aplikacji webowej z wczytaniem danych"""
    
    # URL aplikacji webowej
    base_url = "http://localhost:5000"
    
    print("🧪 Zaawansowany test wysyłania SMS-ów w aplikacji webowej")
    print(f"🌐 URL: {base_url}")
    
    # Krok 1: Wczytaj plik CSV
    print("\n📁 Krok 1: Wczytywanie pliku CSV...")
    
    csv_file_path = "testowy2.csv"
    if not os.path.exists(csv_file_path):
        print(f"❌ Plik {csv_file_path} nie istnieje")
        return
    
    try:
        with open(csv_file_path, 'rb') as f:
            files = {'file': (csv_file_path, f, 'text/csv')}
            response = requests.post(f"{base_url}/upload", files=files, timeout=30)
        
        print(f"📡 Status wczytywania: {response.status_code}")
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
        response = requests.get(f"{base_url}/mapping")
        print(f"📡 Status mapowania: {response.status_code}")
        if response.status_code == 200:
            print("✅ Mapowanie kolumn dostępne")
        else:
            print(f"❌ Błąd mapowania: {response.text}")
            
    except Exception as e:
        print(f"❌ Błąd mapowania: {e}")
    
    # Krok 3: Test wysyłania SMS-ów
    print("\n📱 Krok 3: Test wysyłania SMS-ów...")
    
    test_data = {
        "send_email": False,
        "send_sms": True,
        "selected_rows": [0]  # Testuj pierwszy wiersz
    }
    
    print(f"📤 Dane testowe: {json.dumps(test_data, indent=2)}")
    
    try:
        # Wywołaj API testowego wysyłania
        response = requests.post(
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

if __name__ == "__main__":
    test_sms_sending_advanced() 
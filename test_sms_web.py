#!/usr/bin/env python3
"""
Test wysyłania SMS-ów w aplikacji webowej
"""
import requests
import json

def test_sms_sending():
    """Testuje wysyłanie SMS-ów przez API aplikacji webowej"""
    
    # URL aplikacji webowej
    base_url = "http://localhost:5000"
    
    # Dane testowe
    test_data = {
        "send_email": False,
        "send_sms": True,
        "selected_rows": [0]  # Testuj pierwszy wiersz
    }
    
    print("🧪 Test wysyłania SMS-ów w aplikacji webowej")
    print(f"🌐 URL: {base_url}")
    print(f"📤 Dane: {json.dumps(test_data, indent=2)}")
    
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
            print(f"📋 Wyniki: {json.dumps(result.get('results', []), indent=2)}")
        else:
            print(f"❌ Błąd HTTP: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Błąd połączenia - aplikacja webowa nie jest uruchomiona")
    except Exception as e:
        print(f"❌ Błąd: {e}")

if __name__ == "__main__":
    test_sms_sending() 
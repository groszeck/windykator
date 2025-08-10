import requests
from datetime import datetime

TOKEN = "6EHL0slXu7nrnLHF0KP4kHtT7Ac0kVcs8vdJig66"
API_URL = "https://api.smsapi.pl/sms.do"

print("🧪 Debug odpowiedzi SMSAPI")
print("=" * 50)

# Test 1: Sprawdź autoryzację
print("📡 Test 1: Sprawdzenie autoryzacji")
test_url = "https://api.smsapi.pl/user.do"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/x-www-form-urlencoded"
}

payload = {
    "action": "get",
    "format": "json"
}

try:
    response = requests.post(test_url, data=payload, headers=headers, timeout=10)
    print(f"📊 Status: {response.status_code}")
    print(f"📄 Odpowiedź: {response.text}")
    
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"🔍 JSON: {result}")
        except:
            print("⚠️ Nie JSON")
    else:
        print(f"❌ Błąd HTTP")
        
except Exception as e:
    print(f"❌ Błąd: {e}")

print("\n" + "=" * 50)

# Test 2: Wyślij testowy SMS
print("📡 Test 2: Wysyłanie testowego SMS")
sms_payload = {
    "to": "48501332990",
    "message": "Test debug - " + str(datetime.now().strftime('%H:%M:%S')),
    "format": "json"
}

try:
    response = requests.post(API_URL, data=sms_payload, headers=headers, timeout=10)
    print(f"📊 Status: {response.status_code}")
    print(f"📄 Odpowiedź: {response.text}")
    
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"🔍 JSON: {result}")
        except:
            print("⚠️ Nie JSON")
    else:
        print(f"❌ Błąd HTTP")
        
except Exception as e:
    print(f"❌ Błąd: {e}")

print("=" * 50) 
"""
Test autoryzacji SMS API
"""
import requests
import json

TOKEN = "6EHL0slXu7nrnLHF0KP4kHtT7Ac0kVcs8vdJig66"  # Twój OAuth token
API_URL = "https://api.smsapi.pl/sms.do"

payload = {
    "to": "48501332990",         # numer w formacie międzynarodowym
    "message": "test gpt",       # treść SMS
    "format": "json"             # odpowiedź w JSON
}

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/x-www-form-urlencoded"
}

print("🧪 Test wysyłania SMS z nowym tokenem")
print("=" * 50)
print(f"📱 Numer: {payload['to']}")
print(f"💬 Wiadomość: {payload['message']}")
print(f"🔑 Token: {TOKEN[:10]}...")
print(f"🌐 URL: {API_URL}")
print("=" * 50)

try:
    resp = requests.post(API_URL, data=payload, headers=headers, timeout=10)
    
    print(f"📊 Status HTTP: {resp.status_code}")
    print(f"📄 Odpowiedź: {resp.text}")
    
    if resp.status_code == 200:
        try:
            result = resp.json()
            if result.get('error') == 0:
                print("✅ SMS wysłany pomyślnie!")
                if 'list' in result and len(result['list']) > 0:
                    print(f"📱 ID SMS: {result['list'][0].get('id', 'N/A')}")
            else:
                print(f"❌ Błąd: {result.get('message', 'Nieznany błąd')}")
        except:
            print("⚠️ Odpowiedź nie jest w formacie JSON")
    else:
        print(f"❌ Błąd HTTP: {resp.status_code}")
        
except Exception as e:
    print(f"❌ Błąd połączenia: {e}") 
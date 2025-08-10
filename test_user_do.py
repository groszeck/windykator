import requests

TOKEN = "6EHL0slXu7nrnLHF0KP4kHtT7Ac0kVcs8vdJig66"
URL = "https://api.smsapi.pl/user.do"

print("🧪 Test endpointu /user.do z parametrem action")
print("=" * 50)

# Test 1: Z parametrem action=get
print("📡 Test 1: action=get")
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/x-www-form-urlencoded"
}

payload = {
    "action": "get",
    "format": "json"
}

try:
    response = requests.post(URL, data=payload, headers=headers, timeout=10)
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

# Test 2: Bez parametru action
print("📡 Test 2: bez action")
payload = {
    "format": "json"
}

try:
    response = requests.post(URL, data=payload, headers=headers, timeout=10)
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
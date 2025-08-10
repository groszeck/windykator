"""
Test autoryzacji SMS API z poprawkami
"""
import requests
import json

def test_sms_auth(token):
    """Testuje autoryzację SMS API z poprawkami"""
    print(f"🔍 Testowanie tokena: {token[:10]}...")
    
    # Test 1: OAuth Bearer Token - GET /profile
    print(f"\n🧪 Test 1: OAuth Bearer Token - GET /profile")
    print(f"   📡 URL: https://api.smsapi.com/profile")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get("https://api.smsapi.com/profile", headers=headers, timeout=30)
        print(f"   📊 Status HTTP: {response.status_code}")
        print(f"   📄 Odpowiedź: {response.text[:200]}...")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   🔍 Wynik JSON: {json.dumps(result, indent=6)}")
                
                if 'username' in result or 'points' in result:
                    print("   ✅ OAuth Bearer Token działa!")
                    if 'username' in result:
                        print(f"   👤 Użytkownik: {result.get('username', 'N/A')}")
                    if 'points' in result:
                        print(f"   💰 Punkty: {result.get('points', 'N/A')}")
                    return True
                else:
                    error_msg = result.get('message', 'Nieznany błąd')
                    print(f"   ❌ Błąd autoryzacji OAuth: {error_msg}")
            except json.JSONDecodeError:
                print(f"   ⚠️ Odpowiedź nie jest JSON: {response.text}")
        else:
            print(f"   ❌ Błąd HTTP: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Błąd połączenia: {e}")
    except Exception as e:
        print(f"   ❌ Błąd ogólny: {e}")
    
    # Test 2: Wysyłanie SMS - OAuth Bearer token
    print(f"\n🧪 Test 2: Wysyłanie SMS - OAuth Bearer token")
    print(f"   📡 URL: https://api.smsapi.com/sms.do")
    
    sms_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    sms_payload = {
        'to': 'test',
        'message': 'Test SMS API - OAuth Bearer',
        'format': 'json'
    }
    
    try:
        response = requests.post("https://api.smsapi.com/sms.do", data=sms_payload, headers=sms_headers, timeout=30)
        print(f"   📊 Status HTTP: {response.status_code}")
        print(f"   📄 Odpowiedź: {response.text[:200]}...")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   🔍 Wynik JSON: {json.dumps(result, indent=6)}")
                
                if result.get('error') == 0:
                    print("   ✅ Wysyłanie SMS działa!")
                    if 'list' in result and len(result['list']) > 0:
                        print(f"   📱 SMS ID: {result['list'][0].get('id', 'N/A')}")
                    return True
                else:
                    error_msg = result.get('message', 'Nieznany błąd')
                    print(f"   ❌ Błąd wysyłania SMS: {error_msg}")
            except json.JSONDecodeError:
                print(f"   ⚠️ Odpowiedź nie jest JSON: {response.text}")
        else:
            print(f"   ❌ Błąd HTTP: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Błąd połączenia: {e}")
    except Exception as e:
        print(f"   ❌ Błąd ogólny: {e}")
    
    return False

if __name__ == "__main__":
    # Token do przetestowania
    token = "f9WVDUqFSUH6JOW40UyJubjCkGEJQxCGvce3Qs8A"
    
    print("🧪 Test autoryzacji SMS API z poprawkami OAuth")
    print("=" * 70)
    
    success = test_sms_auth(token)
    
    print("=" * 70)
    if success:
        print("✅ Token jest poprawny!")
    else:
        print("❌ Token nie został rozpoznany!")
        print("\n💡 Możliwe przyczyny:")
        print("- Token może być wygasł")
        print("- Token może wymagać dodatkowych parametrów")
        print("- Sprawdź w panelu SMSAPI czy token jest aktywny") 
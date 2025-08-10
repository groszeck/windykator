"""
Moduł do wysyłania SMS przez SMS API
"""
import requests
import logging
import re
from datetime import datetime

class SMSSender:
    """Klasa do wysyłania SMS przez SMS API"""
    
    def __init__(self, api_token, sender_name=None, api_url="https://api.smsapi.pl/sms.do"):
        self.api_token = api_token
        self.sender_name = sender_name  # None domyślnie
        self.api_url = api_url
        self.logger = logging.getLogger(__name__)
    
    def send_sms(self, phone_number, message):
        """Wysyła SMS przez SMS API używając OAuth Bearer token"""
        if not self.api_token:
            return False, "Brak tokenu SMS API"
        
        try:
            # Przygotuj nagłówki z OAuth Bearer token
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            # Przygotuj dane do wysłania (bez tokenu w payload)
            payload = {
                'to': phone_number,
                'message': message,
                'format': 'json'
            }
            
            # Dodaj nadawcę tylko jeśli jest ustawiony i nie jest None
            if self.sender_name and self.sender_name.strip():
                payload['from'] = self.sender_name
            
            # Wyślij żądanie
            response = requests.post(self.api_url, data=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    self.logger.info(f"📄 Odpowiedź SMSAPI: {result}")
                    
                    # Sprawdź różne możliwe formaty odpowiedzi SMSAPI
                    if result.get('error') == 0:
                        self.logger.info(f"SMS wysłany do: {phone_number}")
                        return True, "SMS wysłany pomyślnie"
                    elif 'list' in result and len(result['list']) > 0:
                        # SMSAPI zwraca sukces w formacie {"count":1,"list":[...]}
                        self.logger.info(f"SMS wysłany do: {phone_number}")
                        return True, "SMS wysłany pomyślnie"
                    elif result.get('error') and result.get('error') != 0:
                        # SMSAPI zwrócił błąd
                        error_msg = result.get('message', 'Nieznany błąd SMS API')
                        self.logger.error(f"Błąd SMS API: {error_msg}")
                        return False, f"Błąd SMS API: {error_msg}"
                    else:
                        # Nieznany format odpowiedzi
                        self.logger.warning(f"Nieznany format odpowiedzi SMSAPI: {result}")
                        return False, f"Nieznany format odpowiedzi SMSAPI"
                except Exception as e:
                    self.logger.error(f"Błąd parsowania odpowiedzi JSON: {e}")
                    self.logger.error(f"Surowa odpowiedź: {response.text}")
                    return False, f"Błąd parsowania odpowiedzi: {str(e)}"
            else:
                self.logger.error(f"Błąd HTTP: {response.status_code}")
                self.logger.error(f"Odpowiedź: {response.text}")
                return False, f"Błąd HTTP: {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Błąd połączenia SMS API: {e}")
            return False, f"Błąd połączenia: {str(e)}"
        except Exception as e:
            self.logger.error(f"Błąd wysyłania SMS do {phone_number}: {e}")
            return False, f"Błąd wysyłania SMS: {str(e)}"
    
    def send_reminder_sms(self, phone_number, template_data, sms_template):
        """Wysyła SMS przypomnienia"""
        try:
            # Debug: wyświetl dane szablonu
            self.logger.info(f"📱 Przygotowywanie SMS dla {phone_number}")
            self.logger.info(f"📱 Template data: {template_data}")
            self.logger.info(f"📱 SMS template: {sms_template}")
            
            # Przygotuj treść SMS
            message = sms_template.format(**template_data)
            self.logger.info(f"📱 Przygotowana wiadomość: {message}")
            
            # Wyślij SMS
            success, message_result = self.send_sms(phone_number, message)
            return success, message_result
            
        except Exception as e:
            self.logger.error(f"Błąd wysyłania SMS przypomnienia: {e}")
            return False, f"Błąd przygotowania SMS: {str(e)}"
    
    def test_connection(self, test_number=None):
        """Testuje połączenie z SMS API używając OAuth Bearer token"""
        try:
            if not self.api_token:
                return False, "Brak tokenu SMS API"
            
            # Sprawdź token przez wysłanie testowego SMS - to jest bardziej niezawodne
            test_url = "https://api.smsapi.pl/sms.do"
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            # Wyślij testowy SMS do sprawdzenia autoryzacji
            payload = {
                'to': '48501332990',  # Numer testowy
                'message': f'Test autoryzacji - {datetime.now().strftime("%H:%M:%S")}',
                'format': 'json'
            }
            
            response = requests.post(test_url, data=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    self.logger.info(f"📄 Odpowiedź test_connection: {result}")
                    
                    # Sprawdź czy SMS został wysłany pomyślnie
                    if result.get('error') == 0 or ('list' in result and len(result['list']) > 0):
                        # Autoryzacja udana - SMS został wysłany
                        if test_number and test_number != '48501332990':
                            # Jeśli podano inny numer testowy, wyślij dodatkowy SMS
                            test_message = f"Test Windykator - Połączenie OK - {datetime.now().strftime('%H:%M:%S')}"
                            success, message = self.send_sms(test_number, test_message)
                            if success:
                                return True, "Test połączenia udany - SMS testowy został wysłany"
                            else:
                                return False, f"Test połączenia nieudany: {message}"
                        else:
                            return True, "Autoryzacja SMS API udana - testowy SMS wysłany"
                    else:
                        error_msg = result.get('message', 'Nieznany błąd SMS API')
                        return False, f"Błąd autoryzacji SMS API: {error_msg}"
                except Exception as e:
                    self.logger.error(f"Błąd parsowania odpowiedzi JSON w test_connection: {e}")
                    self.logger.error(f"Surowa odpowiedź: {response.text}")
                    return False, f"Błąd parsowania odpowiedzi: {str(e)}"
            else:
                self.logger.error(f"Błąd HTTP w test_connection: {response.status_code}")
                self.logger.error(f"Odpowiedź: {response.text}")
                return False, f"Błąd HTTP: {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Błąd testu połączenia SMS API: {e}")
            return False, f"Błąd połączenia: {str(e)}"
        except Exception as e:
            self.logger.error(f"Błąd testu połączenia SMS API: {e}")
            return False, f"Błąd testu połączenia: {str(e)}"
    
    def get_account_info(self):
        """Zwraca informacje o koncie SMS API używając OAuth Bearer token"""
        try:
            if not self.api_token:
                return None
            
            test_url = "https://api.smsapi.pl/user.do"
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            # SMSAPI wymaga parametru 'action' dla /user.do
            payload = {
                'action': 'get',
                'format': 'json'
            }
            
            response = requests.post(test_url, data=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                # Sprawdź czy odpowiedź zawiera dane użytkownika
                if result.get('error') == 0:
                    return {
                        'username': result.get('username', ''),
                        'points': result.get('points', 0),
                        'sender_names': result.get('sender_names', [])
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Błąd pobierania informacji o koncie SMS API: {e}")
            return None
    
    def validate_phone_number(self, phone_number):
        """Waliduje numer telefonu - uproszczona logika"""
        # Usuń wszystko oprócz cyfr
        cleaned = re.sub(r'[^\d]', '', str(phone_number))
        
        # Usuń wiodące 00/48/+48
        if cleaned.startswith('0048'):
            cleaned = cleaned[4:]  # Usuń 0048
        elif cleaned.startswith('48'):
            cleaned = cleaned[2:]  # Usuń 48
        
        # Sprawdź czy numer ma 9 cyfr (polski numer)
        if len(cleaned) == 9:
            return f"48{cleaned}"
        else:
            return None 
"""
Moduł do wysyłania emaili przez Microsoft 365
"""
from O365 import Account
import logging
from datetime import datetime

class EmailSender:
    """Klasa do wysyłania emaili przez Microsoft 365"""
    
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.account = None
        self.logger = logging.getLogger(__name__)
        
        if client_id and client_secret:
            self.account = Account((client_id, client_secret))
    
    def authenticate(self):
        """Autoryzacja z Microsoft 365"""
        if not self.account:
            return False, "Brak konfiguracji Microsoft 365"
        
        try:
            if self.account.authenticate(scopes=['Mail.Send']):
                self.logger.info("Autoryzacja Microsoft 365 udana")
                return True, "Autoryzacja udana"
            else:
                return False, "Błąd autoryzacji Microsoft 365"
        except Exception as e:
            self.logger.error(f"Błąd autoryzacji Microsoft 365: {e}")
            return False, f"Błąd autoryzacji: {str(e)}"
    
    def send_email(self, to_email, subject, html_content, from_name="Dział Windykacji"):
        """Wysyła email przez Microsoft 365"""
        if not self.account:
            return False, "Brak konfiguracji Microsoft 365"
        
        try:
            # Autoryzuj jeśli potrzeba
            auth_success, auth_message = self.authenticate()
            if not auth_success:
                return False, auth_message
            
            # Pobierz mailbox
            mailbox = self.account.mailbox()
            
            # Utwórz wiadomość
            message = mailbox.new_message()
            message.to.add(to_email)
            message.subject = subject
            message.body = html_content
            message.body_type = 'HTML'
            
            # Wyślij wiadomość
            message.send()
            
            self.logger.info(f"Email wysłany do: {to_email}")
            return True, "Email wysłany pomyślnie"
            
        except Exception as e:
            self.logger.error(f"Błąd wysyłania email do {to_email}: {e}")
            return False, f"Błąd wysyłania email: {str(e)}"
    
    def send_reminder_email(self, to_email, template_data, email_template):
        """Wysyła email przypomnienia"""
        try:
            # Przygotuj treść emaila
            subject = "Przypomnienie o płatności"
            html_content = email_template.format(**template_data)
            
            # Wyślij email
            success, message = self.send_email(to_email, subject, html_content)
            return success, message
            
        except Exception as e:
            self.logger.error(f"Błąd wysyłania email przypomnienia: {e}")
            return False, f"Błąd przygotowania email: {str(e)}"
    
    def test_connection(self, test_email=None):
        """Testuje połączenie z Microsoft 365"""
        try:
            # Sprawdź autoryzację
            auth_success, auth_message = self.authenticate()
            if not auth_success:
                return False, auth_message
            
            # Jeśli podano email testowy, wyślij testową wiadomość
            if test_email:
                test_subject = "Test Windykator - Połączenie OK"
                test_body = f"""
                <html>
                <body>
                    <h2>Test połączenia Windykator</h2>
                    <p>Połączenie z Microsoft 365 działa poprawnie!</p>
                    <p>Data testu: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </body>
                </html>
                """
                
                success, message = self.send_email(test_email, test_subject, test_body)
                if success:
                    return True, "Test połączenia udany - wiadomość testowa została wysłana"
                else:
                    return False, f"Test połączenia nieudany: {message}"
            else:
                return True, "Autoryzacja Microsoft 365 udana"
                
        except Exception as e:
            self.logger.error(f"Błąd testu połączenia Microsoft 365: {e}")
            return False, f"Błąd testu połączenia: {str(e)}"
    
    def get_account_info(self):
        """Zwraca informacje o koncie Microsoft 365"""
        if not self.account:
            return None
        
        try:
            # Pobierz informacje o koncie
            account_info = self.account.get_current_user()
            return {
                'name': account_info.display_name,
                'email': account_info.mail,
                'id': account_info.object_id
            }
        except Exception as e:
            self.logger.error(f"Błąd pobierania informacji o koncie: {e}")
            return None 
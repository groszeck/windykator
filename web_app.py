"""
Aplikacja webowa Windykator - interfejs przeglądarkowy
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import os
import logging
from datetime import datetime
import json
import time

# Import istniejących modułów
from config import Config
from data_processor import DataProcessor
from email_sender import EmailSender
from sms_sender import SMSSender

# Konfiguracja Flask
app = Flask(__name__)
app.secret_key = 'windykator_web_secret_key_2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicjalizacja komponentów
config = Config()
data_processor = DataProcessor()
email_sender = None
sms_sender = None

# Globalne zmienne sesji
@app.before_request
def before_request():
    """Inicjalizacja przed każdym żądaniem"""
    if 'data_loaded' not in session:
        session['data_loaded'] = False
    if 'preview_data' not in session:
        session['preview_data'] = []
    if 'column_mapping' not in session:
        session['column_mapping'] = {}

@app.route('/')
def index():
    """Strona główna"""
    return render_template('index.html', 
                         data_loaded=session.get('data_loaded', False),
                         preview_count=len(session.get('preview_data', [])))

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Wczytywanie pliku CSV/TSV/Excel"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nie wybrano pliku', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('Nie wybrano pliku', 'error')
            return redirect(request.url)
        
        # Sprawdź rozszerzenie pliku
        allowed_extensions = {'.csv', '.tsv', '.xlsx', '.xls'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            flash(f'Nieobsługiwany format pliku. Dozwolone: {", ".join(allowed_extensions)}', 'error')
            return redirect(request.url)
        
        if file:
            try:
                # Zapisz plik tymczasowo
                filename = file.filename
                filepath = os.path.join('temp', filename)
                os.makedirs('temp', exist_ok=True)
                file.save(filepath)
                
                logger.info(f"📁 Plik zapisany: {filepath}")
                logger.info(f"📊 Rozmiar pliku: {os.path.getsize(filepath)} bajtów")
                logger.info(f"📋 Typ pliku: {file_ext}")
                
                # Wczytaj dane
                logger.info(f"🔄 Rozpoczynam wczytywanie pliku...")
                load_result = data_processor.load_excel_file(filepath)
                logger.info(f"📊 Wynik wczytywania: {load_result}")
                
                if load_result:
                    logger.info(f"✅ Plik wczytany pomyślnie")
                    logger.info(f"📋 Liczba wierszy: {data_processor.get_row_count()}")
                    logger.info(f"🔗 Mapowanie kolumn: {data_processor.column_mapping}")
                    
                    session['data_loaded'] = True
                    session['column_mapping'] = data_processor.column_mapping
                    
                    # Pobierz dostępne kolumny
                    columns = data_processor.get_columns()
                    logger.info(f"📊 Dostępne kolumny: {columns}")
                    
                    # Pobierz dane do podglądu i zapisz w sesji
                    try:
                        logger.info(f"🔄 Generuję preview_data...")
                        preview_data = data_processor.get_preview_data()
                        session['preview_data'] = preview_data
                        logger.info(f"✅ Pomyślnie wczytano {len(preview_data)} wierszy danych")
                        logger.info(f"📋 Przykładowy wiersz: {preview_data[0] if preview_data else 'BRAK'}")
                    except Exception as e:
                        logger.error(f"❌ Błąd podczas generowania preview_data: {e}")
                        flash(f'Błąd przetwarzania danych: {str(e)}', 'error')
                        return redirect(request.url)
                    
                    flash(f'Plik {filename} został wczytany pomyślnie! Wczytano {len(preview_data)} wierszy.', 'success')
                    return render_template('upload.html', 
                                        columns=columns,
                                        mapping_fields=config.get_mapping_fields())
                else:
                    logger.error(f"❌ Błąd wczytywania pliku - load_excel_file zwrócił False")
                    flash('Błąd wczytywania pliku', 'error')
                    return redirect(request.url)
                    
            except Exception as e:
                logger.error(f"Błąd wczytywania pliku: {e}")
                flash(f'Błąd wczytywania pliku: {str(e)}', 'error')
                return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/mapping', methods=['GET', 'POST'])
def column_mapping():
    """Mapowanie kolumn"""
    if not session.get('data_loaded', False):
        flash('Najpierw wczytaj plik', 'warning')
        return redirect(url_for('upload_file'))
    
    if request.method == 'POST':
        # Pobierz mapowanie z formularza
        mapping = {}
        for field, _ in config.get_mapping_fields():
            column_name = request.form.get(field, '')
            if column_name:
                mapping[field] = column_name
        
        # Ustaw mapowanie
        data_processor.set_column_mapping(mapping)
        session['column_mapping'] = mapping
        
        flash('Mapowanie kolumn zostało zapisane', 'success')
        return redirect(url_for('preview'))
    
    # Pokaż formularz mapowania
    columns = data_processor.get_columns()
    current_mapping = session.get('column_mapping', {})
    
    return render_template('mapping.html',
                         columns=columns,
                         mapping_fields=config.get_mapping_fields(),
                         current_mapping=current_mapping)

@app.route('/preview')
def preview():
    """Podgląd danych"""
    if not session.get('data_loaded', False):
        flash('Najpierw wczytaj plik', 'warning')
        return redirect(url_for('upload_file'))
    
    try:
        # Pobierz dane do podglądu
        preview_data = data_processor.get_preview_data()
        session['preview_data'] = preview_data
        
        return render_template('preview.html', 
                             preview_data=preview_data,
                             data_count=len(preview_data))
    except Exception as e:
        logger.error(f"Błąd generowania podglądu: {e}")
        flash(f'Błąd generowania podglądu: {str(e)}', 'error')
        return redirect(url_for('upload_file'))

@app.route('/templates')
def templates():
    """Zarządzanie szablonami"""
    try:
        # Wczytaj szablony
        email_template = config.load_template('email')
        sms_template = config.load_template('sms')
        
        return render_template('templates.html',
                             email_template=email_template,
                             sms_template=sms_template)
    except Exception as e:
        logger.error(f"Błąd wczytywania szablonów: {e}")
        flash(f'Błąd wczytywania szablonów: {str(e)}', 'error')
        return render_template('templates.html',
                             email_template='',
                             sms_template='')

@app.route('/save_template', methods=['POST'])
def save_template():
    """Zapisywanie szablonu"""
    try:
        template_type = request.form.get('template_type')
        content = request.form.get('content', '')
        
        if template_type in ['email', 'sms']:
            config.save_template(template_type, content)
            flash(f'Szablon {template_type} został zapisany', 'success')
        else:
            flash('Nieprawidłowy typ szablonu', 'error')
            
    except Exception as e:
        logger.error(f"Błąd zapisywania szablonu: {e}")
        flash(f'Błąd zapisywania szablonu: {str(e)}', 'error')
    
    return redirect(url_for('templates'))

@app.route('/sending')
def sending():
    """Strona wysyłki"""
    if not session.get('data_loaded', False):
        flash('Najpierw wczytaj plik', 'warning')
        return redirect(url_for('upload_file'))
    
    if not session.get('preview_data', []):
        flash('Najpierw wygeneruj podgląd danych', 'warning')
        return redirect(url_for('preview'))
    
    return render_template('sending.html',
                         preview_data=session.get('preview_data', []),
                         data_count=len(session.get('preview_data', [])))

@app.route('/api/test_sending', methods=['POST'])
def test_sending():
    """API do testowania wysyłki"""
    try:
        data = request.get_json()
        send_email = data.get('send_email', False)
        send_sms = data.get('send_sms', False)
        
        if not session.get('preview_data', []):
            return jsonify({'success': False, 'message': 'Brak danych do testowania'})
        
        # Pobierz szablony
        email_template = config.load_template('email')
        sms_template = config.load_template('sms')
        
        # Pobierz wybrane wiersze (domyślnie wszystkie jeśli nie podano)
        selected_rows = data.get('selected_rows', [])
        preview_data = session.get('preview_data', [])
        
        # Jeśli nie wybrano konkretnych wierszy, przetestuj wszystkie
        if not selected_rows:
            selected_rows = list(range(len(preview_data)))
        
        test_results = []
        
        for row_index in selected_rows:
            if row_index < len(preview_data):
                item = preview_data[row_index]
                result = {
                    'kontrahent': item.get('kontrahent', ''),
                    'email': item.get('email', ''),
                    'telefon': item.get('telefon', ''),
                    'email_test': None,
                    'sms_test': None
                }
                
                # Test email
                if send_email and item.get('email'):
                    try:
                        # Symuluj test email
                        result['email_test'] = {
                            'success': True,
                            'message': 'Symulacja wysłania email udana',
                            'to': item.get('email'),
                            'subject': '🧪 TEST - Przypomnienie o płatności',
                            'content_preview': email_template[:200] + '...' if len(email_template) > 200 else email_template
                        }
                    except Exception as e:
                        result['email_test'] = {
                            'success': False,
                            'message': f'Błąd testu email: {str(e)}'
                        }
                
                # Test SMS
                if send_sms and item.get('telefon'):
                    try:
                        # Rzeczywisty test SMS - wysyłamy do SMSAPI
                        logger.info(f"🧪 TEST SMS - Wysyłam do: {item.get('telefon')}")
                        
                        # Sprawdź konfigurację SMS
                        api_config = config.load_api_config()
                        if not api_config.get('sms_token'):
                            result['sms_test'] = {
                                'success': False,
                                'message': 'Brak konfiguracji SMS API'
                            }
                        else:
                            # Inicjalizuj SMS sender
                            sms_sender = SMSSender(api_config.get('sms_token'), 
                                                 api_config.get('sms_sender'),
                                                 api_config.get('sms_url', 'https://api.smsapi.pl/sms.do'))
                            
                            # Przygotuj dane szablonu
                            template_data = {
                                'kontrahent': item.get('kontrahent', ''),
                                'nip': item.get('nip', ''),
                                'nr_faktury': item.get('nr_faktury', ''),
                                'email': item.get('email', ''),
                                'telefon': item.get('telefon', ''),
                                'kwota': item.get('kwota', ''),
                                'dni_po_terminie': item.get('dni_po_terminie', ''),
                                'data_faktury': item.get('data_faktury', '')
                            }
                            
                            # Wyślij SMS testowy (z prefiksem TEST)
                            test_template = f"🧪 TEST: {sms_template}"
                            success, message = sms_sender.send_reminder_sms(
                                item.get('telefon'), template_data, test_template
                            )
                            
                            result['sms_test'] = {
                                'success': success,
                                'message': f'TEST SMS: {message}',
                                'to': item.get('telefon'),
                                'content': test_template
                            }
                            
                            logger.info(f"🧪 TEST SMS wynik: {success}, {message}")
                            
                    except Exception as e:
                        logger.error(f"❌ Błąd testu SMS: {e}")
                        result['sms_test'] = {
                            'success': False,
                            'message': f'Błąd testu SMS: {str(e)}'
                        }
                
                test_results.append(result)
        
        return jsonify({
            'success': True,
            'results': test_results,
            'message': f'Test zakończony dla {len(test_results)} pozycji'
        })
        
    except Exception as e:
        logger.error(f"Błąd testowania wysyłki: {e}")
        return jsonify({'success': False, 'message': f'Błąd testowania: {str(e)}'})

@app.route('/api/real_sending', methods=['POST'])
def real_sending():
    """API do rzeczywistej wysyłki"""
    try:
        data = request.get_json()
        send_email = data.get('send_email', False)
        send_sms = data.get('send_sms', False)
        
        logger.info(f"🚀 Rozpoczynam rzeczywistą wysyłkę")
        logger.info(f"📧 Send email: {send_email} (typ: {type(send_email)})")
        logger.info(f"📱 Send SMS: {send_sms} (typ: {type(send_sms)})")
        logger.info(f"📋 Surowe dane: {data}")
        
        if not session.get('preview_data', []):
            return jsonify({'success': False, 'message': 'Brak danych do wysłania'})
        
        # Sprawdź konfigurację i zainicjalizuj sendery
        email_sender = None
        sms_sender = None
        
        if send_email:
            api_config = config.load_api_config()
            if not api_config.get('client_id') or not api_config.get('client_secret'):
                return jsonify({'success': False, 'message': 'Skonfiguruj Microsoft 365 API'})
            
            email_sender = EmailSender(api_config['client_id'], api_config['client_secret'])
        
        if send_sms:
            api_config = config.load_api_config()
            logger.info(f"📱 Konfiguracja SMS: token={api_config.get('sms_token', 'BRAK')[:10]}..., sender={api_config.get('sms_sender', 'BRAK')}, url={api_config.get('sms_url', 'BRAK')}")
            
            if not api_config.get('sms_token'):
                logger.error("❌ Brak tokenu SMS API")
                return jsonify({'success': False, 'message': 'Skonfiguruj SMS API'})
            
            sms_sender = SMSSender(api_config.get('sms_token'), 
                                 api_config.get('sms_sender'),
                                 api_config.get('sms_url', 'https://api.smsapi.pl/sms.do'))
            logger.info(f"✅ SMS sender zainicjalizowany: {sms_sender}")
            logger.info(f"✅ Typ SMS sender: {type(sms_sender)}")
            logger.info(f"✅ SMS sender ma metodę send_reminder_sms: {hasattr(sms_sender, 'send_reminder_sms')}")
        
        # Pobierz szablony
        email_template = config.load_template('email')
        sms_template = config.load_template('sms')
        
        logger.info(f"📧 Szablon email: {len(email_template)} znaków")
        logger.info(f"📱 Szablon SMS: {len(sms_template)} znaków")
        logger.info(f"📱 Szablon SMS treść: {sms_template}")
        
        # Pobierz wybrane wiersze (domyślnie wszystkie jeśli nie podano)
        selected_rows = data.get('selected_rows', [])
        preview_data = session.get('preview_data', [])
        
        # Jeśli nie wybrano konkretnych wierszy, przetestuj wszystkie
        if not selected_rows:
            selected_rows = list(range(len(preview_data)))
        
        logger.info(f"📋 Przetwarzam {len(selected_rows)} wybranych wierszy z {len(preview_data)} dostępnych")
        
        sending_results = []
        
        for i, row_index in enumerate(selected_rows):
            if row_index < len(preview_data):
                item = preview_data[row_index]
            logger.info(f"📋 Przetwarzam item {i+1}/{len(selected_rows)}: {item}")
            
            result = {
                'kontrahent': item.get('kontrahent', ''),
                'email': item.get('email', ''),
                'telefon': item.get('telefon', ''),
                'email_status': None,
                'sms_status': None
            }
            
            # Wyślij email
            if send_email and item.get('email') and email_sender:
                try:
                    logger.info(f"📧 Wysyłam email do: {item.get('email')}")
                    
                    template_data = {
                        'kontrahent': item.get('kontrahent', ''),
                        'nip': item.get('nip', ''),
                        'nr_faktury': item.get('nr_faktury', ''),
                        'email': item.get('email', ''),
                        'telefon': item.get('telefon', ''),
                        'kwota': item.get('kwota', ''),
                        'dni_po_terminie': item.get('dni_po_terminie', ''),
                        'data_faktury': item.get('data_faktury', '')
                    }
                    
                    success, message = email_sender.send_reminder_email(
                        item.get('email'), template_data, email_template
                    )
                    
                    logger.info(f"📧 Email {item.get('email')}: {'✅' if success else '❌'} {message}")
                    
                    result['email_status'] = {
                        'success': success,
                        'message': message
                    }
                except Exception as e:
                    logger.error(f"❌ Błąd wysyłania email: {e}")
                    result['email_status'] = {
                        'success': False,
                        'message': f'Błąd wysyłania email: {str(e)}'
                    }
            elif send_email and item.get('email') and not email_sender:
                result['email_status'] = {
                    'success': False,
                    'message': 'Błąd: Email sender nie został zainicjalizowany'
                }
            
            # Wyślij SMS
            logger.info(f"📱 Sprawdzam warunki SMS: send_sms={send_sms}, telefon={item.get('telefon')}, sms_sender={sms_sender}")
            
            if send_sms and item.get('telefon') and sms_sender:
                try:
                    logger.info(f"📱 Wysyłam SMS do: {item.get('telefon')} dla: {item.get('kontrahent')}")
                    
                    template_data = {
                        'kontrahent': item.get('kontrahent', ''),
                        'nip': item.get('nip', ''),
                        'nr_faktury': item.get('nr_faktury', ''),
                        'email': item.get('email', ''),
                        'telefon': item.get('telefon', ''),
                        'kwota': item.get('kwota', ''),
                        'dni_po_terminie': item.get('dni_po_terminie', ''),
                        'data_faktury': item.get('data_faktury', '')
                    }
                    
                    logger.info(f"📱 Template data: {template_data}")
                    
                    success, message = sms_sender.send_reminder_sms(
                        item.get('telefon'), template_data, sms_template
                    )
                    
                    logger.info(f"📱 SMS {item.get('telefon')}: {'✅' if success else '❌'} {message}")
                    
                    result['sms_status'] = {
                        'success': success,
                        'message': message
                    }
                except Exception as e:
                    logger.error(f"❌ Błąd wysyłania SMS: {e}")
                    result['sms_status'] = {
                        'success': False,
                        'message': f'Błąd wysyłania SMS: {str(e)}'
                    }
            elif send_sms and item.get('telefon') and not sms_sender:
                result['sms_status'] = {
                    'success': False,
                    'message': 'Błąd: SMS sender nie został zainicjalizowany'
                }
            
            sending_results.append(result)
            
            # PRZERWA między wysyłkami (2 sekundy) - tylko jeśli to nie ostatnia pozycja
            if i < len(selected_rows) - 1:
                logger.info(f"⏳ Czekam 2 sekundy przed następną wysyłką...")
                time.sleep(2)
        
        # Logowanie wyników
        logger.info(f"📊 Wyniki wysyłki:")
        for i, result in enumerate(sending_results):
            logger.info(f"  Pozycja {i}: {result.get('kontrahent', 'N/A')}")
            if result.get('email_status'):
                logger.info(f"    Email: {result['email_status'].get('success', False)} - {result['email_status'].get('message', 'N/A')}")
            if result.get('sms_status'):
                logger.info(f"    SMS: {result['sms_status'].get('success', False)} - {result['sms_status'].get('message', 'N/A')}")
        
        return jsonify({
            'success': True,
            'results': sending_results,
            'message': f'Wysyłka zakończona dla {len(sending_results)} pozycji'
        })
        
    except Exception as e:
        logger.error(f"Błąd rzeczywistej wysyłki: {e}")
        return jsonify({'success': False, 'message': f'Błąd wysyłki: {str(e)}'})

@app.route('/config')
def configuration():
    """Strona konfiguracji"""
    try:
        api_config = config.load_api_config()
        return render_template('config.html', api_config=api_config)
    except Exception as e:
        logger.error(f"Błąd wczytywania konfiguracji: {e}")
        flash(f'Błąd wczytywania konfiguracji: {str(e)}', 'error')
        return render_template('config.html', api_config={})

@app.route('/save_config', methods=['POST'])
def save_config():
    """Zapisywanie konfiguracji"""
    try:
        config_data = {
            'client_id': request.form.get('client_id', ''),
            'client_secret': request.form.get('client_secret', ''),
            'test_email': request.form.get('test_email', ''),
            'sms_url': request.form.get('sms_url', 'https://api.smsapi.pl/sms.do'),
            'sms_token': request.form.get('sms_token', ''),
            'sms_sender': request.form.get('sms_sender', ''),
            'sms_test_number': request.form.get('sms_test_number', '')
        }
        
        config.save_api_config(config_data)
        flash('Konfiguracja została zapisana', 'success')
        
    except Exception as e:
        logger.error(f"Błąd zapisywania konfiguracji: {e}")
        flash(f'Błąd zapisywania konfiguracji: {str(e)}', 'error')
    
    return redirect(url_for('configuration'))

@app.route('/export_csv')
def export_csv():
    """Eksport danych do CSV"""
    if not session.get('preview_data', []):
        flash('Brak danych do eksportu', 'warning')
        return redirect(url_for('preview'))
    
    try:
        import csv
        from io import StringIO
        
        # Przygotuj dane do eksportu
        output = StringIO()
        writer = csv.writer(output)
        
        # Nagłówki
        headers = ['Kontrahent', 'NIP', 'Nr Faktury', 'Email', 'Telefon', 'Kwota', 'Dni Po Terminie']
        writer.writerow(headers)
        
        # Dane
        for item in session.get('preview_data', []):
            row = [
                item.get('kontrahent', ''),
                item.get('nip', ''),
                item.get('nr_faktury', ''),
                item.get('email', ''),
                item.get('telefon', ''),
                item.get('kwota', ''),
                item.get('dni_po_terminie', '')
            ]
            writer.writerow(row)
        
        output.seek(0)
        
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=windykator_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
        )
        
    except Exception as e:
        logger.error(f"Błąd eksportu CSV: {e}")
        flash(f'Błąd eksportu CSV: {str(e)}', 'error')
        return redirect(url_for('preview'))

@app.route('/api/test_sms_connection', methods=['POST'])
def test_sms_connection():
    """API do testowania połączenia SMS API"""
    try:
        data = request.get_json()
        sms_token = data.get('sms_token')
        sms_sender = data.get('sms_sender', '')
        sms_url = data.get('sms_url', 'https://api.smsapi.pl/sms.do')
        test_number = data.get('test_number')
        
        if not sms_token:
            return jsonify({'success': False, 'message': 'Brak tokenu SMS API'})
        
        try:
            # Inicjalizuj SMS sender
            sms_sender_instance = SMSSender(sms_token, sms_sender, sms_url)
            
            # Test połączenia
            success, message = sms_sender_instance.test_connection(test_number)
            
            return jsonify({
                'success': success,
                'message': message
            })
            
        except Exception as e:
            logger.error(f"❌ Błąd testu połączenia SMS: {e}")
            return jsonify({
                'success': False,
                'message': f'Błąd testu połączenia: {str(e)}'
            })
            
    except Exception as e:
        logger.error(f"Błąd testu połączenia SMS: {e}")
        return jsonify({'success': False, 'message': f'Błąd: {str(e)}'})

@app.route('/api/send_test_sms', methods=['POST'])
def send_test_sms():
    """API do wysłania testowego SMS-a"""
    try:
        data = request.get_json()
        sms_token = data.get('sms_token')
        sms_sender = data.get('sms_sender', '')
        sms_url = data.get('sms_url', 'https://api.smsapi.pl/sms.do')
        test_number = data.get('test_number')
        
        if not sms_token:
            return jsonify({'success': False, 'message': 'Brak tokenu SMS API'})
        
        if not test_number:
            return jsonify({'success': False, 'message': 'Brak numeru testowego'})
        
        try:
            # Inicjalizuj SMS sender
            sms_sender_instance = SMSSender(sms_token, sms_sender, sms_url)
            
            # Przygotuj testowy szablon
            test_template = "🧪 TEST Windykator - Połączenie OK - " + datetime.now().strftime('%H:%M:%S')
            
            # Wyślij testowy SMS
            success, message = sms_sender_instance.send_sms(test_number, test_template)
            
            return jsonify({
                'success': success,
                'message': message,
                'to': test_number,
                'content': test_template
            })
            
        except Exception as e:
            logger.error(f"❌ Błąd wysyłania testowego SMS: {e}")
            return jsonify({
                'success': False,
                'message': f'Błąd wysyłania: {str(e)}'
            })
            
    except Exception as e:
        logger.error(f"Błąd wysyłania testowego SMS: {e}")
        return jsonify({'success': False, 'message': f'Błąd: {str(e)}'})

@app.errorhandler(404)
def not_found(error):
    """Obsługa błędu 404"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Obsługa błędu 500"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Utwórz folder temp jeśli nie istnieje
    os.makedirs('temp', exist_ok=True)
    
    print("🌐 Uruchamiam aplikację webową Windykator...")
    print("📱 Dostępna pod adresem: http://localhost:5000")
    print("🖥️  Aplikacja desktopowa pozostaje nienaruszona")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000) 
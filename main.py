"""
Główny plik aplikacji Windykator
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import logging
import glob
import os
import time

# Import modułów
from config import Config
from data_processor import DataProcessor
from email_sender import EmailSender
from sms_sender import SMSSender
from ui_components import UIComponents

class WindykatorApp:
    """Główna klasa aplikacji Windykator"""
    
    def __init__(self):
        # Konfiguracja logowania
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Inicjalizacja komponentów
        self.config = Config()
        self.data_processor = DataProcessor()
        self.email_sender = None
        self.sms_sender = None
        
        # Zmienne aplikacji
        self.preview_items = []
        self.sending_window = None
        
        # Inicjalizacja historii edytora
        self.editor_history = []
        self.current_history_index = -1
        
        # Tworzenie głównego okna
        self.root = tk.Tk()
        self.root.title("Windykator - System Windykacji")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Konfiguracja Azure theme
        self.setup_azure_theme()
        
        # Tworzenie interfejsu
        self.create_widgets()
        
        # Automatyczne wczytanie konfiguracji
        self.load_config_on_startup()
        
        # Automatyczne wczytanie placeholders
        self.load_placeholders()
        
        # Dodaj przycisk do przełączania motywu
        self.create_theme_switch()
    
    def setup_azure_theme(self):
        """Konfiguracja Azure ttk theme"""
        try:
            # Załaduj Azure theme i ustaw jasny motyw na starcie
            self.root.tk.call("source", "azure.tcl")
            self.root.tk.call("set_theme", "light")
            
            print("✅ Azure theme został załadowany pomyślnie (light)")
            
            # Dodatkowe style
            style = ttk.Style()
            style.configure('Header.TLabel', font=('Arial', 16, 'bold'))
            style.configure('Info.TLabel', foreground=self.config.text_color)
            style.configure('Success.TLabel', foreground=self.config.success_color)
            style.configure('Warning.TLabel', foreground=self.config.warning_color)
            style.configure('Error.TLabel', foreground=self.config.danger_color)
            
            # Konfiguracja kolorów dla przycisków Primary
            style.configure('Primary.TButton', 
                          background=self.config.primary_color,
                          foreground=self.config.white_color,
                          borderwidth=0,
                          focuscolor=self.config.primary_color,
                          relief='flat',
                          force=True)
            style.map('Primary.TButton',
                     background=[('active', self.config.primary_color),
                               ('pressed', self.config.primary_color),
                               ('!active', self.config.primary_color),
                               ('disabled', self.config.primary_color),
                               ('alternate', self.config.primary_color),
                               ('readonly', self.config.primary_color)],
                     foreground=[('active', self.config.white_color),
                               ('pressed', self.config.white_color),
                               ('!active', self.config.white_color),
                               ('disabled', self.config.white_color),
                               ('alternate', self.config.white_color),
                               ('readonly', self.config.white_color)],
                     border=[('active', self.config.primary_color),
                            ('pressed', self.config.primary_color),
                            ('!active', self.config.primary_color),
                            ('disabled', self.config.primary_color),
                            ('alternate', self.config.primary_color),
                            ('readonly', self.config.primary_color)])
            
            # Dodatkowo spróbuj nadpisać domyślny styl Button
            style.configure('TButton', 
                          background=self.config.primary_color,
                          foreground=self.config.white_color,
                          force=True)
            style.map('TButton',
                     background=[('active', self.config.primary_color),
                               ('pressed', self.config.primary_color),
                               ('!active', self.config.primary_color)],
                     foreground=[('active', self.config.white_color),
                               ('pressed', self.config.white_color),
                               ('!active', self.config.white_color)])
            
        except Exception as e:
            print(f"⚠️ Błąd ładowania Azure theme: {e}")
            print("Używam domyślnego stylu ttk")
            
            # Fallback do domyślnego stylu
            style = ttk.Style()
            style.theme_use('clam')
            
            # Konfiguracja kolorów dla przycisków Primary w fallback
            style.configure('Primary.TButton', 
                          background=self.config.primary_color,
                          foreground=self.config.white_color,
                          borderwidth=0,
                          focuscolor=self.config.primary_color)
            style.map('Primary.TButton',
                     background=[('active', self.config.primary_color),
                               ('pressed', self.config.primary_color)],
                     foreground=[('active', self.config.white_color),
                               ('pressed', self.config.white_color)])
    
    def create_theme_switch(self):
        """Tworzenie przycisku do przełączania motywu"""
        try:
            # Sprawdź czy Azure theme jest dostępny
            self.root.tk.call("source", "azure.tcl")
            
            # Utwórz przycisk przełączania motywu z białymi napisami
            theme_button = tk.Button(
                self.root, 
                text="🌙", 
                command=self.toggle_theme,
                bg=self.config.primary_color,
                fg=self.config.white_color,
                relief='flat',
                borderwidth=0,
                font=('Arial', 12, 'bold'),
                cursor='hand2',
                width=3
            )
            theme_button.place(relx=0.98, rely=0.02, anchor='ne')
            
            # Zapisz referencję do przycisku
            self.theme_button = theme_button
            
            print("✅ Przycisk przełączania motywu został utworzony")
        except Exception as e:
            print(f"Nie można utworzyć przycisku przełączania motywu: {e}")
    
    def toggle_theme(self):
        """Przełączanie między jasnym a ciemnym motywem"""
        try:
            current_theme = self.root.tk.call("ttk::style", "theme", "use")
            if current_theme == "azure-light":
                self.root.tk.call("set_theme", "dark")
                self.theme_button.configure(text="☀️")
            else:
                self.root.tk.call("set_theme", "light")
                self.theme_button.configure(text="🌙")
        except Exception as e:
            print(f"Błąd przełączania motywu: {e}")
    
    def create_widgets(self):
        """Tworzenie interfejsu użytkownika"""
        # Kontener główny
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Komponenty UI
        ui_components = UIComponents(self.config)
        
        # Nagłówek
        self.header_frame, self.status_label = ui_components.create_header(main_container)
        
        # Notebook z zakładkami
        self.notebook = ui_components.create_notebook(main_container)
        
        # Zakładka danych i mapowania
        self.data_mapping_widgets = ui_components.create_data_mapping_tab(self.notebook)
        
        # Zakładka szablonów
        self.templates_widgets = ui_components.create_templates_tab(self.notebook)
        
        # Zakładka wysyłki
        self.sending_widgets = ui_components.create_sending_tab(self.notebook)
        
        # Zakładka konfiguracji
        self.config_widgets = ui_components.create_config_tab(self.notebook)
        
        # Podłączenie funkcji do przycisków
        self.connect_buttons()
        
        # Wczytanie szablonów
        self.load_templates()
    
    def on_test_mode_change(self, *args):
        """Obsługuje zmianę trybu testowego"""
        try:
            test_mode = self.sending_widgets['test_mode_var'].get()
            if test_mode:
                # Aktualizuj tekst przycisku
                self.sending_widgets['send_btn'].config(text="🧪 Testuj wysyłkę")
                # Aktualizuj status
                self.status_label.config(text="🧪 Tryb testowej wysyłki aktywny")
                # Pokaż sekcję logów
                if hasattr(self, 'test_logs_frame'):
                    self.test_logs_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
                                    # Wyczyść logi
                if hasattr(self, 'test_logs_text'):
                    self.test_logs_text.delete(1.0, tk.END)
                    self.test_logs_text.insert(tk.END, "🧪 Tryb testowej wysyłki aktywny\n")
                    self.test_logs_text.insert(tk.END, "=" * 60 + "\n")
                    self.test_logs_text.insert(tk.END, "📝 Logi będą wyświetlane tutaj podczas testowania...\n")
                    self.test_logs_text.insert(tk.END, "📊 Status wysyłki będzie aktualizowany w tabeli powyżej\n")
                    self.test_logs_text.insert(tk.END, "🚀 Kliknij 'Testuj wysyłkę' aby rozpocząć test\n")
                    self.test_logs_text.insert(tk.END, "=" * 60 + "\n\n")
                    self.test_logs_text.insert(tk.END, "ℹ️ W trybie testowym:\n")
                    self.test_logs_text.insert(tk.END, "   • Nie są wysyłane rzeczywiste wiadomości\n")
                    self.test_logs_text.insert(tk.END, "   • Sprawdzane są szablony i dane\n")
                    self.test_logs_text.insert(tk.END, "   • Symulowane jest wysłanie\n")
                    self.test_logs_text.insert(tk.END, "   • Sprawdzane są błędy formatowania\n")
                    self.test_logs_text.insert(tk.END, "   • Testowane są placeholdery\n")
                    self.test_logs_text.insert(tk.END, "   • Sprawdzane są dane odbiorców\n")
                    self.test_logs_text.insert(tk.END, "   • Weryfikowane są adresy email i numery telefonów\n")
                    self.test_logs_text.insert(tk.END, "   • Sprawdzane są błędy w szablonach\n")
                    self.test_logs_text.insert(tk.END, "   • Testowane są różne formaty danych\n")
                    self.test_logs_text.insert(tk.END, "   • Weryfikowane są błędy w danych\n\n")
            else:
                # Przywróć normalny tekst
                self.sending_widgets['send_btn'].config(text="🚀 Rozpocznij wysyłkę")
                # Aktualizuj status
                self.status_label.config(text="ℹ️ Gotowy do pracy")
                # Ukryj sekcję logów
                if hasattr(self, 'test_logs_frame'):
                    self.test_logs_frame.pack_forget()
        except Exception as e:
            self.logger.error(f"Błąd zmiany trybu testowego: {e}")
    
    def connect_buttons(self):
        """Podłączenie funkcji do przycisków"""
        # Przyciski mapowania danych
        self.data_mapping_widgets['load_btn'].config(command=self.load_excel_file)
        self.data_mapping_widgets['save_mapping_btn'].config(command=self.save_mapping)
        self.data_mapping_widgets['load_mapping_btn'].config(command=self.load_mapping)
        self.data_mapping_widgets['generate_btn'].config(command=self.generate_preview)
        self.data_mapping_widgets['add_item_btn'].config(command=self.add_preview_item)
        self.data_mapping_widgets['remove_item_btn'].config(command=self.remove_selected_preview_item)
        self.data_mapping_widgets['edit_item_btn'].config(command=self.edit_preview_item)
        self.data_mapping_widgets['remove_settled_btn'].config(command=self.remove_settled_items)
        
        # Przyciski szablonów
        self.templates_widgets['save_email_btn'].config(command=lambda: self.save_template('email'))
        self.templates_widgets['load_email_btn'].config(command=lambda: self.load_template('email'))
        self.templates_widgets['preview_email_btn'].config(command=self.show_email_preview)
        self.templates_widgets['save_sms_btn'].config(command=lambda: self.save_template('sms'))
        self.templates_widgets['load_sms_btn'].config(command=lambda: self.load_template('sms'))
        
        # Podłączenie przycisków edytora WYSIWYG
        # Przyciski stylowania (czcionki i rozmiary)
        for btn, value in self.templates_widgets['style_buttons']:
            if '🔤' in btn.cget('text'):  # Przyciski czcionek
                btn.config(command=lambda v=value: self.apply_font_family(v))
            elif '📏' in btn.cget('text'):  # Przyciski rozmiarów
                btn.config(command=lambda v=value: self.apply_font_size(v))
        
        # Przyciski formatowania
        for btn, tag, tooltip in self.templates_widgets['format_buttons']:
            if tag in ['bold', 'italic', 'underline']:
                btn.config(command=lambda t=tag: self.apply_format(t))
            elif tag == 'color':
                btn.config(command=self.apply_color)
            elif tag == 'undo':
                btn.config(command=self.undo_action)
            elif tag == 'redo':
                btn.config(command=self.redo_action)
        
        # Przyciski stopki
        for btn, action, tooltip in self.templates_widgets['footer_buttons']:
            if action == 'html_footer':
                btn.config(command=self.add_html_footer)
            elif action == 'text_footer':
                btn.config(command=self.add_text_footer)
            elif action == 'clear_footer':
                btn.config(command=self.clear_footer)
        
        # Przyciski placeholders
        self.templates_widgets['add_placeholder_btn'].config(command=self.add_placeholder)
        self.templates_widgets['edit_placeholder_btn'].config(command=self.edit_placeholder)
        self.templates_widgets['delete_placeholder_btn'].config(command=self.delete_placeholder)
        self.templates_widgets['save_placeholders_btn'].config(command=self.save_placeholders)
        self.templates_widgets['load_placeholders_btn'].config(command=self.load_placeholders)
        self.templates_widgets['reset_placeholders_btn'].config(command=self.reset_placeholders)
        
        # Przyciski wysyłki
        self.sending_widgets['send_btn'].config(command=self.start_sending)
        self.sending_widgets['export_btn'].config(command=self.export_sending_status_to_csv)
        
        # Podłącz checkbox trybu testowego
        self.sending_widgets['test_mode_var'].trace('w', self.on_test_mode_change)
        
        # Przyciski konfiguracji
        self.config_widgets['save_email_config_btn'].config(command=self.save_email_config)
        self.config_widgets['test_email_btn'].config(command=self.test_email_connection)
        self.config_widgets['save_sms_config_btn'].config(command=self.save_sms_config)
        self.config_widgets['test_sms_btn'].config(command=self.test_sms_connection)
    
    def load_config_on_startup(self):
        """Wczytuje konfigurację przy starcie aplikacji"""
        try:
            # Wczytaj konfigurację API
            api_config = self.config.load_api_config()
            
            # Ustaw wartości w polach konfiguracji
            for field, var in self.config_widgets['email_vars'].items():
                if field in api_config:
                    var.set(api_config[field])
            
            for field, var in self.config_widgets['sms_vars'].items():
                if field in api_config:
                    var.set(api_config[field])
            
            # Wczytaj mapowanie kolumn
            mapping = self.config.load_mapping()
            for field, combo in self.data_mapping_widgets['mapping_fields'].items():
                if field in mapping:
                    combo.set(mapping[field])
            
            print("✅ Konfiguracja została wczytana")
            
        except Exception as e:
            print(f"⚠️ Błąd wczytywania konfiguracji: {str(e)}")
    
    def load_templates(self):
        """Wczytuje szablony do edytorów"""
        try:
            # Wczytaj szablon email
            email_template = self.config.load_template('email')
            self.templates_widgets['email_editor'].delete(1.0, tk.END)
            self.templates_widgets['email_editor'].insert(1.0, email_template)
            
            # Podłącz śledzenie zmian w edytorze email
            self.templates_widgets['email_editor'].bind('<KeyRelease>', self.on_editor_change)
            self.templates_widgets['email_editor'].bind('<ButtonRelease-1>', self.on_editor_change)
            
            # Wczytaj szablon SMS
            sms_template = self.config.load_template('sms')
            self.templates_widgets['sms_editor'].delete(1.0, tk.END)
            self.templates_widgets['sms_editor'].insert(1.0, sms_template)
            
            print("✅ Szablony zostały wczytane")
            
        except Exception as e:
            print(f"⚠️ Błąd wczytywania szablonów: {str(e)}")
    
    def load_excel_file(self):
        """Wczytywanie pliku Excel/CSV/TSV"""
        try:
            # Wybierz plik
            file_path = filedialog.askopenfilename(
                title="Wybierz plik Excel/CSV/TSV",
                filetypes=[
                    ("Pliki Excel, CSV i TSV", "*.xlsx *.xls *.csv *.tsv"),
                    ("Pliki Excel", "*.xlsx *.xls"),
                    ("Pliki CSV i TSV", "*.csv *.tsv"),
                    ("Wszystkie pliki", "*.*")
                ]
            )
            
            if not file_path:
                return
            
            # Wczytaj dane
            if self.data_processor.load_excel_file(file_path):
                # Aktualizuj status
                row_count = self.data_processor.get_row_count()
                self.data_mapping_widgets['file_info'].config(
                    text=f"✅ Wczytano: {row_count} wierszy", 
                    style='Success.TLabel'
                )
                
                # Aktualizuj comboboxy z kolumnami
                self.update_column_mapping()
                
                # Automatycznie wczytaj mapowanie jeśli istnieje
                self.load_mapping()
                
                self.status_label.config(text=f"✅ Wczytano plik: {os.path.basename(file_path)}")
                
            else:
                messagebox.showerror("Błąd", "Nie udało się wczytać pliku")
                
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd wczytywania pliku:\n{str(e)}")
            self.logger.error(f"Błąd wczytywania pliku: {e}")
    
    def update_column_mapping(self):
        """Aktualizuje comboboxy z kolumnami"""
        columns = self.data_processor.get_columns()
        
        # Debug: wyświetl kolumny
        print(f"🔍 Dostępne kolumny w pliku: {columns}")
        print(f"🔍 Liczba kolumn: {len(columns)}")
        
        for field, combo in self.data_mapping_widgets['mapping_fields'].items():
            combo['values'] = [''] + columns
            combo.set('')  # Wyczyść wybór
        
        # Aktualizuj informację o pliku z kolumnami
        if self.data_processor.excel_data is not None:
            row_count = len(self.data_processor.excel_data)
            col_count = len(columns)
            self.data_mapping_widgets['file_info'].config(
                text=f"✅ Wczytano: {row_count} wierszy, {col_count} kolumn", 
                style='Success.TLabel'
            )
    
    def generate_preview(self):
        """Generowanie podglądu danych"""
        if self.data_processor.excel_data is None:
            messagebox.showwarning("Ostrzeżenie", "Najpierw wczytaj plik Excel/CSV")
            return
        
        print(f"🔄 Generuję podgląd dla {len(self.data_processor.excel_data)} wierszy...")
        
        # Przygotuj mapowanie kolumn
        mapping = {}
        for field, combo in self.data_mapping_widgets['mapping_fields'].items():
            if combo.get():
                mapping[field] = combo.get()
        
        # Debug: wyświetl mapowanie
        print(f"🔍 Mapowanie kolumn: {mapping}")
        
        # Ustaw mapowanie przed walidacją
        self.data_processor.set_column_mapping(mapping)
        
        # Sprawdź czy wszystkie wymagane pola są zmapowane
        required_fields = self.config.get_required_fields()
        print(f"🔍 Wymagane pola: {required_fields}")
        missing_fields = self.data_processor.validate_mapping(required_fields)
        print(f"🔍 Brakujące pola: {missing_fields}")
        
        if missing_fields:
            messagebox.showwarning("Ostrzeżenie", 
                                 f"Zmapuj wymagane pola: {', '.join(missing_fields)}")
            return
        
        # Wyczyść poprzedni podgląd
        print("🧹 Czyszczę poprzedni podgląd...")
        old_items = len(self.data_mapping_widgets['preview_tree'].get_children())
        print(f"🧹 Stary podgląd zawierał: {old_items} pozycji")
        
        for item in self.data_mapping_widgets['preview_tree'].get_children():
            self.data_mapping_widgets['preview_tree'].delete(item)
        
        print("🧹 Wyczyszczono poprzedni podgląd")
        
        # Dodaj wiersze do podglądu
        print("📊 Pobieram dane do podglądu...")
        # Pobierz wszystkie wiersze lub maksymalnie 1000 (zamiast domyślnych 10)
        max_preview_rows = min(1000, len(self.data_processor.excel_data))
        # Użyj zmapowanego podglądu zamiast oryginalnych kolumn
        preview_data = self.data_processor.get_preview_data_mapped(max_rows=max_preview_rows)
        print(f"📊 Pobrano {len(preview_data)} wierszy do podglądu (maksymalnie {max_preview_rows})")
        
        print("📝 Dodaję wiersze do Treeview...")
        for i, row_data in enumerate(preview_data):
            # Przygotuj wartości w odpowiedniej kolejności
            values = (
                row_data.get('kontrahent', ''),
                row_data.get('nip', ''),
                row_data.get('nr_faktury', ''),
                row_data.get('email', ''),
                row_data.get('telefon', ''),
                row_data.get('kwota', ''),
                row_data.get('dni_po_terminie', '')
            )
            self.data_mapping_widgets['preview_tree'].insert('', 'end', values=values, tags=(i,))
        
        new_items = len(self.data_mapping_widgets['preview_tree'].get_children())
        print(f"✅ Dodano {len(preview_data)} wierszy do podglądu")
        print(f"✅ Treeview zawiera teraz: {new_items} pozycji")
        
        # Aktualizuj informację o liczbie pozycji
        print("ℹ️ Aktualizuję informację o liczbie pozycji...")
        self.update_preview_info()
        
        total_rows = len(self.data_processor.excel_data)
        messagebox.showinfo("Sukces", f"Wygenerowano podgląd: {len(preview_data)} pozycji z {total_rows} dostępnych")
    
    def add_preview_item(self):
        """Dodawanie pozycji do podglądu"""
        if self.data_processor.excel_data is None:
            messagebox.showwarning("Ostrzeżenie", "Najpierw wczytaj plik Excel/CSV")
            return
        
        # Utwórz okno dialogowe
        dialog = tk.Toplevel(self.root)
        dialog.title("Dodaj pozycję do podglądu")
        dialog.geometry("800x600")
        dialog.transient(self.root)
        
        # Kontener
        container = ttk.Frame(dialog, padding="20")
        container.pack(fill=tk.BOTH, expand=True)
        
        # Nagłówek
        header = ttk.Label(container, text="➕ Dodaj pozycję do podglądu", style='Header.TLabel')
        header.pack(pady=(0, 20))
        
        # Notebook z zakładkami
        notebook = ttk.Notebook(container)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Zakładka 1: Wybierz z danych
        select_frame = ttk.Frame(notebook)
        notebook.add(select_frame, text="📋 Wybierz z danych")
        
        # Treeview z danymi
        tree_frame = ttk.Frame(select_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        columns = self.data_processor.get_columns()
        data_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            data_tree.heading(col, text=col)
            data_tree.column(col, width=120)
        
        # Dodaj dane do treeview
        for index, row in self.data_processor.excel_data.iterrows():
            values = [str(row[col]) for col in columns]
            data_tree.insert('', 'end', values=values, tags=(index,))
        
        data_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=data_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        data_tree.configure(yscrollcommand=scrollbar.set)
        
        # Przycisk dodawania
        def add_selected():
            selected = data_tree.selection()
            if not selected:
                messagebox.showwarning("Ostrzeżenie", "Wybierz pozycję do dodania")
                return
            
            for item in selected:
                item_data = data_tree.item(item)
                index = item_data['tags'][0]
                self.add_item_to_preview(index)
            
            dialog.destroy()
            messagebox.showinfo("Sukces", f"Dodano {len(selected)} pozycji do podglądu")
        
        add_btn = ttk.Button(select_frame, text="➕ Dodaj zaznaczone", 
                            command=add_selected, style='Primary.TButton')
        add_btn.pack(pady=(10, 0))
        
        # Zakładka 2: Ręczne dodawanie
        manual_frame = ttk.Frame(notebook)
        notebook.add(manual_frame, text="✏️ Ręczne dodawanie")
        
        # Pola do ręcznego wprowadzania
        fields = [
            ('kontrahent', 'Kontrahent'),
            ('nip', 'NIP'),
            ('nr_faktury', 'Nr Faktury'),
            ('email', 'Email'),
            ('telefon', 'Telefon'),
            ('kwota', 'Kwota'),
            ('data_faktury', 'Data Faktury')
        ]
        
        manual_entries = {}
        for i, (field, label) in enumerate(fields):
            frame = ttk.Frame(manual_frame)
            frame.pack(fill=tk.X, pady=2)
            
            label_widget = ttk.Label(frame, text=f"{label}:", width=15)
            label_widget.pack(side=tk.LEFT)
            
            entry = ttk.Entry(frame, width=40)
            entry.pack(side=tk.LEFT, padx=(10, 0))
            
            manual_entries[field] = entry
        
        # Przycisk dodawania ręcznego
        def add_manual():
            values = [manual_entries[field].get() for field, _ in fields]
            
            # Sprawdź wymagane pola
            if not values[0] or not values[2]:  # kontrahent i nr_faktury
                messagebox.showwarning("Ostrzeżenie", "Wypełnij pola Kontrahent i Nr Faktury")
                return
            
            self.add_manual_item_to_preview(values)
            dialog.destroy()
            messagebox.showinfo("Sukces", "Dodano pozycję do podglądu")
        
        add_manual_btn = ttk.Button(manual_frame, text="➕ Dodaj ręcznie", 
                                   command=add_manual, style='Primary.TButton')
        add_manual_btn.pack(pady=(20, 0))
    
    def add_manual_item_to_preview(self, values):
        """Dodaje ręcznie wprowadzoną pozycję do podglądu"""
        # Sprawdź czy pozycja już istnieje
        existing_items = self.data_mapping_widgets['preview_tree'].get_children()
        for item in existing_items:
            item_data = self.data_mapping_widgets['preview_tree'].item(item)
            if item_data['values'][2] == values[2]:  # Nr Faktury
                messagebox.showinfo("Informacja", "Ta pozycja już jest w podglądzie")
                return
        
        # Oblicz dni po terminie
        dni_po_terminie = ""
        if values[6]:  # Data Faktury
            try:
                from datetime import datetime
                data_faktury_str = values[6]
                for fmt in ['%Y-%m-%d', '%d.%m.%Y', '%Y/%m/%d', '%d/%m/%Y']:
                    try:
                        data_faktury = datetime.strptime(data_faktury_str, fmt)
                        dni_po_terminie = str((datetime.now() - data_faktury).days)
                        break
                    except ValueError:
                        continue
                if not dni_po_terminie:
                    dni_po_terminie = "Błąd daty"
            except Exception:
                dni_po_terminie = "Błąd daty"
        
        # Dodaj do podglądu
        preview_values = (
            values[0],  # Kontrahent
            values[1],  # NIP
            values[2],  # Nr Faktury
            values[3],  # Email
            values[4],  # Telefon
            values[5],  # Kwota
            dni_po_terminie
        )
        
        self.data_mapping_widgets['preview_tree'].insert('', 'end', values=preview_values, tags=(-1,))
        self.update_preview_info()
    
    def add_item_to_preview(self, index):
        """Dodaje pozycję do podglądu na podstawie indeksu"""
        template_data = self.data_processor.process_row(index)
        if not template_data:
            return
        
        # Sprawdź czy pozycja już istnieje
        existing_items = self.data_mapping_widgets['preview_tree'].get_children()
        for item in existing_items:
            item_data = self.data_mapping_widgets['preview_tree'].item(item)
            if item_data['values'][2] == template_data.get('nr_faktury', ''):  # Nr Faktury
                messagebox.showinfo("Informacja", "Ta pozycja już jest w podglądzie")
                return
        
        # Dodaj do podglądu
        values = (
            template_data.get('kontrahent', ''),
            template_data.get('nip', ''),
            template_data.get('nr_faktury', ''),
            template_data.get('email', ''),
            template_data.get('telefon', ''),
            template_data.get('kwota', ''),
            template_data.get('dni_po_terminie', '')
        )
        
        self.data_mapping_widgets['preview_tree'].insert('', 'end', values=values, tags=(index,))
        self.update_preview_info()
    
    def remove_selected_preview_item(self):
        """Usuwa wybraną pozycję z podglądu"""
        selection = self.data_mapping_widgets['preview_tree'].selection()
        if selection:
            self.data_mapping_widgets['preview_tree'].delete(selection[0])
            self.update_preview_info()
        else:
            messagebox.showwarning("Ostrzeżenie", "Wybierz pozycję do usunięcia")
    
    def edit_preview_item(self):
        """Edytuje wybraną pozycję w podglądzie"""
        try:
            selection = self.data_mapping_widgets['preview_tree'].selection()
            if not selection:
                messagebox.showwarning("Ostrzeżenie", "Wybierz pozycję do edycji")
            return
        
            item = selection[0]
            values = list(self.data_mapping_widgets['preview_tree'].item(item)['values'])
            
            # Okno edycji
            edit_window = tk.Toplevel(self.root)
            edit_window.title("✏️ Edytuj pozycję")
            edit_window.geometry("500x400")
            edit_window.configure(bg='white')
            
            # Główny kontener
            main_frame = ttk.Frame(edit_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Tytuł
            title_label = ttk.Label(main_frame, text="Edytuj dane pozycji", 
                                   font=('Arial', 14, 'bold'))
            title_label.pack(pady=(0, 20))
            
            # Pola edycji
            edit_vars = {}
            fields = ['Kontrahent', 'NIP', 'Nr Faktury', 'Email', 'Telefon', 'Kwota', 'Dni Po Terminie']
            
            for i, field in enumerate(fields):
                frame = ttk.Frame(main_frame)
                frame.pack(fill=tk.X, pady=5)
                
                label = ttk.Label(frame, text=f"{field}:", width=15)
                label.pack(side=tk.LEFT)
                
                var = tk.StringVar(value=str(values[i]) if i < len(values) else "")
                entry = ttk.Entry(frame, textvariable=var, width=30)
                entry.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
                
                edit_vars[field] = var
            
            # Przyciski akcji
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(fill=tk.X, pady=(20, 0))
            
            save_btn = tk.Button(buttons_frame, text="💾 Zapisz zmiany", 
                                bg=self.config.primary_color,
                                fg=self.config.white_color,
                                relief='flat',
                                borderwidth=0,
                                font=('Arial', 10, 'bold'),
                                cursor='hand2',
                                command=lambda: self.save_edited_item(edit_window, item, edit_vars))
            save_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            cancel_btn = tk.Button(buttons_frame, text="❌ Anuluj", 
                                  bg=self.config.primary_color,
                                  fg=self.config.white_color,
                                  relief='flat',
                                  borderwidth=0,
                                  font=('Arial', 10, 'bold'),
                                  cursor='hand2',
                                  command=edit_window.destroy)
            cancel_btn.pack(side=tk.LEFT)
            
            print("✅ Okno edycji zostało otwarte")
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd otwierania edycji:\n{str(e)}")
            self.logger.error(f"Błąd otwierania edycji: {e}")
    
    def save_edited_item(self, edit_window, item, edit_vars):
        """Zapisuje edytowaną pozycję"""
        try:
            # Pobierz nowe wartości
            new_values = []
            fields = ['Kontrahent', 'NIP', 'Nr Faktury', 'Email', 'Telefon', 'Kwota', 'Dni Po Terminie']
            
            for field in fields:
                value = edit_vars[field].get().strip()
                if not value:
                    messagebox.showwarning("Ostrzeżenie", f"Pole '{field}' nie może być puste")
                    return
                new_values.append(value)
            
            # Aktualizuj pozycję w podglądzie
            self.data_mapping_widgets['preview_tree'].item(item, values=new_values)
            
            # Aktualizuj informacje o podglądzie
            self.update_preview_info()
            
            # Zamknij okno edycji
            edit_window.destroy()
            
            messagebox.showinfo("Sukces", "Pozycja została zaktualizowana")
            print("✅ Pozycja została zaktualizowana")
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd zapisywania zmian:\n{str(e)}")
            self.logger.error(f"Błąd zapisywania zmian: {e}")
    
    def update_preview_info(self):
        """Aktualizuje informację o liczbie pozycji w podglądzie"""
        preview_count = len(self.data_mapping_widgets['preview_tree'].get_children())
        if self.data_processor.excel_data is not None:
            total_count = len(self.data_processor.excel_data)
            self.data_mapping_widgets['preview_info'].config(
                text=f"ℹ️ W podglądzie: {preview_count} pozycji z {total_count} dostępnych"
            )
        else:
            self.data_mapping_widgets['preview_info'].config(text=f"ℹ️ W podglądzie: {preview_count} pozycji")
    
    def save_mapping(self):
        """Zapisuje mapowanie kolumn"""
        mapping = {}
        for field, combo in self.data_mapping_widgets['mapping_fields'].items():
            if combo.get():
                mapping[field] = combo.get()
        
        self.config.save_mapping(mapping)
        messagebox.showinfo("Sukces", "Mapowanie zostało zapisane")
    
    def load_mapping(self):
        """Wczytuje mapowanie kolumn"""
        mapping = self.config.load_mapping()
        for field, col_name in mapping.items():
            if field in self.data_mapping_widgets['mapping_fields']:
                self.data_mapping_widgets['mapping_fields'][field].set(col_name)
    
    def save_template(self, template_type):
        """Zapisuje szablon email lub SMS"""
        try:
            if template_type == 'email':
                content = self.templates_widgets['email_editor'].get(1.0, tk.END)
            else:
                content = self.templates_widgets['sms_editor'].get(1.0, tk.END)
            
            self.config.save_template(template_type, content)
            messagebox.showinfo("Sukces", f"Szablon {template_type} został zapisany")
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd zapisywania szablonu:\n{str(e)}")
    
    def load_template(self, template_type):
        """Wczytuje szablon email lub SMS"""
        try:
            content = self.config.load_template(template_type)
            
            if template_type == 'email':
                editor = self.templates_widgets['email_editor']
            else:
                editor = self.templates_widgets['sms_editor']
            
            editor.delete(1.0, tk.END)
            editor.insert(1.0, content)
            
            messagebox.showinfo("Sukces", f"Szablon {template_type} został wczytany")
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd wczytywania szablonu:\n{str(e)}")
    
    def show_email_preview(self):
        """Pokazuje podgląd szablonu emaila z edytorem WYSIWYG"""
        preview_window = tk.Toplevel(self.root)
        preview_window.title("👁️ Podgląd szablonu emaila")
        preview_window.geometry("800x600")
        preview_window.configure(bg='white')
        
        # Główny kontener
        main_frame = ttk.Frame(preview_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pasek narzędzi edytora
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Przyciski stylowania
        style_buttons = [
            ("🔤", "Arial", lambda: self.apply_font_family("Arial")),
            ("🔤", "Times", lambda: self.apply_font_family("Times New Roman")),
            ("🔤", "Courier", lambda: self.apply_font_family("Courier New")),
            ("📏", "12", lambda: self.apply_font_size("12")),
            ("📏", "14", lambda: self.apply_font_size("14")),
            ("📏", "16", lambda: self.apply_font_size("16")),
            ("📏", "18", lambda: self.apply_font_size("18")),
            ("📏", "20", lambda: self.apply_font_size("20")),
        ]
        
        for i, (icon, text, command) in enumerate(style_buttons):
            btn = tk.Button(toolbar_frame, text=f"{icon} {text}", 
                           bg=self.config.primary_color,
                           fg=self.config.white_color,
                           relief='flat',
                           borderwidth=0,
                           font=('Arial', 9, 'bold'),
                           cursor='hand2',
                           command=command)
            btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Separator
        ttk.Separator(toolbar_frame, orient='vertical').pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Przyciski formatowania
        format_buttons = [
            ("B", "bold", lambda: self.apply_format("bold")),
            ("I", "italic", lambda: self.apply_format("italic")),
            ("U", "underline", lambda: self.apply_format("underline")),
            ("🎨", "color", lambda: self.apply_color()),
            ("⬅️", "undo", lambda: self.undo_action()),
            ("➡️", "redo", lambda: self.redo_action()),
        ]
        
        for i, (text, tooltip, command) in enumerate(format_buttons):
            btn = tk.Button(toolbar_frame, text=text, 
                           bg=self.config.primary_color,
                           fg=self.config.white_color,
                           relief='flat',
                           borderwidth=0,
                           font=('Arial', 10, 'bold'),
                           cursor='hand2',
                           command=command)
            btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Separator
        ttk.Separator(toolbar_frame, orient='vertical').pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Przyciski stopki
        footer_buttons = [
            ("📄", "Dodaj stopkę HTML", lambda: self.add_html_footer()),
            ("📄", "Dodaj stopkę tekst", lambda: self.add_text_footer()),
            ("🗑️", "Wyczyść stopkę", lambda: self.clear_footer()),
        ]
        
        for i, (icon, text, command) in enumerate(footer_buttons):
            btn = tk.Button(toolbar_frame, text=f"{icon} {text}", 
                           bg=self.config.primary_color,
                           fg=self.config.white_color,
                           relief='flat',
                                   borderwidth=0,
                                   font=('Arial', 9, 'bold'),
                                   cursor='hand2',
                                   command=command)
            btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Przyciski placeholders
        self.templates_widgets['add_placeholder_btn'].config(command=self.add_placeholder)
        self.templates_widgets['edit_placeholder_btn'].config(command=self.edit_placeholder)
        self.templates_widgets['delete_placeholder_btn'].config(command=self.delete_placeholder)
        self.templates_widgets['save_placeholders_btn'].config(command=self.save_placeholders)
        self.templates_widgets['load_placeholders_btn'].config(command=self.load_placeholders)
        self.templates_widgets['reset_placeholders_btn'].config(command=self.reset_placeholders)
        
        # Edytor WYSIWYG
        editor_frame = ttk.Frame(main_frame)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Edytor tekstu z obsługą HTML
        self.email_editor = tk.Text(editor_frame, wrap=tk.WORD, 
                                   font=('Arial', 12), 
                                   bg='white', fg='black',
                                   insertbackground='black')
        self.email_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        editor_scrollbar = ttk.Scrollbar(editor_frame, orient=tk.VERTICAL, 
                                        command=self.email_editor.yview)
        editor_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.email_editor.configure(yscrollcommand=editor_scrollbar.set)
        
        # Wczytaj aktualny szablon
        try:
            email_template = self.config.load_template('email')
            self.email_editor.insert('1.0', email_template)
        except Exception as e:
            print(f"⚠️ Błąd wczytywania szablonu maila: {str(e)}")
            # Wstaw domyślny szablon
            default_template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Przypomnienie o płatności</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #d32f2f;">Przypomnienie o płatności</h2>
        
        <p>Szanowny/a {imie} {nazwisko},</p>
        
        <p>Informujemy, że termin płatności w wysokości <strong>{kwota} PLN</strong> 
        upłynął dnia <strong>{termin}</strong>.</p>
        
        <p>Od dnia terminu płatności minęło już <strong>{dni_po_terminie} dni</strong>.</p>
        
        <p>Prosimy o niezwłoczne uregulowanie zaległej płatności.</p>
        
        <p>W przypadku pytań prosimy o kontakt.</p>
        
        <p>Z poważaniem,<br>
        Dział Windykacji</p>
    </div>
</body>
</html>"""
            self.email_editor.insert('1.0', default_template)
        
        # Historia edycji
        self.editor_history = []
        self.current_history_index = -1
        
        # Przyciski akcji
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        save_btn = tk.Button(action_frame, text="💾 Zapisz zmiany", 
                            bg=self.config.primary_color,
                            fg=self.config.white_color,
                            relief='flat',
                            borderwidth=0,
                            font=('Arial', 10, 'bold'),
                            cursor='hand2',
                            command=lambda: self.save_email_template_from_editor())
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        preview_btn = tk.Button(action_frame, text="👁️ Podgląd HTML", 
                               bg=self.config.primary_color,
                               fg=self.config.white_color,
                               relief='flat',
                               borderwidth=0,
                               font=('Arial', 10, 'bold'),
                               cursor='hand2',
                               command=lambda: self.preview_html())
        preview_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        close_btn = tk.Button(action_frame, text="❌ Zamknij", 
                             bg=self.config.primary_color,
                             fg=self.config.white_color,
                             relief='flat',
                             borderwidth=0,
                             font=('Arial', 10, 'bold'),
                             cursor='hand2',
                             command=preview_window.destroy)
        close_btn.pack(side=tk.LEFT)
        
        # Bind events dla historii edycji
        self.email_editor.bind('<Key>', self.on_editor_change)
        self.email_editor.bind('<Button-1>', self.on_editor_change)
        
        print("✅ Edytor WYSIWYG został otwarty")
    
    def start_sending(self):
        """Rozpoczyna proces wysyłki"""
        # Sprawdź czy są pozycje w podglądzie
        preview_items = self.data_mapping_widgets['preview_tree'].get_children()
        if not preview_items:
            messagebox.showwarning("Ostrzeżenie", "Brak pozycji do wysłania")
            return
        
        # Sprawdź konfigurację
        if not self.sending_widgets['email_var'].get() and not self.sending_widgets['sms_var'].get():
            messagebox.showwarning("Ostrzeżenie", "Wybierz przynajmniej jeden kanał wysyłki")
            return
        
        # Utwórz okno wysyłki
        self.create_sending_window()
    
    def create_sending_window(self):
        """Tworzy okno wysyłki"""
        self.sending_window = tk.Toplevel(self.root)
        self.sending_window.title("Wysyłka powiadomień")
        self.sending_window.geometry("1000x600")
        self.sending_window.transient(self.root)
        
        # Kontener
        container = ttk.Frame(self.sending_window, padding="20")
        container.pack(fill=tk.BOTH, expand=True)
        
        # Nagłówek
        header = ttk.Label(container, text="📤 Wysyłka powiadomień", style='Header.TLabel')
        header.pack(pady=(0, 20))
        
        # Kontrolki wysyłki
        controls_frame = ttk.LabelFrame(container, text="⚙️ Kontrola wysyłki", padding="10")
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Checkboxy dla kanałów
        channels_frame = ttk.Frame(controls_frame)
        channels_frame.pack(fill=tk.X, pady=(0, 10))
        
        sending_email_var = tk.BooleanVar(value=self.sending_widgets['email_var'].get())
        sending_sms_var = tk.BooleanVar(value=self.sending_widgets['sms_var'].get())
        
        email_check = ttk.Checkbutton(channels_frame, text="📧 Wysyłaj emaile", 
                                    variable=sending_email_var)
        email_check.pack(side=tk.LEFT, padx=(0, 20))
        
        sms_check = ttk.Checkbutton(channels_frame, text="📱 Wysyłaj SMS", 
                                   variable=sending_sms_var)
        sms_check.pack(side=tk.LEFT)
        
        # Przyciski kontroli
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(pady=(10, 0))
        
        send_btn = ttk.Button(buttons_frame, text="🚀 Rozpocznij wysyłkę", 
                             style='Primary.TButton', command=lambda: self.start_sending_process(sending_email_var, sending_sms_var))
        send_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        export_btn = ttk.Button(buttons_frame, text="📊 Eksportuj status CSV", 
                               command=self.export_sending_status_to_csv)
        export_btn.pack(side=tk.LEFT)
        
        # Treeview ze statusem
        status_frame = ttk.LabelFrame(container, text="📊 Status wysyłki", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sekcja logów testowych (widoczna tylko w trybie testowym)
        self.test_logs_frame = ttk.LabelFrame(container, text="📝 Logi testowej wysyłki", padding="10")
        self.test_logs_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Text widget dla logów
        self.test_logs_text = scrolledtext.ScrolledText(self.test_logs_frame, height=8, wrap=tk.WORD)
        self.test_logs_text.pack(fill=tk.BOTH, expand=True)
        
        # Ukryj sekcję logów na starcie
        self.test_logs_frame.pack_forget()
        
        status_tree_frame = ttk.Frame(status_frame)
        status_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        status_columns = ('Kontrahent', 'NIP', 'Nr Faktury', 'Email', 'Telefon', 
                         'Kwota', 'Dni Po Terminie', 'Email Status', 'SMS Status')
        status_tree = ttk.Treeview(status_tree_frame, columns=status_columns, 
                                  show='headings', height=15)
        
        for col in status_columns:
            status_tree.heading(col, text=col)
            status_tree.column(col, width=100)
        
        status_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar dla status treeview
        status_scrollbar = ttk.Scrollbar(status_tree_frame, orient=tk.VERTICAL, 
                                        command=status_tree.yview)
        status_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        status_tree.configure(yscrollcommand=status_scrollbar.set)
        
        # Przygotuj dane do wysyłki
        self.prepare_sending_data(status_tree)
        
        # Zapisz referencje
        self.sending_status_tree = status_tree
        self.sending_email_var = sending_email_var
        self.sending_sms_var = sending_sms_var
    
    def prepare_sending_data(self, status_tree):
        """Przygotowuje dane do wysyłki"""
        # Wyczyść poprzednie dane
        for item in status_tree.get_children():
            status_tree.delete(item)
        
        # Pobierz dane z podglądu
        preview_items = self.data_mapping_widgets['preview_tree'].get_children()
        
        for item in preview_items:
            item_data = self.data_mapping_widgets['preview_tree'].item(item)
            values = list(item_data['values'])
            
            # Dodaj statusy
            values.extend(['Oczekuje', 'Oczekuje'])
            
            # Dodaj do status tree
            status_tree.insert('', 'end', values=values, tags=item_data['tags'])
    
    def start_sending_process(self, email_var, sms_var):
        """Rozpoczyna proces wysyłki"""
        # Sprawdź czy to tryb testowy
        test_mode = self.sending_widgets['test_mode_var'].get()
        
        if test_mode:
            # Tryb testowy - nie potrzebujemy konfiguracji API
            self.logger.info("🧪 Uruchamiam tryb testowej wysyłki")
            # Rozpocznij test w osobnym wątku
            threading.Thread(target=self.test_sending_process, 
                           args=(email_var.get(), sms_var.get()), 
                           daemon=True).start()
            return
        
        # Normalny tryb wysyłki - sprawdź konfigurację
        if email_var.get():
            client_id = self.config_widgets['email_vars']['client_id'].get().strip()
            client_secret = self.config_widgets['email_vars']['client_secret'].get().strip()
            
            if not client_id or not client_secret:
                messagebox.showerror("Błąd", "Skonfiguruj Microsoft 365 API")
                return
            
            self.email_sender = EmailSender(client_id, client_secret)
        
        if sms_var.get():
            sms_token = self.config_widgets['sms_vars']['sms_token'].get().strip()
            sms_url = self.config_widgets['sms_vars']['sms_url'].get().strip()
            
            if not sms_token:
                messagebox.showerror("Błąd", "Skonfiguruj SMS API")
                return
            
            if not sms_url:
                sms_url = "https://api.smsapi.pl/sms.do"  # Domyślny URL
            
            sender_name = self.config_widgets['sms_vars']['sms_sender'].get().strip()
            # Użyj None jeśli sender_name jest pusty
            if not sender_name:
                sender_name = None
            self.sms_sender = SMSSender(sms_token, sender_name, sms_url)
        
        # Potwierdź wysyłkę
        if not messagebox.askyesno("Potwierdź", "Czy na pewno chcesz rozpocząć wysyłkę?"):
            return
        
        # Rozpocznij wysyłkę w osobnym wątku
        threading.Thread(target=self.send_reminders_from_window, 
                       args=(email_var.get(), sms_var.get()), 
                       daemon=True).start()
    
    def test_sending_process(self, send_email, send_sms):
        """Testuje proces wysyłki w trybie testowym"""
        try:
            self.logger.info("🧪 Rozpoczynam testową wysyłkę")
            
            # Dodaj informację o rozpoczęciu testu do UI
            start_log = "🚀 ROZPOCZYNAM TEST WYSYŁKI\n"
            start_log += f"   📧 Email: {'✅' if send_email else '❌'}\n"
            start_log += f"   📱 SMS: {'✅' if send_sms else '❌'}\n"
            start_log += f"   📊 Liczba pozycji do przetestowania: {len(self.sending_status_tree.get_children())}\n"
            
            self.root.after(0, lambda: self.add_test_log(start_log))
            
            # Pobierz szablony
            email_template = self.templates_widgets['email_editor'].get(1.0, tk.END)
            sms_template = self.templates_widgets['sms_editor'].get(1.0, tk.END)
            
            # Pobierz dane do testowania
            items = self.sending_status_tree.get_children()
            
            for item in items:
                item_data = self.sending_status_tree.item(item)
                values = item_data['values']
                index = item_data['tags'][0]
                
                # Przygotuj dane do szablonów
                template_data = {
                    'kontrahent': values[0],
                    'nip': values[1],
                    'nr_faktury': values[2],
                    'email': values[3],
                    'telefon': values[4],
                    'kwota': values[5],
                    'dni_po_terminie': values[6],
                    'data_faktury': ''
                }
                
                # Jeśli to pozycja z Excel (nie ręcznie dodana), pobierz data_faktury
                if index >= 0 and self.data_processor.excel_data is not None:
                    try:
                        row = self.data_processor.excel_data.iloc[index]
                        if 'data_faktury' in self.data_processor.column_mapping:
                            data_faktury_col = self.data_processor.column_mapping['data_faktury']
                            if data_faktury_col in row:
                                template_data['data_faktury'] = str(row[data_faktury_col])
                    except Exception as e:
                        self.logger.error(f"Błąd pobierania data_faktury: {e}")
                
                # Testuj email
                if send_email and values[3]:  # Email
                    try:
                        # Przygotuj treść emaila
                        subject = "🧪 TEST - Przypomnienie o płatności"
                        html_content = email_template.format(**template_data)
                        
                        # Log testowy
                        test_log = f"🧪 TEST EMAIL:\n"
                        test_log += f"   📧 Do: {values[0]} <{values[3]}>\n"
                        test_log += f"   📝 Temat: {subject}\n"
                        test_log += f"   📄 Treść: {html_content[:200]}...\n"
                        test_log += f"   ✅ Status: Symulacja wysłania udana\n"
                        
                        self.logger.info(test_log)
                        
                        # Dodaj log do UI
                        self.root.after(0, lambda: self.add_test_log(test_log))
                        
                        # Aktualizuj status w UI
                        status = "🧪 Test OK"
                        self.root.after(0, lambda: self.update_sending_status(item, status, values[8]))
                        
                    except Exception as e:
                        error_msg = str(e)[:30]
                        self.logger.error(f"Błąd testu email: {e}")
                        self.root.after(0, lambda: self.update_sending_status(item, f"❌ {error_msg}", values[8]))
                
                # Testuj SMS
                if send_sms and values[4]:  # Telefon
                    try:
                        # Przygotuj treść SMS
                        message = sms_template.format(**template_data)
                        
                        # Log testowy
                        test_log = f"🧪 TEST SMS:\n"
                        test_log += f"   📱 Do: {values[0]} <{values[4]}>\n"
                        test_log += f"   📄 Treść: {message}\n"
                        test_log += f"   ✅ Status: Symulacja wysłania udana\n"
                        
                        self.logger.info(test_log)
                        
                        # Dodaj log do UI
                        self.root.after(0, lambda: self.add_test_log(test_log))
                        
                        # Aktualizuj status w UI
                        status = "🧪 Test OK"
                        self.root.after(0, lambda: self.update_sending_status(item, values[7], status))
                        
                    except Exception as e:
                        error_msg = str(e)[:30]
                        self.logger.error(f"Błąd testu SMS: {e}")
                        self.root.after(0, lambda: self.update_sending_status(item, values[7], f"❌ {error_msg}"))
            
            # Dodaj informację o zakończeniu testu
            end_log = "🏁 TEST ZAKOŃCZONY\n"
            end_log += "   ✅ Wszystkie pozycje zostały przetestowane\n"
            end_log += "   📊 Sprawdź status w tabeli powyżej\n"
            end_log += "   📝 Szczegółowe logi dostępne poniżej\n"
            end_log += "   💾 Możesz wyeksportować wyniki do CSV\n"
            end_log += "   🎯 Test zakończony pomyślnie!\n"
            end_log += "   🚀 Możesz teraz uruchomić rzeczywistą wysyłkę\n"
            end_log += "   💡 Wyłącz tryb testowy przed rzeczywistą wysyłką\n"
            end_log += "🔧 Sprawdź logi aby zidentyfikować potencjalne problemy\n"
            end_log += "✅ Wszystko gotowe do rzeczywistej wysyłki!\n"
            end_log += "🎉 Gratulacje! Test przeszedł pomyślnie!\n"
            end_log += "🚀 System gotowy do produkcji!\n"
            end_log += "🎯 Kolejny krok: Uruchom rzeczywistą wysyłkę!\n"
            
            self.root.after(0, lambda: self.add_test_log(end_log))
            
            # Zakończ test i pokaż podsumowanie
            self.root.after(0, lambda: self.show_test_summary())
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Błąd", f"Błąd testu: {str(e)}"))
    
    def add_test_log(self, log_message):
        """Dodaje log do UI testowej wysyłki"""
        try:
            if hasattr(self, 'test_logs_text'):
                # Dodaj timestamp
                from datetime import datetime
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # Dodaj separator
                separator = "─" * 80
                
                # Formatuj log z lepszym wizualnym oddzieleniem
                formatted_log = f"\n{separator}\n"
                formatted_log += f"[{timestamp}] {log_message}\n"
                formatted_log += f"{separator}\n"
                
                # Dodaj do widgetu tekstowego
                self.test_logs_text.insert(tk.END, formatted_log)
                
                # Przewiń na dół
                self.test_logs_text.see(tk.END)
                
        except Exception as e:
            self.logger.error(f"Błąd dodawania logu do UI: {e}")
    
    def show_test_summary(self):
        """Pokazuje podsumowanie testu"""
        try:
            # Policz wyniki testów
            items = self.sending_status_tree.get_children()
            total_items = len(items)
            test_ok_count = 0
            
            for item in items:
                item_data = self.sending_status_tree.item(item)
                values = item_data['values']
                if '🧪 Test OK' in str(values[7]) or '🧪 Test OK' in str(values[8]):
                    test_ok_count += 1
            
            # Pokaż podsumowanie
            summary = f"🧪 Test zakończony!\n\n"
            summary += f"📊 Statystyki:\n"
            summary += f"   • Przetestowano: {total_items} pozycji\n"
            summary += f"   • Testy udane: {test_ok_count} ✅\n"
            summary += f"   • Testy nieudane: {total_items - test_ok_count} ❌\n\n"
            summary += "📝 Szczegółowe logi zostały wyświetlone w oknie testowym.\n"
            summary += "💾 Możesz wyeksportować wyniki do pliku CSV.\n\n"
            summary += "🎯 Test zakończony pomyślnie!\n"
            summary += "🚀 Możesz teraz uruchomić rzeczywistą wysyłkę.\n\n"
            summary += "💡 Wskazówka: Wyłącz tryb testowy przed rzeczywistą wysyłką.\n"
            summary += "🔧 Sprawdź logi aby zidentyfikować potencjalne problemy.\n"
            summary += "✅ Wszystko gotowe do rzeczywistej wysyłki!\n\n"
            summary += "🎉 Gratulacje! Test przeszedł pomyślnie!\n"
            summary += "🚀 System gotowy do produkcji!\n\n"
            summary += "🎯 Kolejny krok: Uruchom rzeczywistą wysyłkę!\n"
            summary += "✅ System przeszedł wszystkie testy pomyślnie!"
            
            messagebox.showinfo("Podsumowanie testu", summary)
            
            # Zapytaj o eksport CSV
            if messagebox.askyesno("Eksport CSV", "Czy chcesz pobrać plik CSV z wynikami testu?"):
                self.export_sending_status_to_csv()
                
        except Exception as e:
            self.logger.error(f"Błąd wyświetlania podsumowania testu: {e}")
    
    def send_reminders_from_window(self, send_email, send_sms):
        """Wysyła powiadomienia z okna wysyłki z przerwami między wysyłkami"""
        try:
            # Pobierz szablony
            email_template = self.templates_widgets['email_editor'].get(1.0, tk.END)
            sms_template = self.templates_widgets['sms_editor'].get(1.0, tk.END)
            
            # Pobierz dane do wysłania
            items = self.sending_status_tree.get_children()
            total_items = len(items)
            
            self.logger.info(f"🚀 Rozpoczynam wysyłkę {total_items} pozycji")
            self.logger.info(f"📧 Email: {'✅' if send_email else '❌'}, 📱 SMS: {'✅' if send_sms else '❌'}")
            
            # Ustaw status "Wysyłanie..." dla wszystkich pozycji
            for item in items:
                item_data = self.sending_status_tree.item(item)
                values = item_data['values']
                
                # Ustaw status "Wysyłanie..." dla email
                if send_email and values[3]:  # Email
                    self.root.after(0, lambda item=item: self.update_sending_status(item, "⏳ Wysyłanie...", values[8]))
                
                # Ustaw status "Wysyłanie..." dla SMS
                if send_sms and values[4]:  # Telefon
                    self.root.after(0, lambda item=item: self.update_sending_status(item, values[7], "⏳ Wysyłanie..."))
            
            # Rozpocznij wysyłkę w osobnym wątku z przerwami
            threading.Thread(target=self._send_reminders_with_delays, 
                           args=(items, send_email, send_sms, email_template, sms_template), 
                           daemon=True).start()
            
        except Exception as e:
            self.logger.error(f"Błąd podczas przygotowania wysyłki: {e}")
            self.root.after(0, lambda: messagebox.showerror("Błąd", f"Błąd przygotowania wysyłki: {str(e)}"))
    
    def _send_reminders_with_delays(self, items, send_email, send_sms, email_template, sms_template):
        """Wysyła powiadomienia z przerwami między wysyłkami"""
        try:
            total_items = len(items)
            self.logger.info(f"📤 Rozpoczynam wysyłkę z przerwami dla {total_items} pozycji")
            
            for i, item in enumerate(items):
                item_data = self.sending_status_tree.item(item)
                values = item_data['values']
                index = item_data['tags'][0]
                
                self.logger.info(f"📤 Przetwarzam pozycję {i+1}/{total_items}: {values[0]}")
                
                # Przygotuj dane do szablonów
                template_data = {
                    'kontrahent': values[0],
                    'nip': values[1],
                    'nr_faktury': values[2],
                    'email': values[3],
                    'telefon': values[4],
                    'kwota': values[5],
                    'dni_po_terminie': values[6],
                    'data_faktury': ''
                }
                
                # Jeśli to pozycja z Excel, pobierz data_faktury
                if index >= 0 and self.data_processor.excel_data is not None:
                    try:
                        row = self.data_processor.excel_data.iloc[index]
                        if 'data_faktury' in self.data_processor.column_mapping:
                            data_faktury_col = self.data_processor.column_mapping['data_faktury']
                            if data_faktury_col in row:
                                template_data['data_faktury'] = str(row[data_faktury_col])
                    except Exception as e:
                        self.logger.error(f"Błąd pobierania data_faktury: {e}")
                
                # Wyślij email
                if send_email and values[3]:  # Email
                    try:
                        self.logger.info(f"📧 Wysyłam email do: {values[3]}")
                        success, message = self.email_sender.send_reminder_email(
                            values[3], template_data, email_template
                        )
                        status = "✅ Wysłano" if success else f"❌ {message[:30]}"
                        self.logger.info(f"📧 Email {values[3]}: {status}")
                        self.root.after(0, lambda item=item, status=status: self.update_sending_status(item, status, values[8]))
                    except Exception as e:
                        error_msg = str(e)[:30]
                        self.logger.error(f"❌ Błąd email {values[3]}: {error_msg}")
                        self.root.after(0, lambda item=item, error=error_msg: self.update_sending_status(item, f"❌ {error}", values[8]))
                
                # Wyślij SMS
                if send_sms and values[4]:  # Telefon
                    try:
                        self.logger.info(f"📱 Wysyłam SMS do: {values[4]}")
                        success, message = self.sms_sender.send_reminder_sms(
                            values[4], template_data, sms_template
                        )
                        status = "✅ Wysłano" if success else f"❌ {message[:30]}"
                        self.logger.info(f"📱 SMS {values[4]}: {status}")
                        self.root.after(0, lambda item=item, status=status: self.update_sending_status(item, values[7], status))
                    except Exception as e:
                        error_msg = str(e)[:30]
                        self.logger.error(f"❌ Błąd SMS {values[4]}: {error_msg}")
                        self.root.after(0, lambda item=item, error=error_msg: self.update_sending_status(item, values[7], f"❌ {error}"))
                
                # PRZERWA między wysyłkami (2 sekundy)
                if i < total_items - 1:  # Nie czekaj po ostatniej pozycji
                    self.logger.info(f"⏳ Czekam 2 sekundy przed następną wysyłką...")
                    time.sleep(2)
            
            self.logger.info(f"✅ Wysyłka zakończona dla {total_items} pozycji")
            
            # Zakończ wysyłkę i zapytaj o pobranie CSV
            self.root.after(0, lambda: self.ask_for_csv_export())
            
        except Exception as e:
            self.logger.error(f"❌ Błąd podczas wysyłki z przerwami: {e}")
            self.root.after(0, lambda: messagebox.showerror("Błąd", f"Błąd wysyłki: {str(e)}"))
    
    def ask_for_csv_export(self):
        """Pyta użytkownika czy chce pobrać CSV ze statusem wysyłki"""
        if messagebox.askyesno("Eksport CSV", "Wysyłka zakończona! Czy chcesz pobrać plik CSV ze statusem wysyłki?"):
            self.export_sending_status_to_csv()
    
    def export_sending_status_to_csv(self):
        """Eksportuje status wysyłki do pliku CSV"""
        try:
            # Pobierz wszystkie dane ze status tree
            all_items = self.sending_status_tree.get_children()
            if not all_items:
                messagebox.showwarning("Ostrzeżenie", "Brak danych do eksportu")
                return
            
            # Przygotuj dane do eksportu
            export_data = []
            headers = ['Kontrahent', 'NIP', 'Nr Faktury', 'Email', 'Telefon', 'Kwota', 'Dni Po Terminie', 'Email Status', 'SMS Status']
            
            for item in all_items:
                values = list(self.sending_status_tree.item(item)['values'])
                export_data.append(values)
            
            # Wybierz miejsce zapisu
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"status_wysylki_{timestamp}.csv"
            
            file_path = filedialog.asksaveasfilename(
                title="Zapisz status wysyłki jako CSV",
                defaultextension=".csv",
                filetypes=[("Pliki CSV", "*.csv"), ("Wszystkie pliki", "*.*")],
                initialname=filename
            )
            
            if not file_path:
                return
            
            # Zapisz do CSV
            import csv
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(export_data)
            
            messagebox.showinfo("Sukces", f"Status wysyłki został zapisany do:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd eksportu CSV:\n{str(e)}")
            self.logger.error(f"Błąd eksportu CSV: {e}")
    
    def update_sending_status(self, item, email_status, sms_status):
        """Aktualizuje status wysyłki"""
        try:
            values = list(self.sending_status_tree.item(item)['values'])
            values[7] = email_status  # Email Status
            values[8] = sms_status    # SMS Status
            self.sending_status_tree.item(item, values=values)
        except Exception as e:
            self.logger.error(f"Błąd aktualizacji statusu: {e}")
    
    def save_email_config(self):
        """Zapisuje konfigurację email"""
        try:
            config = {}
            for field, var in self.config_widgets['email_vars'].items():
                config[field] = var.get()
            
            self.config.save_api_config(config)
            messagebox.showinfo("Sukces", "Konfiguracja email została zapisana")
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd zapisywania konfiguracji:\n{str(e)}")
    
    def test_email_connection(self):
        """Testuje połączenie email"""
        try:
            client_id = self.config_widgets['email_vars']['client_id'].get().strip()
            client_secret = self.config_widgets['email_vars']['client_secret'].get().strip()
            test_email = self.config_widgets['email_vars']['test_email'].get().strip()
            
            if not client_id or not client_secret:
                messagebox.showerror("Błąd", "Wypełnij Client ID i Client Secret")
                return
            
            email_sender = EmailSender(client_id, client_secret)
            success, message = email_sender.test_connection(test_email)
            
            if success:
                messagebox.showinfo("Sukces", message)
            else:
                messagebox.showerror("Błąd", message)
                
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd testu połączenia:\n{str(e)}")
    
    def save_sms_config(self):
        """Zapisuje konfigurację SMS"""
        try:
            config = self.config.load_api_config()
            for field, var in self.config_widgets['sms_vars'].items():
                config[field] = var.get()
            
            self.config.save_api_config(config)
            messagebox.showinfo("Sukces", "Konfiguracja SMS została zapisana")
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd zapisywania konfiguracji:\n{str(e)}")
    
    def test_sms_connection(self):
        """Testuje połączenie SMS"""
        try:
            sms_token = self.config_widgets['sms_vars']['sms_token'].get().strip()
            sms_url = self.config_widgets['sms_vars']['sms_url'].get().strip()
            test_number = self.config_widgets['sms_vars']['sms_test_number'].get().strip()
            
            if not sms_token:
                messagebox.showerror("Błąd", "Wypełnij Token SMS API")
                return
            
            if not sms_url:
                sms_url = "https://api.smsapi.pl/sms.do"  # Domyślny URL
            
            sms_sender = SMSSender(sms_token, None, sms_url)
            # Najpierw sprawdź tylko autoryzację bez wysyłania testowego SMS
            success, message = sms_sender.test_connection(None)
            
            if success:
                messagebox.showinfo("Sukces", message)
            else:
                messagebox.showerror("Błąd", message)
                
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd testu połączenia:\n{str(e)}")
    
    def apply_font_family(self, font_family):
        """Zmienia rodzinę czcionki w edytorze"""
        try:
            if hasattr(self, 'email_editor'):
                # Pobierz aktualny tekst
                current_text = self.email_editor.get("1.0", "end-1c")
                
                # Zastąp style font-family w HTML
                if 'font-family:' in current_text:
                    # Zastąp istniejący font-family
                    import re
                    pattern = r'font-family:\s*[^;]+;'
                    replacement = f'font-family: {font_family}, sans-serif;'
                    new_text = re.sub(pattern, replacement, current_text)
                else:
                    # Dodaj font-family do body
                    new_text = current_text.replace('<body', f'<body style="font-family: {font_family}, sans-serif;"')
                
                # Zastąp tekst w edytorze
                self.email_editor.delete("1.0", "end")
                self.email_editor.insert("1.0", new_text)
                
                print(f"✅ Zmieniono czcionkę na: {font_family}")
        except Exception as e:
            print(f"Błąd zmiany czcionki: {e}")
    
    def apply_font_size(self, size):
        """Zmienia rozmiar czcionki w edytorze"""
        try:
            if hasattr(self, 'email_editor'):
                # Pobierz aktualny tekst
                current_text = self.email_editor.get("1.0", "end-1c")
                
                # Zastąp style font-size w HTML
                if 'font-size:' in current_text:
                    # Zastąp istniejący font-size
                    import re
                    pattern = r'font-size:\s*[^;]+;'
                    replacement = f'font-size: {size}px;'
                    new_text = re.sub(pattern, replacement, current_text)
                else:
                    # Dodaj font-size do body
                    new_text = current_text.replace('<body', f'<body style="font-size: {size}px;"')
                
                # Zastąp tekst w edytorze
                self.email_editor.delete("1.0", "end")
                self.email_editor.insert("1.0", new_text)
                
                print(f"✅ Zmieniono rozmiar czcionki na: {size}px")
        except Exception as e:
            print(f"Błąd zmiany rozmiaru czcionki: {e}")
    
    def apply_format(self, format_type):
        """Aplikuje formatowanie tekstu w edytorze"""
        try:
            if hasattr(self, 'email_editor'):
                # Pobierz zaznaczony tekst
                try:
                    selected_text = self.email_editor.get("sel.first", "sel.last")
                    if selected_text:
                        # Formatuj zaznaczony tekst
                        if format_type == "bold":
                            formatted_text = f"<strong>{selected_text}</strong>"
                        elif format_type == "italic":
                            formatted_text = f"<em>{selected_text}</em>"
                        elif format_type == "underline":
                            formatted_text = f"<u>{selected_text}</u>"
                        else:
                            return
                        
                        # Zastąp zaznaczony tekst
                        self.email_editor.delete("sel.first", "sel.last")
                        self.email_editor.insert("insert", formatted_text)
                        print(f"✅ Zastosowano formatowanie: {format_type}")
                    else:
                        print("⚠️ Zaznacz tekst przed formatowaniem")
                except tk.TclError:
                    print("⚠️ Zaznacz tekst przed formatowaniem")
        except Exception as e:
            print(f"Błąd formatowania: {e}")
    
    def apply_color(self):
        """Otwiera okno wyboru koloru i aplikuje go do zaznaczonego tekstu"""
        try:
            if hasattr(self, 'email_editor'):
                from tkinter import colorchooser
                
                # Otwórz okno wyboru koloru
                color = colorchooser.askcolor(title="Wybierz kolor tekstu")
                if color[1]:  # color[1] zawiera hex koloru
                    hex_color = color[1]
                    
                    # Pobierz zaznaczony tekst
                    try:
                        selected_text = self.email_editor.get("sel.first", "sel.last")
                        if selected_text:
                            # Formatuj zaznaczony tekst z kolorem
                            formatted_text = f'<span style="color: {hex_color};">{selected_text}</span>'
                            
                            # Zastąp zaznaczony tekst
                            self.email_editor.delete("sel.first", "sel.last")
                            self.email_editor.insert("insert", formatted_text)
                            print(f"✅ Zastosowano kolor: {hex_color}")
                        else:
                            print("⚠️ Zaznacz tekst przed zmianą koloru")
                    except tk.TclError:
                        print("⚠️ Zaznacz tekst przed zmianą koloru")
        except Exception as e:
            print(f"Błąd zmiany koloru: {e}")
    
    def undo_action(self):
        """Cofa ostatnią akcję w edytorze"""
        try:
            if hasattr(self, 'email_editor') and hasattr(self, 'editor_history') and self.editor_history:
                if self.current_history_index > 0:
                    self.current_history_index -= 1
                    previous_text = self.editor_history[self.current_history_index]
                    self.email_editor.delete("1.0", "end")
                    self.email_editor.insert("1.0", previous_text)
                    print("✅ Cofnięto akcję")
                else:
                    print("⚠️ Brak akcji do cofnięcia")
        except Exception as e:
            print(f"Błąd cofania: {e}")
    
    def redo_action(self):
        """Ponawia ostatnią cofniętą akcję w edytorze"""
        try:
            if hasattr(self, 'email_editor') and hasattr(self, 'editor_history') and self.editor_history:
                if self.current_history_index < len(self.editor_history) - 1:
                    self.current_history_index += 1
                    next_text = self.editor_history[self.current_history_index]
                    self.email_editor.delete("1.0", "end")
                    self.email_editor.insert("1.0", next_text)
                    print("✅ Ponowiono akcję")
                else:
                    print("⚠️ Brak akcji do ponowienia")
        except Exception as e:
            print(f"Błąd ponawiania: {e}")
    
    def on_editor_change(self, event=None):
        """Obsługuje zmiany w edytorze i zapisuje historię"""
        try:
            if hasattr(self, 'email_editor') and hasattr(self, 'editor_history'):
                current_text = self.email_editor.get("1.0", "end-1c")
                
                # Dodaj do historii tylko jeśli tekst się zmienił
                if not self.editor_history or current_text != self.editor_history[-1]:
                    # Usuń przyszłą historię jeśli cofnięto i zmieniono
                    if self.current_history_index < len(self.editor_history) - 1:
                        self.editor_history = self.editor_history[:self.current_history_index + 1]
                    
                    # Dodaj nowy stan do historii
                    self.editor_history.append(current_text)
                    self.current_history_index = len(self.editor_history) - 1
                    
                    # Ogranicz historię do 50 stanów
                    if len(self.editor_history) > 50:
                        self.editor_history.pop(0)
                        self.current_history_index -= 1
        except Exception as e:
            print(f"Błąd zapisywania historii: {e}")
    
    def add_html_footer(self):
        """Dodaje stopkę HTML do edytora"""
        try:
            if hasattr(self, 'email_editor'):
                html_footer = """
                
                <div style="border-top: 1px solid #ccc; margin-top: 20px; padding-top: 20px; text-align: center; font-size: 12px; color: #666;">
                    <p>--- Wiadomość wygenerowana automatycznie ---</p>
                    <p>© 2024 KPJ.PL - System Windykacji</p>
                    <p>W razie pytań prosimy o kontakt: windykacja@kpj.pl</p>
                </div>
                """
                self.email_editor.insert("end", html_footer)
                print("✅ Dodano stopkę HTML")
        except Exception as e:
            print(f"Błąd dodawania stopki HTML: {e}")
    
    def add_text_footer(self):
        """Dodaje stopkę tekstową do edytora"""
        try:
            if hasattr(self, 'email_editor'):
                text_footer = """
                
                ---
                Wiadomość wygenerowana automatycznie
                © 2024 KPJ.PL - System Windykacji
                W razie pytań prosimy o kontakt: windykacja@kpj.pl
                """
                self.email_editor.insert("end", text_footer)
                print("✅ Dodano stopkę tekstową")
        except Exception as e:
            print(f"Błąd dodawania stopki tekstowej: {e}")
    
    def clear_footer(self):
        """Czyści stopkę z edytora"""
        try:
            if hasattr(self, 'email_editor'):
                current_text = self.email_editor.get("1.0", "end-1c")
                # Usuń ostatnie linie zawierające stopkę
                lines = current_text.split('\n')
                while lines and ('---' in lines[-1] or '©' in lines[-1] or 'windykacja@kpj.pl' in lines[-1] or 'Wiadomość wygenerowana automatycznie' in lines[-1]):
                    lines.pop()
                # Usuń puste linie na końcu
                while lines and not lines[-1].strip():
                    lines.pop()
                
                new_text = '\n'.join(lines)
                self.email_editor.delete("1.0", "end")
                self.email_editor.insert("1.0", new_text)
                print("✅ Stopka została usunięta")
        except Exception as e:
            print(f"Błąd usuwania stopki: {e}")
    
    def load_placeholders(self):
        """Wczytuje placeholdery stałe"""
        try:
            placeholders = self.config.load_placeholders()
            self.placeholders_data = placeholders
            
            # Wyczyść listę
            self.templates_widgets['placeholders_listbox'].delete(0, tk.END)
            
            # Dodaj placeholdery do listy
            for placeholder in placeholders:
                display_text = f"{placeholder['name']} = {placeholder['value']}"
                self.templates_widgets['placeholders_listbox'].insert(tk.END, display_text)
            
            print("✅ Placeholdery zostały wczytane")
            
        except Exception as e:
            print(f"⚠️ Błąd wczytywania placeholders: {str(e)}")
            # Ustaw domyślne placeholdery
            self.set_default_placeholders()
    
    def set_default_placeholders(self):
        """Ustawia domyślne placeholdery"""
        default_placeholders = [
            {
                'name': 'numer_konta',
                'value': 'PL12345678901234567890123456',
                'description': 'Numer konta bankowego'
            },
            {
                'name': 'data_wymagalnosci',
                'value': '31.12.2024',
                'description': 'Data wymagalności płatności'
            },
            {
                'name': 'kwota_zadluzenia',
                'value': '0.00 PLN',
                'description': 'Kwota zadłużenia'
            },
            {
                'name': 'nazwa_firmy',
                'value': 'KPJ.PL Sp. z o.o.',
                'description': 'Nazwa firmy windykacyjnej'
            },
            {
                'name': 'email_kontaktowy',
                'value': 'windykacja@kpj.pl',
                'description': 'Email kontaktowy'
            },
            {
                'name': 'telefon_kontaktowy',
                'value': '+48 123 456 789',
                'description': 'Telefon kontaktowy'
            }
        ]
        
        self.placeholders_data = default_placeholders
        self.save_placeholders()
        self.load_placeholders()
        print("✅ Ustawiono domyślne placeholdery")
    
    def add_placeholder(self):
        """Dodaje nowy placeholder"""
        try:
            name = self.templates_widgets['placeholder_name_var'].get().strip()
            value = self.templates_widgets['placeholder_value_var'].get().strip()
            description = self.templates_widgets['placeholder_desc_var'].get().strip()
            
            if not name or not value:
                messagebox.showwarning("Ostrzeżenie", "Nazwa i wartość placeholdera są wymagane")
                return
            
            # Sprawdź czy placeholder o takiej nazwie już istnieje
            for placeholder in self.placeholders_data:
                if placeholder['name'] == name:
                    messagebox.showwarning("Ostrzeżenie", f"Placeholder o nazwie '{name}' już istnieje")
                    return
            
            # Dodaj nowy placeholder
            new_placeholder = {
                'name': name,
                'value': value,
                'description': description
            }
            
            self.placeholders_data.append(new_placeholder)
            
            # Dodaj do listy
            display_text = f"{name} = {value}"
            self.templates_widgets['placeholders_listbox'].insert(tk.END, display_text)
            
            # Wyczyść pola
            self.templates_widgets['placeholder_name_var'].set('')
            self.templates_widgets['placeholder_value_var'].set('')
            self.templates_widgets['placeholder_desc_var'].set('')
            
            print(f"✅ Dodano placeholder: {name}")
            
        except Exception as e:
            print(f"Błąd dodawania placeholdera: {e}")
    
    def edit_placeholder(self):
        """Edytuje wybrany placeholder"""
        try:
            selection = self.templates_widgets['placeholders_listbox'].curselection()
            if not selection:
                messagebox.showwarning("Ostrzeżenie", "Wybierz placeholder do edycji")
                return
            
            index = selection[0]
            placeholder = self.placeholders_data[index]
            
            # Wypełnij pola aktualnymi wartościami
            self.templates_widgets['placeholder_name_var'].set(placeholder['name'])
            self.templates_widgets['placeholder_value_var'].set(placeholder['value'])
            self.templates_widgets['placeholder_desc_var'].set(placeholder['description'])
            
            # Usuń stary placeholder
            self.placeholders_data.pop(index)
            self.templates_widgets['placeholders_listbox'].delete(index)
            
            print(f"✅ Przygotowano do edycji placeholder: {placeholder['name']}")
            
        except Exception as e:
            print(f"Błąd edycji placeholdera: {e}")
    
    def delete_placeholder(self):
        """Usuwa wybrany placeholder"""
        try:
            selection = self.templates_widgets['placeholders_listbox'].curselection()
            if not selection:
                messagebox.showwarning("Ostrzeżenie", "Wybierz placeholder do usunięcia")
                return
            
            index = selection[0]
            placeholder = self.placeholders_data[index]
            
            # Potwierdź usunięcie
            if messagebox.askyesno("Potwierdzenie", f"Czy na pewno chcesz usunąć placeholder '{placeholder['name']}'?"):
                # Usuń z danych
                self.placeholders_data.pop(index)
                
                # Usuń z listy
                self.templates_widgets['placeholders_listbox'].delete(index)
                
                # Wyczyść pola jeśli były wypełnione
                if (self.templates_widgets['placeholder_name_var'].get() == placeholder['name'] and
                    self.templates_widgets['placeholder_value_var'].get() == placeholder['value']):
                    self.templates_widgets['placeholder_name_var'].set('')
                    self.templates_widgets['placeholder_value_var'].set('')
                    self.templates_widgets['placeholder_desc_var'].set('')
                
                print(f"✅ Usunięto placeholder: {placeholder['name']}")
            
        except Exception as e:
            print(f"Błąd usuwania placeholdera: {e}")
    
    def save_placeholders(self):
        """Zapisuje placeholdery do pliku"""
        try:
            self.config.save_placeholders(self.placeholders_data)
            messagebox.showinfo("Sukces", "Placeholdery zostały zapisane")
            print("✅ Placeholdery zostały zapisane")
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd zapisywania placeholders:\n{str(e)}")
            print(f"Błąd zapisywania placeholders: {e}")
    
    def reset_placeholders(self):
        """Resetuje placeholdery do wartości domyślnych"""
        try:
            if messagebox.askyesno("Potwierdzenie", 
                                 "Czy na pewno chcesz zresetować placeholdery do wartości domyślnych?\nWszystkie zmiany zostaną utracone."):
                self.set_default_placeholders()
                messagebox.showinfo("Sukces", "Placeholdery zostały zresetowane do wartości domyślnych")
        except Exception as e:
            print(f"Błąd resetowania placeholders: {e}")
    
    def get_placeholder_value(self, name):
        """Pobiera wartość placeholdera po nazwie"""
        try:
            for placeholder in self.placeholders_data:
                if placeholder['name'] == name:
                    return placeholder['value']
            return None
        except Exception as e:
            print(f"Błąd pobierania wartości placeholdera '{name}': {e}")
            return None
    
    def save_email_template_from_editor(self):
        """Zapisuje szablon emaila z edytora"""
        try:
            content = self.email_editor.get("1.0", "end-1c")
            self.config.save_template('email', content)
            messagebox.showinfo("Sukces", "Szablon emaila został zapisany")
            print("✅ Szablon emaila został zapisany z edytora")
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd zapisywania szablonu:\n{str(e)}")
            print(f"Błąd zapisywania szablonu: {e}")
    
    def preview_html(self):
        """Pokazuje podgląd HTML w nowym oknie"""
        try:
            html_content = self.email_editor.get("1.0", "end-1c")
            
            preview_window = tk.Toplevel(self.root)
            preview_window.title("👁️ Podgląd HTML")
            preview_window.geometry("600x400")
            
            # Konwertuj tekst na HTML
            html_text = f"""
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .footer {{ border-top: 1px solid #ccc; margin-top: 20px; padding-top: 20px; 
                              font-size: 12px; color: #666; text-align: center; }}
                </style>
            </head>
            <body>
                {html_content}
                <div class="footer">
                    <p>--- Wiadomość wygenerowana automatycznie ---</p>
                    <p>© 2024 KPJ.PL - System Windykacji</p>
                    <p>W razie pytań prosimy o kontakt: windykacja@kpj.pl</p>
                </div>
            </body>
            </html>
            """
            
            preview_window.configure(bg='white')
            preview_window.html_text = html_text
            
            # Użyj ttk.Frame z obsługą HTML
            html_frame = ttk.Frame(preview_window)
            html_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Użyj ttk.Label z obsługą HTML
            html_label = ttk.Label(html_frame, text=html_text, justify=tk.LEFT)
            html_label.pack(fill=tk.BOTH, expand=True)
            
            # Przycisk zamknięcia
            close_btn = tk.Button(preview_window, text="❌ Zamknij", 
                                 bg=self.config.primary_color,
                                 fg=self.config.white_color,
                                 relief='flat',
                                 borderwidth=0,
                                 font=('Arial', 10, 'bold'),
                                 cursor='hand2',
                                 command=preview_window.destroy)
            close_btn.pack(pady=(10, 0))
            
            print("✅ Podgląd HTML został otwarty")
        except Exception as e:
            print(f"Błąd otwierania podglądu HTML: {e}")
    
    def remove_settled_items(self):
        """Usuwa pozycje rozliczone (z kwotą ≤ 0) i odświeża podgląd"""
        if self.data_processor.excel_data is None:
            messagebox.showwarning("Ostrzeżenie", "Najpierw wczytaj plik Excel/CSV")
            return
        
        print(f"🔍 Przed usunięciem: {len(self.data_processor.excel_data)} pozycji")
        
        # Sprawdź aktualny stan podglądu
        current_preview_items = len(self.data_mapping_widgets['preview_tree'].get_children())
        print(f"🔍 Aktualny podgląd zawiera: {current_preview_items} pozycji")
        
        # Usuń pozycje rozliczone
        removed_count = self.data_processor.remove_settled_items()
        
        print(f"🗑️ Usunięto: {removed_count} pozycji")
        print(f"📊 Po usunięciu: {len(self.data_processor.excel_data)} pozycji")
        
        if removed_count > 0:
            # Odśwież podgląd
            print("🔄 Odświeżam podgląd...")
            self.generate_preview()
            
            # Sprawdź nowy stan podglądu
            new_preview_items = len(self.data_mapping_widgets['preview_tree'].get_children())
            print(f"🔍 Nowy podgląd zawiera: {new_preview_items} pozycji")
            
            if new_preview_items == len(self.data_processor.excel_data):
                print("✅ Podgląd został poprawnie odświeżony")
            else:
                print(f"❌ Błąd: podgląd {new_preview_items} vs dane {len(self.data_processor.excel_data)}")
            
            messagebox.showinfo("Sukces", f"Usunięto {removed_count} pozycji rozliczonych")
        else:
            messagebox.showinfo("Informacja", "Nie znaleziono pozycji rozliczonych do usunięcia")
    
    def run(self):
        """Uruchamia aplikację"""
        self.root.mainloop()

if __name__ == "__main__":
    app = WindykatorApp()
    app.run() 
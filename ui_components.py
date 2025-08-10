"""
Moduł z komponentami UI dla aplikacji Windykator
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import logging

class UIComponents:
    """Klasa z komponentami UI"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def create_header(self, parent):
        """Tworzy nagłówek aplikacji"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Tytuł aplikacji
        title_label = ttk.Label(header_frame, text="📧 Windykator", 
                               style='Header.TLabel', font=('Arial', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Status aplikacji
        status_label = ttk.Label(header_frame, text="ℹ️ Gotowy do pracy", 
                                style='Info.TLabel')
        status_label.pack(side=tk.RIGHT)
        
        return header_frame, status_label
    
    def create_notebook(self, parent):
        """Tworzy notebook z zakładkami"""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        return notebook
    
    def create_data_mapping_tab(self, notebook):
        """Tworzy zakładkę mapowania danych"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="📊 Dane i Mapowanie")
        
        # Kontener główny
        main_frame = ttk.Frame(tab, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sekcja wczytywania pliku
        file_frame = ttk.LabelFrame(main_frame, text="📁 Wczytaj plik Excel/CSV", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        load_btn = tk.Button(file_frame, text="📂 Wybierz plik", 
                             bg=self.config.primary_color,
                             fg=self.config.white_color,
                             relief='flat',
                             borderwidth=0,
                             font=('Arial', 10, 'bold'),
                             cursor='hand2')
        load_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        file_info = ttk.Label(file_frame, text="ℹ️ Nie wybrano pliku", style='Info.TLabel')
        file_info.pack(side=tk.LEFT)
        
        # Sekcja mapowania kolumn
        mapping_frame = ttk.LabelFrame(main_frame, text="🔗 Mapowanie kolumn", padding="10")
        mapping_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Grid dla pól mapowania
        mapping_fields = {}
        fields = self.config.get_mapping_fields()
        
        for i, (field, label) in enumerate(fields):
            row = i // 2
            col = (i % 2) * 2
            
            # Label
            label_widget = ttk.Label(mapping_frame, text=f"{label}:")
            label_widget.grid(row=row, column=col, sticky='w', padx=(0, 5), pady=2)
            
            # Combobox
            combo = ttk.Combobox(mapping_frame, width=25, state='readonly')
            combo.grid(row=row, column=col+1, sticky='ew', padx=(0, 10), pady=2)
            
            mapping_fields[field] = combo
        
        # Przyciski mapowania
        mapping_buttons_frame = ttk.Frame(mapping_frame)
        mapping_buttons_frame.grid(row=len(fields)//2 + 1, column=0, columnspan=4, pady=(10, 0))
        
        save_mapping_btn = tk.Button(mapping_buttons_frame, text="💾 Zapisz mapowanie", 
                                     bg=self.config.primary_color,
                                     fg=self.config.white_color,
                                     relief='flat',
                                     borderwidth=0,
                                     font=('Arial', 10, 'bold'),
                                     cursor='hand2')
        save_mapping_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        load_mapping_btn = tk.Button(mapping_buttons_frame, text="📂 Wczytaj mapowanie", 
                                     bg=self.config.primary_color,
                                     fg=self.config.white_color,
                                     relief='flat',
                                     borderwidth=0,
                                     font=('Arial', 10, 'bold'),
                                     cursor='hand2')
        load_mapping_btn.pack(side=tk.LEFT)
        
        # Sekcja podglądu
        preview_frame = ttk.LabelFrame(main_frame, text="👁️ Podgląd danych", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Przyciski podglądu
        preview_buttons_frame = ttk.Frame(preview_frame)
        preview_buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        generate_btn = tk.Button(preview_buttons_frame, text="🔄 Generuj podgląd", 
                                 bg=self.config.primary_color,
                                 fg=self.config.white_color,
                                 relief='flat',
                                 borderwidth=0,
                                 font=('Arial', 10, 'bold'),
                                 cursor='hand2')
        generate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        add_item_btn = tk.Button(preview_buttons_frame, text="➕ Dodaj pozycję", 
                                 bg=self.config.primary_color,
                                 fg=self.config.white_color,
                                 relief='flat',
                                 borderwidth=0,
                                 font=('Arial', 10, 'bold'),
                                 cursor='hand2')
        add_item_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        remove_item_btn = tk.Button(preview_buttons_frame, text="➖ Usuń pozycję", 
                                    bg=self.config.primary_color,
                                    fg=self.config.white_color,
                                    relief='flat',
                                    borderwidth=0,
                                    font=('Arial', 10, 'bold'),
                                    cursor='hand2')
        remove_item_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        edit_item_btn = tk.Button(preview_buttons_frame, text="✏️ Edytuj pozycję", 
                                  bg=self.config.primary_color,
                                  fg=self.config.white_color,
                                  relief='flat',
                                  borderwidth=0,
                                  font=('Arial', 10, 'bold'),
                                  cursor='hand2')
        edit_item_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        remove_settled_btn = tk.Button(preview_buttons_frame, text="🗑️ Usuń rozliczone", 
                                       bg=self.config.warning_color,
                                       fg=self.config.white_color,
                                       relief='flat',
                                       borderwidth=0,
                                       font=('Arial', 10, 'bold'),
                                       cursor='hand2')
        remove_settled_btn.pack(side=tk.LEFT)
        
        # Treeview z podglądem
        preview_tree_frame = ttk.Frame(preview_frame)
        preview_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('Kontrahent', 'NIP', 'Nr Faktury', 'Email', 'Telefon', 'Kwota', 'Dni Po Terminie')
        preview_tree = ttk.Treeview(preview_tree_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            preview_tree.heading(col, text=col)
            preview_tree.column(col, width=120)
        
        preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar dla treeview
        preview_scrollbar = ttk.Scrollbar(preview_tree_frame, orient=tk.VERTICAL, command=preview_tree.yview)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        preview_tree.configure(yscrollcommand=preview_scrollbar.set)
        
        # Informacja o liczbie pozycji
        preview_info = ttk.Label(preview_frame, text="ℹ️ W podglądzie: 0 pozycji", style='Info.TLabel')
        preview_info.pack(pady=(5, 0))
        
        return {
            'load_btn': load_btn,
            'save_mapping_btn': save_mapping_btn,
            'load_mapping_btn': load_mapping_btn,
            'generate_btn': generate_btn,
            'add_item_btn': add_item_btn,
            'remove_item_btn': remove_item_btn,
            'edit_item_btn': edit_item_btn,
            'remove_settled_btn': remove_settled_btn,
            'mapping_fields': mapping_fields,
            'preview_tree': preview_tree,
            'preview_info': preview_info,
            'file_info': file_info
        }
    
    def create_templates_tab(self, notebook):
        """Tworzy zakładkę szablonów"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="📝 Szablony")
        
        # Kontener główny
        main_frame = ttk.Frame(tab, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook dla szablonów
        templates_notebook = ttk.Notebook(main_frame)
        templates_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Zakładka Email z edytorem WYSIWYG
        email_tab = ttk.Frame(templates_notebook)
        templates_notebook.add(email_tab, text="📧 Edytor Email WYSIWYG")
        
        email_frame = ttk.Frame(email_tab, padding="10")
        email_frame.pack(fill=tk.BOTH, expand=True)
        
        # Pasek narzędzi edytora WYSIWYG
        email_toolbar_frame = ttk.Frame(email_frame)
        email_toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Przyciski stylowania
        style_buttons = []
        for text, value in [
            ("🔤 Arial", "Arial"),
            ("🔤 Times", "Times New Roman"),
            ("🔤 Courier", "Courier New"),
            ("📏 12", "12"),
            ("📏 14", "14"),
            ("📏 16", "16"),
            ("📏 18", "18"),
            ("📏 20", "20"),
        ]:
            btn = ttk.Button(email_toolbar_frame, text=text, width=8)
            btn.pack(side=tk.LEFT, padx=(0, 5))
            style_buttons.append((btn, value))
        
        # Separator
        ttk.Separator(email_toolbar_frame, orient='vertical').pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Przyciski formatowania
        format_buttons = []
        for text, tag, tooltip in [
            ("B", "bold", "Pogrubienie"),
            ("I", "italic", "Kursywa"),
            ("U", "underline", "Podkreślenie"),
            ("🎨", "color", "Kolor"),
            ("⬅️", "undo", "Cofnij"),
            ("➡️", "redo", "Ponów"),
        ]:
            btn = ttk.Button(email_toolbar_frame, text=text, width=4)
            btn.pack(side=tk.LEFT, padx=(0, 5))
            format_buttons.append((btn, tag, tooltip))
        
        # Separator
        ttk.Separator(email_toolbar_frame, orient='vertical').pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Przyciski stopki
        footer_buttons = []
        for text, action, tooltip in [
            ("📄 HTML", "html_footer", "Dodaj stopkę HTML"),
            ("📄 Tekst", "text_footer", "Dodaj stopkę tekst"),
            ("🗑️", "clear_footer", "Wyczyść stopkę"),
        ]:
            btn = ttk.Button(email_toolbar_frame, text=text, width=6)
            btn.pack(side=tk.LEFT, padx=(0, 5))
            footer_buttons.append((btn, action, tooltip))
        
        # Edytor Email WYSIWYG
        email_editor = tk.Text(email_frame, wrap=tk.WORD, height=20, 
                              font=('Arial', 12), bg='white', fg='black')
        email_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Scrollbar dla edytora email
        email_scrollbar = ttk.Scrollbar(email_frame, orient=tk.VERTICAL, command=email_editor.yview)
        email_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        email_editor.configure(yscrollcommand=email_scrollbar.set)
        
        # Przyciski akcji Email
        email_buttons_frame = ttk.Frame(email_frame)
        email_buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        save_email_btn = ttk.Button(email_buttons_frame, text="💾 Zapisz szablon", 
                                   style='Primary.TButton')
        save_email_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        load_email_btn = ttk.Button(email_buttons_frame, text="📂 Wczytaj szablon")
        load_email_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        preview_email_btn = ttk.Button(email_buttons_frame, text="👁️ Edytor WYSIWYG")
        preview_email_btn.pack(side=tk.LEFT)
        
        # Zakładka SMS
        sms_tab = ttk.Frame(templates_notebook)
        templates_notebook.add(sms_tab, text="📱 Szablon SMS")
        
        sms_frame = ttk.Frame(sms_tab, padding="10")
        sms_frame.pack(fill=tk.BOTH, expand=True)
        
        # Edytor SMS
        sms_editor = scrolledtext.ScrolledText(sms_frame, wrap=tk.WORD, height=15)
        sms_editor.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Przyciski SMS
        sms_buttons_frame = ttk.Frame(sms_frame)
        sms_buttons_frame.pack(fill=tk.X)
        
        save_sms_btn = ttk.Button(sms_buttons_frame, text="💾 Zapisz szablon", 
                                 style='Primary.TButton')
        save_sms_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        load_sms_btn = ttk.Button(sms_buttons_frame, text="📂 Wczytaj szablon")
        load_sms_btn.pack(side=tk.LEFT)
        
        # Zakładka Placeholdery stałe
        placeholders_tab = ttk.Frame(templates_notebook)
        templates_notebook.add(placeholders_tab, text="🔧 Placeholdery stałe")
        
        placeholders_frame = ttk.Frame(placeholders_tab, padding="10")
        placeholders_frame.pack(fill=tk.BOTH, expand=True)
        
        # Opis placeholders
        description_label = ttk.Label(placeholders_frame, 
                                    text="Edytuj stałe wartości używane w szablonach maili i SMS",
                                    font=('Arial', 10, 'bold'))
        description_label.pack(pady=(0, 15))
        
        # Kontener dla placeholders
        placeholders_container = ttk.Frame(placeholders_frame)
        placeholders_container.pack(fill=tk.BOTH, expand=True)
        
        # Lista placeholders z możliwością edycji
        placeholders_list_frame = ttk.Frame(placeholders_container)
        placeholders_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Nagłówek listy
        list_header = ttk.Label(placeholders_list_frame, text="Lista placeholders:", font=('Arial', 9, 'bold'))
        list_header.pack(anchor=tk.W, pady=(0, 5))
        
        # Lista placeholders
        placeholders_listbox = tk.Listbox(placeholders_list_frame, height=12, selectmode=tk.SINGLE)
        placeholders_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar dla listy
        list_scrollbar = ttk.Scrollbar(placeholders_list_frame, orient=tk.VERTICAL, command=placeholders_listbox.yview)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        placeholders_listbox.configure(yscrollcommand=list_scrollbar.set)
        
        # Panel edycji placeholdera
        edit_frame = ttk.Frame(placeholders_container)
        edit_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Nagłówek edycji
        edit_header = ttk.Label(edit_frame, text="Edycja placeholdera:", font=('Arial', 9, 'bold'))
        edit_header.pack(anchor=tk.W, pady=(0, 10))
        
        # Nazwa placeholdera
        name_frame = ttk.Frame(edit_frame)
        name_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(name_frame, text="Nazwa:").pack(anchor=tk.W)
        placeholder_name_var = tk.StringVar()
        placeholder_name_entry = ttk.Entry(name_frame, textvariable=placeholder_name_var, width=25)
        placeholder_name_entry.pack(fill=tk.X, pady=(2, 0))
        
        # Wartość placeholdera
        value_frame = ttk.Frame(edit_frame)
        value_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(value_frame, text="Wartość:").pack(anchor=tk.W)
        placeholder_value_var = tk.StringVar()
        placeholder_value_entry = ttk.Entry(value_frame, textvariable=placeholder_value_var, width=25)
        placeholder_value_entry.pack(fill=tk.X, pady=(2, 0))
        
        # Opis placeholdera
        desc_frame = ttk.Frame(edit_frame)
        desc_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(desc_frame, text="Opis:").pack(anchor=tk.W)
        placeholder_desc_var = tk.StringVar()
        placeholder_desc_entry = ttk.Entry(desc_frame, textvariable=placeholder_desc_var, width=25)
        placeholder_desc_entry.pack(fill=tk.X, pady=(2, 0))
        
        # Przyciski akcji
        actions_frame = ttk.Frame(edit_frame)
        actions_frame.pack(fill=tk.X)
        
        add_placeholder_btn = ttk.Button(actions_frame, text="➕ Dodaj", width=10)
        add_placeholder_btn.pack(fill=tk.X, pady=(0, 5))
        
        edit_placeholder_btn = ttk.Button(actions_frame, text="✏️ Edytuj", width=10)
        edit_placeholder_btn.pack(fill=tk.X, pady=(0, 5))
        
        delete_placeholder_btn = ttk.Button(actions_frame, text="🗑️ Usuń", width=10)
        delete_placeholder_btn.pack(fill=tk.X, pady=(0, 5))
        
        # Przyciski zarządzania
        manage_frame = ttk.Frame(placeholders_frame)
        manage_frame.pack(fill=tk.X, pady=(15, 0))
        
        save_placeholders_btn = ttk.Button(manage_frame, text="💾 Zapisz placeholdery", 
                                         style='Primary.TButton')
        save_placeholders_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        load_placeholders_btn = ttk.Button(manage_frame, text="📂 Wczytaj placeholdery")
        load_placeholders_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        reset_placeholders_btn = ttk.Button(manage_frame, text="🔄 Resetuj domyślne")
        reset_placeholders_btn.pack(side=tk.LEFT)
        
        return {
            'email_editor': email_editor,
            'sms_editor': sms_editor,
            'save_email_btn': save_email_btn,
            'load_email_btn': load_email_btn,
            'preview_email_btn': preview_email_btn,
            'save_sms_btn': save_sms_btn,
            'load_sms_btn': load_sms_btn,
            'style_buttons': style_buttons,
            'format_buttons': format_buttons,
            'footer_buttons': footer_buttons,
            'placeholders_listbox': placeholders_listbox,
            'placeholder_name_var': placeholder_name_var,
            'placeholder_value_var': placeholder_value_var,
            'placeholder_desc_var': placeholder_desc_var,
            'add_placeholder_btn': add_placeholder_btn,
            'edit_placeholder_btn': edit_placeholder_btn,
            'delete_placeholder_btn': delete_placeholder_btn,
            'save_placeholders_btn': save_placeholders_btn,
            'load_placeholders_btn': load_placeholders_btn,
            'reset_placeholders_btn': reset_placeholders_btn
        }
    
    def create_sending_tab(self, notebook):
        """Tworzy zakładkę wysyłki"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="📤 Wysyłka")
        
        # Kontener główny
        main_frame = ttk.Frame(tab, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Kontrolki wysyłki
        control_frame = ttk.Frame(tab)
        control_frame.pack(fill=tk.X, pady=(10, 20))
        
        # Checkboxy
        email_var = tk.BooleanVar(value=True)
        sms_var = tk.BooleanVar(value=True)
        
        email_check = ttk.Checkbutton(control_frame, text="📧 Email", 
                                      variable=email_var)
        email_check.pack(side=tk.LEFT)
        
        sms_check = ttk.Checkbutton(control_frame, text="📱 SMS", 
                                    variable=sms_var)
        sms_check.pack(side=tk.LEFT)
        
        # Przyciski kontroli
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.pack(pady=(10, 0))
        
        send_btn = tk.Button(buttons_frame, text="🚀 Rozpocznij wysyłkę", 
                             bg=self.config.primary_color,
                             fg=self.config.white_color,
                             relief='flat',
                             borderwidth=0,
                             font=('Arial', 10, 'bold'),
                             cursor='hand2')
        send_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        export_btn = tk.Button(buttons_frame, text="📊 Eksportuj status CSV", 
                               bg=self.config.primary_color,
                               fg=self.config.white_color,
                               relief='flat',
                               borderwidth=0,
                               font=('Arial', 10, 'bold'),
                               cursor='hand2')
        export_btn.pack(side=tk.LEFT)
        
        # Sekcja statusu wysyłki
        status_frame = ttk.LabelFrame(main_frame, text="📊 Status wysyłki", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview ze statusem
        status_tree_frame = ttk.Frame(status_frame)
        status_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        status_columns = ('Kontrahent', 'NIP', 'Nr Faktury', 'Email', 'Telefon', 
                         'Kwota', 'Dni Po Terminie', 'Email Status', 'SMS Status')
        status_tree = ttk.Treeview(status_tree_frame, columns=status_columns, 
                                  show='headings', height=8)
        
        for col in status_columns:
            status_tree.heading(col, text=col)
            status_tree.column(col, width=100)
        
        status_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar dla status treeview
        status_scrollbar = ttk.Scrollbar(status_tree_frame, orient=tk.VERTICAL, 
                                        command=status_tree.yview)
        status_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        status_tree.configure(yscrollcommand=status_scrollbar.set)
        
        return {
            'email_var': email_var,
            'sms_var': sms_var,
            'send_btn': send_btn,
            'export_btn': export_btn,
            'status_tree': status_tree
        }
    
    def create_config_tab(self, notebook):
        """Tworzy zakładkę konfiguracji"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="⚙️ Konfiguracja")
        
        # Kontener główny
        main_frame = ttk.Frame(tab, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook dla konfiguracji
        config_notebook = ttk.Notebook(main_frame)
        config_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Zakładka Email
        email_config_tab = ttk.Frame(config_notebook)
        config_notebook.add(email_config_tab, text="📧 Email (Microsoft 365)")
        
        email_config_frame = ttk.Frame(email_config_tab, padding="10")
        email_config_frame.pack(fill=tk.BOTH, expand=True)
        
        # Pola konfiguracji Email
        email_fields = [
            ('client_id', 'Client ID:'),
            ('client_secret', 'Client Secret:'),
            ('test_email', 'Email testowy:')
        ]
        
        email_vars = {}
        for field, label in email_fields:
            frame = ttk.Frame(email_config_frame)
            frame.pack(fill=tk.X, pady=2)
            
            label_widget = ttk.Label(frame, text=label, width=15)
            label_widget.pack(side=tk.LEFT)
            
            var = tk.StringVar()
            entry = ttk.Entry(frame, textvariable=var, width=50)
            entry.pack(side=tk.LEFT, padx=(10, 0))
            
            email_vars[field] = var
        
        # Przyciski konfiguracji
        config_buttons_frame = ttk.Frame(tab)
        config_buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        save_email_config_btn = tk.Button(config_buttons_frame, text="💾 Zapisz konfigurację email", 
                                          bg=self.config.primary_color,
                                          fg=self.config.white_color,
                                          relief='flat',
                                          borderwidth=0,
                                          font=('Arial', 10, 'bold'),
                                          cursor='hand2')
        save_email_config_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        test_email_btn = tk.Button(config_buttons_frame, text="🧪 Test połączenia email", 
                                   bg=self.config.primary_color,
                                   fg=self.config.white_color,
                                   relief='flat',
                                   borderwidth=0,
                                   font=('Arial', 10, 'bold'),
                                   cursor='hand2')
        test_email_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        save_sms_config_btn = tk.Button(config_buttons_frame, text="💾 Zapisz konfigurację SMS", 
                                        bg=self.config.primary_color,
                                        fg=self.config.white_color,
                                        relief='flat',
                                        borderwidth=0,
                                        font=('Arial', 10, 'bold'),
                                        cursor='hand2')
        save_sms_config_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        test_sms_btn = tk.Button(config_buttons_frame, text="🧪 Test połączenia SMS", 
                                 bg=self.config.primary_color,
                                 fg=self.config.white_color,
                                 relief='flat',
                                 borderwidth=0,
                                 font=('Arial', 10, 'bold'),
                                 cursor='hand2')
        test_sms_btn.pack(side=tk.LEFT)
        
        # Zakładka SMS
        sms_config_tab = ttk.Frame(config_notebook)
        config_notebook.add(sms_config_tab, text="📱 SMS (SMS API)")
        
        sms_config_frame = ttk.Frame(sms_config_tab, padding="10")
        sms_config_frame.pack(fill=tk.BOTH, expand=True)
        
        # Pola konfiguracji SMS
        sms_fields = [
            ('sms_url', 'Host SMS API:'),
            ('sms_token', 'Token SMS API:'),
            ('sms_sender', 'Nazwa nadawcy:'),
            ('sms_test_number', 'Numer testowy:')
        ]
        
        sms_vars = {}
        for field, label in sms_fields:
            frame = ttk.Frame(sms_config_frame)
            frame.pack(fill=tk.X, pady=2)
            
            label_widget = ttk.Label(frame, text=label, width=15)
            label_widget.pack(side=tk.LEFT)
            
            var = tk.StringVar()
            entry = ttk.Entry(frame, textvariable=var, width=50)
            entry.pack(side=tk.LEFT, padx=(10, 0))
            
            sms_vars[field] = var
        
        # Przyciski SMS
        sms_config_buttons_frame = ttk.Frame(sms_config_frame)
        sms_config_buttons_frame.pack(pady=(20, 0))
        
        save_sms_config_btn = tk.Button(sms_config_buttons_frame, text="💾 Zapisz konfigurację", 
                                       bg=self.config.primary_color,
                                       fg=self.config.white_color,
                                       relief='flat',
                                       borderwidth=0,
                                       font=('Arial', 10, 'bold'),
                                       cursor='hand2')
        save_sms_config_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        test_sms_btn = tk.Button(sms_config_buttons_frame, text="🧪 Test połączenia",
                                 bg=self.config.primary_color,
                                 fg=self.config.white_color,
                                 relief='flat',
                                 borderwidth=0,
                                 font=('Arial', 10, 'bold'),
                                 cursor='hand2')
        test_sms_btn.pack(side=tk.LEFT)
        
        return {
            'email_vars': email_vars,
            'sms_vars': sms_vars,
            'save_email_config_btn': save_email_config_btn,
            'test_email_btn': test_email_btn,
            'save_sms_config_btn': save_sms_config_btn,
            'test_sms_btn': test_sms_btn
        } 
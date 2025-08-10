import pandas as pd
import random
from datetime import datetime, timedelta

def generate_sample_data():
    """Generuje przykładowe dane windykacyjne do testowania aplikacji"""
    
    # Lista przykładowych imion i nazwisk
    first_names = ['Jan', 'Anna', 'Piotr', 'Maria', 'Andrzej', 'Katarzyna', 'Tomasz', 'Agnieszka', 
                   'Marek', 'Barbara', 'Grzegorz', 'Ewa', 'Michał', 'Elżbieta', 'Krzysztof', 'Monika']
    
    last_names = ['Kowalski', 'Nowak', 'Wiśniewski', 'Wójcik', 'Kowalczyk', 'Kamiński', 'Lewandowski',
                  'Zieliński', 'Szymański', 'Woźniak', 'Dąbrowski', 'Kozłowski', 'Jankowski', 'Mazur']
    
    # Generowanie danych
    data = []
    
    for i in range(20):  # 20 przykładowych rekordów
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        # Generowanie nazwy kontrahenta
        kontrahent = f"{first_name} {last_name} Sp. z o.o."
        
        # Generowanie NIP
        nip = f"{random.randint(100000000, 999999999)}"
        
        # Generowanie numeru faktury
        nr_faktury = f"FV/{random.randint(2023, 2024)}/{random.randint(1000, 9999)}"
        
        # Generowanie email
        email = f"{first_name.lower()}.{last_name.lower()}@example.com"
        
        # Generowanie telefonu
        phone = f"+48{random.randint(500000000, 999999999)}"
        
        # Generowanie kwoty (1000-50000 PLN) z 2 cyframi po przecinku
        amount = round(random.uniform(1000, 50000), 2)
        # Konwertuj na string z przecinkiem jako separatorem
        amount = f"{amount:.2f}".replace('.', ',')
        
        # Generowanie daty faktury (30-180 dni wstecz)
        days_overdue = random.randint(30, 180)
        data_faktury = datetime.now() - timedelta(days=days_overdue)
        
        data.append({
            'Nazwa Kontrahenta': kontrahent,
            'NIP': nip,
            'Numer Faktury': nr_faktury,
            'Email': email,
            'Telefon': phone,
            'Kwota': amount,
            'Data Faktury': data_faktury.strftime('%Y-%m-%d'),
            'Dni po terminie': days_overdue
        })
    
    # Tworzenie DataFrame
    df = pd.DataFrame(data)
    
    # Zapisywanie do pliku Excel
    filename_excel = 'przyklad_danych_windykacyjnych.xlsx'
    df.to_excel(filename_excel, index=False)
    
    # Zapisywanie do pliku CSV
    filename_csv = 'przyklad_danych_windykacyjnych.csv'
    df.to_csv(filename_csv, index=False, encoding='utf-8')
    
    print(f"Wygenerowano przykładowe dane:")
    print(f"- Excel: {filename_excel}")
    print(f"- CSV: {filename_csv}")
    print(f"Liczba rekordów: {len(data)}")
    print("\nPrzykładowe dane:")
    print(df.head())
    
    return filename_excel, filename_csv

if __name__ == "__main__":
    generate_sample_data() 
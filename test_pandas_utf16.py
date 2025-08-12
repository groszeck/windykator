#!/usr/bin/env python3
"""
Prosty test pandas z UTF-16
"""

import pandas as pd

def test_pandas_utf16():
    """Testuje czy pandas radzi sobie z UTF-16"""
    
    file_path = "Brak płatności - sms 12.08.csv"
    
    print(f"🔍 Testuję pandas z plikiem: {file_path}")
    print("=" * 50)
    
    try:
        # Próba 1: Z UTF-16-LE i tabulatorem
        print("📊 Próba 1: UTF-16-LE + tabulator")
        df = pd.read_csv(file_path, encoding='utf-16-le', sep='\t')
        print(f"   ✅ Sukces! Wiersze: {len(df)}, Kolumny: {len(df.columns)}")
        print(f"   🔗 Kolumny: {list(df.columns)}")
        return True
    except Exception as e:
        print(f"   ❌ Błąd: {e}")
    
    try:
        # Próba 2: Z UTF-16-BE i tabulatorem
        print("\n📊 Próba 2: UTF-16-BE + tabulator")
        df = pd.read_csv(file_path, encoding='utf-16-be', sep='\t')
        print(f"   ✅ Sukces! Wiersze: {len(df)}, Kolumny: {len(df.columns)}")
        print(f"   🔗 Kolumny: {list(df.columns)}")
        return True
    except Exception as e:
        print(f"   ❌ Błąd: {e}")
    
    try:
        # Próba 3: Automatyczne wykrywanie
        print("\n📊 Próba 3: Automatyczne wykrywanie")
        df = pd.read_csv(file_path, encoding=None, sep=None)
        print(f"   ✅ Sukces! Wiersze: {len(df)}, Kolumny: {len(df.columns)}")
        print(f"   🔗 Kolumny: {list(df.columns)}")
        return True
    except Exception as e:
        print(f"   ❌ Błąd: {e}")
    
    return False

if __name__ == "__main__":
    test_pandas_utf16() 
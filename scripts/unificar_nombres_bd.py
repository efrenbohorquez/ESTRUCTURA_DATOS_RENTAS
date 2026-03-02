"""
script_unificar_bd.py
Reemplaza menciones a bases de datos antiguas por BaseRentasVF_2022_2025.xlsx
en todos los notebooks y archivos Markdown.
"""
import glob
import json
import re

older_dbs = [
    r'BaseRentasVF_limpieza21feb_FINAL\.xlsx',
    r'rentas2021_2025\.xlsx',
    r'BaseRentasVF\.xlsx',
    r'BaseRentasCedidas\s*\(1\)\.xlsx',
    r'BaseRentasCedidas\.xlsx',
    r'BaseRentasVF_limpieza21feb_sin2020\.xlsx',
    r'BaseRentasVF_limpieza21feb_sin2021_ene_sep\.xlsx',
    r'rentas_panel_deflactado\.csv'
]

NEW_DB = 'BaseRentasVF_2022_2025.xlsx'

files_to_check = glob.glob('notebooks/*.ipynb') + glob.glob('docs/*.ipynb')

for f in files_to_check:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            
        modified = False
        for old in older_dbs:
            if re.search(old, content, flags=re.IGNORECASE):
                content = re.sub(old, NEW_DB, content, flags=re.IGNORECASE)
                modified = True
                
        if modified:
            with open(f, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"✅ Actualizado: {f}")
    except Exception as e:
        print(f"Error procesando {f}: {e}")

md_files = glob.glob('*.md') + glob.glob('docs/*.md')
for f in md_files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            
        modified = False
        for old in older_dbs:
            if re.search(old, content, flags=re.IGNORECASE):
                content = re.sub(old, NEW_DB, content, flags=re.IGNORECASE)
                modified = True
                
        if modified:
            with open(f, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"✅ Actualizado MD: {f}")
    except Exception as e:
        print(f"Error procesando {f}: {e}")

print("Terminado.")

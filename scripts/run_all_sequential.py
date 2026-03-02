"""
run_all_sequential.py — Ejecuta TODOS los notebooks en orden y reporta estado.
"""
import subprocess, sys, time
from pathlib import Path

ROOT = Path(r'C:\Users\efren\Music\ESTRUCTURA DATOS RENTAS')
NB_DIR = ROOT / 'notebooks'

notebooks = [
    '01_EDA_Completo.ipynb',
    '02_Estacionalidad.ipynb',
    '03_Correlacion_Macro.ipynb',
    '04_SARIMA.ipynb',
    '05_SARIMAX.ipynb',
    '06_Prophet.ipynb',
    '07_XGBoost.ipynb',
    '08_LSTM.ipynb',
    '09_Comparacion_Modelos.ipynb',
    '10_Segmentacion_Panel.ipynb',
    '11_Modelado_Panel.ipynb',
]

results = []
for nb in notebooks:
    nb_path = NB_DIR / nb
    if not nb_path.exists():
        results.append((nb, 'NOT FOUND', 0))
        continue
    
    print(f"\n{'='*60}")
    print(f"Ejecutando: {nb}")
    print('='*60)
    start = time.time()
    
    try:
        proc = subprocess.run(
            ['jupyter', 'nbconvert', '--execute', '--to', 'notebook',
             '--inplace', '--ExecutePreprocessor.timeout=300',
             str(nb_path)],
            capture_output=True, text=True, timeout=360, cwd=str(ROOT)
        )
        elapsed = time.time() - start
        
        if proc.returncode == 0 or 'Writing' in proc.stderr:
            results.append((nb, 'OK', elapsed))
            print(f"  -> OK ({elapsed:.0f}s)")
        else:
            # Extraer error significativo
            err = proc.stderr[-300:] if proc.stderr else 'unknown'
            results.append((nb, f'ERROR: {err[:100]}', elapsed))
            print(f"  -> ERROR ({elapsed:.0f}s)")
            print(f"     {err[:200]}")
    except subprocess.TimeoutExpired:
        results.append((nb, 'TIMEOUT (>360s)', time.time()-start))
        print(f"  -> TIMEOUT")
    except Exception as e:
        results.append((nb, f'EXCEPTION: {e}', 0))
        print(f"  -> EXCEPTION: {e}")

print(f"\n{'='*60}")
print("REPORTE FINAL")
print('='*60)
ok = sum(1 for _,s,_ in results if s == 'OK')
print(f"\nResultados: {ok}/{len(results)} exitosos\n")
for nb, status, t in results:
    icon = 'OK' if status == 'OK' else 'FAIL'
    print(f"  [{icon}] {nb:40s} {t:6.0f}s  {status}")

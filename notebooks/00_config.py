"""
00_config.py — Configuración Centralizada del Sistema de Análisis de Rentas Cedidas
====================================================================================
Importar en cada notebook con:
    %run 00_config.py
"""

from pathlib import Path
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

warnings.filterwarnings('ignore')

# ============================================================
# 1. RUTAS DEL PROYECTO
# ============================================================
# Resolver PROJECT_ROOT de forma robusta (funciona con %run, exec, import)
try:
    _THIS_DIR = Path(__file__).resolve().parent
except NameError:
    _THIS_DIR = Path(os.getcwd())

PROJECT_ROOT = _THIS_DIR.parent if _THIS_DIR.name == 'notebooks' else _THIS_DIR
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
OUTPUTS_FIGURES = PROJECT_ROOT / "outputs" / "figures"
OUTPUTS_FORECASTS = PROJECT_ROOT / "outputs" / "forecasts"
OUTPUTS_REPORTS = PROJECT_ROOT / "outputs" / "reports"

# Crear directorios si no existen
for _d in [DATA_RAW, DATA_PROCESSED, OUTPUTS_FIGURES, OUTPUTS_FORECASTS, OUTPUTS_REPORTS]:
    _d.mkdir(parents=True, exist_ok=True)

# Archivo fuente de datos principal
DATA_FILE = PROJECT_ROOT / "BaseRentasVF_2022_2025.xlsx"
if not DATA_FILE.exists():
    DATA_FILE = DATA_RAW / "BaseRentasVF_2022_2025.xlsx"

# ============================================================
# 2. PARÁMETROS DEL ANÁLISIS
# ============================================================
COL_FECHA = 'FechaRecaudo'
COL_VALOR = 'ValorRecaudo'
COL_RECAUDO_NETO = 'Recaudo_Neto'

# Periodo de análisis (Ene 2022 — Dic 2025, acorde al dataset)
FECHA_INICIO = '2022-01-01'
FECHA_FIN = '2025-12-31'

# Split Train/Test
# Train: Ene 2022 → Sep 2025 (45 meses)
# Test (Backtest):  Oct, Nov, Dic 2025 (3 meses — pronóstico DENTRO de 2025)
TRAIN_END = '2025-09-30'
TEST_START = '2025-10-01'

# Ventana de validación final (Cierre Nov-Dic para reporte Word)
VALIDATION_START = '2025-11-01'
VALIDATION_END = '2025-12-31'

HORIZONTE_PRONOSTICO = 3

# Frecuencia estacional
ESTACIONALIDAD = 12

# ============================================================
# 3. VARIABLES MACROECONÓMICAS
# ============================================================
MACRO_DATA = {
    2021: {'IPC': 5.62, 'Salario_Minimo': 3.50, 'UPC': 5.00},
    2022: {'IPC': 13.12, 'Salario_Minimo': 10.07, 'UPC': 5.42},
    2023: {'IPC': 9.28, 'Salario_Minimo': 16.00, 'UPC': 16.23},
    2024: {'IPC': 5.81, 'Salario_Minimo': 12.06, 'UPC': 12.01},  # DANE final 2024
    2025: {'IPC': 4.50, 'Salario_Minimo': 9.50, 'UPC': 8.00},    # Proyección 2025 y SMLV decreto
}

MESES_PICO = [1, 7]        # Enero y Julio
MESES_FESTIVIDAD = [6, 12]  # Junio y Diciembre

# ============================================================
# 4. SISTEMA DE VISUALIZACIÓN PROFESIONAL
# ============================================================
_scripts_dir = str(PROJECT_ROOT / 'scripts')
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

_VIZ_THEME_LOADED = False
try:
    from viz_theme import (
        # Constantes de tipografía
        FONT_FAMILY, FONT_TITLE, FONT_SUBTITLE, FONT_AXIS, FONT_TICK,
        FONT_LEGEND, FONT_ANNOTATION, FONT_WATERMARK,
        # Colores principales
        C_PRIMARY, C_SECONDARY, C_TERTIARY, C_QUATERNARY,
        C_QUINARY, C_SENARY, C_SEPTENARY,
        # Colores de soporte
        C_GRID, C_BACKGROUND, C_TEXT, C_TEXT_LIGHT, C_HIGHLIGHT,
        C_CI_FILL, C_CI_BORDER, C_POSITIVE, C_NEGATIVE,
        C_TRAIN, C_TEST, C_BAR_PEAK, C_BAR_NORMAL, C_BAR_VALLEY,
        # Diccionario de colores por modelo
        COLORES_MODELOS, PALETTE_SEQUENTIAL, PALETTE_DIVERGING,
        # Dimensiones
        FIGSIZE_FULL, FIGSIZE_WIDE, FIGSIZE_STANDARD, FIGSIZE_DUAL,
        FIGSIZE_QUAD, FIGSIZE_SMALL, FIGSIZE_SQUARE,
        # Funciones
        aplicar_tema_profesional, formato_pesos, formato_pesos_eje,
        formato_porcentaje, titulo_profesional, marca_agua,
        anotar_pico, linea_media, zona_train_test, leyenda_profesional,
        guardar_figura,
        # Gráficas prediseñadas
        grafica_serie_tiempo, grafica_barras_estacional, grafica_residuos,
        grafica_pronostico, grafica_comparacion_modelos, tabla_metricas,
        grafica_radar,
    )
    _VIZ_THEME_LOADED = True
except ImportError as e:
    print(f'  ⚠️ viz_theme.py no cargado: {e} — usando tema básico')
    # --- Fallback mínimo ---
    C_PRIMARY = '#1B2A4A'; C_SECONDARY = '#C0392B'; C_TERTIARY = '#2980B9'
    C_QUATERNARY = '#27AE60'; C_QUINARY = '#E67E22'; C_SENARY = '#8E44AD'
    C_SEPTENARY = '#16A085'; C_CI_FILL = '#D5E8F0'
    FIGSIZE_STANDARD = (14, 6); FIGSIZE_WIDE = (16, 6)
    FIGSIZE_FULL = (14, 7); FIGSIZE_QUAD = (16, 12); FIGSIZE_SMALL = (8, 5)
    COLORES_MODELOS = {
        'real': C_PRIMARY, 'sarima': C_SECONDARY, 'sarimax': C_TERTIARY,
        'prophet': C_QUATERNARY, 'xgboost': C_QUINARY, 'lstm': C_SENARY,
        'ensemble': C_SEPTENARY, 'ci': C_CI_FILL,
    }
    def formato_pesos(valor, pos=None):
        if abs(valor) >= 1e9: return f'${valor/1e9:,.0f}MM'
        elif abs(valor) >= 1e6: return f'${valor/1e6:,.0f}M'
        return f'${valor:,.0f}'
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update({'figure.figsize': FIGSIZE_STANDARD, 'figure.dpi': 150,
                         'font.size': 11, 'axes.titlesize': 14, 'axes.titleweight': 'bold'})
    sns.set_palette('husl')

# Alias de compatibilidad (funciona con o sin viz_theme)
COLORES = {
    'real': C_PRIMARY, 'sarima': C_SECONDARY, 'sarimax': C_TERTIARY,
    'prophet': C_QUATERNARY, 'xgboost': C_QUINARY, 'lstm': C_SENARY,
    'ensemble': C_SEPTENARY, 'ci': C_CI_FILL,
}
FIGSIZE_LARGE = FIGSIZE_QUAD if _VIZ_THEME_LOADED else (16, 10)

# ============================================================
# 5. INFORMACIÓN DEL PROYECTO
# ============================================================
PROYECTO_NOMBRE = "Sistema de Análisis y Pronóstico de Rentas Cedidas"
PROYECTO_ENTIDAD = "Departamentos y Distritos de Colombia"
PROYECTO_PERIODO = f"{FECHA_INICIO} a {FECHA_FIN}"

print(f"✅ Config cargada — Datos: {DATA_FILE.name} | Periodo: {PROYECTO_PERIODO}")
if _VIZ_THEME_LOADED:
    print(f"  🎨 Tema profesional activo — DPI 300, tipografía serif, paleta académica")

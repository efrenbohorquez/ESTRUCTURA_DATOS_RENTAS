# Sistema de Análisis y Pronóstico de Rentas Cedidas

> **Investigación Doctoral** — Caracterización avanzada del recaudo de rentas cedidas (licores, cigarrillos y azar) giradas por ADRES a entidades territoriales de Colombia, 2022-2025.

## Estructura del Repositorio

```
├── notebooks/              # Pipeline analítico secuencial
│   ├── 00_config.py        # Configuración centralizada (rutas, fechas, parámetros)
│   ├── 01_EDA_Completo     # Análisis Exploratorio de Datos
│   ├── 02_Estacionalidad   # Descomposición estacional y patrones temporales
│   ├── 03_Correlacion_Macro# Correlación con variables macroeconómicas (IPC, SMLV)
│   ├── 04_SARIMA           # Modelo SARIMA base
│   ├── 05_SARIMAX          # Modelo SARIMAX con variables exógenas
│   ├── 06_Prophet          # Facebook Prophet con changepoints
│   ├── 07_XGBoost          # Gradient Boosting con features temporales
│   ├── 08_LSTM             # Red neuronal LSTM
│   ├── 09_Comparacion      # Benchmarking multiescala (MAPE, RMSE, MAE)
│   ├── 10_Segmentacion     # Tipificación K-Means de entidades territoriales
│   └── 11_Modelado_Panel   # SARIMAX vs XGBoost por tipología
├── scripts/                # Utilidades y temas visuales
│   ├── viz_theme.py        # Sistema de visualización profesional (DPI 300)
│   ├── utils.py            # Funciones auxiliares
│   ├── model_helpers.py    # Helpers de modelado
│   └── pipeline_panel_completo.py  # Pipeline ejecutable de 5 fases
├── data/                   # Datos (raw y procesados)
├── outputs/                # Resultados generados
│   ├── figures/            # Gráficas de alta resolución
│   ├── forecasts/          # CSVs de pronósticos
│   ├── reports/            # Reportes PDF
│   └── panel/              # Resultados del análisis de panel
├── docs/                   # Documentación y notebooks complementarios
├── requirements.txt        # Dependencias Python
└── README.md               # Este archivo
```

## Parámetros del Análisis

| Parámetro | Valor |
|-----------|-------|
| **Período** | Enero 2022 – Diciembre 2025 |
| **Entrenamiento** | Ene 2022 – Sep 2025 (45 meses) |
| **Backtest** | Oct – Dic 2025 (3 meses) |
| **Horizonte** | 3 meses |
| **Estacionalidad** | 12 (mensual) |

## Modelos Implementados

| Modelo | Tipo | MAPE Agregado |
|--------|------|:-------------:|
| **SARIMAX** | Econométrico | ~14.5% |
| **Prophet** | Descomposición | ~12% |
| **XGBoost** | Machine Learning | **~6.6%** |
| **LSTM** | Deep Learning | ~15% |

## Segmentación de Entidades (K-Means)

| Tipología | Entidades | Descripción |
|-----------|:---------:|-------------|
| Consolidados | 55 | Gobernaciones principales (Antioquia, Valle, Cundinamarca) |
| Emergentes | 235 | Recaudo medio-alto, volatilidad moderada |
| Dependientes | 475 | Bajo recaudo, alta dependencia del SGP |
| Críticos | 334 | Recaudo mínimo, alta volatilidad |

## Requisitos

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
# Pipeline completo de panel
python scripts/pipeline_panel_completo.py

# Ejecución de notebooks individuales
jupyter nbconvert --execute notebooks/01_EDA_Completo.ipynb
```

## Dataset

El archivo principal `BaseRentasVF_2022_2025.xlsx` contiene 141,753 transacciones de giros de rentas cedidas con las columnas:

- `FechaRecaudo` — Fecha del giro
- `NitBeneficiarioAportante` — NIT de la entidad territorial
- `NombreBeneficiarioAportante` — Nombre de la entidad
- `ValorRecaudo` — Monto del giro (COP)

## Autor

Investigación doctoral en Economía de la Salud — Análisis de la resiliencia fiscal de las entidades territoriales frente a las rentas cedidas del sistema de salud en Colombia.

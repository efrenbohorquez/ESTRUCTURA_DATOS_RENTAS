"""
Pipeline Completo: Segmentación + Modelado Panel de Rentas Cedidas
Adaptado a la estructura real del dataset BaseRentasVF_2022_2025.xlsx
Columnas: FechaRecaudo, NitBeneficiarioAportante, NombreBeneficiarioAportante, ValorRecaudo
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import ccf
import warnings
warnings.filterwarnings('ignore')

sns.set_theme(style='whitegrid', context='notebook')
OUT = 'outputs/panel'
import os; os.makedirs(OUT, exist_ok=True)

# ═══════════════════════════════════════════════════════════
# FASE 1: CARGA Y PREPARACIÓN DEL PANEL
# ═══════════════════════════════════════════════════════════
print("=" * 60)
print("FASE 1: Carga y Preparación de Datos")
print("=" * 60)

df = pd.read_excel('BaseRentasVF_2022_2025.xlsx')
df['FechaRecaudo'] = pd.to_datetime(df['FechaRecaudo'])

# Filtrar desde Ene 2022 (acorde al dataset)
df = df[df['FechaRecaudo'] >= '2022-01-01'].copy()
df['YearMonth'] = df['FechaRecaudo'].dt.to_period('M')

# Agregar a nivel mensual por entidad
panel = df.groupby(['NombreBeneficiarioAportante', 'YearMonth'])['ValorRecaudo'].sum().reset_index()
panel.columns = ['Entidad', 'Periodo', 'Recaudo']
panel['Fecha'] = panel['Periodo'].dt.to_timestamp()

# Filtrar solo entidades con al menos 24 meses de datos (2 años)
conteo = panel.groupby('Entidad')['Periodo'].count()
entidades_validas = conteo[conteo >= 24].index
panel = panel[panel['Entidad'].isin(entidades_validas)].copy()

print(f"Entidades con >= 24 meses de datos: {len(entidades_validas)}")
print(f"Total registros mensuales: {len(panel)}")

# ═══════════════════════════════════════════════════════════
# FASE 2: CLASIFICACIÓN JERÁRQUICA (TIPOLOGÍAS)
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("FASE 2: Clasificación Jerárquica de Entidades")
print("=" * 60)

stats = panel.groupby('Entidad')['Recaudo'].agg(['mean', 'sum', 'std']).reset_index()
stats['CV'] = stats['std'] / stats['mean'].replace(0, np.nan)
stats['CV'] = stats['CV'].fillna(0)

# K-Means con 4 clusters sobre log(recaudo total) y CV
features_km = np.column_stack([
    np.log1p(stats['sum'].clip(lower=0).values),
    stats['CV'].clip(upper=10).values
])
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
stats['Cluster'] = kmeans.fit_predict(features_km)

# Asignar nombres lógicos basados en recaudo medio
cluster_rank = stats.groupby('Cluster')['sum'].mean().sort_values(ascending=False).index
nombres = {
    cluster_rank[0]: '1_Consolidados',
    cluster_rank[1]: '2_Emergentes',
    cluster_rank[2]: '3_Dependientes',
    cluster_rank[3]: '4_Críticos'
}
stats['Tipologia'] = stats['Cluster'].map(nombres)

print("\nDistribución de Tipologías:")
print(stats['Tipologia'].value_counts().to_string())
print("\nEstadísticas por Tipología:")
resumen = stats.groupby('Tipologia')[['mean', 'CV']].mean()
resumen.columns = ['Recaudo_Medio', 'CV_Medio']
print(resumen.to_string())

# Guardar clasificación
stats.to_csv(f'{OUT}/clasificacion_entidades.csv', index=False)
panel = panel.merge(stats[['Entidad', 'Tipologia']], on='Entidad', how='left')

# ═══════════════════════════════════════════════════════════
# FASE 3: ELECTROCARDIOGRAMA FISCAL (BOX-PLOTS)
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("FASE 3: Análisis Descriptivo y Estacionalidad")
print("=" * 60)

panel['Mes'] = panel['Fecha'].dt.month
tipologias = sorted(panel['Tipologia'].dropna().unique())

fig, axes = plt.subplots(2, 2, figsize=(16, 12), sharex=True)
axes = axes.flatten()
for i, tipo in enumerate(tipologias):
    ax = axes[i]
    data_tipo = panel[panel['Tipologia'] == tipo]
    sns.boxplot(data=data_tipo, x='Mes', y='Recaudo', ax=ax, palette='viridis')
    ax.set_title(f'Electrocardiograma Fiscal: {tipo}', fontweight='bold')
    ax.set_ylabel('Recaudo ($)')
    ax.ticklabel_format(style='plain', axis='y')
plt.tight_layout()
plt.savefig(f'{OUT}/electrocardiograma_fiscal.png', dpi=150, bbox_inches='tight')
plt.close()
print("Boxplots guardados en outputs/panel/electrocardiograma_fiscal.png")

# Cross-Correlation (Hipótesis del Rezago)
print("\nPrueba de Correlación Cruzada (Hipótesis del Rezago):")
serie_total = panel.groupby('Fecha')['Recaudo'].sum().sort_index()
if len(serie_total) >= 24:
    serie_diff = serie_total.diff().dropna()
    corr_cruza = ccf(serie_diff.values, serie_diff.values)[:13]
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(range(13), corr_cruza, color='steelblue')
    ax.axhline(0, color='black', lw=1)
    ax.set_title('Auto-Correlación Cruzada del Recaudo Agregado (Δ mensual)')
    ax.set_xlabel('Lags (Meses)')
    ax.set_ylabel('Correlación')
    ax.set_xticks(range(13))
    plt.tight_layout()
    plt.savefig(f'{OUT}/ccf_rezago.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  Lag 0:", round(corr_cruza[0], 3))
    print("  Lag 1:", round(corr_cruza[1], 3))
    print("  Lag 12:", round(corr_cruza[12], 3))

# ═══════════════════════════════════════════════════════════
# FASE 4: MODELADO PREDICTIVO (SARIMAX por Tipología)
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("FASE 4: Modelado Predictivo y Benchmarking")
print("=" * 60)

fecha_corte = pd.Timestamp('2025-09-30')
resultados = []

for tipo in tipologias:
    print(f"\n--- Tipología: {tipo} ---")
    
    # Agregar recaudo mensual por tipología
    serie = panel[panel['Tipologia'] == tipo].groupby('Fecha')['Recaudo'].sum().sort_index()
    serie.index = pd.DatetimeIndex(serie.index)
    serie = serie.asfreq('MS', fill_value=0)
    
    train = serie[serie.index <= fecha_corte]
    test = serie[serie.index > fecha_corte]
    
    if len(test) == 0:
        print(f"  Sin datos de test para {tipo}")
        continue
    
    print(f"  Train: {len(train)} meses | Test: {len(test)} meses")
    
    # SARIMAX (sin exógenas ya que el dataset no incluye IPC directamente)
    try:
        modelo = SARIMAX(train, order=(1, 1, 1), seasonal_order=(0, 1, 1, 12),
                         enforce_stationarity=False, enforce_invertibility=False)
        fit = modelo.fit(disp=False, maxiter=200)
        pred = fit.forecast(steps=len(test))
        
        y_true = test.values
        y_pred = pred.values
        
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mape = np.mean(np.abs((y_true - y_pred) / np.where(y_true != 0, y_true, 1))) * 100
        
        resultados.append({
            'Tipologia': tipo,
            'Modelo': 'SARIMAX',
            'MAE': mae,
            'RMSE': rmse,
            'MAPE': round(mape, 2)
        })
        print(f"  SARIMAX -> MAPE: {mape:.2f}%, MAE: {mae:,.0f}, RMSE: {rmse:,.0f}")
    except Exception as e:
        print(f"  SARIMAX Error: {e}")
    
    # XGBoost (Feature Engineering puro sobre series)
    try:
        import xgboost as xgb
        
        df_xgb = pd.DataFrame({'Recaudo': serie})
        df_xgb['Lag_1'] = df_xgb['Recaudo'].shift(1)
        df_xgb['Lag_2'] = df_xgb['Recaudo'].shift(2)
        df_xgb['Lag_12'] = df_xgb['Recaudo'].shift(12)
        df_xgb['Mes'] = df_xgb.index.month
        df_xgb['Trimestre'] = df_xgb.index.quarter
        df_xgb = df_xgb.dropna()
        
        feats = ['Lag_1', 'Lag_2', 'Lag_12', 'Mes', 'Trimestre']
        train_xgb = df_xgb[df_xgb.index <= fecha_corte]
        test_xgb = df_xgb[df_xgb.index > fecha_corte]
        
        if len(train_xgb) > 10 and len(test_xgb) > 0:
            model_xgb = xgb.XGBRegressor(n_estimators=100, max_depth=3,
                                          learning_rate=0.05, objective='reg:absoluteerror')
            model_xgb.fit(train_xgb[feats], train_xgb['Recaudo'])
            pred_xgb = model_xgb.predict(test_xgb[feats])
            
            y_true_xgb = test_xgb['Recaudo'].values
            mae_x = mean_absolute_error(y_true_xgb, pred_xgb)
            rmse_x = np.sqrt(mean_squared_error(y_true_xgb, pred_xgb))
            mape_x = np.mean(np.abs((y_true_xgb - pred_xgb) / np.where(y_true_xgb != 0, y_true_xgb, 1))) * 100
            
            resultados.append({
                'Tipologia': tipo,
                'Modelo': 'XGBoost',
                'MAE': mae_x,
                'RMSE': rmse_x,
                'MAPE': round(mape_x, 2)
            })
            print(f"  XGBoost -> MAPE: {mape_x:.2f}%, MAE: {mae_x:,.0f}, RMSE: {rmse_x:,.0f}")
    except Exception as e:
        print(f"  XGBoost Error: {e}")

# ═══════════════════════════════════════════════════════════
# FASE 5: REPORTE DE RESULTADOS
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("FASE 5: Reporte Final de Métricas OOS")
print("=" * 60)

if resultados:
    df_res = pd.DataFrame(resultados)
    print("\nTabla de Métricas (Out-of-Sample: Oct-Dic 2025):")
    pivot = df_res.pivot(index='Tipologia', columns='Modelo', values='MAPE')
    print(pivot.to_string())
    
    df_res.to_csv(f'{OUT}/metricas_oos_panel.csv', index=False)
    
    # Gráfico comparativo
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=df_res, x='Tipologia', y='MAPE', hue='Modelo', palette='Set1', ax=ax)
    ax.set_title('MAPE de Backtesting por Tipología (Oct-Dic 2025)', fontweight='bold', fontsize=14)
    ax.set_ylabel('MAPE (%)')
    ax.set_xlabel('Tipología de Entidad Territorial')
    plt.tight_layout()
    plt.savefig(f'{OUT}/mape_comparativo.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\nGráfico guardado en {OUT}/mape_comparativo.png")
else:
    print("No se generaron resultados de backtesting.")

print("\n" + "=" * 60)
print("PIPELINE COMPLETADO EXITOSAMENTE")
print("=" * 60)

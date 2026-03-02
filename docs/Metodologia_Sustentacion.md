# Metodología de Predicción de Rentas Cedidas - Quibdó

El presente documento detalla el marco metodológico, las decisiones de arquitectura de datos y las especificaciones de los modelos econométricos y de machine learning implementados para pronosticar el recaudo de rentas cedidas en el municipio de Quibdó. 

Esta sustentación técnica sirve como anexo metodológico para el informe final de gestión de flujo de caja y proyección de ingresos tributarios y no tributarios.

---

## 1. Diseño Experimental y Delimitación Temporal

Debido a los profundos cambios estructurales y a la distorsión estadística ocasionada por la pandemia del COVID-19 (2020-2021) y el posterior rebote económico, el ensamble de modelos se configuró bajo los siguientes parámetros de diseño experimental:

- **Período de Entrenamiento (Train):** Enero de 2022 a Septiembre de 2025 (45 observaciones mensuales). Se limitó el horizonte histórico para evitar sesgos provocados por anomalías pre-2022, asegurando que los modelos capturen la dinámica inflacionaria y de recaudo contemporánea.
- **Período de Validación (Test / Backtest):** Octubre a Diciembre de 2025 (3 observaciones mensuales). Representa el trimestre de cierre fiscal, el cual exhibe históricamente la mayor volatilidad por picos de recaudo.
- **Ventana de Observación Limitada:** Al contar con $N = 48$ meses en total, el diseño econométrico debe penalizar la sobre-parametrización. Por ende, los algoritmos seleccionados equilibran la flexibilidad (para adaptarse a picos) con la regularización (para evitar *overfitting*).

---

## 2. Variables y Tratamiento de Datos

### 2.1. Endógena (Var. Objetivo)
- **Recaudo Neto:** Ingresos efectivos reportados mensualmente. Para arquitecturas de Deep Learning (LSTM), se emplea una transformación logarítmica $\log(1+x)$ para estabilizar la varianza y mitigar los efectos de picos extremos, revirtiendo la transformación (exponenciación) en la etapa de inferencia.

### 2.2. Exógenas (Predictores)
- **Macro-económicas:** Se incluyeron el Índice de Precios al Consumidor (IPC) y el Salario Mínimo Legal Vigente (SMLV). Para evitar el problema empírico de no conocer el valor futuro exacto de estas variables en tiempo de producción, **se enrutaron como variables rezagadas (Lag $t-1$)**. De esta forma, el modelo predice el recaudo del mes $t$ utilizando la inflación conocida del mes $t-1$.
- **Temporales Estructurales:** Identificadores escalares y categóricos del mes del año y del trimestre, utilizados profusamente en los modelos de ensamble.

---

## 3. Arquitectura de Modelamiento (Modelos Competidores)

A fin de generar un consenso sólido, se enfrentaron cuatro familias metodológicas distintas, reduciendo el riesgo de modelo (*Model Risk*).

### 3.1. Familia Estadística Clásica: SARIMAX
- **Especificación:** Modelo Auto-Regresivo Integrado de Media Móvil con Exógenas y factor Estacional.
- **Sustentación:** Asume relaciones lineales subyacentes. Se forzó a incluir retardos endógenos e impacto lineal del factor inflacionario (IPC Lagged). Se configuró un proceso de selección automática de hiperparámetros limitando el orden a $(P, D, Q)_{12}$ debido a los 45 datos de entrenamiento.

### 3.2. Familia de Descomposición Aditiva/Multiplicativa: Prophet
- **Especificación:** Desarrollado por Meta (Facebook), este algoritmo descompone la serie en tendencia, estacionalidad y festividades (*holidays*).
- **Sustentación:** Se aplicó una **estacionalidad de tipo multiplicativa**, puesto que la varianza cíclica del recaudo aumenta proporcionalmente con los valores nominales inflados del recaudo general. Adicionalmente, se forzaron variables de *holidays* customizadas para **Julio** y **Diciembre**, marcando institucionalmente los meses de picos anómalos previstos. La regresión emplea Changepoints automáticos adaptativos desde 2022.

### 3.3. Familia de Ensamble Basado en Árboles: XGBoost
- **Especificación:** Extreme Gradient Boosting. Un ensamble de cientos de árboles de decisión iterativos que modelan los residuales (debilidades) de los árboles previos.
- **Sustentación:** Se reestructuró la serie temporal en un problema tabular supervisado mediante la creación ingenieril de características (*feature engineering*): Lags endógenos de 1, 2 y 12 meses. Para dotarlo de robustez ante valores atípicos severos (los picos gigantes de recaudo de fin de año), la *Loss Function* fue configurada hacia metodologías orientadas al Error Absoluto (MAE-like o Pseudo-Huber), amortiguando la corrección por gradiente excesiva causada por meses anómalos.

### 3.4. Familia Deep Learning: Memoria a Corto y Largo Plazo (LSTM)
- **Especificación:** Red Neuronal Recurrente (RNN) nativa de PyTorch.
- **Sustentación:** Diseñada para recordar patrones temporales de larga duración. Al tener una red teóricamente "hambrienta" de datos emparejada con un set de apenas 48 puntos de datos, su uso es experimental. La sustentación de su fiabilidad descansa en el **Test de Ljung-Box para ruido blanco** sobre sus residuales iterativos: si los errores probabilísticos no albergan correlación serial residual, el modelo logró extraer matemáticamente todo patrón determinístico.

---

## 4. Criterio de Evaluación y Agregación Multiescala

La formulación algorítmica arrojó predicciones discretas mensuales. Sin embargo, para fines de **Planeación Presupuestal y Control de Flujo de Caja Público**, visualizar el error estrictamente al mes no es sufiente, ya que los retrasos contables de pocos días pueden desfasar la recaudación del 31 del mes al día 1 del mes siguiente, castigando artificialmente al modelo algorítmico cuando sistémicamente el dinero sí ingresó en ese período fiscal continuo.

Para subsanar este fenómeno (el cual es empíricamente válido en contabilidad gubernamental), se consolidó el desempeño bajo una metodología de **Evaluación Multiescala**:
1. Se calculan las predicciones base (Mensuales).
2. Se unifican estocásticamente las frecuencias al compás **Bimestral (2M)** y **Trimestral (3M)** mediante la función sumatoria del recaudo.
3. Se vuelve a calcular el Mean Absolute Percentage Error (MAPE). 

### Interpretación Financiera
Si un modelo manifiesta un MAPE mensual del 15%, pero su recálculo en la métrica Trimestral desciende abruptamente al 6%, se dictamina que **el modelo es estructuralmente preciso en la estimación de caja**, y que el error original recaía íntegramente en la variabilidad intra-trimestral de cobros o pagos, pero el gran total proyectado es altisimamente confiable para establecer un Plan Operativo Anual de Inversiones (POAI).

---
*Este marco proporciona un blindaje técnico, estadístico y financiero frente a las decisiones basadas en los reportes arrojados por los cuadernos de automatización analítica (Jupyter).*

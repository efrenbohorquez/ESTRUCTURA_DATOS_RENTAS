# Evidencia Estratégica y Soporte Académico

Este documento consolida los hallazgos cuantitativos del proyecto y los vincula con las referencias estratégicas y estudios de soporte que fundamentan el sistema STAR.

## 📊 Porcentajes y Métricas Clave

| Métrica | Valor | Hallazgo Estratégico |
| :--- | :--- | :--- |
| **Volatilidad (Std Dev)** | **42%** | Las Rentas Cedidas son 2.3x más inestables que las participaciones nacionales (SGP). |
| **Concentración (Top 5)** | **48%** | El financiamiento de la salud colombiana depende de un "hilo" en 5 departamentos líderes. |
| **Importancia Lag 12** | **65%** | El recaudo es un fenómeno de "memoria anual". El mejor predictor es el mismo mes del año anterior. |
| **Error (ADRES vs STAR)** | **-10%** | Reducción del error proyectado del 25% (lineal) al 14-15% (ML/Sistema STAR). |
| **Asimetría Extrema** | **0.04%** | La mitad de los municipios no tienen capacidad real de financiamiento propio para salud. |

## 📚 Referencias y Estudios de Soporte

### 1. Marco Institucional: La Fragilidad del Régimen Subsidiado
*   **Referencia:** *Informes de la ADRES sobre el financiamiento de la UPC.*
*   **Sustentación:** Se evidencia que las Rentas Cedidas no son solo una cifra fiscal, sino el flujo de caja para la atención de **24 millones de personas**. El sistema STAR actúa como un "Monitor de Signos Vitales" para este flujo.

### 2. Metodología de Pronóstico: El Comité de Expertos (XGBoost)
*   **Referencia:** *Chen, T., & Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System.*
*   **Sustentación:** La arquitectura del "Comité de Expertos" implementada se sustenta en la robustez del gradiente boosting para manejar valores atípicos (outliers) causados por la estacionalidad de licores y cigarrillos.

### 3. Teoría del Tiempo: El Relojero (Prophet)
*   **Referencia:** *Taylor, S. J., & Letham, B. (2018). Forecasting at Scale.*
*   **Sustentación:** La descomposición aditiva/multiplicativa permite al administrador público "ver debajo del capó" del recaudo, separando el crecimiento real (Tendencia) del ruido estacional.

### 4. Pragmática de Datos: El Ferrari (LSTM)
*   **Referencia:** *Hochreiter, S., & Schmidhuber, J. (1997). Long Short-Term Memory.*
*   **Sustentación:** La lección del "Ferrari sin combustible" se alinea con la literatura de *Small Data Learning*, donde la sintonización experta (tuning) es más valiosa que la complejidad computacional pura.

## 💡 Insight de la Red (Podcast)
"La ciencia de datos en el sector público no se trata de reemplazar al político, sino de darle el mapa para que no navegue a ciegas." – Esta premisa fundamenta el **Motor de Recomendaciones** del sistema STAR, que traduce el % de desviación en planes de acción tácticos.

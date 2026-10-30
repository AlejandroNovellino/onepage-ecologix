# One Page Ejecutivo · Proyecto Ecologix

Dashboard en Streamlit del One Page de seguimiento definido en el Manual (Módulo 7):
estado general, avance vs plan, 7 KPIs con semáforo, Curva S (PV/EV/AC), alertas y próximas decisiones.
Los datos son ficticios y se editan en vivo desde la barra lateral.

## Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Desplegar en Streamlit Community Cloud

1. Subir `app.py`, `requirements.txt` y la carpeta `.streamlit/` a un repositorio de GitHub.
2. En https://share.streamlit.io → **New app** → elegir el repo y `app.py` como archivo principal.

## Reglas de cálculo

- PV = BAC × % planificado · EV = BAC × % real
- SPI = EV / PV · %SV = (EV − PV) / PV · CPI = EV / AC · %CV = (EV − AC) / EV
- Semáforo: Verde ≥ 0.90 (o ≥ 90% / ≥ −10%), Ámbar 0.80–0.89, Rojo < 0.80
- Estado general = peor estado entre los 7 indicadores

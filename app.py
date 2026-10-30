"""One Page Ejecutivo de Seguimiento - Proyecto Ecologix.

Dashboard en Streamlit basado en el Manual de Seguimiento (Módulo 7).
Ejecutar con:  streamlit run app.py
"""

from datetime import date, datetime
import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="One Page · Proyecto Ecologix", page_icon="📊", layout="wide")

# ---------------------------------------------------------------------------
# Paleta (colores nativos del tema oscuro de Streamlit)
# ---------------------------------------------------------------------------
VERDE, AMBAR, ROJO, AZUL = "#21c354", "#ffa421", "#ff4b4b", "#60b4ff"
COLOR_ESTADO = {"Verde": VERDE, "Ámbar": AMBAR, "Rojo": ROJO}
COLOR_PRIORIDAD = {"Alta": ROJO, "Media": AMBAR, "Baja": VERDE}
ORDEN_ESTADO = {"Verde": 0, "Ámbar": 1, "Rojo": 2}
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
TOTAL_SPRINTS = 14  # 7 meses en Sprints de 2 semanas
FASES = [
    "Conceptualización",
    "Diseño y planificación",
    "Desarrollo",
    "Desarrollo y pruebas",
    "Pruebas",
    "Despliegue y posproducción",
]

DEFAULTS = {
    "proyecto": "Proyecto Ecologix",
    "po": "Laura Méndez",
    "sprint": 5,
    "fecha": date(2026, 11, 15),
    "fase": "Desarrollo y pruebas",
    "plan": 58,
    "real": 54,
    "bac": 120,
    "ac": 72,
    "chr": 86,
    "cpe": 92,
    "tae": 88,
    "hito": "Integración con sistemas externos",
    "hito_estado": "En retraso",
    "diag_auto": True,
    "diag_manual": "Avance cercano al plan, con alertas en hitos críticos, costos y aceptación de entregables.",
    "linea_base": False,
}

ALERTAS_DEFAULT = pd.DataFrame(
    [
        {"Alerta": "Retraso en integraciones externas", "Detalle": "Impacta el hito de integración.", "Prioridad": "Alta"},
        {"Alerta": "Sobrecosto de soporte técnico", "Detalle": "5% por encima del plan.", "Prioridad": "Alta"},
        {"Alerta": "Riesgo de aprobación tardía", "Detalle": "Dependencia del cliente.", "Prioridad": "Media"},
    ]
)
DECISIONES_DEFAULT = pd.DataFrame(
    [
        {"Decisión": "Repriorizar backlog", "Responsable": "PO", "Fecha": date(2026, 11, 18)},
        {"Decisión": "Reforzar QA", "Responsable": "Scrum Master", "Fecha": date(2026, 11, 17)},
        {"Decisión": "Escalar validación", "Responsable": "Sponsor + PO", "Fecha": date(2026, 11, 19)},
    ]
)

for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)
st.session_state.setdefault("editor_ver", 0)


def restablecer():
    for k, v in DEFAULTS.items():
        st.session_state[k] = v
    st.session_state.editor_ver += 1


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def fmt_fecha(d: date) -> str:
    return f"{d.day} {MESES[d.month - 1]} {d.year}"


def fmt_dinero(v_k: float) -> str:
    """Recibe miles de dólares y devuelve '$120k' o '$64.8k'."""
    return f"${v_k:,.0f}k" if abs(v_k - round(v_k)) < 0.05 else f"${v_k:,.1f}k"


def semaforo(valor: float, verde: float, ambar: float) -> str:
    if valor >= verde:
        return "Verde"
    if valor >= ambar:
        return "Ámbar"
    return "Rojo"


def badge(estado: str, color: str | None = None) -> str:
    c = color or COLOR_ESTADO[estado]
    return (
        f'<span class="badge" style="color:{c};background:{c}22;">'
        f'<span class="dot" style="background:{c};"></span>{estado}</span>'
    )


def s_shape(t: float) -> float:
    """Curva logística normalizada (0 en t=0) para simular una curva S."""
    k, mid = 0.45, TOTAL_SPRINTS / 2
    f = lambda x: 1 / (1 + math.exp(-k * (x - mid)))
    return f(t) - f(0)


# ---------------------------------------------------------------------------
# Barra lateral: datos editables
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Datos del reporte")
    st.caption("Modifica los valores y el One Page se actualiza en vivo.")

    with st.expander("Encabezado", expanded=False):
        st.text_input("Proyecto", key="proyecto")
        st.text_input("Product Owner", key="po")
        st.slider("Sprint actual", 1, TOTAL_SPRINTS, key="sprint")
        st.date_input("Fecha de corte", key="fecha", format="DD/MM/YYYY")
        st.selectbox("Fase actual", FASES, key="fase")

    with st.expander("Avance y costos (EVM)", expanded=True):
        st.slider("Avance planificado (%)", 1, 100, key="plan")
        st.slider("Avance real (%)", 0, 100, key="real")
        st.slider("Presupuesto BAC (k$)", 50, 500, step=5, key="bac")
        st.slider("Costo real AC (k$)", 1, 600, key="ac")
        st.text_input("Hito crítico del ciclo", key="hito")
        st.radio("Estado del hito", ["Cumplido", "En retraso"], key="hito_estado", horizontal=True)

    with st.expander("Indicadores operativos", expanded=True):
        st.slider("CHR · Hitos ruta crítica en plazo (%)", 0, 100, key="chr")
        st.slider("CPE · Cobertura de pruebas (%)", 0, 100, key="cpe")
        st.slider("TAE · Aceptación de entregables (%)", 0, 100, key="tae")

    with st.expander("Alertas (máx. 3)", expanded=False):
        alertas_df = st.data_editor(
            ALERTAS_DEFAULT,
            key=f"alertas_{st.session_state.editor_ver}",
            num_rows="dynamic",
            hide_index=True,
            width="stretch",
            column_config={
                "Prioridad": st.column_config.SelectboxColumn(options=["Alta", "Media", "Baja"], required=True),
            },
        )

    with st.expander("Próximas decisiones (máx. 3)", expanded=False):
        decisiones_df = st.data_editor(
            DECISIONES_DEFAULT,
            key=f"decisiones_{st.session_state.editor_ver}",
            num_rows="dynamic",
            hide_index=True,
            width="stretch",
            column_config={
                "Responsable": st.column_config.SelectboxColumn(
                    options=["PO", "Scrum Master", "Sponsor", "Sponsor + PO", "PMO", "Finanzas"]
                ),
                "Fecha": st.column_config.DateColumn(format="DD/MM/YYYY"),
            },
        )

    with st.expander("Diagnóstico y gráfico", expanded=False):
        st.toggle("Diagnóstico automático", key="diag_auto")
        if not st.session_state.diag_auto:
            st.text_area("Diagnóstico ejecutivo (máx. 2 líneas)", key="diag_manual", max_chars=180)
        st.toggle("Mostrar línea base completa en la Curva S", key="linea_base")

    st.button("↺ Restablecer valores", on_click=restablecer, width="stretch")

s = st.session_state

# ---------------------------------------------------------------------------
# Cálculos EVM y semáforos (según el Manual de Seguimiento)
# ---------------------------------------------------------------------------
bac = float(s.bac)
pv = bac * s.plan / 100
ev = bac * s.real / 100
ac = float(s.ac)

spi = round(ev / pv, 2)
sv_pct = round((ev - pv) / pv * 100, 1)
cpi = round(ev / ac, 2)
cv_pct = round((ev - ac) / ev * 100, 1) if ev > 0 else -100.0

kpis = [
    # (sigla, valor mostrado, estado, área, meta)
    ("SPI", f"{spi:.2f}", semaforo(spi, 0.90, 0.80), "cronograma", "≥ 0.90"),
    ("%SV", f"{sv_pct:+.1f}%".replace("+", ""), semaforo(sv_pct, -10, -20), "cronograma", "≥ -10%"),
    ("CHR", f"{s.chr}%", semaforo(s.chr, 90, 80), "hitos críticos", "≥ 90%"),
    ("CPI", f"{cpi:.2f}", semaforo(cpi, 0.90, 0.80), "costos", "≥ 0.90"),
    ("%CV", f"{cv_pct:+.1f}%".replace("+", ""), semaforo(cv_pct, -10, -20), "costos", "≥ -10%"),
    ("CPE", f"{s.cpe}%", semaforo(s.cpe, 90, 80), "calidad de pruebas", "≥ 90%"),
    ("TAE", f"{s.tae}%", semaforo(s.tae, 90, 80), "aceptación de entregables", "≥ 90%"),
]

estado_global = max((k[2] for k in kpis), key=ORDEN_ESTADO.get)
rojos = list(dict.fromkeys(k[3] for k in kpis if k[2] == "Rojo"))
ambar = list(dict.fromkeys(k[3] for k in kpis if k[2] == "Ámbar"))


def unir(items: list[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " y " + items[-1]


if not s.diag_auto:
    diagnostico = s.diag_manual
elif estado_global == "Verde":
    diagnostico = "Proyecto alineado al plan: los 7 indicadores se mantienen dentro del rango de tolerancia."
elif estado_global == "Ámbar":
    avance = "cercano al plan" if spi >= 0.90 else "por debajo del plan"
    diagnostico = f"Avance {avance}, con alertas en {unir(ambar)}. Se activa PAC para el próximo Sprint."
else:
    diagnostico = f"Desviación crítica en {unir(rojos)}. Requiere escalamiento al Sponsor en 48–72 h."

# ---------------------------------------------------------------------------
# Estilos
# ---------------------------------------------------------------------------
st.markdown(
    """
<style>
.block-container {padding-top: 2rem; padding-bottom: 1rem;}
.op-title {font-size: 2rem !important; font-weight: 700; line-height: 1.2;}
.op-sub {opacity: .65; margin-top: .25rem;}
.op-label {font-size: .8rem; opacity: .65;}
.op-status {display:flex; align-items:center; gap:.75rem;}
.op-status .big-dot {width: 28px; height: 28px; border-radius: 50%; flex-shrink: 0;}
.op-status .val {font-size: 1.5rem; font-weight: 700; line-height: 1.1;}
.op-h {font-size: 1.15rem; font-weight: 600; margin-bottom: .75rem;}
.tiles {display:grid; gap:.6rem;}
.grid-avance {grid-template-columns:repeat(2,minmax(0,1fr));}
.grid-kpi {grid-template-columns:repeat(7,minmax(0,1fr)); gap:.45rem;}
.grid-kpi .tile {padding:.6rem .5rem;}
@media (max-width: 1100px) {.grid-kpi {grid-template-columns:repeat(4,minmax(0,1fr));}}
@media (max-width: 640px) {.grid-kpi, .grid-avance {grid-template-columns:repeat(2,minmax(0,1fr));}}
.tile {border:1px solid rgba(250,250,250,.12); border-radius:.6rem; padding:.7rem .7rem;
       background: rgba(255,255,255,.025);}
.tile .lbl {font-size:.85rem; opacity:.75;}
.tile .num {font-size:1.45rem; font-weight:700; margin:.15rem 0 .35rem; white-space:nowrap;}
.tile .meta {font-size:.72rem; opacity:.5; margin-top:.35rem;}
.tile-icon {display:flex; gap:.6rem; align-items:center;}
.tile-icon .ico {width:36px; height:36px; border-radius:50%; display:flex; align-items:center;
                 justify-content:center; font-size:1.25rem; flex-shrink:0;}
.badge {display:inline-flex; align-items:center; gap:.3rem; padding:.15rem .5rem; border-radius:999px;
        font-size:.75rem; white-space:nowrap; font-weight:600;}
.badge .dot {width:9px; height:9px; border-radius:50%;}
.subrow {display:flex; flex-wrap:wrap; gap:1.25rem; font-size:.85rem; opacity:.8; margin-top:.75rem;}
.item {display:flex; gap:.8rem; align-items:flex-start; padding:.8rem 0;
       border-top:1px solid rgba(250,250,250,.1);}
.item:first-of-type {border-top:none;}
.item .ico {width:34px; height:34px; border-radius:50%; display:flex; align-items:center;
            justify-content:center; font-weight:700; flex-shrink:0;}
.item .body {flex:1; min-width:0;}
.item .t {font-weight:600; font-size:.95rem;}
.item .d {font-size:.85rem; opacity:.65;}
.item .side {font-size:.85rem; opacity:.75; white-space:nowrap;}
.empty {opacity:.5; font-size:.9rem; padding:.5rem 0;}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Bloque 1 · Estado general
# ---------------------------------------------------------------------------
with st.container(border=True):
    c1, c2, c3, c4 = st.columns([3.2, 1.2, 3.2, 1.3], vertical_alignment="center")
    c1.markdown(
        f'<div class="op-title">{s.proyecto}</div>'
        f'<div class="op-sub">{s.po} · Sprint {s.sprint} · {fmt_fecha(s.fecha)} · {s.fase}</div>',
        unsafe_allow_html=True,
    )
    c2.markdown(
        f'<div class="op-status"><div class="big-dot" style="background:{COLOR_ESTADO[estado_global]}"></div>'
        f'<div><div class="op-label">Estado general</div><div class="val">{estado_global}</div></div></div>',
        unsafe_allow_html=True,
    )
    c3.markdown(
        f'<div style="font-weight:600">Diagnóstico ejecutivo</div><div style="opacity:.75">{diagnostico}</div>',
        unsafe_allow_html=True,
    )
    ahora = datetime.now()
    c4.markdown(
        f'<div style="text-align:right"><div class="op-label">Última actualización</div>'
        f'<div style="opacity:.8">{fmt_fecha(ahora.date())} · {ahora:%H:%M}</div></div>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Bloque 2 · Avance vs Plan  |  Bloque 3 · Indicadores
# ---------------------------------------------------------------------------
izq, der = st.columns([0.85, 1.4])

with izq, st.container(border=True, height=330):
    st.markdown('<div class="op-h">Avance vs Plan</div>', unsafe_allow_html=True)
    tiles = [
        ("🎯", AZUL, "Planificado", f"{s.plan}%"),
        ("📈", AZUL, "Real", f"{s.real}%"),
        ("💰", VERDE, "Presupuesto BAC", fmt_dinero(bac)),
        ("🧾", AMBAR, "Costo AC", fmt_dinero(ac)),
    ]
    html = '<div class="tiles grid-avance">'
    for ico, col, lbl, val in tiles:
        html += (
            f'<div class="tile tile-icon"><div class="ico" style="background:{col}22">{ico}</div>'
            f'<div><div class="lbl">{lbl}</div><div class="num" style="margin:0">{val}</div></div></div>'
        )
    html += "</div>"
    hito_color = VERDE if s.hito_estado == "Cumplido" else ROJO
    html += (
        f'<div class="subrow"><span>PV <b>{fmt_dinero(pv)}</b></span><span>EV <b>{fmt_dinero(ev)}</b></span>'
        f'<span>Hito crítico: <b>{s.hito}</b> {badge(s.hito_estado, hito_color)}</span></div>'
    )
    st.markdown(html, unsafe_allow_html=True)

with der, st.container(border=True, height=330):
    st.markdown('<div class="op-h">Indicadores de desempeño</div>', unsafe_allow_html=True)
    html = '<div class="tiles grid-kpi">'
    for sigla, val, estado, _, meta in kpis:
        html += (
            f'<div class="tile"><div class="lbl">{sigla}</div><div class="num">{val}</div>'
            f'{badge(estado)}<div class="meta">Meta {meta}</div></div>'
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Bloque 4 · Curva S  |  Bloque 5 · Alertas  |  Bloque 6 · Decisiones
# ---------------------------------------------------------------------------
g, a, d = st.columns([1.45, 1, 1])
ALTO = 470

with g, st.container(border=True, height=ALTO):
    st.markdown('<div class="op-h">Curva S · Valor ganado</div>', unsafe_allow_html=True)

    n = s.sprint
    xs = list(range(n + 1))
    base_n = s_shape(n)
    pv_s = [pv * s_shape(i) / base_n for i in xs]
    # SPI y CPI se van alejando gradualmente de 1 hasta su valor actual
    ev_s = [p * (1 + (ev / pv - 1) * (i / n)) for i, p in zip(xs, pv_s)]
    ac_s = [e / (1 + ((ev / ac if ac else 1) - 1) * (i / n)) if e else 0 for i, e in zip(xs, ev_s)]
    etiquetas = ["Inicio"] + [f"S{i}" for i in xs[1:]]

    fig = go.Figure()
    if s.linea_base and n < TOTAL_SPRINTS:
        xb = list(range(n, TOTAL_SPRINTS + 1))
        rango = s_shape(TOTAL_SPRINTS) - base_n
        pv_b = [pv + (bac - pv) * (s_shape(i) - base_n) / rango for i in xb]
        fig.add_trace(go.Scatter(
            x=xb, y=[v * 1000 for v in pv_b], name="PV línea base", mode="lines",
            line=dict(color=AZUL, dash="dot", width=2), opacity=0.6,
            hovertemplate="S%{x}: $%{y:,.0f}<extra>PV línea base</extra>",
        ))
        fig.add_vline(x=n, line=dict(color="rgba(250,250,250,.35)", dash="dash"))
        etiquetas += [f"S{i}" for i in xb[1:]]

    for nombre, ys, color, fill in [
        ("PV (Planificado)", pv_s, AZUL, None),
        ("EV (Valor ganado)", ev_s, VERDE, "tozeroy"),
        ("AC (Costo real)", ac_s, ROJO, None),
    ]:
        fig.add_trace(go.Scatter(
            x=xs, y=[v * 1000 for v in ys], name=nombre, mode="lines+markers",
            line=dict(color=color, width=2.5), marker=dict(size=7), fill=fill,
            fillcolor="rgba(33,195,84,0.07)",
            hovertemplate="%{y:$,.0f}<extra>" + nombre + "</extra>",
        ))
    fig.update_layout(
        height=360,
        margin=dict(l=0, r=10, t=10, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(tickmode="array", tickvals=list(range(len(etiquetas))), ticktext=etiquetas, showgrid=False),
        yaxis=dict(tickprefix="$", tickformat="~s", gridcolor="rgba(250,250,250,.08)", rangemode="tozero"),
    )
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    st.caption("Vista ilustrativa de la evolución acumulada por Sprint.")


def lista_html(items: list[str]) -> str:
    return "".join(items) if items else '<div class="empty">Sin elementos registrados.</div>'


alertas = alertas_df.dropna(subset=["Alerta"]).head(3)
with a, st.container(border=True, height=ALTO):
    st.markdown(f'<div class="op-h">Alertas y puntos de atención · {len(alertas)}</div>', unsafe_allow_html=True)
    items = []
    for _, r in alertas.iterrows():
        pr = r.get("Prioridad") or "Media"
        col = COLOR_PRIORIDAD.get(pr, AMBAR)
        ico = "!" if pr == "Alta" else "⚠"
        items.append(
            f'<div class="item"><div class="ico" style="background:{col}22;color:{col}">{ico}</div>'
            f'<div class="body"><div class="t">{r["Alerta"]}</div><div class="d">{r.get("Detalle") or ""}</div></div>'
            f'<span class="badge" style="color:{col};background:{col}22">{pr}</span></div>'
        )
    st.markdown(lista_html(items), unsafe_allow_html=True)

decisiones = decisiones_df.dropna(subset=["Decisión"]).head(3)
with d, st.container(border=True, height=ALTO):
    st.markdown(f'<div class="op-h">Próximas decisiones · {len(decisiones)}</div>', unsafe_allow_html=True)
    items = []
    for i, (_, r) in enumerate(decisiones.iterrows(), start=1):
        f = r.get("Fecha")
        fecha_txt = fmt_fecha(pd.to_datetime(f).date()) if pd.notna(f) else "Sin fecha"
        items.append(
            f'<div class="item"><div class="ico" style="background:{AZUL}22;color:{AZUL}">{i}</div>'
            f'<div class="body"><div class="t">{r["Decisión"]}</div><div class="d">{r.get("Responsable") or ""}</div></div>'
            f'<div class="side">{fecha_txt}</div></div>'
        )
    st.markdown(lista_html(items), unsafe_allow_html=True)

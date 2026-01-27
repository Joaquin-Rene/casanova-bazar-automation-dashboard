import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import unicodedata

# -----------------------------------------------------------------------------
# CONFIG
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CasaNova Bazar | Editorial Dashboard (Light v3)",
    layout="wide",
)

# -----------------------------------------------------------------------------
# Editorial Luxury (Light) CSS — más grande, limpio y legible
# -----------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&family=Montserrat:wght@300;400;500;600&display=swap');

:root{
  --ink: #1F1C1A;
  --cream: #F5F0E8;
  --paper: #FFFFFF;
  --accent: #9B3E2A;   /* ladrillo más oscuro */
  --accent2: #D4C4B0;
}

/* Base */
html, body, [class*="css"]  {
  font-family: 'Montserrat', system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
  font-size: 18.5px;
  color: var(--ink);
}
h1, h2, h3, h4 {
  font-family: 'Playfair Display', Georgia, 'Times New Roman', serif;
  letter-spacing: 0.2px;
  color: var(--ink);
}
h2 { font-size: 2.10rem; }
h3 { font-size: 1.55rem; }

/* Layout spacing */
.block-container {
  padding-top: 1.25rem;
  padding-bottom: 2.5rem;
  max-width: 1600px;
}

/* Hide footer */
footer {visibility: hidden;}

/* Sidebar */
section[data-testid="stSidebar"] {
  border-right: 1px solid rgba(31,28,26,0.10);
}
section[data-testid="stSidebar"] .block-container {
  padding-top: 1.15rem;
}

/* KPI cards */
div[data-testid="stMetric"] {
  background: rgba(255,255,255,0.97);
  border: 1px solid rgba(31,28,26,0.10);
  box-shadow: 0 14px 42px rgba(0,0,0,0.08);
  padding: 16px 16px 12px 16px;
  border-radius: 18px;
}
div[data-testid="stMetric"] label {
  font-size: 0.88rem;
  letter-spacing: 0.9px;
  text-transform: uppercase;
  opacity: 0.78;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
  font-size: 2.15rem;
}

/* Pills (multiselect tags) */
span[data-baseweb="tag"] {
  background-color: rgba(212,196,176,0.55) !important;
  border: 1px solid rgba(31,28,26,0.16) !important;
}
span[data-baseweb="tag"] * { color: var(--ink) !important; }

/* Tables */
div[data-testid="stDataFrame"] {
  border: 1px solid rgba(31,28,26,0.10);
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 14px 42px rgba(0,0,0,0.08);
}

/* Section divider */
.hr {
  height: 1px;
  background: rgba(31,28,26,0.12);
  margin: 22px 0;
}
.caption { opacity: 0.85; }

/* Tabs */
button[role="tab"] { font-size: 1.02rem; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# GOOGLE SHEETS SETTINGS
# -----------------------------------------------------------------------------
SHEET_ID = "1klKOjOawuBF8lBAFUwg3b6WjZ1fjuXUld2_xtbNjgTQ"
GID_VENTAS = "0"           # ventas_bazar
GID_RESUMEN = "281676852"  # resumen_diario

# -----------------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------------
INK = "#1F1C1A"
ACCENT = "#9B3E2A"   # ladrillo más contrastado
GRID = "rgba(31,28,26,0.12)"
AXIS_LINE = "rgba(31,28,26,0.25)"
PLOT_BG = "rgba(255,255,255,0.70)"   # “papel” detrás del gráfico

def strip_accents(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [strip_accents(c).strip().lower().replace(" ", "_") for c in df.columns]
    return df

def to_numeric_series(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.astype(str).str.replace(",", ".", regex=False).str.strip(), errors="coerce")

@st.cache_data(ttl=300)
def load_sheet_csv(sheet_id: str, gid: str) -> pd.DataFrame:
    url1 = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    url2 = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"
    try:
        return pd.read_csv(url1)
    except Exception:
        return pd.read_csv(url2)

def money_fmt(x: float) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    return f"${x:,.0f}".replace(",", ".")

def pct_fmt(x: float) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    return f"{x*100:.1f}%"

def plotly_editorial(fig, title=None, height=460):
    """Estilo editorial claro + máximo contraste para ejes/labels."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=PLOT_BG,
        font=dict(color=INK, family="Montserrat", size=14),
        margin=dict(l=18, r=18, t=70, b=30),
        height=height,
        title=dict(
            text=title or "",
            x=0.01,
            xanchor="left",
            font=dict(family="Playfair Display", size=20, color=INK),
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(
        gridcolor=GRID,
        zerolinecolor=GRID,
        tickfont=dict(color=INK, size=14),
        title_font=dict(color=INK, size=14),
        showline=True,
        linewidth=1,
        linecolor=AXIS_LINE,
    )
    fig.update_yaxes(
        gridcolor=GRID,
        zerolinecolor=GRID,
        tickfont=dict(color=INK, size=14),
        title_font=dict(color=INK, size=14),
        showline=True,
        linewidth=1,
        linecolor=AXIS_LINE,
    )
    return fig

def style_bars(fig, opacity=0.95):
    """Fuerza color y bordes (evita barras 'lavadas' sobre fondo claro)."""
    fig.update_traces(
        marker=dict(
            color=ACCENT,
            opacity=opacity,
            line=dict(width=1, color="rgba(31,28,26,0.18)")
        )
    )
    return fig

def style_hist(fig, opacity=0.90):
    fig.update_traces(
        marker=dict(
            color=ACCENT,
            opacity=opacity,
            line=dict(width=1, color="rgba(31,28,26,0.18)")
        )
    )
    return fig

def style_line(fig):
    fig.update_traces(line=dict(width=4, color=ACCENT), marker=dict(size=8, color=ACCENT))
    return fig

# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
st.sidebar.markdown("### Controles")
if st.sidebar.button("🔄 Actualizar datos"):
    st.cache_data.clear()
    st.rerun()

use_resumen = st.sidebar.toggle("Usar resumen_diario para tendencias", value=True)

with st.sidebar.expander("📌 Cómo leer este dashboard", expanded=False):
    st.markdown("""
- **Overview**: KPIs, tendencia y alertas automáticas.
- **Comercial**: canal/categoría/producto que explica ventas.
- **Operación**: tiempos de entrega, cancelaciones, reseñas.
- **Datos**: tabla filtrada + descarga CSV.
""")

# -----------------------------------------------------------------------------
# LOAD DATA
# -----------------------------------------------------------------------------
try:
    ventas_raw = load_sheet_csv(SHEET_ID, GID_VENTAS)
    resumen_raw = load_sheet_csv(SHEET_ID, GID_RESUMEN)
except Exception as e:
    st.error("No pude leer Google Sheets. Revisá permisos: “Cualquier persona con el enlace → Lector”.")
    st.exception(e)
    st.stop()

ventas = normalize_columns(ventas_raw)
resumen = normalize_columns(resumen_raw)

# Fechas
if "fecha_pedido" in ventas.columns:
    ventas["fecha_pedido"] = pd.to_datetime(ventas["fecha_pedido"], errors="coerce", dayfirst=True)
if "fecha_analizada" in resumen.columns:
    resumen["fecha_analizada"] = pd.to_datetime(resumen["fecha_analizada"], errors="coerce", dayfirst=True)

# Numéricos ventas
for col in ["unidades", "precio_unitario", "descuento_pct", "costo_envio", "dias_entrega", "resena", "reseña", "importe_total"]:
    if col in ventas.columns:
        ventas[col] = to_numeric_series(ventas[col])

if "reseña" in ventas.columns and "resena" not in ventas.columns:
    ventas["resena"] = ventas["reseña"]

# Ventas netas por fila
if "importe_total" in ventas.columns and ventas["importe_total"].notna().any():
    ventas["ventas_netas"] = ventas["importe_total"]
else:
    ventas["ventas_netas"] = (
        (ventas.get("unidades", 0).fillna(0) * ventas.get("precio_unitario", 0).fillna(0))
        * (1 - ventas.get("descuento_pct", 0).fillna(0) / 100)
    )

# Numéricos resumen
for col in ["ventas_netas_dia", "ticket_promedio_dia", "pct_cancelados_dia", "entrega_promedio_dias", "rating_promedio"]:
    if col in resumen.columns:
        resumen[col] = to_numeric_series(resumen[col])

# Compat nombres alternativos
if "canal_superior" in resumen.columns and "canal_top" not in resumen.columns:
    resumen["canal_top"] = resumen["canal_superior"]
if "categoria_superior" in resumen.columns and "categoria_top" not in resumen.columns:
    resumen["categoria_top"] = resumen["categoria_superior"]

# -----------------------------------------------------------------------------
# FILTERS
# -----------------------------------------------------------------------------
ventas = ventas.dropna(subset=["fecha_pedido"])
if ventas.empty:
    st.error("No hay filas con fecha_pedido válida en ventas_bazar.")
    st.stop()

min_date = ventas["fecha_pedido"].min().date()
max_date = ventas["fecha_pedido"].max().date()

st.sidebar.markdown("### Rango de fechas")
date_range = st.sidebar.date_input(" ", (min_date, max_date))
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

df = ventas[(ventas["fecha_pedido"].dt.date >= start_date) & (ventas["fecha_pedido"].dt.date <= end_date)].copy()

def multiselect_filter(col: str, label: str):
    global df
    if col in df.columns:
        opts = sorted([x for x in df[col].dropna().unique()])
        selected = st.sidebar.multiselect(label, opts, default=opts)
        df = df[df[col].isin(selected)]

st.sidebar.markdown("### Filtros")
multiselect_filter("canal", "Canal")
multiselect_filter("categoria", "Categoría")
multiselect_filter("provincia_envio", "Provincia")
multiselect_filter("estado_pedido", "Estado")

# -----------------------------------------------------------------------------
# KPI CALCS
# -----------------------------------------------------------------------------
total_ventas = float(df["ventas_netas"].sum())
pedidos = int(df["id_pedido"].nunique()) if "id_pedido" in df.columns else int(len(df))
ticket = float(total_ventas / pedidos) if pedidos else 0

cancelados = int((df["estado_pedido"].astype(str).str.lower() == "cancelado").sum()) if "estado_pedido" in df.columns else 0
pct_cancel = (cancelados / pedidos) if pedidos else 0

entrega_avg = 0.0
if "dias_entrega" in df.columns:
    aux = df.loc[df["dias_entrega"] > 0, "dias_entrega"]
    entrega_avg = float(aux.mean()) if len(aux) else 0.0

rating_avg = 0.0
if "resena" in df.columns:
    aux = df.loc[df["resena"] > 0, "resena"]
    rating_avg = float(aux.mean()) if len(aux) else 0.0

# Highlights
top_channel = df.groupby("canal")["ventas_netas"].sum().sort_values(ascending=False).head(1).index[0] if "canal" in df.columns and len(df) else "—"
top_category = df.groupby("categoria")["ventas_netas"].sum().sort_values(ascending=False).head(1).index[0] if "categoria" in df.columns and len(df) else "—"
top_product = df.groupby("producto")["ventas_netas"].sum().sort_values(ascending=False).head(1).index[0] if "producto" in df.columns and len(df) else "—"
last_date = df["fecha_pedido"].max().date() if len(df) else None

# -----------------------------------------------------------------------------
# HEADER
# -----------------------------------------------------------------------------
st.markdown("## CasaNova Bazar")
st.markdown("### Dashboard Ejecutivo — visión editorial del negocio")
st.caption("Fuente: Google Sheets + automatización con n8n (dataset ficticio).")

k1, k2, k3, k4, k5, k6 = st.columns([1.2, 0.9, 1.1, 0.95, 1.0, 0.9])
k1.metric("Ventas netas", money_fmt(total_ventas))
k2.metric("Pedidos", f"{pedidos}")
k3.metric("Ticket promedio", money_fmt(ticket))
k4.metric("% Cancelados", pct_fmt(pct_cancel))
k5.metric("Entrega prom.", f"{entrega_avg:.1f} días" if entrega_avg else "—")
k6.metric("Rating prom.", f"{rating_avg:.2f}" if rating_avg else "—")

st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TABS
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🛒 Comercial", "🚚 Operación", "🧾 Datos"])

# ---------------------------
# TAB 1: OVERVIEW
# ---------------------------
with tab1:
    left, right = st.columns([2.2, 1.0], gap="large")

    with left:
        st.subheader("Tendencias de ventas")
        st.caption("Identifica picos/caídas. Luego cruza con canal/categoría/productos en Comercial.")

        if use_resumen and "fecha_analizada" in resumen.columns and "ventas_netas_dia" in resumen.columns:
            r = resumen.dropna(subset=["fecha_analizada"]).copy()
            r = r[(r["fecha_analizada"].dt.date >= start_date) & (r["fecha_analizada"].dt.date <= end_date)]
            r = r.sort_values("fecha_analizada")
            trend_df = r.rename(columns={"fecha_analizada": "fecha", "ventas_netas_dia": "ventas_netas"})
            note = "Tendencia basada en KPIs pre-calculados por n8n (resumen_diario)."
        else:
            daily = df.groupby(df["fecha_pedido"].dt.date)["ventas_netas"].sum().reset_index()
            daily.columns = ["fecha", "ventas_netas"]
            trend_df = daily.sort_values("fecha")
            note = "Tendencia recalculada desde ventas_bazar (en tiempo real)."

        fig = px.line(trend_df, x="fecha", y="ventas_netas", markers=True)
        fig = style_line(fig)
        fig = plotly_editorial(fig, title="Ventas netas por día", height=540)
        st.plotly_chart(fig, use_container_width=True)
        st.caption(note)

    with right:
        st.subheader("Highlights")
        st.caption("Resumen editorial: quién tracciona ventas y qué mirar primero.")
        st.markdown(f"""
- **Última fecha con datos:** `{last_date}`
- **Canal líder:** **{top_channel}**
- **Categoría líder:** **{top_category}**
- **Producto líder:** *{top_product}*
""")

        st.markdown("#### ⚠️ Alertas")
        if "observaciones" in resumen.columns and "fecha_analizada" in resumen.columns:
            alerts = resumen.dropna(subset=["fecha_analizada"]).copy()
            alerts = alerts[(alerts["fecha_analizada"].dt.date >= start_date) & (alerts["fecha_analizada"].dt.date <= end_date)]
            alerts = alerts[alerts["observaciones"].astype(str).str.strip().str.upper() != "OK"]
            if len(alerts):
                st.dataframe(
                    alerts[["fecha_analizada", "observaciones"]].sort_values("fecha_analizada", ascending=False),
                    use_container_width=True,
                    hide_index=True
                )
                st.caption("Se generan automáticamente en n8n (reglas sobre entrega, cancelación y rating).")
            else:
                st.success("Sin alertas en el rango seleccionado.")
        else:
            st.info("No hay columna observaciones en resumen_diario.")

    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

    st.subheader("KPIs diarios (calidad operativa)")
    st.caption("Ticket, cancelaciones y entrega: señales tempranas de fricción en la operación.")

    if use_resumen and "fecha_analizada" in resumen.columns:
        r2 = resumen.dropna(subset=["fecha_analizada"]).copy()
        r2 = r2[(r2["fecha_analizada"].dt.date >= start_date) & (r2["fecha_analizada"].dt.date <= end_date)]
        r2 = r2.sort_values("fecha_analizada")

        cA, cB, cC = st.columns(3, gap="large")

        if "ticket_promedio_dia" in r2.columns:
            with cA:
                fig = px.line(r2, x="fecha_analizada", y="ticket_promedio_dia", markers=True)
                fig = style_line(fig)
                fig = plotly_editorial(fig, title="Ticket promedio", height=400)
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Si sube: mix más caro o más unidades por pedido.")

        if "pct_cancelados_dia" in r2.columns:
            with cB:
                fig = px.line(r2, x="fecha_analizada", y="pct_cancelados_dia", markers=True)
                fig = style_line(fig)
                fig = plotly_editorial(fig, title="% Cancelaciones", height=400)
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Si sube: revisar pagos, stock o promesas de entrega.")

        if "entrega_promedio_dias" in r2.columns:
            with cC:
                fig = px.line(r2, x="fecha_analizada", y="entrega_promedio_dias", markers=True)
                fig = style_line(fig)
                fig = plotly_editorial(fig, title="Entrega promedio (días)", height=400)
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Cuando sube, suele bajar satisfacción y recompra.")

# ---------------------------
# TAB 2: COMERCIAL
# ---------------------------
with tab2:
    st.subheader("Distribución por canal y categoría")
    st.caption("Objetivo: entender dónde se genera la demanda y qué mix de productos explica las ventas.")

    a, b = st.columns(2, gap="large")

    with a:
        if "canal" in df.columns:
            by_channel = df.groupby("canal")["ventas_netas"].sum().sort_values(ascending=False).reset_index()
            fig = px.bar(by_channel, x="canal", y="ventas_netas")
            fig = style_bars(fig, opacity=0.96)
            fig = plotly_editorial(fig, title="Ventas por canal", height=520)
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Lectura: canales con mayor facturación. Cruza con cancelaciones en Operación.")
        else:
            st.info("No hay columna 'canal'.")

    with b:
        if "categoria" in df.columns:
            by_cat = df.groupby("categoria")["ventas_netas"].sum().sort_values(ascending=False).reset_index()
            fig = px.bar(by_cat, x="categoria", y="ventas_netas")
            fig = style_bars(fig, opacity=0.96)
            fig = plotly_editorial(fig, title="Ventas por categoría", height=520)
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Lectura: mix de ventas. Ideal para decidir stock y campañas.")
        else:
            st.info("No hay columna 'categoria'.")

    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

    st.subheader("Top productos")
    st.caption("Top por ventas netas en el rango filtrado. Útil para priorizar reposición y creatividades.")
    if "producto" in df.columns:
        by_prod = df.groupby("producto")["ventas_netas"].sum().sort_values(ascending=False).head(12).reset_index()
        fig = px.bar(by_prod, x="ventas_netas", y="producto", orientation="h")
        fig = style_bars(fig, opacity=0.96)
        fig = plotly_editorial(fig, title="Top 12 productos (ventas netas)", height=600)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Día de la semana")
    st.caption("Planificación de publicaciones y promos: qué días convierten mejor.")
    df["dia_semana"] = df["fecha_pedido"].dt.day_name()
    by_dow = df.groupby("dia_semana")["ventas_netas"].sum().reset_index()
    order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    by_dow["dia_semana"] = pd.Categorical(by_dow["dia_semana"], categories=order, ordered=True)
    by_dow = by_dow.sort_values("dia_semana")

    fig = px.bar(by_dow, x="dia_semana", y="ventas_netas")
    fig = style_bars(fig, opacity=0.94)
    fig = plotly_editorial(fig, title="Ventas por día de la semana", height=460)
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# TAB 3: OPERACIÓN
# ---------------------------
with tab3:
    st.subheader("Logística, cancelaciones y calidad")
    st.caption("Objetivo: detectar fricciones operativas que impactan en reputación y ventas.")

    c1, c2, c3 = st.columns(3, gap="large")

    with c1:
        st.markdown("#### Estado de pedidos")
        if "estado_pedido" in df.columns:
            st.dataframe(
                df["estado_pedido"].value_counts().rename_axis("estado").reset_index(name="conteo"),
                use_container_width=True,
                hide_index=True
            )
            st.caption("Si sube “En tránsito”, revisar logística; si sube “Cancelado”, revisar pagos/stock.")
        else:
            st.info("No hay columna estado_pedido.")

    with c2:
        st.markdown("#### Entrega (días)")
        if "dias_entrega" in df.columns:
            aux = df[df["dias_entrega"] > 0].copy()
            if len(aux):
                fig = px.histogram(aux, x="dias_entrega", nbins=10)
                fig = style_hist(fig, opacity=0.92)   # ← fuerza ladrillo
                fig = plotly_editorial(fig, title="Distribución de días de entrega", height=470)
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Colas largas suelen indicar cuellos en correo o preparación.")
            else:
                st.info("No hay días_entrega > 0 en el rango.")
        else:
            st.info("No hay columna dias_entrega.")

    with c3:
        st.markdown("#### Reseñas")
        if "resena" in df.columns:
            aux = df[df["resena"] > 0].copy()
            if len(aux):
                fig = px.histogram(aux, x="resena", nbins=5)
                fig = style_hist(fig, opacity=0.92)   # ← fuerza ladrillo
                fig = plotly_editorial(fig, title="Distribución de rating", height=470)
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Si cae, revisar calidad, embalaje y tiempos.")
            else:
                st.info("No hay reseñas > 0 en el rango.")
        else:
            st.info("No hay columna resena/reseña.")

    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

    st.subheader("Notas de clientes (Voice of Customer)")
    st.caption("Siguiente nivel: IA para etiquetar feedback (envío, calidad, atención).")
    if "notas_cliente" in df.columns:
        notes = df["notas_cliente"].dropna().astype(str)
        if len(notes):
            st.dataframe(notes.to_frame("notas_cliente"), use_container_width=True, hide_index=True)
        else:
            st.caption("No hay notas en el rango filtrado.")
    else:
        st.caption("No hay columna notas_cliente.")

# ---------------------------
# TAB 4: DATOS
# ---------------------------
with tab4:
    st.subheader("Dataset filtrado")
    st.caption("Vista transaccional para auditoría. Descargá CSV filtrado para análisis externo.")

    cols_show = [c for c in [
        "id_pedido","fecha_pedido","canal","sku","producto","categoria","subcategoria",
        "unidades","precio_unitario","descuento_pct","ventas_netas","costo_envio",
        "metodo_pago","provincia_envio","ciudad_envio","tipo_cliente","estado_pedido",
        "dias_entrega","resena","notas_cliente"
    ] if c in df.columns]

    st.dataframe(df[cols_show].sort_values("fecha_pedido", ascending=False), use_container_width=True, hide_index=True)

    st.download_button(
        "⬇️ Descargar CSV (filtrado)",
        data=df[cols_show].to_csv(index=False).encode("utf-8"),
        file_name="casanova_ventas_filtrado.csv",
        mime="text/csv"
    )

st.caption("Tip: si n8n actualiza Google Sheets, tocá “Actualizar datos” para refrescar el dashboard.")

import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from pathlib import Path

# ── Data ──────────────────────────────────────────────────────────────────────
DB = Path(__file__).parent.parent / "databases"
na = ["\\N"]

races        = pd.read_csv(DB / "races.csv",        na_values=na)
results      = pd.read_csv(DB / "results.csv",      na_values=na)
drivers      = pd.read_csv(DB / "drivers.csv",      na_values=na)
constructors = pd.read_csv(DB / "constructors.csv", na_values=na)

races = races[races["year"] >= 1990]

df = results.merge(races, on="raceId")
df = df.merge(drivers, on="driverId")
df = df.merge(constructors, on="constructorId")

cols_drop = [
    "fp1_date", "fp1_time", "fp2_date", "fp2_time", "fp3_date", "fp3_time",
    "quali_date", "quali_time", "sprint_date", "sprint_time",
    "url_x", "url_y", "url", "number_y", "time_y",
]
df = df.drop(columns=[c for c in cols_drop if c in df.columns])
df = df.rename(columns={"number_x": "number", "name_x": "race_name", "name_y": "constructor_name"})

df["code"]          = df["code"].fillna(df["surname"].str[:3].str.upper())
df["date"]          = pd.to_datetime(df["date"],  errors="coerce")
df["dob"]           = pd.to_datetime(df["dob"],   errors="coerce")
df["full_name"]     = (df["forename"].astype(str) + " " + df["surname"].astype(str)).str.strip()
df["is_winner"]     = df["position"] == 1
df["is_podium"]     = df["position"].between(1, 3)
df["dnf"]           = df["position"].isna()
df["decade"]        = (df["year"] // 10 * 10).astype(int).astype(str) + "s"
df["age_at_race"]   = ((df["date"] - df["dob"]).dt.days / 365.25).round().astype("Int64")
df["nationality_x"] = df["nationality_x"].astype(str).str.strip().str.title()

# ── KPIs ──────────────────────────────────────────────────────────────────────
n_temporadas      = df["year"].nunique()
n_corridas        = df["raceId"].nunique()
n_pilotos         = df["driverId"].nunique()
n_equipes         = df["constructorId"].nunique()
piloto_recordista = df[df["is_winner"]]["full_name"].value_counts().idxmax()
equipe_recordista = str(df[df["is_winner"]]["constructor_name"].value_counts().idxmax())
periodo           = f"{df['year'].min()}–{df['year'].max()}"

# ── Tokens ────────────────────────────────────────────────────────────────────
C_RED    = "#E8002D"
C_DARK   = "#0D0D13"
C_WHITE  = "#FFFFFF"
C_BG     = "#F4F5F7"
C_TEXT   = "#111827"
C_MUTED  = "#6B7280"
C_BORDER = "#E5E7EB"
FONT     = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"

CUSTOM_CSS = """
* { box-sizing: border-box; }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.15); border-radius: 10px; }

.tab-parent {
    background: transparent !important;
    border-bottom: 1px solid #E5E7EB !important;
    padding: 0 16px !important;
    display: flex !important;
}
.tab {
    font-family: 'Inter', -apple-system, sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #9CA3AF !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    background: #FFFFFF !important;
    padding: 13px 20px !important;
    cursor: pointer !important;
    transition: color 0.18s !important;
    letter-spacing: 0.1px !important;
}
.tab:hover { color: #374151 !important; }
.tab--selected {
    color: #E8002D !important;
    border-bottom: 2px solid #E8002D !important;
    font-weight: 600 !important;
    background: #FFFFFF !important;
}

.rc-slider-handle,
.rc-slider-handle:hover,
.rc-slider-handle:active,
.rc-slider-handle-dragging {
    border-color: #E8002D !important;
    background-color: #E8002D !important;
    box-shadow: 0 0 0 5px rgba(232,0,45,0.1) !important;
    opacity: 1 !important;
}
.rc-slider-track { background-color: #E8002D !important; height: 3px !important; }
.rc-slider-rail  { background-color: #E5E7EB !important; height: 3px !important; }

.Select--multi .Select-value {
    background-color: rgba(232,0,45,0.07) !important;
    border-color: rgba(232,0,45,0.2) !important;
    border-radius: 4px !important;
    color: #B50024 !important;
    font-size: 11px !important;
}
.Select--multi .Select-value-icon {
    border-right-color: rgba(232,0,45,0.2) !important;
    color: #B50024 !important;
}
.Select--multi .Select-value-icon:hover {
    background: rgba(232,0,45,0.12) !important;
}
"""

# ── Helpers ───────────────────────────────────────────────────────────────────
def apply_chart_style(fig):
    fig.update_layout(
        font_family=FONT,
        font_color=C_TEXT,
        title_font=dict(size=13, color="#1F2937", family=FONT),
        title_x=0,
        plot_bgcolor=C_WHITE,
        paper_bgcolor=C_WHITE,
        margin=dict(l=16, r=16, t=48, b=16),
        legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0,
                    font=dict(size=11, color=C_MUTED)),
    )
    fig.update_xaxes(gridcolor="#F3F4F6", linecolor=C_BORDER, zeroline=False,
                     tickfont=dict(color=C_MUTED, size=10),
                     title_font=dict(color=C_MUTED, size=11))
    fig.update_yaxes(gridcolor="#F3F4F6", linecolor=C_BORDER, zeroline=False,
                     tickfont=dict(color=C_MUTED, size=10),
                     title_font=dict(color=C_MUTED, size=11))
    return fig

def chart_card(child, style=None):
    base = {
        "backgroundColor": C_WHITE,
        "borderRadius": "14px",
        "boxShadow": "0 1px 3px rgba(0,0,0,0.05), 0 4px 16px rgba(0,0,0,0.06)",
        "overflow": "hidden",
        "margin": "8px",
        "border": f"1px solid {C_BORDER}",
    }
    if style:
        base.update(style)
    return html.Div(child, style=base)

def card_kpi(titulo, valor):
    v         = str(valor)
    is_num    = v.replace(",", "").isdigit()
    font_size = "26px" if len(v) <= 10 else "14px"
    v_color   = C_RED if is_num else "#1F2937"
    return html.Div([
        html.P(titulo, style={
            "margin": "0 0 10px 0", "fontSize": "10px", "color": C_MUTED,
            "letterSpacing": "1px", "textTransform": "uppercase", "fontWeight": "600",
        }),
        html.Div(v, style={
            "color": v_color, "fontWeight": "800",
            "fontSize": font_size, "lineHeight": "1.1",
        }),
    ], style={
        "backgroundColor": C_WHITE,
        "borderRadius": "12px",
        "padding": "20px 16px",
        "textAlign": "center",
        "flex": "1",
        "margin": "0 5px",
        "boxShadow": "0 1px 3px rgba(0,0,0,0.05), 0 2px 8px rgba(0,0,0,0.04)",
        "border": f"1px solid {C_BORDER}",
    })

def insight(texto):
    return html.P(texto, style={
        "fontSize": "12px", "color": "#374151", "margin": "0 0 8px 0",
        "padding": "10px 12px", "backgroundColor": "#FAFAFA",
        "border": f"1px solid {C_BORDER}",
        "borderLeft": f"3px solid {C_RED}",
        "borderRadius": "0 6px 6px 0",
        "lineHeight": "1.55",
    })

def section_label(text):
    return html.P(text, style={
        "margin": "0 0 8px 0", "fontSize": "10px", "color": C_MUTED,
        "fontWeight": "700", "textTransform": "uppercase", "letterSpacing": "0.8px",
    })

# ── Static figures — Dashboard 1 ──────────────────────────────────────────────
top_pilotos = (
    df[df["is_winner"]]
    .groupby("full_name").size()
    .nlargest(10).reset_index(name="vitorias").sort_values("vitorias")
)
fig_pilotos = px.bar(
    top_pilotos, x="vitorias", y="full_name", orientation="h",
    title="Top 10 Pilotos — Vitórias (1990–2024)",
    labels={"vitorias": "Vitórias", "full_name": ""},
    color="vitorias", color_continuous_scale="Blues",
)
fig_pilotos.update_layout(coloraxis_showscale=False)
apply_chart_style(fig_pilotos)

top_equipes_d1 = (
    df[df["is_winner"]]
    .groupby("constructor_name").size()
    .nlargest(10).reset_index(name="vitorias").sort_values("vitorias")
)
fig_equipes = px.bar(
    top_equipes_d1, x="vitorias", y="constructor_name", orientation="h",
    title="Top 10 Equipes — Vitórias (1990–2024)",
    labels={"vitorias": "Vitórias", "constructor_name": ""},
    color="vitorias", color_continuous_scale="Reds",
)
fig_equipes.update_layout(coloraxis_showscale=False)
apply_chart_style(fig_equipes)

top8 = df[df["is_winner"]]["constructor_name"].value_counts().head(8).index.tolist()
vit_decada = (
    df[(df["is_winner"]) & (df["constructor_name"].isin(top8))]
    .groupby(["decade", "constructor_name"]).size()
    .reset_index(name="vitorias").sort_values("decade")
)
fig_decada = px.bar(
    vit_decada, x="decade", y="vitorias", color="constructor_name",
    barmode="group", title="Vitórias por Década — Top 8 Equipes",
    labels={"decade": "Década", "vitorias": "Vitórias", "constructor_name": ""},
)
fig_decada.update_layout(legend_title="")
apply_chart_style(fig_decada)

dnf_ano = df.groupby("year")["dnf"].mean().mul(100).reset_index(name="taxa_dnf")
fig_dnf = px.area(
    dnf_ano, x="year", y="taxa_dnf",
    title="Taxa de Abandono (DNF) por Temporada",
    labels={"year": "Temporada", "taxa_dnf": "DNF (%)"},
    color_discrete_sequence=[C_RED],
)
apply_chart_style(fig_dnf)

# ── Filter options ─────────────────────────────────────────────────────────────
todas_equipes = df[df["is_winner"]]["constructor_name"].value_counts().index.tolist()
top5_default  = todas_equipes[:5]

# ── App ────────────────────────────────────────────────────────────────────────
app = Dash(
    __name__,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"
    ],
)

app.index_string = f"""<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>F1 Analytics</title>
        {{%favicon%}}
        {{%css%}}
        <style>{CUSTOM_CSS}</style>
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>"""

# ── Nav bar ───────────────────────────────────────────────────────────────────
nav_bar = html.Div([
    html.Div([
        html.Span(style={
            "display": "inline-block", "width": "8px", "height": "8px",
            "backgroundColor": C_RED, "borderRadius": "50%", "marginRight": "10px",
        }),
        html.Span("F1", style={
            "color": "#FFFFFF", "fontWeight": "800", "fontSize": "15px", "letterSpacing": "1px",
        }),
        html.Span(" Dashboard", style={
            "color": "rgba(255,255,255,0.4)", "fontWeight": "400",
            "fontSize": "13px", "marginLeft": "2px",
        }),
    ], style={"display": "flex", "alignItems": "center"}),

    html.Div([
        html.Span(periodo,               style={"color": "rgba(255,255,255,0.35)", "fontSize": "11px"}),
        html.Span("  ·  ",              style={"color": "rgba(255,255,255,0.15)", "fontSize": "11px"}),
        html.Span(f"{n_corridas} corridas", style={"color": "rgba(255,255,255,0.35)", "fontSize": "11px"}),
        html.Span("  ·  ",              style={"color": "rgba(255,255,255,0.15)", "fontSize": "11px"}),
        html.Span(f"{n_pilotos} pilotos",  style={"color": "rgba(255,255,255,0.35)", "fontSize": "11px"}),
        html.Span("  ·  ",              style={"color": "rgba(255,255,255,0.15)", "fontSize": "11px"}),
        html.Span(f"{n_equipes} equipes",  style={"color": "rgba(255,255,255,0.35)", "fontSize": "11px"}),
    ], style={"display": "flex", "alignItems": "center"}),
], style={
    "display": "flex",
    "justifyContent": "space-between",
    "alignItems": "center",
    "backgroundColor": C_DARK,
    "padding": "0 24px",
    "height": "44px",
    "fontFamily": FONT,
    "borderBottom": "1px solid rgba(255,255,255,0.05)",
})

# ── Layout constants ──────────────────────────────────────────────────────────
SIDEBAR_STYLE = {
    "flexShrink": 0,
    "flexBasis": "22%",
    "padding": "24px 20px",
    "backgroundColor": C_WHITE,
    "borderRight": f"1px solid {C_BORDER}",
    "boxSizing": "border-box",
}
CONTENT_STYLE = {
    "flex": "1",
    "padding": "8px",
    "backgroundColor": C_BG,
    "boxSizing": "border-box",
    "minWidth": 0,
}
TAB_STYLE    = {"backgroundColor": C_WHITE, "fontFamily": FONT}
TAB_SELECTED = {"backgroundColor": C_WHITE, "fontFamily": FONT}

# ── Dashboard 1 ───────────────────────────────────────────────────────────────
dashboard1 = html.Div([
    html.Div([
        card_kpi("Temporadas",        n_temporadas),
        card_kpi("Corridas",          n_corridas),
        card_kpi("Pilotos",           n_pilotos),
        card_kpi("Equipes",           n_equipes),
        card_kpi("Piloto Recordista", piloto_recordista),
        card_kpi("Equipe Recordista", equipe_recordista),
    ], style={"display": "flex", "padding": "20px 14px 4px 14px", "backgroundColor": C_BG}),

    html.Div([
        chart_card(dcc.Graph(id="d1-pilotos", figure=fig_pilotos), style={"flex": "1"}),
        chart_card(dcc.Graph(id="d1-equipes", figure=fig_equipes), style={"flex": "1"}),
    ], style={"display": "flex", "padding": "0 8px", "backgroundColor": C_BG}),

    html.Div([
        chart_card(dcc.Graph(id="d1-decada", figure=fig_decada), style={"flex": "1"}),
        chart_card(dcc.Graph(id="d1-dnf",    figure=fig_dnf),    style={"flex": "1"}),
    ], style={"display": "flex", "padding": "0 8px 16px 8px", "backgroundColor": C_BG}),
], style={"backgroundColor": C_BG})

# ── Dashboard 2 ───────────────────────────────────────────────────────────────
dashboard2 = html.Div([
    html.Div([
        html.Div([
            html.H3("Filtros", style={
                "margin": "0 0 20px 0", "color": "#1F2937",
                "fontSize": "11px", "fontWeight": "700",
                "letterSpacing": "1.2px", "textTransform": "uppercase",
            }),
            section_label("Período"),
            dcc.RangeSlider(
                id="slider-anos", min=1990, max=2024, step=1, value=[1990, 2024],
                marks={y: {"label": str(y), "style": {"fontSize": "10px", "color": C_MUTED}}
                       for y in range(1990, 2025, 5)},
                tooltip={"placement": "bottom", "always_visible": False},
            ),
            html.Div(style={"height": "18px"}),
            section_label("Equipes"),
            dcc.Dropdown(
                id="dropdown-equipes",
                options=[{"label": eq, "value": eq} for eq in todas_equipes],
                value=top5_default, multi=True,
                placeholder="Selecione equipes...",
                style={"fontSize": "12px", "marginTop": "4px"},
            ),
            html.Hr(style={"margin": "22px 0 18px 0", "borderColor": C_BORDER}),
            html.H4("Achados do período", style={
                "margin": "0 0 14px 0", "color": "#1F2937",
                "fontSize": "11px", "fontWeight": "700",
                "letterSpacing": "1.2px", "textTransform": "uppercase",
            }),
            html.Div(id="d2-achados"),
        ], style=SIDEBAR_STYLE),

        html.Div([
            chart_card(dcc.Graph(id="d2-linha-vitorias")),
            html.Div([
                chart_card(dcc.Graph(id="d2-scatter-grid"), style={"flex": "1"}),
                chart_card(dcc.Graph(id="d2-bar-equipes"),  style={"flex": "1"}),
            ], style={"display": "flex"}),
            html.Div([
                chart_card(dcc.Graph(id="d2-area-dnf"),      style={"flex": "1"}),
                chart_card(dcc.Graph(id="d2-scatter-idade"), style={"flex": "1"}),
            ], style={"display": "flex"}),
        ], style=CONTENT_STYLE),

    ], style={"display": "flex", "minHeight": "80vh"}),
], style={"backgroundColor": C_BG})

# ── Layout ────────────────────────────────────────────────────────────────────
app.layout = html.Div([
    nav_bar,
    dcc.Tabs(
        value="tab-1",
        children=[
            dcc.Tab(label="Visão Geral",           value="tab-1",
                    children=[dashboard1],
                    style=TAB_STYLE, selected_style=TAB_SELECTED),
            dcc.Tab(label="Exploração Interativa", value="tab-2",
                    children=[dashboard2],
                    style=TAB_STYLE, selected_style=TAB_SELECTED),
        ],
        style={"backgroundColor": C_WHITE},
    ),
], style={"fontFamily": FONT, "backgroundColor": C_BG, "minHeight": "100vh"})


# ── Callback ──────────────────────────────────────────────────────────────────
@app.callback(
    [Output("d2-linha-vitorias", "figure"),
     Output("d2-scatter-grid",   "figure"),
     Output("d2-bar-equipes",    "figure"),
     Output("d2-area-dnf",       "figure"),
     Output("d2-scatter-idade",  "figure"),
     Output("d2-achados",        "children")],
    [Input("slider-anos",      "value"),
     Input("dropdown-equipes", "value")],
)
def atualizar_dashboard2(anos, equipes):
    ano_min, ano_max = anos
    equipes = equipes or todas_equipes

    dff    = df[(df["year"] >= ano_min) & (df["year"] <= ano_max)]
    dff_eq = dff[dff["constructor_name"].isin(equipes)]

    vit_ano = (
        dff_eq[dff_eq["is_winner"]]
        .groupby(["year", "constructor_name"]).size()
        .reset_index(name="vitorias")
    )
    fig1 = px.line(
        vit_ano, x="year", y="vitorias", color="constructor_name", markers=True,
        title=f"Vitórias por Temporada — {ano_min}–{ano_max}",
        labels={"year": "Temporada", "vitorias": "Vitórias", "constructor_name": ""},
    )
    fig1.update_layout(legend_title="")
    apply_chart_style(fig1)

    grid_pos = (
        dff_eq[dff_eq["position"].notna()]
        .groupby("grid")
        .agg(media_posicao=("positionOrder", "mean"), corridas=("resultId", "count"))
        .reset_index()
    )
    grid_pos = grid_pos[grid_pos["grid"].between(1, 20) & (grid_pos["corridas"] >= 10)]
    corr_grid = round(grid_pos["grid"].corr(grid_pos["media_posicao"]), 2)
    fig2 = px.scatter(
        grid_pos, x="grid", y="media_posicao", size="corridas",
        title=f"Grid vs Posição Final  ·  r = {corr_grid}",
        labels={"grid": "Grid", "media_posicao": "Posição final média", "corridas": "Corridas"},
        color="media_posicao", color_continuous_scale="RdYlGn_r",
    )
    fig2.update_layout(coloraxis_showscale=False)
    apply_chart_style(fig2)

    vit_eq = (
        dff_eq[dff_eq["is_winner"]]
        .groupby("constructor_name").size()
        .reset_index(name="vitorias").sort_values("vitorias", ascending=False)
    )
    fig3 = px.bar(
        vit_eq, x="constructor_name", y="vitorias",
        title=f"Vitórias por Equipe — {ano_min}–{ano_max}",
        labels={"constructor_name": "", "vitorias": "Vitórias"},
        color="vitorias", color_continuous_scale="Reds",
    )
    fig3.update_layout(coloraxis_showscale=False)
    apply_chart_style(fig3)

    dnf_periodo = dff.groupby("year")["dnf"].mean().mul(100).reset_index(name="taxa_dnf")
    fig4 = px.area(
        dnf_periodo, x="year", y="taxa_dnf",
        title=f"Taxa de Abandono (DNF) — {ano_min}–{ano_max}",
        labels={"year": "Temporada", "taxa_dnf": "DNF (%)"},
        color_discrete_sequence=[C_RED],
    )
    apply_chart_style(fig4)

    idade_pts = (
        dff_eq.dropna(subset=["age_at_race"])
        .groupby("age_at_race")
        .agg(media_pontos=("points", "mean"), corridas=("resultId", "count"))
        .reset_index()
    )
    idade_pts = idade_pts[
        idade_pts["age_at_race"].between(18, 50) & (idade_pts["corridas"] >= 10)
    ]
    corr_idade = round(idade_pts["age_at_race"].corr(idade_pts["media_pontos"]), 2)
    fig5 = px.scatter(
        idade_pts, x="age_at_race", y="media_pontos", size="corridas",
        title=f"Idade vs Pontos Médios  ·  r = {corr_idade}",
        labels={"age_at_race": "Idade", "media_pontos": "Pontos médios", "corridas": "Corridas"},
        color="media_pontos", color_continuous_scale="Blues",
    )
    fig5.update_layout(coloraxis_showscale=False)
    apply_chart_style(fig5)

    lider_eq      = vit_eq.iloc[0] if not vit_eq.empty else None
    dnf_medio     = dnf_periodo["taxa_dnf"].mean() if not dnf_periodo.empty else 0
    dnf_tendencia = "queda" if dnf_periodo["taxa_dnf"].iloc[-1] < dnf_periodo["taxa_dnf"].iloc[0] else "alta"

    achados = [
        insight(f"Líder: {lider_eq['constructor_name']} — {int(lider_eq['vitorias'])} vitórias") if lider_eq is not None else "",
        insight(f"Correlação grid → posição: r = {corr_grid}"),
        insight(f"Correlação idade → pontos: r = {corr_idade}"),
        insight(f"DNF médio: {dnf_medio:.1f}% ({dnf_tendencia} no período)"),
    ]

    return fig1, fig2, fig3, fig4, fig5, achados


if __name__ == "__main__":
    app.run(debug=True)

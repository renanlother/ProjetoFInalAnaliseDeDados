import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from pathlib import Path

# Data
DB = Path(__file__).parent.parent / "databases"
na = ["\\N"]

races = pd.read_csv(DB / "races.csv", na_values=na)
results = pd.read_csv(DB / "results.csv", na_values=na)
drivers = pd.read_csv(DB / "drivers.csv", na_values=na)
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

df["code"] = df["code"].fillna(df["surname"].str[:3].str.upper())
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["dob"] = pd.to_datetime(df["dob"], errors="coerce")
df["full_name"] = (df["forename"].astype(str) + " " + df["surname"].astype(str)).str.strip()
df["is_winner"] = df["position"] == 1
df["is_podium"] = df["position"].between(1, 3)
df["dnf"] = df["position"].isna()
df["decade"] = (df["year"] // 10 * 10).astype(int).astype(str) + "s"
df["age_at_race"] = ((df["date"] - df["dob"]).dt.days / 365.25).round().astype("Int64")
df["nationality_x"] = df["nationality_x"].astype(str).str.strip().str.title()

# KPIs
n_temporadas = df["year"].nunique()
n_corridas = df["raceId"].nunique()
n_pilotos = df["driverId"].nunique()
n_equipes = df["constructorId"].nunique()
piloto_recordista = df[df["is_winner"]]["full_name"].value_counts().idxmax()
equipe_recordista = str(df[df["is_winner"]]["constructor_name"].value_counts().idxmax())
periodo = f"{df['year'].min()}–{df['year'].max()}"

# Tokens
C_RED = "#E8002D"
C_DARK = "#0A0D14"
C_WHITE = "#1A2235"
C_BG = "#111722"
C_TEXT = "#F1F5F9"
C_MUTED = "#94A3B8"
C_BORDER = "#2D3748"
FONT = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
SCALE_QTD = [[0, "#FFD700"], [0.5, "#FF6B35"], [1, "#E8002D"]]

CUSTOM_CSS = """
* { box-sizing: border-box; }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.12); border-radius: 10px; }

.tab-parent {
    background: #111722 !important;
    border-bottom: 1px solid #2D3748 !important;
    padding: 0 8px !important;
    display: flex !important;
}
.tab { cursor: pointer !important; transition: color 0.18s, background 0.18s !important; }
.tab:hover { color: #F1F5F9 !important; background: #1A2235 !important; }

:root {
    --Dash-Fill-Interactive-Strong: #E8002D;
    --Dash-Fill-Interactive-Weak: rgba(232,0,45,0.12);
    --Dash-Fill-Inverse-Strong: #1A2235;
    --Dash-Text-Primary: #F1F5F9;
    --Dash-Text-Strong: #F1F5F9;
    --Dash-Text-Weak: #94A3B8;
    --Dash-Text-Disabled: #64748B;
    --Dash-Stroke-Strong: #2D3748;
    --Dash-Stroke-Weak: rgba(45,55,72,0.3);
    --Dash-Fill-Primary-Hover: rgba(232,0,45,0.08);
    --Dash-Fill-Primary-Active: rgba(232,0,45,0.15);
    --Dash-Fill-Disabled: #2D3748;
    --Dash-Shading-Strong: rgba(0,0,0,0.5);
    --Dash-Shading-Weak: rgba(0,0,0,0.3);
}

.dash-dropdown-option:hover { background-color: #2D3748 !important; }
.dash-dropdown-option[data-selected] { background-color: rgba(232,0,45,0.15) !important; }

.dash-slider-tooltip { color: #F1F5F9 !important; background-color: #1A2235 !important; border-color: #2D3748 !important; }
.dash-range-slider-input { color: #F1F5F9 !important; background-color: #1A2235 !important; border: 1px solid #2D3748 !important; border-radius: 4px !important; }
"""

# Helpers
def apply_chart_style(fig):
    fig.update_layout(
        font=dict(family=FONT, color=C_TEXT, size=18),
        title_font=dict(size=22, color=C_TEXT, family=FONT),
        title_x=0,
        title_pad=dict(l=12),
        plot_bgcolor=C_WHITE,
        paper_bgcolor=C_WHITE,
        margin=dict(l=16, r=16, t=64, b=16),
        legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0,
                    font=dict(size=17, color=C_TEXT)),
        coloraxis_colorbar=dict(
            tickfont=dict(color=C_TEXT, size=15),
            title_font=dict(color=C_TEXT, size=16),
        ),
    )
    fig.update_xaxes(gridcolor=C_BORDER, linecolor=C_BORDER, zeroline=False,
                     tickfont=dict(color=C_TEXT, size=16),
                     title_font=dict(color=C_TEXT, size=18))
    fig.update_yaxes(gridcolor=C_BORDER, linecolor=C_BORDER, zeroline=False,
                     tickfont=dict(color=C_TEXT, size=16),
                     title_font=dict(color=C_TEXT, size=18))
    return fig

def chart_card(child, style=None):
    base = {
        "backgroundColor": C_WHITE,
        "borderRadius": "14px",
        "boxShadow": "0 2px 8px rgba(0,0,0,0.4), 0 1px 2px rgba(0,0,0,0.3)",
        "overflow": "hidden",
        "margin": "8px",
        "border": f"1px solid {C_BORDER}",
    }
    if style:
        base.update(style)
    return html.Div(child, style=base)

def card_kpi(titulo, valor):
    v = str(valor)
    is_num = v.replace(",", "").isdigit()
    font_size = "38px" if len(v) <= 10 else "20px"
    v_color = C_RED if is_num else C_TEXT
    return html.Div([
        html.P(titulo, style={
            "margin": "0 0 10px 0", "fontSize": "14px", "color": C_MUTED,
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
        "boxShadow": "0 2px 8px rgba(0,0,0,0.4)",
        "border": f"1px solid {C_BORDER}",
    })

def insight(texto):
    return html.P(texto, style={
        "fontSize": "16px", "color": C_TEXT, "margin": "0 0 8px 0",
        "padding": "10px 12px", "backgroundColor": C_BG,
        "border": f"1px solid {C_BORDER}",
        "borderLeft": f"3px solid {C_RED}",
        "borderRadius": "0 6px 6px 0",
        "lineHeight": "1.55",
    })

def section_label(text):
    return html.P(text, style={
        "margin": "0 0 8px 0", "fontSize": "14px", "color": C_MUTED,
        "fontWeight": "700", "textTransform": "uppercase", "letterSpacing": "0.8px",
    })

# Static figures - Dashboard 1
top_pilotos = (
    df[df["is_winner"]]
    .groupby("full_name").size()
    .nlargest(10).reset_index(name="vitorias").sort_values("vitorias")
)
fig_pilotos = px.bar(
    top_pilotos, x="vitorias", y="full_name", orientation="h",
    title="Top 10 Pilotos - Vitórias (1990–2024)",
    labels={"vitorias": "Vitórias", "full_name": ""},
    color="vitorias", color_continuous_scale=SCALE_QTD,
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
    title="Top 10 Equipes - Vitórias (1990–2024)",
    labels={"vitorias": "Vitórias", "constructor_name": ""},
    color="vitorias", color_continuous_scale=SCALE_QTD,
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
    barmode="group", title="Vitórias por Década - Top 8 Equipes",
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

# Filter options
todas_equipes = df[df["is_winner"]]["constructor_name"].value_counts().index.tolist()
top5_default = todas_equipes[:5]

# App
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
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
        <style>{CUSTOM_CSS}</style>
    </body>
</html>"""

# Nav bar
nav_bar = html.Div([
    html.Div([
        html.Span(style={
            "display": "inline-block", "width": "8px", "height": "8px",
            "backgroundColor": C_RED, "borderRadius": "50%", "marginRight": "10px",
        }),
        html.Span("F1", style={
            "color": "#FFFFFF", "fontWeight": "800", "fontSize": "20px", "letterSpacing": "1px",
        }),
        html.Span(" Dashboard", style={
            "color": "rgba(255,255,255,0.4)", "fontWeight": "400",
            "fontSize": "17px", "marginLeft": "2px",
        }),
    ], style={"display": "flex", "alignItems": "center"}),

    html.Div([
        html.Span(periodo, style={"color": "rgba(255,255,255,0.35)", "fontSize": "15px"}),
        html.Span("  ·  ", style={"color": "rgba(255,255,255,0.15)", "fontSize": "15px"}),
        html.Span(f"{n_corridas} corridas", style={"color": "rgba(255,255,255,0.35)", "fontSize": "15px"}),
        html.Span("  ·  ", style={"color": "rgba(255,255,255,0.15)", "fontSize": "15px"}),
        html.Span(f"{n_pilotos} pilotos", style={"color": "rgba(255,255,255,0.35)", "fontSize": "15px"}),
        html.Span("  ·  ", style={"color": "rgba(255,255,255,0.15)", "fontSize": "15px"}),
        html.Span(f"{n_equipes} equipes", style={"color": "rgba(255,255,255,0.35)", "fontSize": "15px"}),
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

# Layout constants
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
TAB_STYLE = {
    "backgroundColor": C_BG,
    "color": C_MUTED,
    "fontFamily": FONT,
    "fontSize": "18px",
    "fontWeight": "500",
    "padding": "16px 32px",
    "border": "none",
    "borderBottom": f"2px solid transparent",
    "borderRadius": "0",
}
TAB_SELECTED = {
    "backgroundColor": C_BG,
    "color": C_TEXT,
    "fontFamily": FONT,
    "fontSize": "18px",
    "fontWeight": "700",
    "padding": "16px 32px",
    "border": "none",
    "borderTop": "none",
    "borderLeft": "none",
    "borderRight": "none",
    "borderBottom": f"3px solid {C_RED}",
    "borderRadius": "0",
}

# Dashboard 1
dashboard1 = html.Div([
    html.Div([
        card_kpi("Temporadas", n_temporadas),
        card_kpi("Corridas", n_corridas),
        card_kpi("Pilotos", n_pilotos),
        card_kpi("Equipes", n_equipes),
        card_kpi("Piloto Recordista", piloto_recordista),
        card_kpi("Equipe Recordista", equipe_recordista),
    ], style={"display": "flex", "padding": "20px 14px 4px 14px", "backgroundColor": C_BG}),

    html.Div([
        chart_card(dcc.Graph(id="d1-pilotos", figure=fig_pilotos), style={"flex": "1"}),
        chart_card(dcc.Graph(id="d1-equipes", figure=fig_equipes), style={"flex": "1"}),
    ], style={"display": "flex", "padding": "0 8px", "backgroundColor": C_BG}),

    html.Div([
        chart_card(dcc.Graph(id="d1-decada", figure=fig_decada), style={"flex": "1"}),
        chart_card(dcc.Graph(id="d1-dnf", figure=fig_dnf), style={"flex": "1"}),
    ], style={"display": "flex", "padding": "0 8px 16px 8px", "backgroundColor": C_BG}),
], style={"backgroundColor": C_BG})

# Dashboard 2
dashboard2 = html.Div([
    html.Div([
        html.Div([
            html.H3("Filtros", style={
                "margin": "0 0 20px 0", "color": C_TEXT,
                "fontSize": "17px", "fontWeight": "700",
                "letterSpacing": "1.2px", "textTransform": "uppercase",
            }),
            section_label("Período"),
            dcc.RangeSlider(
                id="slider-anos", min=1990, max=2024, step=1, value=[1990, 2024],
                marks={y: {"label": str(y), "style": {"fontSize": "14px", "color": C_TEXT}}
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
                style={
                    "fontSize": "16px", "marginTop": "4px",
                    "backgroundColor": C_DARK, "color": C_TEXT,
                    "border": f"1px solid {C_BORDER}",
                },
            ),
            html.Hr(style={"margin": "22px 0 18px 0", "borderColor": C_BORDER}),
            html.H4("Achados do período", style={
                "margin": "0 0 14px 0", "color": C_TEXT,
                "fontSize": "17px", "fontWeight": "700",
                "letterSpacing": "1.2px", "textTransform": "uppercase",
            }),
            html.Div(id="d2-achados"),
        ], style=SIDEBAR_STYLE),

        html.Div([
            chart_card(dcc.Graph(id="d2-linha-vitorias")),
            html.Div([
                chart_card(dcc.Graph(id="d2-scatter-grid"), style={"flex": "1"}),
                chart_card(dcc.Graph(id="d2-bar-equipes"), style={"flex": "1"}),
            ], style={"display": "flex"}),
            html.Div([
                chart_card(dcc.Graph(id="d2-hist-idade"), style={"flex": "1"}),
                chart_card(dcc.Graph(id="d2-scatter-idade"), style={"flex": "1"}),
            ], style={"display": "flex"}),
            chart_card(dcc.Graph(id="d2-heatmap")),
        ], style=CONTENT_STYLE),

    ], style={"display": "flex", "minHeight": "80vh"}),
], style={"backgroundColor": C_BG})

# Layout
app.layout = html.Div([
    nav_bar,
    dcc.Tabs(
        value="tab-1",
        colors={"border": C_BORDER, "primary": C_RED, "background": C_BG},
        children=[
            dcc.Tab(label="Visão Geral", value="tab-1",
                    children=[dashboard1],
                    style=TAB_STYLE, selected_style=TAB_SELECTED),
            dcc.Tab(label="Exploração Interativa", value="tab-2",
                    children=[dashboard2],
                    style=TAB_STYLE, selected_style=TAB_SELECTED),
        ],
        style={"backgroundColor": C_BG, "borderBottom": f"1px solid {C_BORDER}"},
    ),
], style={"fontFamily": FONT, "backgroundColor": C_BG, "minHeight": "100vh"})

# Callback
@app.callback(
    [Output("d2-linha-vitorias", "figure"),
     Output("d2-scatter-grid", "figure"),
     Output("d2-bar-equipes", "figure"),
     Output("d2-hist-idade", "figure"),
     Output("d2-scatter-idade", "figure"),
     Output("d2-heatmap", "figure"),
     Output("d2-achados", "children")],
    [Input("slider-anos", "value"),
     Input("dropdown-equipes", "value")],
)
def atualizar_dashboard2(anos, equipes):
    ano_min, ano_max = anos
    equipes = equipes or todas_equipes

    dff = df[(df["year"] >= ano_min) & (df["year"] <= ano_max)]
    dff_eq = dff[dff["constructor_name"].isin(equipes)]

    vit_ano = (
        dff_eq[dff_eq["is_winner"]]
        .groupby(["year", "constructor_name"]).size()
        .reset_index(name="vitorias")
    )
    fig1 = px.line(
        vit_ano, x="year", y="vitorias", color="constructor_name", markers=True,
        title=f"Vitórias por Temporada - {ano_min}–{ano_max}",
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
        title=f"Vitórias por Equipe - {ano_min}–{ano_max}",
        labels={"constructor_name": "", "vitorias": "Vitórias"},
        color="vitorias", color_continuous_scale=SCALE_QTD,
    )
    fig3.update_layout(coloraxis_showscale=False)
    apply_chart_style(fig3)

    vit_idade = (
        dff_eq[dff_eq["is_winner"] & dff_eq["age_at_race"].notna()]
        .groupby("age_at_race").size()
        .reset_index(name="vitorias")
    )
    fig4 = px.bar(
        vit_idade, x="age_at_race", y="vitorias",
        title=f"Vitórias por Idade - {ano_min}–{ano_max}",
        labels={"age_at_race": "Idade", "vitorias": "Vitórias"},
        color="vitorias", color_continuous_scale=SCALE_QTD,
    )
    fig4.update_layout(coloraxis_showscale=False)
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
        color="media_pontos", color_continuous_scale=SCALE_QTD,
    )
    fig5.update_layout(coloraxis_showscale=False)
    apply_chart_style(fig5)

    cols_corr = ["grid", "positionOrder", "points", "age_at_race", "laps"]
    labels_corr = ["Grid", "Posição Final", "Pontos", "Idade", "Voltas"]
    corr_data = dff_eq[cols_corr].dropna().corr().round(2)
    fig6 = px.imshow(
        corr_data,
        x=labels_corr, y=labels_corr,
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        title=f"Correlação entre Variáveis - {ano_min}–{ano_max}",
        text_auto=True,
    )
    apply_chart_style(fig6)

    lider_eq = vit_eq.iloc[0] if not vit_eq.empty else None
    pico_idade = int(vit_idade.loc[vit_idade["vitorias"].idxmax(), "age_at_race"]) if not vit_idade.empty else "-"

    achados = [
        insight(f"Líder: {lider_eq['constructor_name']} - {int(lider_eq['vitorias'])} vitórias") if lider_eq is not None else "",
        insight(f"Correlação grid - posição: r = {corr_grid}"),
        insight(f"Correlação idade - pontos: r = {corr_idade}"),
        insight(f"Idade com mais vitórias: {pico_idade} anos"),
    ]

    return fig1, fig2, fig3, fig4, fig5, fig6, achados


if __name__ == "__main__":
    app.run(debug=True)

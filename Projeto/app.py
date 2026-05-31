import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc
from pathlib import Path

# ---------------------------------------------------------------------------
# Carregamento e preparação dos dados
# ---------------------------------------------------------------------------
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
df["code"]      = df["code"].fillna(df["surname"].str[:3].str.upper())
df["date"]      = pd.to_datetime(df["date"], errors="coerce")
df["full_name"] = (df["forename"].astype(str) + " " + df["surname"].astype(str)).str.strip()
df["is_winner"] = df["position"] == 1
df["is_podium"] = df["position"].between(1, 3)
df["dnf"]       = df["position"].isna()
df["decade"]    = (df["year"] // 10 * 10).astype(int).astype(str) + "s"

# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------
n_temporadas      = df["year"].nunique()
n_corridas        = df["raceId"].nunique()
n_pilotos         = df["driverId"].nunique()
n_equipes         = df["constructorId"].nunique()
piloto_recordista = df[df["is_winner"]]["full_name"].value_counts().idxmax()
equipe_recordista = str(df[df["is_winner"]]["constructor_name"].value_counts().idxmax())
periodo           = f"{df['year'].min()} – {df['year'].max()}"

# ---------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------

# top 10 pilotos por vitórias
top_pilotos = (
    df[df["is_winner"]]
    .groupby("full_name")
    .size()
    .nlargest(10)
    .reset_index(name="vitorias")
    .sort_values("vitorias")
)
fig_pilotos = px.bar(
    top_pilotos,
    x="vitorias",
    y="full_name",
    orientation="h",
    title="Top 10 pilotos com mais vitórias",
    labels={"vitorias": "Vitórias", "full_name": "Piloto"},
    color="vitorias",
    color_continuous_scale="Blues",
)
fig_pilotos.update_layout(template="plotly_white", coloraxis_showscale=False, margin=dict(l=10, r=10, t=40, b=10))

# top 10 equipes por vitórias
top_equipes = (
    df[df["is_winner"]]
    .groupby("constructor_name")
    .size()
    .nlargest(10)
    .reset_index(name="vitorias")
    .sort_values("vitorias")
)
fig_equipes = px.bar(
    top_equipes,
    x="vitorias",
    y="constructor_name",
    orientation="h",
    title="Top 10 equipes com mais vitórias",
    labels={"vitorias": "Vitórias", "constructor_name": "Equipe"},
    color="vitorias",
    color_continuous_scale="Reds",
)
fig_equipes.update_layout(template="plotly_white", coloraxis_showscale=False, margin=dict(l=10, r=10, t=40, b=10))

# vitórias das top 8 equipes por década
top8 = df[df["is_winner"]]["constructor_name"].value_counts().head(8).index.tolist()
vit_decada = (
    df[(df["is_winner"]) & (df["constructor_name"].isin(top8))]
    .groupby(["decade", "constructor_name"])
    .size()
    .reset_index(name="vitorias")
    .sort_values("decade")
)
fig_decada = px.bar(
    vit_decada,
    x="decade",
    y="vitorias",
    color="constructor_name",
    barmode="group",
    title="Vitórias por década — top 8 equipes",
    labels={"decade": "Década", "vitorias": "Vitórias", "constructor_name": "Equipe"},
)
fig_decada.update_layout(template="plotly_white", legend_title="Equipe", margin=dict(l=10, r=10, t=40, b=10))

# taxa de abandono por temporada
dnf_ano = (
    df.groupby("year")["dnf"]
    .mean()
    .mul(100)
    .reset_index(name="taxa_dnf")
)
fig_dnf = px.area(
    dnf_ano,
    x="year",
    y="taxa_dnf",
    title="Taxa de abandono (DNF) por temporada",
    labels={"year": "Temporada", "taxa_dnf": "DNF (%)"},
    color_discrete_sequence=["#EF553B"],
)
fig_dnf.update_layout(template="plotly_white", margin=dict(l=10, r=10, t=40, b=10))

# ---------------------------------------------------------------------------
# Helpers de layout
# ---------------------------------------------------------------------------
def card_kpi(titulo, valor):
    return html.Div(
        children=[
            html.P(titulo, style={"margin": "0", "fontSize": "12px", "color": "#888888"}),
            html.H3(str(valor), style={"margin": "6px 0 0 0", "color": "#1a1a2e", "fontSize": "22px"}),
        ],
        style={
            "backgroundColor": "#ffffff",
            "border": "1px solid #e0e0e0",
            "borderRadius": "8px",
            "padding": "16px 12px",
            "textAlign": "center",
            "display": "inline-block",
            "width": "14%",
            "margin": "0 6px",
            "boxShadow": "0 2px 6px rgba(0,0,0,0.06)",
        }
    )

def linha_graficos(esq, dir):
    return html.Div(
        children=[
            html.Div(children=[esq], style={"width": "48%", "display": "inline-block", "verticalAlign": "top", "padding": "0 8px"}),
            html.Div(children=[dir], style={"width": "48%", "display": "inline-block", "verticalAlign": "top", "padding": "0 8px"}),
        ],
        style={"marginTop": "16px"}
    )

# ---------------------------------------------------------------------------
# App e layout
# ---------------------------------------------------------------------------
app = Dash()

app.layout = html.Div(
    children=[

        # cabeçalho
        html.Div(
            children=[
                html.H1("Fórmula 1 — Visão Geral", style={"margin": "0", "color": "#ffffff", "fontSize": "28px"}),
                html.P(f"Análise do período {periodo} · {n_corridas} corridas · {n_pilotos} pilotos · {n_equipes} equipes",
                       style={"margin": "6px 0 0 0", "color": "#cccccc", "fontSize": "14px"}),
            ],
            style={
                "backgroundColor": "#1a1a2e",
                "padding": "24px 32px",
            }
        ),

        # cards KPI
        html.Div(
            children=[
                card_kpi("Temporadas", n_temporadas),
                card_kpi("Corridas", n_corridas),
                card_kpi("Pilotos", n_pilotos),
                card_kpi("Equipes", n_equipes),
                card_kpi("Piloto recordista", piloto_recordista),
                card_kpi("Equipe recordista", equipe_recordista),
            ],
            style={"textAlign": "center", "padding": "24px 24px 8px 24px"}
        ),

        # gráficos — linha 1
        linha_graficos(
            dcc.Graph(id="grafico-pilotos", figure=fig_pilotos),
            dcc.Graph(id="grafico-equipes", figure=fig_equipes),
        ),

        # gráficos — linha 2
        linha_graficos(
            dcc.Graph(id="grafico-decada", figure=fig_decada),
            dcc.Graph(id="grafico-dnf",    figure=fig_dnf),
        ),

    ],
    style={
        "fontFamily": "Arial, sans-serif",
        "backgroundColor": "#f4f6f9",
        "minHeight": "100vh",
        "paddingBottom": "32px",
    }
)

if __name__ == "__main__":
    app.run(debug=True)

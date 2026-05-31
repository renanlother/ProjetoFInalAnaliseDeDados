import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from pathlib import Path

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

df["code"]        = df["code"].fillna(df["surname"].str[:3].str.upper())
df["date"]        = pd.to_datetime(df["date"],  errors="coerce")
df["dob"]         = pd.to_datetime(df["dob"],   errors="coerce")
df["full_name"]   = (df["forename"].astype(str) + " " + df["surname"].astype(str)).str.strip()
df["is_winner"]   = df["position"] == 1
df["is_podium"]   = df["position"].between(1, 3)
df["dnf"]         = df["position"].isna()
df["decade"]      = (df["year"] // 10 * 10).astype(int).astype(str) + "s"
df["age_at_race"] = ((df["date"] - df["dob"]).dt.days / 365.25).round().astype("Int64")
df["nationality_x"] = df["nationality_x"].astype(str).str.strip().str.title()

n_temporadas      = df["year"].nunique()
n_corridas        = df["raceId"].nunique()
n_pilotos         = df["driverId"].nunique()
n_equipes         = df["constructorId"].nunique()
piloto_recordista = df[df["is_winner"]]["full_name"].value_counts().idxmax()
equipe_recordista = str(df[df["is_winner"]]["constructor_name"].value_counts().idxmax())
periodo           = f"{df['year'].min()} – {df['year'].max()}"

top_pilotos = (
    df[df["is_winner"]]
    .groupby("full_name").size()
    .nlargest(10).reset_index(name="vitorias").sort_values("vitorias")
)
fig_pilotos = px.bar(
    top_pilotos, x="vitorias", y="full_name", orientation="h",
    title="Top 10 pilotos com mais vitórias",
    labels={"vitorias": "Vitórias", "full_name": "Piloto"},
    color="vitorias", color_continuous_scale="Blues",
)
fig_pilotos.update_layout(template="plotly_white", coloraxis_showscale=False,
                          margin=dict(l=10, r=10, t=40, b=10))

top_equipes_d1 = (
    df[df["is_winner"]]
    .groupby("constructor_name").size()
    .nlargest(10).reset_index(name="vitorias").sort_values("vitorias")
)
fig_equipes = px.bar(
    top_equipes_d1, x="vitorias", y="constructor_name", orientation="h",
    title="Top 10 equipes com mais vitórias",
    labels={"vitorias": "Vitórias", "constructor_name": "Equipe"},
    color="vitorias", color_continuous_scale="Reds",
)
fig_equipes.update_layout(template="plotly_white", coloraxis_showscale=False,
                          margin=dict(l=10, r=10, t=40, b=10))

top8 = df[df["is_winner"]]["constructor_name"].value_counts().head(8).index.tolist()
vit_decada = (
    df[(df["is_winner"]) & (df["constructor_name"].isin(top8))]
    .groupby(["decade", "constructor_name"]).size()
    .reset_index(name="vitorias").sort_values("decade")
)
fig_decada = px.bar(
    vit_decada, x="decade", y="vitorias", color="constructor_name",
    barmode="group", title="Vitórias por década — top 8 equipes",
    labels={"decade": "Década", "vitorias": "Vitórias", "constructor_name": "Equipe"},
)
fig_decada.update_layout(template="plotly_white", legend_title="Equipe",
                         margin=dict(l=10, r=10, t=40, b=10))

dnf_ano = df.groupby("year")["dnf"].mean().mul(100).reset_index(name="taxa_dnf")
fig_dnf = px.area(
    dnf_ano, x="year", y="taxa_dnf",
    title="Taxa de abandono (DNF) por temporada",
    labels={"year": "Temporada", "taxa_dnf": "DNF (%)"},
    color_discrete_sequence=["#EF553B"],
)
fig_dnf.update_layout(template="plotly_white", margin=dict(l=10, r=10, t=40, b=10))

todas_equipes = df[df["is_winner"]]["constructor_name"].value_counts().index.tolist()
top5_default  = todas_equipes[:5]

SIDEBAR = {"width": "23%", "display": "inline-block", "verticalAlign": "top",
           "padding": "20px 16px", "backgroundColor": "#f0f2f5",
           "minHeight": "80vh", "boxSizing": "border-box"}

CONTEUDO = {"width": "75%", "display": "inline-block", "verticalAlign": "top",
            "padding": "16px 12px", "boxSizing": "border-box"}

COL2 = {"width": "48%", "display": "inline-block", "verticalAlign": "top", "padding": "0 6px"}

def card_kpi(titulo, valor):
    return html.Div(
        children=[
            html.P(titulo, style={"margin": "0", "fontSize": "12px", "color": "#888888"}),
            html.H3(str(valor), style={"margin": "6px 0 0 0", "color": "#1a1a2e", "fontSize": "22px"}),
        ],
        style={
            "backgroundColor": "#ffffff", "border": "1px solid #e0e0e0",
            "borderRadius": "8px", "padding": "16px 12px", "textAlign": "center",
            "display": "inline-block", "width": "14%", "margin": "0 6px",
            "boxShadow": "0 2px 6px rgba(0,0,0,0.06)",
        }
    )

def linha2(esq, dir):
    return html.Div(
        children=[html.Div(esq, style=COL2), html.Div(dir, style=COL2)],
        style={"marginTop": "12px"}
    )

app = Dash()

cabecalho = html.Div(
    children=[
        html.H1("Fórmula 1 — Dashboard Analítico",
                style={"margin": "0", "color": "#ffffff", "fontSize": "26px"}),
        html.P(f"Período {periodo} · {n_corridas} corridas · {n_pilotos} pilotos · {n_equipes} equipes",
               style={"margin": "6px 0 0 0", "color": "#cccccc", "fontSize": "13px"}),
    ],
    style={"backgroundColor": "#1a1a2e", "padding": "22px 32px"}
)

dashboard1 = html.Div([
    html.Div(
        children=[
            card_kpi("Temporadas",        n_temporadas),
            card_kpi("Corridas",          n_corridas),
            card_kpi("Pilotos",           n_pilotos),
            card_kpi("Equipes",           n_equipes),
            card_kpi("Piloto recordista", piloto_recordista),
            card_kpi("Equipe recordista", equipe_recordista),
        ],
        style={"textAlign": "center", "padding": "24px 24px 8px 24px"}
    ),
    linha2(
        dcc.Graph(id="d1-pilotos", figure=fig_pilotos),
        dcc.Graph(id="d1-equipes", figure=fig_equipes),
    ),
    linha2(
        dcc.Graph(id="d1-decada", figure=fig_decada),
        dcc.Graph(id="d1-dnf",    figure=fig_dnf),
    ),
])

dashboard2 = html.Div([
    html.Div(
        children=[
            # sidebar de filtros
            html.Div([
                html.H3("Filtros", style={"marginTop": "0", "color": "#1a1a2e"}),

                html.Label("Período (anos):"),
                dcc.RangeSlider(
                    id="slider-anos",
                    min=1990, max=2024, step=1,
                    value=[1990, 2024],
                    marks={y: str(y) for y in range(1990, 2025, 5)},
                    tooltip={"placement": "bottom", "always_visible": False},
                ),

                html.Br(),

                html.Label("Equipes:"),
                dcc.Dropdown(
                    id="dropdown-equipes",
                    options=[{"label": eq, "value": eq} for eq in todas_equipes],
                    value=top5_default,
                    multi=True,
                    placeholder="Selecione equipes...",
                ),

                html.Br(),

                html.Label("Mostrar pilotos de:"),
                dcc.RadioItems(
                    id="radio-escopo-pilotos",
                    options=[
                        {"label": "Equipes selecionadas", "value": "filtrado"},
                        {"label": "Todos os pilotos",     "value": "todos"},
                    ],
                    value="todos",
                    labelStyle={"display": "block", "marginBottom": "6px"},
                ),
            ], style=SIDEBAR),

            # área de gráficos
            html.Div([
                # gráfico 1 — largura total
                dcc.Graph(id="d2-linha-vitorias"),

                # gráficos 2 e 3
                linha2(
                    dcc.Graph(id="d2-bar-pilotos"),
                    dcc.Graph(id="d2-bar-equipes"),
                ),

                # gráficos 4 e 5
                linha2(
                    dcc.Graph(id="d2-area-dnf"),
                    dcc.Graph(id="d2-hist-idade"),
                ),
            ], style=CONTEUDO),
        ],
        style={"marginTop": "8px"}
    )
])

app.layout = html.Div(
    children=[
        cabecalho,
        dcc.Tabs(
            value="tab-1",
            children=[
                dcc.Tab(label="Visão Geral",          value="tab-1", children=[dashboard1]),
                dcc.Tab(label="Exploração Interativa", value="tab-2", children=[dashboard2]),
            ],
            style={"fontFamily": "Arial, sans-serif"},
        ),
    ],
    style={"fontFamily": "Arial, sans-serif", "backgroundColor": "#f4f6f9", "minHeight": "100vh"}
)

@app.callback(
    [Output("d2-linha-vitorias", "figure"),
     Output("d2-bar-pilotos",    "figure"),
     Output("d2-bar-equipes",    "figure"),
     Output("d2-area-dnf",       "figure"),
     Output("d2-hist-idade",     "figure")],
    [Input("slider-anos",           "value"),
     Input("dropdown-equipes",      "value"),
     Input("radio-escopo-pilotos",  "value")],
)
def atualizar_dashboard2(anos, equipes, escopo_pilotos):
    ano_min, ano_max = anos
    equipes = equipes or todas_equipes

    dff     = df[(df["year"] >= ano_min) & (df["year"] <= ano_max)]
    dff_eq  = dff[dff["constructor_name"].isin(equipes)]

    # gráfico 1 — vitórias por temporada para as equipes selecionadas (linha)
    vit_ano = (
        dff_eq[dff_eq["is_winner"]]
        .groupby(["year", "constructor_name"]).size()
        .reset_index(name="vitorias")
    )
    fig1 = px.line(
        vit_ano, x="year", y="vitorias", color="constructor_name",
        markers=True,
        title=f"Vitórias por temporada — equipes selecionadas ({ano_min}–{ano_max})",
        labels={"year": "Temporada", "vitorias": "Vitórias", "constructor_name": "Equipe"},
    )
    fig1.update_layout(template="plotly_white", legend_title="Equipe",
                       margin=dict(l=10, r=10, t=40, b=10))

    # gráfico 2 — top 15 pilotos por vitórias (barra horizontal)
    base_pilotos = dff_eq if escopo_pilotos == "filtrado" else dff
    top_p = (
        base_pilotos[base_pilotos["is_winner"]]
        .groupby("full_name").size()
        .nlargest(15).reset_index(name="vitorias").sort_values("vitorias")
    )
    titulo_p = "Top 15 pilotos" + (" (equipes selecionadas)" if escopo_pilotos == "filtrado" else "")
    fig2 = px.bar(
        top_p, x="vitorias", y="full_name", orientation="h",
        title=f"{titulo_p} — {ano_min}–{ano_max}",
        labels={"vitorias": "Vitórias", "full_name": "Piloto"},
        color="vitorias", color_continuous_scale="Blues",
    )
    fig2.update_layout(template="plotly_white", coloraxis_showscale=False,
                       margin=dict(l=10, r=10, t=40, b=10))

    # gráfico 3 — vitórias por equipe selecionada no período (barra vertical)
    vit_eq = (
        dff_eq[dff_eq["is_winner"]]
        .groupby("constructor_name").size()
        .reset_index(name="vitorias").sort_values("vitorias", ascending=False)
    )
    fig3 = px.bar(
        vit_eq, x="constructor_name", y="vitorias",
        title=f"Vitórias por equipe ({ano_min}–{ano_max})",
        labels={"constructor_name": "Equipe", "vitorias": "Vitórias"},
        color="vitorias", color_continuous_scale="Reds",
    )
    fig3.update_layout(template="plotly_white", coloraxis_showscale=False,
                       margin=dict(l=10, r=10, t=40, b=10))

    # gráfico 4 — taxa de DNF por temporada no período (área)
    dnf_periodo = (
        dff.groupby("year")["dnf"].mean().mul(100).reset_index(name="taxa_dnf")
    )
    fig4 = px.area(
        dnf_periodo, x="year", y="taxa_dnf",
        title=f"Taxa de abandono (DNF) — {ano_min} a {ano_max}",
        labels={"year": "Temporada", "taxa_dnf": "DNF (%)"},
        color_discrete_sequence=["#EF553B"],
    )
    fig4.update_layout(template="plotly_white", margin=dict(l=10, r=10, t=40, b=10))

    # gráfico 5 — distribuição de idade dos vencedores no período (histograma)
    venc = dff[dff["is_winner"]].dropna(subset=["age_at_race"])
    fig5 = px.histogram(
        venc, x="age_at_race", nbins=20,
        title=f"Distribuição de idade dos vencedores ({ano_min}–{ano_max})",
        labels={"age_at_race": "Idade na corrida", "count": "Vitórias"},
        color_discrete_sequence=["#AB63FA"],
    )
    fig5.update_layout(template="plotly_white", bargap=0.05,
                       margin=dict(l=10, r=10, t=40, b=10))

    return fig1, fig2, fig3, fig4, fig5


if __name__ == "__main__":
    app.run(debug=True)

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

# ==========================
# 1) CARREGAR DADOS
# ==========================
df = pd.read_csv("terror_decadas.csv")
df["ano"] = df["release_date"].str[:4]

decadas_unicas = sorted(df["decada"].unique())


# ==========================
# 2) CRIAÇÃO DOS GRÁFICOS
# ==========================

def grafico_barras(df_filtrado):
    contagem = df_filtrado["decada"].value_counts().sort_index().reset_index()
    contagem.columns = ["decada", "qtd"]
    return px.bar(contagem,
                  x="decada",
                  y="qtd",
                  title="Quantidade de filmes por década",
                  color="qtd",
                  text="qtd")


def grafico_linha_media(df_filtrado):
    medias = df_filtrado.groupby("decada")["vote_average"].mean().reset_index()
    return px.line(medias,
                   x="decada",
                   y="vote_average",
                   markers=True,
                   title="Nota média por década")


def grafico_popularidade(df_filtrado):
    pop = df_filtrado.groupby("decada")["popularity"].mean().reset_index()
    return px.line(pop,
                   x="decada",
                   y="popularity",
                   markers=True,
                   title="Popularidade média por década")


def grafico_boxplot(df_filtrado):
    return px.box(df_filtrado,
                  x="decada",
                  y="vote_average",
                  points="all",
                  title="Distribuição de notas por década")


# ==========================
# 3) INICIAR APP
# ==========================
app = Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])

# ==========================
# 4) LAYOUT — MODELO B (2 COLUNAS)
# ==========================
app.layout = dbc.Container([

    html.H1("Terror ao Longo das Décadas",
            className="text-center mt-4 mb-4"),

    # ---------------------- CARDS RESUMO ----------------------
    dbc.Row([
        dbc.Col(dbc.Card(
            dbc.CardBody([
                html.H4("Total de Filmes"),
                html.H2(f"{len(df)}")
            ]), color="primary", inverse=True
        ), width=4),

        dbc.Col(dbc.Card(
            dbc.CardBody([
                html.H4("Maior Década"),
                html.H2(df["decada"].value_counts().idxmax())
            ]), color="success", inverse=True
        ), width=4),

        dbc.Col(dbc.Card(
            dbc.CardBody([
                html.H4("Década Mais Bem Avaliada"),
                html.H2(df.groupby("decada")["vote_average"].mean().idxmax())
            ]), color="danger", inverse=True
        ), width=4),
    ], className="mb-4"),

    # ---------------------- FILTROS ----------------------
    dbc.Row([
        dbc.Col([
            html.Label("Filtrar por Década:"),
            dcc.Dropdown(
                options=[{"label": d, "value": d} for d in decadas_unicas],
                value=None,
                id="filtro-decada",
                placeholder="Selecione uma década (opcional)"
            )
        ], width=6),

        dbc.Col([
            html.Label("Nota mínima:"),
            dcc.Slider(
                min=0, max=10, step=0.5, value=0,
                marks={i: str(i) for i in range(0, 11)},
                id="filtro-nota"
            )
        ], width=6),
    ], className="mb-5"),

    # ---------------------- GRADE DE GRÁFICOS ----------------------
    dbc.Row([
        dbc.Col(dcc.Graph(id="graf-barras"), width=6),
        dbc.Col(dcc.Graph(id="graf-media"), width=6),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id="graf-pop"), width=6),
        dbc.Col(dcc.Graph(id="graf-box"), width=6),
    ]),

], fluid=True)


# ==========================
# 5) CALLBACKS (INTERATIVIDADE)
# ==========================
@app.callback(
    Output("graf-barras", "figure"),
    Output("graf-media", "figure"),
    Output("graf-pop", "figure"),
    Output("graf-box", "figure"),
    Input("filtro-decada", "value"),
    Input("filtro-nota", "value"),
)
def atualizar_graficos(decada, nota_minima):

    df_filtrado = df[df["vote_average"] >= nota_minima]

    if decada:
        df_filtrado = df_filtrado[df_filtrado["decada"] == decada]

    return (
        grafico_barras(df_filtrado),
        grafico_linha_media(df_filtrado),
        grafico_popularidade(df_filtrado),
        grafico_boxplot(df_filtrado)
    )


# ==========================
# 6) RODAR APP
# ==========================
if __name__ == "__main__":
    app.run(debug=True)

import pandas as pd
import plotly.express as px
import plotly.io as pio
from dash import Dash, dcc, html, Input, Output, State

# ======================================================
#  TEMA VERMELHO PERSONALIZADO
# ======================================================
pio.templates["vermelho_tema"] = pio.templates["plotly_dark"]
pio.templates["vermelho_tema"].layout.update(
    paper_bgcolor="#1a1a1a",
    plot_bgcolor="#1a1a1a",
    font=dict(color="#ffffff"),
    colorway=[
        "#e63946",  # vermelho principal
        "#a8dadc",  # azul claro
        "#f1faee",  # branco gelo
        "#457b9d",  # azul médio
        "#1d3557",  # azul escuro
    ],
)
pio.templates.default = "vermelho_tema"

# ======================================================
#  CARREGAR DADOS
# ======================================================
df_dec = pd.read_csv("terror_decadas.csv")
df_dec["ano"] = df_dec["release_date"].str[:4]

df_sub = pd.read_csv("top10_subgeneros.csv")

# ======================================================
#  INICIALIZA APP
# ======================================================
app = Dash(__name__)

# ======================================================
#  LAYOUT COM NAVEGAÇÃO ENTRE PÁGINAS
# ======================================================
app.layout = html.Div(
    style={"padding": "0px", "fontFamily": "Arial"},
    children=[

        # ---------- NAVBAR ----------
        html.Div(
            style={
                "backgroundColor": "#e63946",
                "padding": "15px",
                "display": "flex",
                "gap": "20px",
                "alignItems": "center",
            },
            children=[
                html.H1(
                    "Terror",
                    style={"margin": "0", "paddingRight": "40px", "color": "white"},
                ),
                html.Button("Décadas", id="btn-decadas",
                            style={"background": "#1a1a1a", "color": "white",
                                   "border": "1px solid white", "padding": "8px",
                                   "cursor": "pointer", "borderRadius": "5px"}),

                html.Button("Subgêneros", id="btn-subgeneros",
                            style={"background": "#1a1a1a", "color": "white",
                                   "border": "1px solid white", "padding": "8px",
                                   "cursor": "pointer", "borderRadius": "5px"}),
            ],
        ),

        # Onde as páginas serão carregadas
        html.Div(id="pagina-conteudo", style={"padding": "20px"}),
    ],
)

# ======================================================
#  PÁGINA DAS DÉCADAS
# ======================================================
def pagina_decadas():

    return html.Div(
        children=[

            html.H2("Terror ao Longo das Décadas 🎥🩸", style={"color": "#e63946"}),

            # ---------- FILTROS ----------
            html.Div(
                style={
                    "display": "flex",
                    "gap": "20px",
                    "marginTop": "20px",
                },
                children=[

                    # Filtro por década
                    html.Div(
                        style={"flex": "1"},
                        children=[
                            html.Label("Filtrar por Década:"),
                            dcc.Dropdown(
                                id="filtro-decada",
                                options=[{"label": d, "value": d}
                                         for d in sorted(df_dec["decada"].unique())],
                                value=None,
                                placeholder="Selecione a década...",
                                style={
                                    "backgroundColor": "#333",
                                    "color": "white",
                                    "border": "1px solid #e63946",
                                },
                            ),
                        ],
                    ),

                    # Filtro por nota mínima
                    html.Div(
                        style={"flex": "1"},
                        children=[
                            html.Label("Nota mínima:"),
                            dcc.Slider(
                                id="filtro-nota",
                                min=0,
                                max=10,
                                value=0,
                                step=0.5,
                                marks={i: str(i)
                                       for i in range(0, 11)},
                            ),
                        ],
                    ),
                ],
            ),

            html.Br(),

            # ---------- GRÁFICOS ----------
            dcc.Graph(id="graf-barra"),
            dcc.Graph(id="graf-linha"),
            dcc.Graph(id="graf-box"),
        ]
    )


# ======================================================
#  PÁGINA DOS SUBGÊNEROS
# ======================================================
def pagina_subgeneros():

    fig = px.bar(
        df_sub,
        x="titulo",
        y="popularidade",
        color="subgenero",
        title="Top 10 – Filmes Mais Populares por Subgênero de Terror",
    )

    fig.update_layout(xaxis_tickangle=-45)

    return html.Div(
        children=[
            html.H2("Top 10 Subgêneros de Terror💀", style={"color": "#e63946"}),

            dcc.Graph(figure=fig),
        ]
    )


# ======================================================
#  CALLBACK PARA TROCAR A PÁGINA
# ======================================================
@app.callback(
    Output("pagina-conteudo", "children"),
    Input("btn-decadas", "n_clicks"),
    Input("btn-subgeneros", "n_clicks"),
)
def mudar_pagina(btn_dec, btn_sub):

    if btn_sub and (btn_sub > (btn_dec or 0)):
        return pagina_subgeneros()

    return pagina_decadas()


# ======================================================
#  CALLBACK DOS GRÁFICOS DO DASHBOARD 1
# ======================================================
@app.callback(
    Output("graf-barra", "figure"),
    Output("graf-linha", "figure"),
    Output("graf-box", "figure"),
    Input("filtro-decada", "value"),
    Input("filtro-nota", "value"),
)
def atualizar_graficos(decada, nota_min):

    df_filtro = df_dec.copy()

    if decada:
        df_filtro = df_filtro[df_filtro["decada"] == decada]

    df_filtro = df_filtro[df_filtro["vote_average"] >= nota_min]

    # --- Gráfico 1: Barras ---
    contagem = df_filtro["decada"].value_counts().sort_index().reset_index()
    contagem.columns = ["decada", "qtd"]

    fig_barra = px.bar(
        contagem,
        x="decada",
        y="qtd",
        title="Quantidade de Filmes por Década",
        text="qtd",
    )

    # --- Gráfico 2: Linha ---
    medias = df_filtro.groupby("decada")["vote_average"].mean().reset_index()
    fig_linha = px.line(
        medias,
        x="decada",
        y="vote_average",
        markers=True,
        title="Nota Média por Década",
    )

    # --- Gráfico 3: Boxplot ---
    fig_box = px.box(
        df_filtro,
        x="decada",
        y="vote_average",
        points="all",
        title="Distribuição das Notas por Década (Boxplot)",
    )

    return fig_barra, fig_linha, fig_box


# ======================================================
#  RUN
# ======================================================
if __name__ == "__main__":
    app.run(debug=True)

# PANDAS: leitura e manipulação de dados
# PLOTLY: visualizações interativas
# PLOTLY.IO: personalização de temas
# DASH: framework web para dashboards interativos
# DCC: componentes interativos do Dash (dropdown, sliders, gráficos)



import pandas as pd
import plotly.express as px
import plotly.io as pio
from dash import Dash, dcc, html, Input, Output, State

#  TEMA VERMELHO PERSONALIZADO

pio.templates["vermelho_tema"] = pio.templates["plotly_dark"]


# TEXTO E PALETA PADRÃO DOS GRÁFICOS

pio.templates["vermelho_tema"].layout.update(
    paper_bgcolor="#1a1a1a",
    plot_bgcolor="#1a1a1a",
    font=dict(color="#ffffff"),
    colorway=[
        "#e63946",  
        "#a8dadc",  
        "#f1faee",  
        "#457b9d",  
        "#1d3557",  
    ],
)
# DEFINIR TEMA PADRÃO

pio.templates.default = "vermelho_tema"


#  CARREGAMENTO DOS ARQUIVOS CSV

# Carrega dados de terror por década
df_dec = pd.read_csv("terror_decadas.csv")

# Cria coluna apenas com o ano
df_dec["ano"] = df_dec["release_date"].str[:4]


# Carrega dados de subgêneros (top 10 por popularidade)
df_sub = pd.read_csv("top10_subgeneros.csv")


# INICIALIZAÇÃO DO APP DASH

app = Dash(__name__)  # CRIA APP PRINCIPAL

#  LAYOUT PRINCIPAL (estrutura da página)

app.layout = html.Div(
    style={"padding": "0px", "fontFamily": "Arial"},
    children=[

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

        html.Div(id="pagina-conteudo", style={"padding": "20px"}),
    ],
)

#  PÁGINA 1 - ANÁLISE POR DÉCADAS

def pagina_decadas():

    return html.Div(
        children=[

            html.H2("Terror ao Longo das Décadas 🎥🩸", style={"color": "#e63946"}),

            # FILTROS 

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

            # GRÁFICOS 
            dcc.Graph(id="graf-barra"),
            dcc.Graph(id="graf-linha"),
            dcc.Graph(id="graf-box"),
        ]
    )


#  PÁGINA 2 - SUBGÊNEROS (TOP 10)

def pagina_subgeneros():

    fig = px.bar(
        df_sub,
        x="titulo",
        y="popularidade",
        color="subgenero",
        title="Top 10 – Filmes Mais Populares por Subgênero de Terror",
    )

    # rotaciona os nomes dos filmes para não ficarem sobrepostos

    fig.update_layout(xaxis_tickangle=-45)

    return html.Div(
        children=[
            html.H2("Top 10 Subgêneros de Terror💀", style={"color": "#e63946"}),

            dcc.Graph(figure=fig),
        ]
    )


#  CALLBACK PARA TROCAR A PÁGINA -> DA PÁGINA 1 PARA A 2

@app.callback(
    Output("pagina-conteudo", "children"),
    Input("btn-decadas", "n_clicks"),
    Input("btn-subgeneros", "n_clicks"),
)
def mudar_pagina(btn_dec, btn_sub):

    if btn_sub and (btn_sub > (btn_dec or 0)):
        return pagina_subgeneros()

    return pagina_decadas()


#  CALLBACK DO DASHBOARD (ATUALIZA GRÁFICOS DINAMICAMENTE)
# Sempre que o filtro de década ou de nota mudar, os três gráficos são atualizados automaticamente.

@app.callback(
    Output("graf-barra", "figure"),
    Output("graf-linha", "figure"),
    Output("graf-box", "figure"),
    Input("filtro-decada", "value"),
    Input("filtro-nota", "value"),
)
def atualizar_graficos(decada, nota_min):

    # CÓPIA DO DATAFRAME ORIGINAL
    df_filtro = df_dec.copy()

    # FILTRA PELA DÉCADA, SE SELECIONADA
    if decada:
        df_filtro = df_filtro[df_filtro["decada"] == decada]

    # FILTRA PELA NOTA MÍNIMA
    df_filtro = df_filtro[df_filtro["vote_average"] >= nota_min]

    # GRÁFICO 1: BARRAS (quantidade de filmes por década)
    contagem = df_filtro["decada"].value_counts().sort_index().reset_index()
    contagem.columns = ["decada", "qtd"]

    fig_barra = px.bar(
        contagem,
        x="decada",
        y="qtd",
        title="Quantidade de Filmes por Década",
        text="qtd",
    )

    # GRÁFICO 2: LINHA (nota média por década)
    medias = df_filtro.groupby("decada")["vote_average"].mean().reset_index()
    fig_linha = px.line(
        medias,
        x="decada",
        y="vote_average",
        markers=True,
        title="Nota Média por Década",
    )

    #  GRÁFICO 3: BOXPLOT (distribuição das notas por década)
    fig_box = px.box(
        df_filtro,
        x="decada",
        y="vote_average",
        points="all",
        title="Distribuição das Notas por Década (Boxplot)",
    )

    return fig_barra, fig_linha, fig_box



if __name__ == "__main__":
    app.run(debug=True)

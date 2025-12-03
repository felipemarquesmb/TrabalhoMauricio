import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html

df_dec = pd.read_csv("terror_decadas.csv")

# Preparo
df_dec["ano"] = df_dec["release_date"].str[:4]

# Gráficos
contagem = df_dec["decada"].value_counts().sort_index().reset_index()
contagem.columns = ["decada", "qtd"]
fig_contagem = px.bar(contagem, x="decada", y="qtd", title="Quantidade de filmes por década")

medias = df_dec.groupby("decada")["vote_average"].mean().reset_index()
fig_medias = px.line(medias, x="decada", y="vote_average", markers=True, title="Nota média por década")

pop = df_dec.groupby("decada")["popularity"].mean().reset_index()
fig_pop = px.line(pop, x="decada", y="popularity", markers=True, title="Popularidade média por década")

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Terror ao longo das décadas", style={"textAlign": "center"}),

    html.H2("Filmes por década"),
    dcc.Graph(figure=fig_contagem),

    html.H2("Nota média por década"),
    dcc.Graph(figure=fig_medias),

    html.H2("Popularidade média por década"),
    dcc.Graph(figure=fig_pop)
])

if __name__ == "__main__":
    app.run(debug=True)


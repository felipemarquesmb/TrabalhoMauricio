import requests 
import pandas as pd

API_KEY = "7302c45066156f82c4de35011d2ad782"

def coletar_terror_por_decada(inicio, fim):
    filmes = []
    page = 1

    while True:
        url = ("https://api.themoviedb.org/3/discover/movie"
            f"?api_key={API_KEY}"
            "&with_genres=27"
            f"&primary_release_date.gte={inicio}-01-01"
            f"&primary_release_date.lte={fim}-12-31"
            f"&page={page}")
        
        r = requests.get(url)
        dados = r.json()

        if "results" not in dados:
            break

        filmes.extend(dados["results"])

        if page >= dados["total_pages"]:
            break

        page += 1

    return filmes

decadas = {
    "1980-1989": (1980, 1989),
    "1990-1999": (1990, 1999),
    "2000-2009": (2000, 2009),
    "2010-2019": (2010, 2019),
    "2020-2025": (2020, 2025)
}

todos_os_filmes = []

for nome, (inicio, fim) in decadas.items():
    print(f"Coletando {nome}...")
    filmes = coletar_terror_por_decada(inicio, fim)
    for f in filmes:
        f["decada"] = nome
    todos_os_filmes.extend(filmes)

df = pd.DataFrame(todos_os_filmes)
df.to_csv("terror_decadas.csv", index=False)

print("Arquivo salvo como terror_decadas.csv!")



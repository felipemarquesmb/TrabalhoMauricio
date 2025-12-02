import requests
import pandas as pd
import os
import pickle
from time import sleep

API_KEY = "7302c45066156f82c4de35011d2ad782"
BASE_URL = "https://api.themoviedb.org/3"


SUBGENEROS = {
    "slasher": ["slasher", "serial killer", "knife", "stalker"],
    "found_footage": ["found footage"],
    "gore": ["gore", "extreme violence"],
    "paranormal": ["ghost", "demon", "haunted house"],
    "psicologico": ["psychological horror", "psychological thriller"]
}


CACHE_FILE = "cache_filmes.pkl"

def salvar_cache(data):
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(data, f)

def carregar_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "rb") as f:
            return pickle.load(f)
    return None


def coletar_filmes_terror(paginas=5):
    filmes = []
    
    for page in range(1, paginas + 1):
        url = (
            f"{BASE_URL}/discover/movie?api_key={API_KEY}"
            "&with_genres=27"
            "&sort_by=popularity.desc"
            f"&page={page}"
        )

        r = requests.get(url).json()
        filmes.extend(r.get("results", []))
        sleep(0.1)

    return filmes


def pegar_keywords(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/keywords?api_key={API_KEY}"
    r = requests.get(url).json()
    return [k["name"].lower() for k in r.get("keywords", [])]


def top10_por_subgenero(filmes):
    resultados = {}

    for subgenero, palavras in SUBGENEROS.items():
        filtrados = []

        for f in filmes:
            keywords = f.get("keywords", [])
            if any(p in keywords for p in palavras):
                filtrados.append(f)

        filtrados = sorted(filtrados, key=lambda x: x["popularity"], reverse=True)

        resultados[subgenero] = filtrados[:10]  # TOP 10

    return resultados


def main():
    cache = carregar_cache()
    if cache:
        print("📦 Cache carregado!")
        dados = cache
    else:
        print("⏳ Coletando filmes...")
        filmes = coletar_filmes_terror()

        print("🔍 Coletando keywords...")
        for f in filmes:
            f["keywords"] = pegar_keywords(f["id"])
            sleep(0.15)

        dados = filmes
        salvar_cache(dados)
        print("💾 Cache salvo!")

    print("🏆 Gerando Top 10 por subgênero...")
    top10 = top10_por_subgenero(dados)

    linhas = []
    for sub, filmes in top10.items():
        for f in filmes:
            linhas.append({
                "subgenero": sub,
                "titulo": f["title"],
                "popularidade": f["popularity"],
                "ano": f.get("release_date", "")[:4]
            })

    df = pd.DataFrame(linhas)
    df.to_csv("top10_subgeneros.csv", index=False)

    print("📁 Arquivo gerado: top10_subgeneros.csv")

if __name__ == "__main__":
    main()

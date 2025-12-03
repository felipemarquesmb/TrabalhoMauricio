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
        try:
            with open(CACHE_FILE, "rb") as f:
                return pickle.load(f)
        except Exception:
            print("Cache corrompido — recriando...")
            os.remove(CACHE_FILE)
            return None
    return None


def seguro_request(url):
    """Evita erros de SSL e timeout."""
    try:
        r = requests.get(url, timeout=10)
        return r.json()
    except Exception:
        print("Erro em requisição — tentando de novo...")
        sleep(1)
        try:
            r = requests.get(url, timeout=10)
            return r.json()
        except Exception:
            print("Falhou de novo — pulando...")
            return {}


def coletar_filmes_terror(paginas=5):
    filmes = []

    for page in range(1, paginas + 1):
        print(f"Página {page}...")
        url = (
            f"{BASE_URL}/discover/movie?api_key={API_KEY}"
            "&with_genres=27"
            "&sort_by=popularity.desc"
            f"&page={page}"
        )

        dados = seguro_request(url)
        filmes.extend(dados.get("results", []))
        sleep(0.2)  # espera leve para não sobrecarregar

    return filmes


def pegar_keywords(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/keywords?api_key={API_KEY}"
    dados = seguro_request(url)
    return [k["name"].lower() for k in dados.get("keywords", [])]


def top10_por_subgenero(filmes):
    resultados = {}

    for subgenero, palavras in SUBGENEROS.items():
        filtrados = []

        for f in filmes:
            keywords = f.get("keywords", [])
            if any(p in keywords for p in palavras):
                filtrados.append(f)

        filtrados = sorted(filtrados, key=lambda x: x["popularity"], reverse=True)

        resultados[subgenero] = filtrados[:10]

    return resultados


def main():
    cache = carregar_cache()
    if cache:
        print("Cache carregado!")
        filmes = cache
    else:
        print("Coletando filmes mais populares...")
        filmes = coletar_filmes_terror()

        print("Coletando keywords (pode levar 1–3 minutos)...")
        for f in filmes:
            f["keywords"] = pegar_keywords(f["id"])
            sleep(0.15)

        salvar_cache(filmes)
        print("Cache salvo!")

    print("🏆 Gerando Top 10 por subgênero...")
    top10 = top10_por_subgenero(filmes)

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

    print("Arquivo gerado: top10_subgeneros.csv")


if __name__ == "__main__":
    main()

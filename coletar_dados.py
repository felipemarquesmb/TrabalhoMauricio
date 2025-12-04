import requests
import pandas as pd
import time

API_KEY = "7302c45066156f82c4de35011d2ad782"
BASE_URL = "https://api.themoviedb.org/3"
GENRE_HORROR = 27

# Limites mais altos, mas seguros
MAX_PAGES = 200
SLEEP_BETWEEN_REQUESTS = 0.15

DECADAS = {
    "1980-1989": (1980, 1989),
    "1990-1999": (1990, 1999),
    "2000-2009": (2000, 2009),
    "2010-2019": (2010, 2019),
    "2020-2025": (2020, 2025),
}


def seguro_get(url, params=None):
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except:
        return {}


def coletar_por_decada(inicio, fim):
    filmes = []
    page = 1

    while True:
        params = {
            "api_key": API_KEY,
            "with_genres": GENRE_HORROR,
            "primary_release_date.gte": f"{inicio}-01-01",
            "primary_release_date.lte": f"{fim}-12-31",
            "page": page,
            "sort_by": "popularity.desc",
            "language": "en-US",
        }

        dados = seguro_get(f"{BASE_URL}/discover/movie", params)
        results = dados.get("results", [])
        total_pages = dados.get("total_pages", 1)

        if not results:
            break

        filmes.extend(results)

        if page >= total_pages:
            break

        if page >= MAX_PAGES:
            print(f"⚠ Limite seguro atingido ({MAX_PAGES} páginas).")
            break

        page += 1
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    return filmes


def main():
    todos = []
    print("\n=== COLETANDO DADOS REALISTAS ===\n")

    for dec, (inicio, fim) in DECADAS.items():
        print(f">>> Década {dec}")
        filmes = coletar_por_decada(inicio, fim)

        # FILTROS IMPORTANTES
        filtrados = []
        for f in filmes:
            if not f.get("release_date"):
                continue
            if f.get("vote_average", 0) < 1:
                continue
            if f.get("vote_count", 0) < 10:
                continue
            if f.get("popularity", 0) < 5:
                continue
            if GENRE_HORROR not in f.get("genre_ids", []):
                continue

            f["decada"] = dec
            filtrados.append(f)

        print(f"  Encontrados (filtrados): {len(filtrados)}\n")
        todos.extend(filtrados)

    df = pd.DataFrame(todos)

    # Criar coluna ano
    df["ano"] = df["release_date"].astype(str).str[:4]

    # Remover duplicados
    df = df.drop_duplicates(subset="id")

    df.to_csv("terror_decadas.csv", index=False)
    print("Arquivo salvo: terror_decadas.csv")
    print(f"TOTAL FINAL: {len(df)} filmes\n")


if __name__ == "__main__":
    main()

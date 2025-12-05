import requests      # biblioteca para fazer requisições HTTP (API TMDB)
import pandas as pd  # para criar o DataFrame e salvar CSV
import time          # para colocar pausas entre requisições

API_KEY = "7302c45066156f82c4de35011d2ad782"    # chave de acesso da API TMDB
BASE_URL = "https://api.themoviedb.org/3"       # URL base da API TMDB          
GENRE_HORROR = 27                               # ID do gênero Terror na API TMDB             


#  LIMITES DE SEGURANÇA PARA EVITAR BLOQUEIO DA API

MAX_PAGES = 200                # limite máximo de páginas por década (evita travar IP)
SLEEP_BETWEEN_REQUESTS = 0.15  # espera entre requisições (150ms -> seguro)

DECADAS = {
    "1980-1989": (1980, 1989),
    "1990-1999": (1990, 1999),
    "2000-2009": (2000, 2009),
    "2010-2019": (2010, 2019),
    "2020-2025": (2020, 2025),
}

# FUNÇÃO AUXILIAR: REQUISIÇÃO SEGURA À API
# Retorna sempre um dicionário. Se der erro na API,
# retornamos {} ao invés de quebrar o código.

def seguro_get(url, params=None):
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except:
        return {}


#  FUNÇÃO PRINCIPAL DE COLETA: baixa filmes de uma década

def coletar_por_decada(inicio, fim):
    filmes = []
    page = 1

    while True:
        # Parâmetros enviados para o endpoint discover/movie
        params = {
            "api_key": API_KEY,
            "with_genres": GENRE_HORROR,                    # garante que seja terror
            "primary_release_date.gte": f"{inicio}-01-01",
            "primary_release_date.lte": f"{fim}-12-31",
            "page": page,                                   # página da busca
            "sort_by": "popularity.desc",                   # ordena por popularidade
            "language": "en-US",                            # idioma dos dados
        }

        # Faz a requisição para a página atual
        dados = seguro_get(f"{BASE_URL}/discover/movie", params)
        
        # Extrai os resultados (lista de filmes)
        results = dados.get("results", [])

        # Quantidade total de páginas disponíveis segundo a API
        total_pages = dados.get("total_pages", 1)

        if not results:
            break

        filmes.extend(results)

        if page >= total_pages:
            break

        # Se atingir o limite de segurança -> parar
        if page >= MAX_PAGES:
            print(f"⚠ Limite seguro atingido ({MAX_PAGES} páginas).")
            break

        page += 1

        # Espera pequena para evitar bloqueio pelo TMDB
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    return filmes


# FUNÇÃO PRINCIPAL DO SCRIPT

def main():
    todos = []   # lista que armazenará todos os filmes de todas décadas
    print("\n=== COLETANDO DADOS REALISTAS ===\n")

    for dec, (inicio, fim) in DECADAS.items():
        print(f">>> Década {dec}")

        # coleta bruta -> sem filtragem
        filmes = coletar_por_decada(inicio, fim)

        # FILTROS IMPORTANTES
        # - remoção de filmes sem data
        # - remover filmes com nota suspeita (< 1)
        # - remover filmes com poucos votos (< 10)
        # - popularidade mínima para evitar filmes obscuros sem dados
        # - garantir que o filme realmente tem o gênero terror incluso

        filtrados = []
        for f in filmes:

            # Ignorar filmes sem data de lançamento
            if not f.get("release_date"):
                continue

            # Nota mínima (descarta notas 0 sem avaliações reais)
            if f.get("vote_average", 0) < 1:
                continue

            # Votos mínimos (descarta filmes com poucas avaliações)
            if f.get("vote_count", 0) < 10:
                continue

            # Popularidade mínima para remover filmes aleatórios da API
            if f.get("popularity", 0) < 5:
                continue

            # Confirma que o gênero terror está entre os gêneros do filme
            if GENRE_HORROR not in f.get("genre_ids", []):
                continue

            f["decada"] = dec
            filtrados.append(f)

        print(f"  Encontrados (filtrados): {len(filtrados)}\n")

        # Adiciona todos os filmes filtrados ao conjunto final
        todos.extend(filtrados)

    df = pd.DataFrame(todos)

    # Criar coluna ano
    df["ano"] = df["release_date"].astype(str).str[:4]

    # Remover duplicados
    df = df.drop_duplicates(subset="id")

    #  EXPORTAR RESULTADO PARA CSV
    
    df.to_csv("terror_decadas.csv", index=False)
    print("Arquivo salvo: terror_decadas.csv")
    print(f"TOTAL FINAL: {len(df)} filmes\n")


if __name__ == "__main__":
    main()

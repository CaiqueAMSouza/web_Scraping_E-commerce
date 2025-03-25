import requests
from bs4 import BeautifulSoup
import pandas as pd

# Função para extrair dados de uma página
def extrair_dados_pagina(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Referer": "https://www.magazineluiza.com.br/",
    }

    try:
        response = requests.get(url, headers=headers, verify=True)
    except requests.exceptions.SSLError as e:
        print(f"Erro de SSL: {e}")
        return None

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        produtos = soup.select('#__next > div > main > section:nth-child(5) > div.sc-cqaSWz.iEauxH > div > ul > li')

        nomes = []
        links = []
        precos = []

        for produto in produtos:
            try:
                # Extraindo o nome do produto
                nome = produto.find('h2').text.strip()
                nomes.append(nome)

                # Extraindo o link do produto
                link = produto.find('a')['href']
                link_completo = f"https://www.magazineluiza.com.br{link}"
                links.append(link_completo)

                # Extraindo o preço do produto e removendo "ou "
                preco = produto.find('p', {'data-testid': 'price-value'}).text.strip()
                preco = preco.replace("ou ", "")  # Remove o texto "ou "
                precos.append(preco)
            except AttributeError as e:
                print(f"Erro ao extrair dados de um produto: {e}")
                continue

        return pd.DataFrame({'nome': nomes, 'link': links, 'preco': precos})
    else:
        print(f"Erro ao acessar a página {url}: {response.status_code}")
        return None

# URL base da página de celulares e smartphones da Magazine Luiza
base_url = "https://www.magazineluiza.com.br/celulares-e-smartphones/l/te/"

# Lista para armazenar todos os dados
todos_dados = []

# Loop para percorrer todas as 17 páginas
for pagina in range(1, 18):
    url_pagina = f"{base_url}?page={pagina}"
    print(f"Extraindo dados da página {pagina}...")
    dados_pagina = extrair_dados_pagina(url_pagina)
    if dados_pagina is not None:
        todos_dados.append(dados_pagina)

# Concatenando todos os dados em um único DataFrame
if todos_dados:
    df_final = pd.concat(todos_dados, ignore_index=True)

    # Salvando os dados em um arquivo Excel (.xlsx)
    df_final.to_excel('produtos_magazine_luiza.xlsx', index=False)
    print("Dados salvos com sucesso em 'produtos_magazine_luiza.xlsx'")
else:
    print("Nenhum dado foi extraído.")
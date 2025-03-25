from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Configurações do Chrome
options = Options()
# options.add_argument("--headless")  # Remova o comentário para executar em modo headless
options.add_argument("--disable-gpu")  # Desabilitar aceleração por GPU
options.add_argument("--window-size=1920,1080")  # Definir tamanho da janela

# Inicializar o WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Lista para armazenar os dados dos produtos
produtos_data = []

# Lista de marcas conhecidas
marcas_conhecidas = ["Apple", "Samsung", "Xiaomi", "Motorola", "LG", "Asus", "Huawei", "Nokia", "Sony", "Infinix", "Realme","oppo",""]

# Função para identificar a marca a partir do nome do produto
def identificar_marca(nome_produto):
    for marca in marcas_conhecidas:
        if marca.lower() in nome_produto.lower():  # Verifica se a marca está no nome do produto
            return marca
    return "Outra"  # Se não encontrar a marca, retorna "Outra"

# Função para rolar a página e carregar todos os produtos
def scroll_page():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Aguardar o carregamento dos novos produtos
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# Função para coletar os produtos de uma página
def coletar_produtos():
    try:
        # Encontrar todos os elementos dos produtos
        produtos = driver.find_elements(By.CSS_SELECTOR, '#__next > div > main > section:nth-child(5) > div.sc-cqaSWz.iEauxH > div > ul > li')
        
        if produtos:
            for produto in produtos:
                try:
                    # Extrair nome do produto
                    nome = produto.find_element(By.CSS_SELECTOR, 'h2').text
                    
                    # Extrair link do produto
                    link = produto.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                    
                    # Extrair preço do produto
                    try:
                        preco = produto.find_element(By.CSS_SELECTOR, 'li a div.sc-fedTIj.cRoAUl div.sc-iGgWBj.ftWanB.sc-BQMaI.hJcuHp div div p[data-testid="price-value"]').text
                        
                        # Remover a palavra "ou" do preço, se existir
                        if "ou" in preco:
                            preco = preco.replace("ou", "").strip()  # Remove "ou" e espaços extras
                        
                        # Converter o preço para float (removendo "R$" e substituindo "," por ".")
                        preco_float = float(preco.replace("R$", "").replace(".", "").replace(",", "."))
                    except Exception as e:
                        print(f"Erro ao extrair preço: {e}")
                        preco = "Preço não disponível"
                        preco_float = None
                    
                    # Identificar a marca do produto
                    marca = identificar_marca(nome)
                    
                    # Adicionar os dados à lista
                    produtos_data.append({
                        'Nome': nome,
                        'Link': link,
                        'Preço': preco,
                        'Preço Float': preco_float,  # Adicionando o preço como float para cálculos
                        'Marca': marca  # Adicionando a marca do produto
                    })
                except Exception as e:
                    print(f"Erro ao extrair dados de um produto: {e}")
        else:
            print("Nenhum produto encontrado na página!")
    except Exception as e:
        print(f"Erro ao buscar produtos: {e}")


# Iterar sobre as páginas de 1 a 17
for pagina in range(1, 18):
    print(f"Coletando dados da página {pagina}...")
    
    # URL da página de produtos
    url = f'https://www.magazineluiza.com.br/celulares-e-smartphones/l/te/?page={pagina}'
    driver.get(url)

    try:
        # Aguardar o carregamento dos produtos
        WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#__next > div > main > section:nth-child(5) > div.sc-cqaSWz.iEauxH > div > ul'))
        )
        print(f"Página {pagina} carregada com sucesso!")

        # Rolagem da página para carregar todos os produtos
        scroll_page()

        # Coletar os produtos da página
        coletar_produtos()
    except Exception as e:
        print(f"Erro ao carregar a página {pagina}: {e}")


# Fechar o navegador
driver.quit()

# Processar os dados coletados
if produtos_data:
    # Converter a lista de produtos em um DataFrame
    df = pd.DataFrame(produtos_data)
    
    # Calcular a média dos preços
    media_preco = df['Preço Float'].mean()
    print(f"Média de preço dos produtos: R$ {media_preco:.2f}")

    
    frequencia_marcas = df['Marca'].value_counts()
    marca_mais_vendida = frequencia_marcas.idxmax()
    quantidade_mais_vendida = frequencia_marcas.max()

    # Adicionar a informação da marca mais vendida ao DataFrame
    df['Marca Mais Vendida'] = marca_mais_vendida
    df['Quantidade Mais Vendida'] = quantidade_mais_vendida

    # Exibir a marca mais vendida no console
    print(f"A marca mais vendida é {marca_mais_vendida} com {quantidade_mais_vendida} produtos.")


    df['media de preço:'] = media_preco
    
    # Adicionar uma coluna com a diferença em relação à média
    df['Diferença em Relação à Média'] = df['Preço Float'] - media_preco
    
    # Adicionar uma coluna com o status do preço (acima ou abaixo da média)
    df['Status do Preço'] = df['Diferença em Relação à Média'].apply(lambda x: 'Acima da Média' if x > 0 else 'Abaixo da Média')
    
    # Salvar os dados em um arquivo Excel
    df.to_excel('produtos_magalu.xlsx', index=False)
    print("Dados salvos em 'produtos_magalu_celular.xlsx'")
else:
    print("Nenhum dado foi coletado para salvar.")

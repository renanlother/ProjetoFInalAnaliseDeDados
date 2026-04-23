import requests 
import pandas as pd
from bs4 import BeautifulSoup
import time

dados = []

for pagina in range(1, 50):  # percorre 50 páginas
    url = f"https://site.gov.br/dados?page={pagina}"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")
    
    # extrai os dados da página atual
    registros = soup.find_all("div", class_="registro")
    for r in registros:
        dados.append({
            "nome": r.find("span", class_="nome").text.strip(),
            "valor": r.find("span", class_="valor").text.strip()
        })
    
    time.sleep(1)  # boa prática: não sobrecarregar o servidor

df = pd.DataFrame(dados)
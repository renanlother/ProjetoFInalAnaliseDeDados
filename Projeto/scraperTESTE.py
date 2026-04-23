import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

livros = []
pagina = 1

while True:
    url = f"https://books.toscrape.com/catalogue/page-{pagina}.html"
    response = requests.get(url)
    
    # quando acabar as páginas encerra o loop
    if response.status_code != 200:
        break
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    for livro in soup.find_all("article", class_="product_pod"):
        titulo = livro.find("h3").find("a")["title"]
        preco = livro.find("p", class_="price_color").text.strip()
        avaliacao = livro.find("p", class_="star-rating")["class"][1]
        
        livros.append({
            "titulo": titulo,
            "preco": preco,
            "avaliacao": avaliacao
        })
    
    print(f"Página {pagina} coletada — {len(livros)} livros até agora")
    pagina += 1
    time.sleep(1)

df = pd.DataFrame(livros)
df.to_csv("livros.csv", index=False)
print(f"{len(df)} livros salvos.")
import requests
import pandas as pd
import time

resultados = []

for ano in range(1990, 2025):
    pagina = 0
    
    while True:
        url = f"https://api.jolpi.ca/ergast/f1/{ano}/results.json"
        params = {
            "limit": 100,   # registros por página
            "offset": pagina * 100
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        corridas = data["MRData"]["RaceTable"]["Races"]
        
        # quando não há mais dados, para o loop
        if not corridas:
            break
        
        for corrida in corridas:
            for piloto in corrida["Results"]:
                resultados.append({
                    "ano":        ano,
                    "rodada":     corrida["round"],
                    "circuito":   corrida["Circuit"]["circuitName"],
                    "pais":       corrida["Circuit"]["Location"]["country"],
                    "piloto":     piloto["Driver"]["familyName"],
                    "equipe":     piloto["Constructor"]["name"],
                    "posicao":    piloto["position"],
                    "pontos":     piloto["points"],
                    "grid":       piloto["grid"],
                    "voltas":     piloto["laps"],
                    "status":     piloto["status"]
                })
        
        print(f"{ano} — página {pagina + 1} coletada")
        pagina += 1
        time.sleep(0.5)

df = pd.DataFrame(resultados)
df.to_csv("databases/f1_jolpica.csv", index=False)
print(f"\nPronto! {len(df)} registros salvos.")
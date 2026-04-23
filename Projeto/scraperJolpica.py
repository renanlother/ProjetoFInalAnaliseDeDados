import requests
import pandas as pd
import time

#lista de registros
resultados = []

#percorre cada temporada nesse range (1990-2024)
for ano in range(1990, 2025):
    pagina = 0
    
    #loop da paginação, enquanto tiver dados continua coletando
    while True:
        url = f"https://api.jolpi.ca/ergast/f1/{ano}/results.json"
        #parametros para controlar a paginação (100 registros por página)
        #offset é o número de registros a pular, ou seja, página 0 começa do registro 0, página 1 começa do registro 100, etc
        params = {
            "limit": 100,   #registros por página
            "offset": pagina * 100
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        #extrai as corridas do json gerado pela API
        corridas = data["MRData"]["RaceTable"]["Races"]
        
        #acabam os dados acaba o loop
        if not corridas:
            break
        
        #percorre cada corrida e cada piloto dentro dela
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
                    "status":     piloto["status"] #ex:Finished, Retired, Accident
                })
        
        print(f"{ano} — página {pagina + 1} coletada")
        pagina += 1
        time.sleep(0.5) #evita sobrecarregar o servidor

df = pd.DataFrame(resultados)
df.to_csv("databases/f1_jolpica.csv", index=False)
print(f"\nPronto! {len(df)} registros salvos.")
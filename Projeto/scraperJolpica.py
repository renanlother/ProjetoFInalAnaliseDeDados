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
        
        for tentativa in range(5): # tenta até 5 vezes caso a API falhe ou rate-limite
            response = requests.get(url, params=params) # faz a requisição
            if response.status_code == 429: # API retornou "too many requests"
                wait = 2 ** tentativa # backoff exponencial: 1, 2, 4, 8, 16 segundos
                print(f"Rate limit — aguardando {wait}s...") # avisa o usuário
                time.sleep(wait) # espera antes de tentar de novo
                continue # volta para o início do loop de tentativas
            if response.status_code != 200 or not response.text.strip(): # resposta vazia ou erro HTTP
                print(f"Resposta inesperada {response.status_code} em {ano} p{pagina+1}: {response.text[:200]}") # mostra o erro
                time.sleep(2) # pequena pausa antes de tentar de novo
                continue # tenta novamente
            break # resposta válida, sai do loop de tentativas
        else: # executado se o loop terminar sem break (todas as tentativas falharam)
            print(f"Falha após 5 tentativas em {ano} p{pagina+1}, pulando.") # avisa e abandona esta página
            break # sai do while True para ir para o próximo ano

        data = response.json() # converte a resposta para dicionário Python
        
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
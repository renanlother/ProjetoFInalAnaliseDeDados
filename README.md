# ProjetoFInalAnaliseDeDados
O projeto final da disciplina tem como objetivo aplicar, de forma integrada, os conceitos e ferramentas estudados ao longo do semestre para desenvolver um dashboard interativo de análise de dados utilizando Python e a biblioteca Dash.

Mais do que a construção técnica do dashboard, espera-se que os grupos realizem uma análise descritiva consistente e orientada à geração de insights, sendo capazes de interpretar os dados e extrair informações relevantes que apoiem a tomada de decisão ou a compreensão do fenômeno analisado.

Os grupos deverão conduzir todo o processo de análise de dados, desde a obtenção e preparação dos dados até a construção de visualizações interativas que comuniquem, de forma clara, os principais achados do projeto.

O tema é livre, porém o conjunto de dados deve permitir a realização de uma análise exploratória significativa e, principalmente, a identificação de padrões, relações e comportamentos que resultem em insights relevantes e bem fundamentados.

Sugere-se a utilização de bases públicas, como por exemplo:

    dados governamentais
    dados abertos
    bases de organizações públicas
    bases disponibilizadas em portais de dados abertos

Exemplos:

    dados do IBGE
    dados do DataSUS
    dados do Portal Brasileiro de Dados Abertos
    dados do Kaggle
    dados de mobilidade urbana
    dados econômicos
    dados educacionais

Requisitos do conjunto de dados

O dataset utilizado deve atender aos seguintes critérios:

    possuir no mínimo 10.000 registros
    conter pelo menos dois arquivos distintos
    possuir dados que permitam análise comparativa e geração de insights

 
Pipeline de Ciência de Dados

O projeto deverá contemplar as seguintes etapas:
1. Aquisição de dados

Leitura dos arquivos utilizando Python e Pandas. Opcionalmente, os alunos poderão desenvolver um crawler ou script de coleta automática de dados.
2. Integração de dados

Os dados provenientes de diferentes arquivos devem ser integrados utilizando operações de concatenação e merge. 
3. Limpeza e tratamento dos dados

O projeto deve demonstrar:

    tratamento de valores ausentes
    remoção de inconsistências
    padronização de formatos
    preparação dos dados para análise

4. Transformação de dados

Aplicação de técnicas vistas em aula, como:

    padronização
    criação de novas variáveis
    agregações

5. Análise exploratória

Os alunos deverão explorar os dados utilizando gráficos e estatísticas descritivas, buscando identificar padrões relevantes.

É obrigatório que a análise resulte na identificação de insights, tais como:

    tendências nos dados
    relações entre variáveis
    comportamentos inesperados
    comparações relevantes entre grupos
    possíveis explicações para os padrões observados

Os insights devem ser interpretados e contextualizados, não apenas apresentados. Ou seja, os alunos devem explicar o que foi encontrado e por que isso é relevante.

 
Construção do Dashboard

O projeto deverá conter dois dashboards distintos.

O dashboard não deve apenas apresentar gráficos, mas sim organizar e comunicar os principais insights obtidos na análise.

As visualizações devem ser escolhidas de forma intencional, de modo a facilitar a interpretação dos dados e destacar os padrões mais importantes identificados.
Dashboard 1 — Visão Geral

Este dashboard deve apresentar uma visão resumida dos dados, semelhante a um painel executivo.

Deve conter:

    principais indicadores
    gráficos sintéticos
    visualização clara e objetiva

Este dashboard deve ser pensado para comunicar rapidamente as informações mais importantes.
Dashboard 2 — Exploração Interativa

Este dashboard deve permitir que o usuário explore os dados de forma mais detalhada.

Requisitos mínimos:

    seleção de categorias
    comparação entre variáveis
    pelo menos 5 visualizações
    pelo menos 2 filtros interativos
    uso de diferentes tipos de gráficos
    organização clara das informações
    layout organizado

Design e comunicação visual

O dashboard deve seguir boas práticas de comunicação visual, incluindo:

    clareza das informações
    organização visual
    uso adequado de cores
    títulos e legendas explicativas

Recomenda-se seguir princípios apresentados no livro: Storytelling with Data — Cole Nussbaumer Knaflic

O dashboard deve buscar contar uma história com os dados, permitindo que o usuário compreenda rapidamente os principais padrões encontrados.

 
Bônus — Coleta automática de dados

Grupos que desenvolverem um crawler ou script de coleta automática de dados poderão receber:

+1 ponto no projeto

Este crawler pode, por exemplo:

    coletar dados de APIs

    extrair dados de páginas web

Entregáveis

Cada grupo deverá entregar:

    Código do projeto (Link para github ou o script) 

    Arquivo com os dados brutos utilizados

    Breve relatório em formato de apresentação explicando todo o pipeline:

        fonte dos dados
        etapas de preparação
        Os principais insights encontrados


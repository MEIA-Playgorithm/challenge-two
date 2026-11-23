# **Estado da Arte — Inteligência Artificial aplicada ao Basquetebol**

AAUTIA — Aprendizagem Automática | PLANTIA — Planeamento em Inteligência Artificial

**Tema do projeto:** *Sistema Inteligente de Apoio à Decisão de Treinadores de Basquetebol através de Machine Learning e Planeamento Automático.*

Esta primeira versão do estado da arte apresenta **trabalhos científicos reais, publicados e com referências verificáveis**, sobre previsão de resultados, avaliação de jogadores, composição de equipas, substituições, otimização e planeamento de estratégias.

A investigação foi organizada em duas partes, seguindo a divisão das unidades curriculares:

- **AAUTIA (50%)** — modelos preditivos, aprendizagem supervisionada, avaliação de desempenho e previsão de resultados.
- **PLANTIA (50%)** — escolha de alinhamentos, substituições, otimização de decisões, processos de Markov e planeamento sob incerteza.

Os trabalhos foram identificados através de editoras científicas, revistas académicas, repositórios universitários e publicações com DOI. A apresentação é feita em português, mantendo os títulos originais para facilitar a localização.

# **Parte I — Estado da Arte de AAUTIA**

## **1. Previsão de resultados no basquetebol europeu**

Lampis, T., Ntzoufras, I., Vassalos, V. e Dimitriou, S. (2023)

**Artigo:** *Predictions of European Basketball Match Results with Machine Learning Algorithms*

**Publicação:** Journal of Sports Analytics.

[Consultar artigo científico — DOI](https://doi.org/10.3233/JSA-220639?utm_source=chatgpt.com)

### **Objetivo e metodologia**

Este trabalho investiga a previsão de resultados de jogos de basquetebol em quatro competições europeias: EuroLeague, EuroCup, Liga Grega e Liga Espanhola ACB.

Os investigadores utilizaram **5 214 jogos realizados entre 2013 e 2018**, construindo indicadores a partir das estatísticas históricas das equipas.

Foram comparados vários modelos, nomeadamente:

- Regressão Logística;
- Random Forest;
- XGBoost;
- Combinações de modelos (*ensemble learning*).

O estudo utilizou ainda sistemas de classificação de equipas, como Elo, PageRank e *pi-rating*, e indicadores de desempenho para enriquecer os dados de entrada.

### **Resultados obtidos**

Os modelos com indicadores adicionais superaram os modelos de referência mais simples em aproximadamente 3 a 5 pontos percentuais de exatidão.

Não foi identificado um algoritmo universalmente superior. O desempenho dependeu da competição e das características dos dados.

Os autores também verificaram a importância dos indicadores de forma recente e dos sistemas de classificação na previsão dos resultados.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://journals.sagepub.com\&sz=32)

Sage Journals

### **Relevância para AAUTIA**

Este é um dos trabalhos mais importantes para o nosso projeto porque fornece uma metodologia diretamente reproduzível: construir características históricas, comparar algoritmos e avaliar previsões com métricas como *accuracy*, *F1-score* e *Brier score*.

**Aplicação proposta:** utilizar Regressão Logística, Random Forest e XGBoost para prever vitórias, comparando modelos baseados apenas em resultados com outros que incluam estatísticas das equipas e indicadores individuais.

## **2. Integração de XGBoost e IA explicável na previsão de resultados da NBA**

Ouyang, Y., Li, X., Zhou, W., Hong, W., Zheng, W., Qi, F. e Peng, L. (2024)

**Artigo:** *Integration of Machine Learning XGBoost and SHAP Models for NBA Game Outcome Prediction and Quantitative Analysis Methodology*

**Publicação:** PLOS ONE, 19(7), e0307478.

[Consultar artigo completo — acesso aberto](https://doi.org/10.1371/journal.pone.0307478?utm_source=chatgpt.com)

### **Objetivo e metodologia**

Os autores desenvolveram um sistema de previsão de resultados da NBA utilizando dados das temporadas de 2021 a 2023.

O trabalho combina duas tecnologias:

**XGBoost:** algoritmo de aprendizagem supervisionada baseado em conjuntos de árvores de decisão, utilizado para prever resultados.

**SHAP:** técnica de explicabilidade que permite estimar a contribuição das diferentes variáveis para as previsões realizadas pelo modelo.

O sistema analisa indicadores de desempenho e permite atualizar as previsões em diferentes momentos de uma partida.

### **Resultados e conclusões**

O estudo demonstra uma abordagem para prever resultados e identificar quais os indicadores estatísticos que mais influenciam as previsões.

A integração de SHAP permite interpretar os modelos, em vez de apresentar apenas uma probabilidade de vitória.

Os autores disponibilizaram também o código utilizado na investigação.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://journals.plos.org\&sz=32)

PLOS

[Código do trabalho no GitHub](https://github.com/YanOuyang514/NBA-game-outcome-prediction-and-quantitative-analysis-methodology?utm_source=chatgpt.com)

### **Relevância para AAUTIA**

Este artigo é especialmente útil porque o nosso projeto não deve limitar-se a informar o treinador de que existe determinada probabilidade de vitória.

Deve explicar **quais os fatores que contribuem para essa previsão**.

Por exemplo, o sistema poderá indicar que uma previsão foi influenciada pelo desempenho defensivo recente, pela eficiência dos lançamentos e pelo rendimento histórico de determinados alinhamentos.

Importa distinguir estas explicações estatísticas de afirmações causais sobre o que acontecerá se o treinador alterar uma decisão.

## **3. Previsão dos resultados da NBA com Machine Learning**

Horvat, T., Job, J., Logozar, R. e Livada, Č. (2023)

**Artigo:** *A Data-Driven Machine Learning Algorithm for Predicting the Outcomes of NBA Games*

**Publicação:** Symmetry, 15(4), 798.

[Consultar artigo científico](https://doi.org/10.3390/sym15040798?utm_source=chatgpt.com)

### **Objetivo e metodologia**

Este trabalho propõe um modelo baseado em dados para prever resultados de jogos da NBA.

Os autores dão particular importância à construção de indicadores estatísticos, procurando transformar os dados disponíveis em variáveis com capacidade preditiva.

O estudo estabelece uma formulação matemática para as estatísticas de basquetebol e para os indicadores derivados, utilizando-os na construção de modelos de aprendizagem automática.

### **Contributos**

Um dos aspetos relevantes é a preocupação com a definição rigorosa das variáveis utilizadas nos modelos.

A qualidade das características extraídas dos dados é determinante para a capacidade de generalização das previsões.

Este trabalho reforça a importância de construir uma base de dados coerente antes de escolher algoritmos mais complexos.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://doi.org\&sz=32)

DOI

### **Relevância para AAUTIA**

No nosso projeto, poderá servir de referência para construir indicadores como:

- eficiência ofensiva e defensiva;
- média de pontos nos últimos jogos;
- aproveitamento dos lançamentos;
- ressaltos ofensivos e defensivos;
- assistências e perdas de bola.

Estes indicadores devem ser calculados apenas com informação disponível antes de cada partida, evitando a utilização inadvertida de dados futuros.

## **4. Previsão de resultados durante o decorrer do jogo**

Kandhway, K. (2025)

**Artigo:** *In-Play Outcome Prediction of an Ongoing Basketball Game Using Machine Learning*

**Publicação:** Journal of Prediction Markets, 18(2).

[Consultar o artigo científico](https://doi.org/10.5750/jpm.v18i2.2155?utm_source=chatgpt.com)

### **Objetivo e metodologia**

Este trabalho investiga a previsão do vencedor de um jogo de basquetebol **enquanto a partida está a decorrer**.

Ao contrário dos modelos pré-jogo, o sistema atualiza as previsões com base na evolução da partida.

Foram utilizados dados da NBA correspondentes a oito temporadas, de 2015/2016 a 2022/2023.

O estudo integra técnicas de aprendizagem supervisionada e utiliza SHAP para interpretar a importância das diferentes variáveis.

### **Resultados obtidos**

Os autores reportam uma exatidão global de aproximadamente **74%**, com resultados que variam entre cerca de 63% e 90% em diferentes estados do jogo.

Os resultados mostram também que a importância das variáveis se altera ao longo da partida.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://doi.org\&sz=32)

DOI

### **Relevância para AAUTIA**

Este trabalho fundamenta uma evolução do nosso sistema para decisões em tempo real.

Por exemplo, o treinador poderia receber uma previsão atualizada após o terceiro período, considerando a diferença pontual, o tempo restante e as estatísticas acumuladas.

Numa primeira fase, considero preferível manter a previsão pré-jogo; a previsão dinâmica poderá constituir uma experiência complementar.

## **5. Revisão sistemática de aplicações de IA à previsão de basquetebol**

Li, C., Zhang, H., Zhang, Y., Shen, J. e An, R. (2025)

**Artigo:** *The Application of Artificial Intelligence Techniques in Predicting Game Outcomes of Professional Basketball League: A Systematic Review*

**Publicação:** PLOS ONE, 20(6), e0326326.

[Consultar revisão sistemática completa](https://doi.org/10.1371/journal.pone.0326326?utm_source=chatgpt.com)

### **Objetivo e metodologia**

Esta revisão analisa a aplicação de métodos de Inteligência Artificial à previsão de resultados em ligas profissionais de basquetebol.

Foram incluídos **34 estudos científicos**, com uma janela de pesquisa centrada em trabalhos publicados entre 2019 e 2024.

A revisão compara diferentes abordagens, incluindo redes neuronais, Random Forest e modelos combinados.

### **Conclusões**

Os autores identificam resultados promissores para diferentes algoritmos e salientam a importância da seleção de características e da preparação dos dados.

Recomendam também melhorias na validação dos modelos, maior diversidade de competições analisadas e investigação sobre previsão dinâmica e transferência de aprendizagem.

Alguns trabalhos analisados reportam valores de exatidão muito elevados. Porém, esses resultados não devem ser entendidos como desempenhos garantidos ou diretamente comparáveis, porque os conjuntos de dados, as variáveis e os procedimentos de validação diferem.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://journals.plos.org\&sz=32)

PLOS

### **Relevância para AAUTIA**

Este será um artigo central da introdução e do enquadramento científico.

Permite justificar a seleção dos algoritmos, identificar abordagens já exploradas e estabelecer critérios de avaliação para o trabalho experimental.

# **Parte II — Estado da Arte de PLANTIA**

Esta parte é especialmente importante para diferenciar o projeto de um simples sistema de previsão.

O objetivo passa a ser investigar trabalhos nos quais a informação estatística é utilizada para **escolher ações, comparar estratégias e apoiar decisões dos treinadores**.

## **6. Modelação de substituições através de processos estocásticos**

Bhat, H. S., Huang, L.-H. e Rodriguez, S.

**Artigo:** *Learning Stochastic Models for Basketball Substitutions from Play-by-Play Data*

**Publicação:** CEUR Workshop Proceedings, Volume 1970.

[Consultar artigo científico — PDF integral](https://ceur-ws.org/Vol-1970/paper-08.pdf?utm_source=chatgpt.com)

### **Objetivo e metodologia**

Este é um dos trabalhos mais próximos do projeto que pretendemos desenvolver.

Os investigadores procuraram modelar a dinâmica das substituições no basquetebol, utilizando dados *play-by-play* de todos os jogos da fase regular da NBA de 2014/2015.

Foram considerados dois elementos:

1. A evolução dos diferentes conjuntos de cinco jogadores em campo.
2. O desempenho associado a cada alinhamento, medido através do diferencial de pontos (*plus/minus*).

O processo de substituição foi representado através de uma **cadeia de Markov de tempo contínuo**, com taxas de transição estimadas a partir dos dados.

Foram igualmente utilizadas técnicas de regressão para estimar o desempenho de cada alinhamento.

### **Resultados obtidos**

O modelo foi utilizado para simular os playoffs da NBA.

Os autores conseguiram prever corretamente os vencedores de **12 das 15 séries**, correspondendo a uma taxa de acerto de 80% nessa avaliação específica.

Este resultado deve ser interpretado com prudência devido à dimensão reduzida da amostra de séries.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://ceur-ws.org\&sz=32)

ceur-ws.org

### **Relevância para PLANTIA**

Este trabalho fornece uma fundamentação direta para construir um módulo que simula diferentes decisões de substituição.

No nosso projeto, poderíamos utilizar um modelo semelhante para estimar transições entre alinhamentos e testar políticas alternativas.

**Limitação:** o artigo modela substituições observadas e simula resultados; não demonstra, por si só, que as substituições recomendadas por uma política diferente seriam causalmente superiores.

## **7. Planeamento de estratégias de lançamento com processos de decisão de Markov**

Sandholtz, N. e Bornn, L. (2020)

**Artigo:** *Markov Decision Processes with Dynamic Transition Probabilities: An Analysis of Shooting Strategies in Basketball*

**Publicação:** The Annals of Applied Statistics, 14(3), 1122–1145.

[Consultar artigo científico — DOI](https://doi.org/10.1214/20-AOAS1348?utm_source=chatgpt.com)[Consultar PDF integral](https://www.lukebornn.com/papers/sandholtz_aoas_2020.pdf?utm_source=chatgpt.com)

### **Objetivo e metodologia**

O trabalho utiliza **Processos de Decisão de Markov (MDP)** para estudar decisões relacionadas com lançamentos no basquetebol.

Os investigadores consideram que as decisões são influenciadas pelo estado da posse de bola, pela localização dos jogadores e pelo tempo disponível no relógio de lançamento.

A metodologia combina:

- Processos de decisão de Markov não estacionários;
- Modelos Bayesianos hierárquicos;
- Estimação de probabilidades de transição;
- Simulação de políticas alternativas.

Uma característica importante é que as probabilidades de transição variam ao longo da posse de bola, refletindo a pressão crescente para lançar antes de terminar o tempo disponível.

### **Contributos e resultados**

Os autores desenvolveram um simulador capaz de comparar políticas de lançamento e analisar alterações na eficiência e na produção ofensiva esperadas.

O estudo demonstra como utilizar modelos probabilísticos para experimentar decisões alternativas em vez de observar apenas o comportamento histórico das equipas.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.lukebornn.com\&sz=32)

lukebornn.com

### **Relevância para PLANTIA**

Este trabalho é particularmente útil para definir formalmente um problema de planeamento.

Podemos adaptar a abordagem de MDP para representar decisões do treinador:

\\[ MDP=(S,A,T,R,\gamma) \\]

Em que:

- \\(S\\) representa os estados do jogo e dos jogadores;
- \\(A\\) representa decisões possíveis;
- \\(T\\) define as probabilidades de transição;
- \\(R\\) representa a recompensa associada às decisões;
- \\(\gamma\\) é o fator de desconto das recompensas futuras.

A extensão para escolha de alinhamentos e gestão de fadiga será uma proposta do nosso projeto, e não uma funcionalidade já demonstrada neste artigo.

## **8. Avaliação e gestão de alinhamentos através de modelos estatísticos**

Grassetti, L., Bellio, R., Di Gaspero, L., Fonseca, G. e Vidoni, P. (2021)

**Artigo:** *An Extended Regularized Adjusted Plus-Minus Analysis for Lineup Management in Basketball Using Play-by-Play Data*

**Publicação:** IMA Journal of Management Mathematics, 32(4), 385–409.

[Consultar artigo científico](https://doi.org/10.1093/imaman/dpaa022?utm_source=chatgpt.com)

### **Objetivo e metodologia**

Os investigadores procuraram avaliar a eficiência das diferentes combinações de cinco jogadores utilizadas durante os jogos.

Utilizaram dados *play-by-play* e estatísticas de **240 partidas da EuroLeague 2018/2019**.

O trabalho parte do indicador *Adjusted Plus-Minus* e desenvolve um modelo estatístico que permite avaliar contribuições individuais e coletivas.

A abordagem utiliza regularização Bayesiana e distribuições posteriores para analisar e ordenar jogadores e alinhamentos.

### **Contributos**

O modelo permite distinguir diferentes dimensões de desempenho e analisar os efeitos individuais e coletivos dos jogadores.

Os autores destacam a utilidade desta informação para a gestão de equipas e para atualizar avaliações ao longo da temporada.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://doi.org\&sz=32)

DOI

### **Relevância para PLANTIA**

No nosso projeto, o planeador precisa de estimar o valor de diferentes combinações de jogadores.

Este artigo fornece uma base científica para essa avaliação.

Por exemplo, em vez de escolher simplesmente os cinco jogadores com melhores estatísticas individuais, o sistema poderá considerar a eficiência conjunta de cada alinhamento.

A estimativa estatística do desempenho seria fornecida ao algoritmo de planeamento, que procuraria selecionar uma combinação adequada às restrições definidas.

## **9. Modelo híbrido de otimização de alinhamentos**

Rodríguez Aguilar, R., Infante-Escudero, R. e Marmolejo Saucedo, J. A. (2020)

**Artigo:** *A Hybrid Model for Improving the Performance of Basketball Lineups*

**Publicação:** Data Analysis and Optimization for Engineering and Computing Problems, Springer.

[Consultar publicação científica](https://doi.org/10.1007/978-3-030-48149-0_5?utm_source=chatgpt.com)[Registo no repositório da Universidade Panamericana](https://scripta.up.edu.mx/handle/20.500.12552/1768?utm_source=chatgpt.com)

### **Objetivo e metodologia**

Este estudo apresenta um modelo de otimização dos alinhamentos de equipas da NBA.

A abordagem procura selecionar conjuntos de jogadores com melhor desempenho, recorrendo a técnicas de otimização e à avaliação de eficiência técnica.

Os autores consideram diferentes variáveis de entrada e de resultado para comparar as combinações escolhidas.

### **Resultados**

Segundo o resumo publicado, os alinhamentos selecionados pelo modelo apresentaram maior eficiência técnica na avaliação efetuada.

Os autores concluem que a combinação de métodos de otimização e avaliação de eficiência pode apoiar decisões na gestão de equipas.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://scripta.up.edu.mx\&sz=32)

Universidad Panamericana

### **Relevância para PLANTIA**

Este trabalho permite justificar a utilização de programação matemática para a seleção de jogadores.

No nosso sistema, poderemos definir variáveis binárias:

\\[ x_i= \begin{cases} 1,&\text{se o jogador }i\text{ for selecionado}\\\ 0,&\text{caso contrário} \end{cases} \\]

Com a restrição:

\\[ \sum\_{i=1}^{n}x_i=5 \\]

O planeador deverá escolher exatamente cinco jogadores, respeitando também restrições de disponibilidade, fadiga ou composição da equipa.

Esta formulação específica é uma proposta de implementação para o nosso projeto.

## **10. Avaliação de rotações através de cadeias de Markov**

Kolias, P., Stavropoulos, N. e colaboradores (2022)

**Artigo:** *Evaluating Basketball Player's Rotation Line-Ups Performance via Statistical Markov Chain Modelling*

**Publicação:** International Journal of Sports Science & Coaching, 17(1).

[Consultar artigo científico](https://doi.org/10.1177/17479541211009083?utm_source=chatgpt.com)

### **Objetivo e metodologia**

O estudo investiga o desempenho ofensivo e defensivo de diferentes alinhamentos utilizados por equipas da Liga Grega de Basquetebol.

Os investigadores analisaram **1 131 fases de posse de bola**.

Foram calculados indicadores de eficiência ofensiva e defensiva associados a diferentes formações, utilizando modelação estatística e estimativas das posses de bola.

### **Contributos**

O estudo fornece uma metodologia quantitativa para comparar alinhamentos, atendendo às necessidades específicas da equipa.

A análise pode apoiar a escolha entre formações com diferentes características ofensivas ou defensivas.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://journals.sagepub.com\&sz=32)

Sage Journals

### **Relevância para PLANTIA**

No nosso projeto, o treinador poderá definir objetivos diferentes:

- Recuperar uma desvantagem pontual;
- Preservar uma vantagem nos minutos finais;
- Melhorar a eficiência defensiva;
- Manter um alinhamento equilibrado.

A avaliação dos alinhamentos permitirá comparar opções em função do objetivo.

É necessário distinguir esta avaliação estatística da otimização das substituições futuras: a segunda exigirá um algoritmo adicional de planeamento.

## **11. Aprendizagem por reforço para estratégias táticas**

Chen, X. e colaboradores (2022)

**Artigo:** *ReLiable: Offline Reinforcement Learning for Tactical Strategies in Professional Basketball Games*

**Publicação:** Proceedings of the 31st ACM International Conference on Information & Knowledge Management (CIKM 2022), pp. 3023–3032.

[Consultar publicação científica na ACM](https://doi.org/10.1145/3511808.3557105?utm_source=chatgpt.com)

### **Objetivo e metodologia**

Este trabalho investiga a aplicação de **aprendizagem por reforço offline** à análise de estratégias táticas no basquetebol profissional.

A abordagem procura aprender políticas de decisão a partir de dados históricos, sem depender de executar novas ações durante jogos reais.

Este ponto é importante porque experimentar livremente estratégias durante uma competição profissional pode ser inviável.

### **Contributos**

O artigo apresenta uma abordagem para estudar políticas de decisão num ambiente desportivo dinâmico, considerando a natureza sequencial das ações e a informação disponível nos registos históricos.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://doi.org\&sz=32)

DOI

### **Relevância para PLANTIA**

Este trabalho será uma referência para uma eventual extensão com Reinforcement Learning.

Contudo, não recomendo começar diretamente por aprendizagem por reforço.

Primeiro, devemos construir um simulador e validar as suas transições. Só depois fará sentido investigar se um agente consegue aprender políticas superiores às estratégias definidas previamente.

## **12. Redes de substituições e desempenho competitivo**

Guo, T., Cui, Y., Min, W., Zhang, W., Mi, J. e Shen, Y. (2023)

**Artigo:** *Exploring the Relationship Between Basketball Rotation and Competitive Performance Using Substitution Network Analysis*

**Publicação:** Journal of Sports Sciences.

[Consultar artigo científico](https://doi.org/10.1080/02640414.2023.2189216?utm_source=chatgpt.com)

### **Objetivo e metodologia**

Os investigadores estudaram as relações entre os padrões de substituição dos jogadores e o desempenho competitivo das equipas.

Foram analisados **574 214 eventos de substituição**, recolhidos ao longo de dez temporadas da NBA.

As substituições foram representadas através de redes, permitindo estudar as relações entre jogadores, a estrutura das rotações e os padrões associados ao desempenho.

### **Resultados**

O estudo identificou associações entre características das redes de substituição e o desempenho das equipas.

Os autores concluíram que a análise de redes pode fornecer informação útil para a gestão dos jogadores e para a organização das rotações.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.tandfonline.com\&sz=32)

Taylor & Francis Online

### **Relevância para PLANTIA**

Esta abordagem é especialmente interessante para complementar o planeamento.

Podemos construir uma rede na qual os nós representam jogadores e as ligações representam relações de substituição ou coexistência em campo.

O planeador poderá utilizar esses indicadores como parte da avaliação dos alinhamentos.

As associações identificadas são observacionais; não devemos concluir automaticamente que reproduzir determinada rede de substituições melhora o desempenho.

# **Parte III — Análise crítica e relação com o projeto**

## **13. Comparação dos trabalhos encontrados**

A tabela seguinte resume os trabalhos mais relevantes, os métodos utilizados e a sua possível aplicação.

| Referência                      | Área    | Métodos principais                    | Contributo para o projeto      |
| ------------------------------- | ------- | ------------------------------------- | ------------------------------ |
| Lampis et al. (2023)            | AAUTIA  | Regressão Logística, RF, XGBoost, Elo | Previsão de vitórias           |
| Ouyang et al. (2024)            | AAUTIA  | XGBoost, SHAP                         | Previsão explicável            |
| Horvat et al. (2023)            | AAUTIA  | ML, indicadores estatísticos          | Engenharia de características  |
| Kandhway (2025)                 | AAUTIA  | ML supervisionado, SHAP               | Previsão durante o jogo        |
| Li et al. (2025)                | AAUTIA  | Revisão sistemática                   | Seleção e avaliação de modelos |
| Bhat et al.                     | PLANTIA | Cadeias de Markov, regressão          | Modelação de substituições     |
| Sandholtz e Bornn (2020)        | PLANTIA | MDP, modelos Bayesianos               | Políticas e simulação          |
| Grassetti et al. (2021)         | PLANTIA | Modelos Bayesianos, plus-minus        | Avaliação de alinhamentos      |
| Rodríguez Aguilar et al. (2020) | PLANTIA | Otimização matemática                 | Seleção do cinco               |
| Kolias et al. (2022)            | PLANTIA | Cadeias de Markov                     | Avaliação de rotações          |
| Chen et al. (2022)              | PLANTIA | Reinforcement Learning offline        | Aprendizagem de políticas      |
| Guo et al. (2023)               | PLANTIA | Análise de redes                      | Estruturas de substituições    |

## **14. Que problemas continuam por resolver?**

Os estudos analisados mostram que existem abordagens consolidadas para prever resultados e avaliar o desempenho das equipas. Também existem trabalhos relevantes sobre substituições, alinhamentos e políticas táticas.

Contudo, a literatura identificada revela oportunidades para investigar a sua integração.

**Previsão de resultados**

Está amplamente estudada. Existem modelos de ML comparados em diferentes competições e temporadas.

**Avaliação de jogadores e alinhamentos**

Existem modelos estatísticos e métodos de otimização que permitem estimar o desempenho de diferentes combinações de jogadores.

**Planeamento integrado de várias jornadas**

Os trabalhos apresentados não demonstram diretamente uma solução completa que combine previsão de vitórias, seleção do cinco, gestão de minutos, fadiga e cumprimento de objetivos ao longo de vários jogos.

**Avaliação do efeito das decisões**

Não basta observar que um alinhamento venceu mais jogos. É necessário considerar o adversário, o contexto da partida e a incerteza para estimar o que poderia acontecer após uma decisão alternativa.

Esta análise não demonstra que não existam outros sistemas integrados. Identifica uma oportunidade de investigação **a partir do conjunto de publicações aqui verificado**.

## **15. Proposta de contribuição científica**

A contribuição pretendida será a integração de dois módulos que normalmente são analisados de forma separada.

AAUTIA

**Aprender a prever**

Prever probabilidades de vitória e desempenho dos alinhamentos

PLANTIA

**Aprender a decidir**

Comparar sequências de escolhas, restrições e resultados esperados

**Sistema integrado de apoio ao treinador**

Escolha do cinco, distribuição de minutos, rotação, simulação e planeamento de objetivos

### **Questões de investigação propostas**

**Q1 — AAUTIA:** Qual dos algoritmos de ML estudados apresenta melhor desempenho na previsão de resultados de jogos de basquetebol, utilizando indicadores históricos e estatísticas dos jogadores?

**Q2 — AAUTIA:** Em que medida a inclusão de informação sobre os alinhamentos melhora a capacidade preditiva dos modelos?

**Q3 — PLANTIA:** Como formular a seleção de jogadores e a distribuição de minutos como um problema de otimização sujeito a restrições?

**Q4 — PLANTIA:** Qual dos métodos de planeamento testados apresenta melhores resultados na maximização das vitórias esperadas e no cumprimento dos objetivos definidos?

**Q5 — Integração:** A utilização de previsões produzidas por ML melhora os resultados simulados de um planeador, quando comparado com estratégias fixas ou heurísticas simples?

## **16. Experiências propostas a partir do estado da arte**

| Experiência                                          | UC               | Referências de apoio              |
| ---------------------------------------------------- | ---------------- | --------------------------------- |
| E1 — Comparação de três modelos para prever vitórias | AAUTIA           | Lampis, Horvat                    |
| E2 — Importância das variáveis e explicabilidade     | AAUTIA           | Ouyang, Kandhway                  |
| E3 — Previsão de rendimento dos alinhamentos         | AAUTIA           | Grassetti, Kolias                 |
| E4 — Otimização do cinco inicial                     | PLANTIA          | Rodríguez Aguilar, Grassetti      |
| E5 — Modelação de substituições por Markov           | PLANTIA          | Bhat, Kolias                      |
| E6 — Comparação de planeamento por simulação e MDP   | PLANTIA          | Sandholtz, Chen                   |
| E7 — Planeamento integrado de cinco jogos            | AAUTIA + PLANTIA | Integração proposta neste projeto |

As experiências deverão ser comparadas em dados de teste cronologicamente posteriores aos dados de treino. Para o planeamento, será essencial definir o mesmo ambiente simulado e as mesmas restrições para todos os algoritmos, evitando comparações injustas.

## **17. Texto de síntese para incluir no relatório**

### Síntese do Estado da Arte e Motivação do Trabalho

A aplicação da Inteligência Artificial ao basquetebol tem evoluído significativamente, especialmente nas áreas da previsão de resultados, avaliação do desempenho individual e coletivo, análise tática e apoio à decisão dos treinadores.

No domínio da Aprendizagem Automática, Lampis et al. (2023) demonstraram a aplicação de algoritmos como Regressão Logística, Random Forest e XGBoost à previsão de resultados de competições europeias de basquetebol. O estudo evidenciou a importância da utilização de indicadores históricos de desempenho e de sistemas de classificação das equipas para melhorar a capacidade preditiva dos modelos.

Ouyang et al. (2024) exploraram a integração de XGBoost com técnicas de Inteligência Artificial Explicável, nomeadamente SHAP, permitindo não apenas prever resultados, mas também identificar as variáveis que mais contribuem para as previsões. Esta dimensão é particularmente relevante em sistemas de apoio à decisão, nos quais a compreensão dos resultados apresentados constitui um requisito importante.

No domínio do Planeamento em Inteligência Artificial, Bhat, Huang e Rodriguez desenvolveram modelos estocásticos para representar substituições entre alinhamentos de jogadores, utilizando dados detalhados de eventos da NBA. Sandholtz e Bornn (2020) aplicaram Processos de Decisão de Markov à análise de estratégias de lançamento, demonstrando a possibilidade de utilizar modelos probabilísticos e simulação para comparar diferentes políticas de decisão.

Por sua vez, Grassetti et al. (2021) investigaram a avaliação de alinhamentos através de modelos estatísticos baseados em dados *play-by-play*, enquanto Rodríguez Aguilar et al. (2020) apresentaram um modelo de otimização para apoiar a seleção de combinações de jogadores.

Apesar dos contributos identificados, permanece relevante investigar a integração de modelos preditivos com técnicas de planeamento automático para apoiar decisões que envolvem simultaneamente a escolha de jogadores, a gestão dos minutos de utilização e a definição de objetivos competitivos ao longo de várias partidas.

Neste contexto, o presente trabalho propõe desenvolver um sistema inteligente de apoio à decisão de treinadores de basquetebol, integrando algoritmos de Machine Learning com métodos de planeamento e otimização sob restrições.

O sistema terá como objetivo estimar probabilidades de resultado, avaliar alternativas de composição da equipa e comparar estratégias de gestão dos jogadores ao longo de um horizonte temporal definido.

A avaliação experimental permitirá analisar a qualidade dos modelos preditivos e comparar diferentes algoritmos de planeamento, considerando objetivos como maximizar vitórias esperadas, gerir a utilização do plantel e aumentar a probabilidade simulada de atingir metas competitivas.

Deste modo, pretende-se contribuir para a investigação de sistemas integrados de previsão e planeamento aplicados ao basquetebol, com particular atenção à explicabilidade, à incerteza dos modelos e à avaliação rigorosa das decisões recomendadas.

## **18. Referências prioritárias para leitura**

Para iniciar a leitura dos artigos completos, selecionaria estes seis trabalhos, por ordem de utilidade para o projeto:

| Prioridade | Trabalho                                                                                        | Motivo                                             |
| ---------- | ----------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| 1          | [Lampis et al. (2023)](https://doi.org/10.3233/JSA-220639?utm_source=chatgpt.com)               | Metodologia de comparação de ML                    |
| 2          | [Bhat et al. — Substituições](https://ceur-ws.org/Vol-1970/paper-08.pdf?utm_source=chatgpt.com) | Aproximação direta ao módulo de treinador          |
| 3          | [Sandholtz e Bornn (2020)](https://doi.org/10.1214/20-AOAS1348?utm_source=chatgpt.com)          | Fundamentação do planeamento por MDP               |
| 4          | [Grassetti et al. (2021)](https://doi.org/10.1093/imaman/dpaa022?utm_source=chatgpt.com)        | Modelação do desempenho de alinhamentos            |
| 5          | [Ouyang et al. (2024)](https://doi.org/10.1371/journal.pone.0307478?utm_source=chatgpt.com)     | XGBoost e explicabilidade                          |
| 6          | [Chen et al. (2022)](https://doi.org/10.1145/3511808.3557105?utm_source=chatgpt.com)            | Políticas táticas e Reinforcement Learning offline |

**Conclusão:** estes trabalhos permitem sustentar cientificamente um projeto dividido entre AAUTIA e PLANTIA, com objetivos próprios para cada unidade curricular e uma componente de integração comum.

A próxima etapa do estado da arte deverá ser aprofundar a comparação dos métodos, incluindo formulações matemáticas, datasets utilizados, resultados quantitativos, limitações e critérios de avaliação. Isso permitirá transformar esta revisão inicial numa secção académica completa, com referências bibliográficas normalizadas em IEEE ou APA.

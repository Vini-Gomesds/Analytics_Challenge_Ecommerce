# Entendimento do negócio (CRISP-DM, fase 1)

## Contexto

A Olist conecta pequenos e médios lojistas a grandes marketplaces brasileiros por meio de um único contrato. A base pública reúne cerca de 100 mil pedidos feitos entre 2016 e 2018, com clientes, itens, produtos, vendedores, pagamentos, avaliações e geolocalização por CEP. Os dados são reais e foram anonimizados.

## Público e decisão apoiada

O público são investidores e acionistas do setor de e-commerce. A decisão que o estudo apoia é a alocação de capital: em quais alavancas investir para crescer a receita de forma sustentável.

## Pergunta do estudo

**Onde a Olist deve priorizar seus próximos investimentos, entre logística, retenção de clientes e portfólio de categorias e regiões, para sustentar o crescimento da receita?**

A resposta é uma recomendação de investimento priorizada, apoiada nos dados e com um indicador de acompanhamento para cada alavanca.

## Perguntas norteadoras

### P1. Desempenho comercial

Como a receita evoluiu entre 2017 e 2018 e onde ela está concentrada?

- O que revela ao investidor: o ritmo de crescimento e o risco de concentração.
- Métricas: receita, pedidos, valor médio por pedido, crescimento de jan–ago/2018 sobre jan–ago/2017, participação das 10 maiores categorias e dos estados, e meios de pagamento.

### P2. Logística e satisfação

Quanto o atraso na entrega se relaciona com a insatisfação do cliente, e onde o problema é mais grave?

- O que revela ao investidor: o principal risco operacional e de reputação.
- Métricas: prazo de entrega, % de pedidos atrasados, folga do prazo prometido, nota média e % de insatisfeitos por faixa de atraso, e atraso por estado.

### P3. Retenção e valor do cliente

Os clientes voltam a comprar, e a primeira experiência influencia essa volta?

- O que revela ao investidor: se o crescimento é sustentável ou depende só da conquista de novos clientes.
- Métricas: % de clientes que voltaram, dias até a 2ª compra, retenção por mês da 1ª compra, grupos de clientes por valor e tempo sem comprar, e volta por nota da 1ª compra.

## Hipóteses e resultados

| ID | Hipótese | Como foi testada | Resultado |
| --- | --- | --- | --- |
| H1 | A receita está concentrada em São Paulo e em poucas categorias | Participação dos estados e das 10 maiores categorias na receita | **Confirmada em parte.** São Paulo tem 38,3% da receita, e o Sudeste, cerca de 64%; as 10 maiores categorias somam 62,4%, mas nenhuma passa de cerca de 9% |
| H2 | O atraso na entrega é o principal detrator da avaliação | Nota média e % de insatisfeitos por faixa de atraso | **Confirmada em parte.** A nota cai de 4,3 para 2,3 com o atraso, e a insatisfação vai de cerca de 10% para até 80%; outros fatores, como o frete, não foram comparados |
| H3 | A recompra é baixa, e o crescimento depende da conquista constante de novos clientes | % de clientes que voltaram, retenção por mês da 1ª compra e evolução da receita | **Confirmada.** Só 2,2% dos clientes voltaram, a retenção fica abaixo de 1% em todos os meses e a receita parou de crescer em 2018 |

## Critérios de sucesso

- **Negócio:** recomendação de investimento priorizada, com um indicador de acompanhamento para cada alavanca.
- **Análise:** cada pergunta respondida com as métricas de [definicoes_metricas.md](definicoes_metricas.md) e números conciliados entre o script e o painel.
- **Entrega:** relatório, apresentação e vídeo contam a mesma história, e o repositório reproduz as tabelas tratadas com um comando.

## Escopo

- **Inclui:** 8 das 9 tabelas da base e os pedidos de jan/2017 a ago/2018, sem cancelados e indisponíveis.
- **Não inclui:** dados externos, a tabela de geolocalização, o texto dos comentários das avaliações e previsões de receita. As decisões estão registradas em [qualidade_dados.md](qualidade_dados.md).

## Premissas e limitações

- Ferramentas: Python na exploração e no tratamento, e Power BI no modelo, nas medidas e no painel.
- Os dados vêm de uma única fonte pública e vão até agosto de 2018: as conclusões valem como estudo de caso, e não como diagnóstico atual da empresa.
- As análises mostram associações, e não relações de causa e efeito.
- A base não traz custos nem margens, o que impede calcular o retorno de cada investimento.
# Definições de métricas

Cada métrica tem uma única definição, aplicada no script de tratamento (`src/transformacoes.py`) e nas medidas do Power BI. Os nomes das tabelas e colunas seguem o [dicionário de dados](dicionario_dados.md).

## Regras gerais

| Regra | Definição |
| --- | --- |
| Período | Pedidos com data de compra de 01/01/2017 a 31/08/2018 |
| Pedido válido | Status diferente de cancelado (`canceled`) e indisponível (`unavailable`) |
| Pedido entregue | Status entregue (`delivered`) e data de entrega preenchida |
| Cliente | A pessoa (`customer_unique_id`); o `customer_id` muda a cada pedido |
| Compra | Uma data de compra do cliente; pedidos no mesmo dia contam como uma compra só |
| Avaliação | Uma por pedido: a resposta mais recente |
| Receita | Preço dos produtos, sem frete. O valor pago inclui frete e vouchers e só entra na análise de meios de pagamento |
| Atraso | Compara só as datas, sem a hora, porque a data prometida vem sempre às 00:00 |

## Vendas (P1)

| Métrica | Como é calculada |
| --- | --- |
| Receita | Soma do preço dos itens (`fItensPedido[preco]`), igual à soma de `fPedidos[receita]` |
| Pedidos | Número de pedidos em `fPedidos` |
| Valor médio por pedido | Receita ÷ pedidos |
| Clientes | Número de clientes distintos (`customer_unique_id`) |
| Crescimento | (Valor de jan–ago/2018 ÷ valor de jan–ago/2017) − 1, para receita e pedidos |
| Participação na receita | Receita do recorte (categoria, estado ou região) ÷ receita total |
| Participação por meio de pagamento | Valor pago na forma de pagamento ÷ valor pago total (`fPagamentos[valor_pago]`) |

## Entrega e satisfação (P2)

| Métrica | Como é calculada |
| --- | --- |
| Prazo de entrega | Média de dias entre a compra e a entrega, nos pedidos entregues (`dias_entrega`) |
| Dias de atraso | Data de entrega − data prometida; positivo é atraso (`dias_atraso`) |
| % de pedidos atrasados | Pedidos entregues depois da data prometida ÷ pedidos entregues (`atrasado`) |
| Folga do prazo | Média de dias entre a entrega e a data prometida, nos pedidos entregues no prazo |
| Nota média | Média da nota de 1 a 5 dos pedidos avaliados (`nota`) |
| % de insatisfeitos | Pedidos com nota 1 ou 2 ÷ pedidos avaliados (`insatisfeito`) |
| Faixa de atraso | 8 faixas, de "15+ dias antes" a "15+ dias de atraso", ordenadas por `ordem_faixa` |
| Atraso por estado | % de pedidos atrasados por estado do cliente, só nos estados com pelo menos 100 entregas |

## Clientes (P3)

| Métrica | Como é calculada |
| --- | --- |
| % de clientes que voltaram | Clientes com compras em 2 ou mais datas ÷ clientes (`voltou`) |
| Dias até a 2ª compra | Mediana de dias entre a 1ª e a 2ª compra, entre os clientes que voltaram (`dias_ate_2a_compra`) |
| Receita dos clientes que voltaram | Receita desses clientes ÷ receita total |
| Receita por cliente | Receita ÷ clientes, comparada entre quem voltou e quem comprou uma vez |
| Retenção por mês da 1ª compra | Clientes do mês da 1ª compra que compraram de novo de 1 a 12 meses depois ÷ total de clientes daquele mês (`fCoorte[retencao]`); só entram os meses já ocorridos até ago/2018 |
| Grupo de clientes | Regras na tabela abaixo (`segmento`) |
| Volta por nota da 1ª compra | % de clientes que voltaram, por nota dada à 1ª compra; com mais de um pedido no primeiro dia, vale a menor nota |

### Grupos de clientes

Alto valor são os 20% de maior gasto no período (percentil 80 do valor). Compra recente é a última compra feita até 180 dias antes de 31/08/2018. As regras são aplicadas nesta ordem:

| Grupo | Regra |
| --- | --- |
| Recorrentes | Compraram em 2 ou mais datas |
| Alto valor recentes | Alto valor e compra recente |
| Alto valor em risco | Alto valor e mais de 180 dias sem comprar |
| Novos de menor valor | Fora do alto valor e compra recente |
| Inativos de menor valor | Fora do alto valor e mais de 180 dias sem comprar |
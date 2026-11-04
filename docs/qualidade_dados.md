# Qualidade dos dados e decisões

Registro dos problemas encontrados na exploração (`notebooks/exploracao.ipynb`), do impacto de cada um e do tratamento aplicado no script `src/transformacoes.py`. A coluna Notebook indica a seção em que o problema aparece.

Status: **Tratado** (regra aplicada no script) ou **Sem impacto** (o problema existe, mas não afeta as análises).

| ID | Tabela | Problema | Notebook | Impacto | Tratamento | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Q01 | customers | `customer_id` muda a cada pedido | 2.2 | Clientes igual a pedidos e recompra zerada | Cliente identificado pelo `customer_unique_id` | Tratado |
| Q02 | orders | Meses com pouco volume em 2016 e em set–out/2018 | 4 | Tendência e crescimento distorcidos | Período de jan/2017 a ago/2018; crescimento comparado entre jan–ago de cada ano | Tratado |
| Q03 | orders | Pedidos cancelados e indisponíveis | 3.3 | Vendas que não aconteceram contadas como receita | Excluídos da análise | Tratado |
| Q04 | orders | Pedidos entregues sem data de entrega | 3.1 | Prazo e atraso calculados sobre datas vazias | Fora das métricas de prazo e atraso | Tratado |
| Q05 | orders | Data prometida sempre às 00:00 | 1.3 | Entrega no próprio dia prometido contada como atraso | Atraso calculado comparando só as datas | Tratado |
| Q06 | orders | Pedidos do mesmo cliente no mesmo dia | — | Compra dividida contada como recompra | Recompra contada por datas distintas de compra | Tratado |
| Q07 | order_items, order_payments | Pedidos sem itens ou sem pagamento | 2.3 | Pedidos sem valor nos cruzamentos | Mantidos em fPedidos com valores em branco; a receita vem dos itens | Tratado |
| Q08 | order_payments | Várias linhas de pagamento por pedido | 3.2 | Receita duplicada se o cruzamento for feito linha a linha | Pagamentos somados por pedido em fPedidos; fPagamentos mantém uma linha por pagamento | Tratado |
| Q09 | order_payments | Pagamentos com 0 parcela e tipo `not_defined` | 3.2 | Distorção na análise de parcelamento | 0 parcela tratado como pagamento à vista; tipo rotulado como "Não definido" | Tratado |
| Q10 | order_payments, order_items | Valor pago diferente de itens + frete, porque inclui vouchers | — | Receita diferente conforme a fonte usada | Receita sempre pelo preço dos produtos; valor pago só na análise de meios de pagamento | Tratado |
| Q11 | order_reviews | Pedidos com mais de uma avaliação | 3.2 | Nota duplicada nas médias | Mantida a avaliação mais recente de cada pedido | Tratado |
| Q12 | products | Produtos sem categoria | 3.1 | Produtos fora dos gráficos por categoria | Categoria "Sem categoria" | Tratado |
| Q13 | products, category_translation | Categorias sem tradução para o inglês | 2.3 | Rótulos vazios nos gráficos | O painel usa a categoria em português | Tratado |
| Q14 | category_translation | Cabeçalho do arquivo com caractere invisível (BOM) | 1.1 | Nome de coluna quebrado e cruzamento falhando | Leitura com `encoding="utf-8-sig"` | Tratado |
| Q15 | customers, sellers | CEP lido como número perde o zero à esquerda | 1.1 | CEPs de São Paulo errados | CEP lido como texto | Tratado |
| Q16 | geolocation | Vários pontos por prefixo de CEP | 1 | Linhas multiplicadas nos cruzamentos | Tabela fora do escopo | Sem impacto |
| Q17 | products | Colunas com grafia errada (`product_name_lenght`, `product_description_lenght`) | — | Erro ao referenciar as colunas | Colunas não usadas no modelo | Sem impacto |

## Validações automáticas

O script confere as regras abaixo antes de gravar os arquivos. Se uma delas falhar, ele para com erro e nenhum arquivo é gravado.

- Nenhum pedido repetido em fPedidos e nenhum item repetido em fItensPedido.
- Nenhum cliente repetido em dClientes e nenhum produto repetido em dProdutos.
- Todo item tem produto e vendedor cadastrados.
- A receita somada pelos itens é igual à receita somada pelos pedidos.
- O número de clientes não passa o de pedidos.

## Conciliação entre script e painel

O script imprime os totais na etapa 9. Eles foram comparados com o painel, com os filtros de período de 01/01/2017 a 31/08/2018 e todas as regiões.

| Indicador | Script (etapa 9) | Painel |
| --- | --- | --- |
| Receita | R$ 13,4 milhões | R$ 13,4 milhões |
| Pedidos | 97,9 mil | 97,9 mil |
| Clientes | 95 mil | 95 mil |
| Clientes que voltaram | 2,2% | 2,2% |
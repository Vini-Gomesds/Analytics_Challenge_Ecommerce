from pathlib import Path

import numpy as np
import pandas as pd

try:
    RAIZ = Path(__file__).resolve().parents[1]
except NameError:  # em notebook, abra-o com a pasta do repositório como diretório atual
    RAIZ = Path.cwd()

DIR_RAW = RAIZ / "data" / "raw"
DIR_OUT = RAIZ / "data" / "processed"
DIR_OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Parâmetros e tabelas de apoio
# ---------------------------------------------------------------------------

INICIO = pd.Timestamp("2017-01-01")
FIM = pd.Timestamp("2018-08-31")
STATUS_INVALIDOS = ["canceled", "unavailable"]

STATUS = {
    "delivered": "Entregue", "shipped": "Enviado", "invoiced": "Faturado",
    "processing": "Em processamento", "approved": "Aprovado", "created": "Criado",
}
FORMAS_PAGAMENTO = {
    "credit_card": "Cartão de crédito", "boleto": "Boleto", "voucher": "Voucher",
    "debit_card": "Cartão de débito", "not_defined": "Não definido",
}
UFS = {
    "AC": ("Acre", "Norte"), "AL": ("Alagoas", "Nordeste"), "AP": ("Amapá", "Norte"),
    "AM": ("Amazonas", "Norte"), "BA": ("Bahia", "Nordeste"), "CE": ("Ceará", "Nordeste"),
    "DF": ("Distrito Federal", "Centro-Oeste"), "ES": ("Espírito Santo", "Sudeste"),
    "GO": ("Goiás", "Centro-Oeste"), "MA": ("Maranhão", "Nordeste"), "MT": ("Mato Grosso", "Centro-Oeste"),
    "MS": ("Mato Grosso do Sul", "Centro-Oeste"), "MG": ("Minas Gerais", "Sudeste"), "PA": ("Pará", "Norte"),
    "PB": ("Paraíba", "Nordeste"), "PR": ("Paraná", "Sul"), "PE": ("Pernambuco", "Nordeste"),
    "PI": ("Piauí", "Nordeste"), "RJ": ("Rio de Janeiro", "Sudeste"), "RN": ("Rio Grande do Norte", "Nordeste"),
    "RS": ("Rio Grande do Sul", "Sul"), "RO": ("Rondônia", "Norte"), "RR": ("Roraima", "Norte"),
    "SC": ("Santa Catarina", "Sul"), "SP": ("São Paulo", "Sudeste"), "SE": ("Sergipe", "Nordeste"),
    "TO": ("Tocantins", "Norte"),
}
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]
DIAS_SEMANA = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
               "sexta-feira", "sábado", "domingo"]
FAIXAS_ATRASO = ["15+ dias antes", "8 a 14 dias antes", "1 a 7 dias antes", "No dia prometido",
                 "1 a 3 dias de atraso", "4 a 7 dias de atraso", "8 a 14 dias de atraso", "15+ dias de atraso"]
SEGMENTOS = ["Recorrentes", "Alto valor recentes", "Alto valor em risco",
             "Novos de menor valor", "Inativos de menor valor"]


def ler(arquivo, **opcoes):
    return pd.read_csv(DIR_RAW / arquivo, encoding="utf-8-sig", **opcoes)


def salvar(tabela, nome):
    tabela.to_csv(DIR_OUT / f"{nome}.csv", sep=";", decimal=",", index=False,
                  encoding="utf-8-sig", date_format="%Y-%m-%d")
    print(f"  {nome:22} {len(tabela):>8,} linhas")


# ---------------------------------------------------------------------------
# 1. Carga
# ---------------------------------------------------------------------------

print("1. Carregando os dados brutos")
orders = ler("olist_orders_dataset.csv", parse_dates=[
    "order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date"])
items = ler("olist_order_items_dataset.csv")
payments = ler("olist_order_payments_dataset.csv")
reviews = ler("olist_order_reviews_dataset.csv", parse_dates=["review_answer_timestamp"])
customers = ler("olist_customers_dataset.csv", dtype={"customer_zip_code_prefix": str})
sellers = ler("olist_sellers_dataset.csv", dtype={"seller_zip_code_prefix": str})
products = ler("olist_products_dataset.csv")
traducao = ler("product_category_name_translation.csv")

# ---------------------------------------------------------------------------
# 2. Seleção: período de análise e pedidos válidos
# ---------------------------------------------------------------------------

print("2. Selecionando pedidos válidos de jan/2017 a ago/2018")
orders["data_compra"] = orders["order_purchase_timestamp"].dt.normalize()
no_periodo = orders["data_compra"].between(INICIO, FIM)
valido = ~orders["order_status"].isin(STATUS_INVALIDOS)
pedidos = orders[no_periodo & valido].copy()
print(f"   {len(orders):,} pedidos no total | {(~no_periodo).sum():,} fora do período | "
      f"{(no_periodo & ~valido).sum():,} cancelados ou indisponíveis | {len(pedidos):,} mantidos")

# ---------------------------------------------------------------------------
# 3. Fato pedidos: cliente, entrega, avaliação, valores e pagamento
# ---------------------------------------------------------------------------

print("3. Montando fato_pedidos")

# Cliente: a pessoa é o customer_unique_id; o customer_id muda a cada pedido

pedidos = pedidos.merge(
    customers[["customer_id", "customer_unique_id", "customer_city", "customer_state"]],
    on="customer_id", how="left",
).rename(columns={"customer_state": "uf_cliente", "customer_city": "cidade_cliente"})

# Entrega: compara só as datas, porque a data prometida vem sempre às 00:00

pedidos["data_entrega"] = pedidos["order_delivered_customer_date"].dt.normalize()
pedidos["data_prometida"] = pedidos["order_estimated_delivery_date"].dt.normalize()
entregue = (pedidos["order_status"] == "delivered") & pedidos["data_entrega"].notna()
pedidos["entregue"] = entregue.astype(int)
pedidos["dias_entrega"] = (pedidos["data_entrega"] - pedidos["data_compra"]).dt.days.where(entregue).astype("Int64")
pedidos["dias_atraso"] = (pedidos["data_entrega"] - pedidos["data_prometida"]).dt.days.where(entregue).astype("Int64")
pedidos["atrasado"] = (pedidos["dias_atraso"] > 0).astype("Int64")

faixa = pd.cut(pedidos["dias_atraso"].astype(float),
               bins=[-np.inf, -15, -8, -1, 0, 3, 7, 14, np.inf], labels=FAIXAS_ATRASO)
pedidos["faixa_atraso"] = faixa.astype(object)
pedidos["ordem_faixa"] = pd.Series(faixa.cat.codes + 1, index=pedidos.index).where(faixa.notna()).astype("Int64")

# Avaliação: uma por pedido, a resposta mais recente

avaliacoes = (
    reviews.sort_values("review_answer_timestamp")
    .drop_duplicates("order_id", keep="last")[["order_id", "review_score"]]
    .rename(columns={"review_score": "nota"})
)
pedidos = pedidos.merge(avaliacoes, on="order_id", how="left")
pedidos["nota"] = pedidos["nota"].astype("Int64")
pedidos["insatisfeito"] = (pedidos["nota"] <= 2).astype("Int64")

# Valores dos itens: receita = preço dos produtos; frete à parte

totais_itens = items.groupby("order_id").agg(
    qtd_itens=("order_item_id", "count"), receita=("price", "sum"), frete=("freight_value", "sum")
).reset_index()
pedidos = pedidos.merge(totais_itens, on="order_id", how="left")

# Pagamento: valor pago total e forma de pagamento de maior valor no pedido

totais_pag = payments.groupby("order_id").agg(
    valor_pago=("payment_value", "sum"), parcelas=("payment_installments", "max")
).reset_index()
principal = (
    payments.sort_values("payment_value")
    .drop_duplicates("order_id", keep="last")[["order_id", "payment_type"]]
)
pedidos = pedidos.merge(totais_pag, on="order_id", how="left").merge(principal, on="order_id", how="left")
pedidos["forma_pagamento"] = pedidos["payment_type"].map(FORMAS_PAGAMENTO)
pedidos["parcelas"] = pedidos["parcelas"].clip(lower=1).astype("Int64")  # 0 parcelas = pagamento à vista
pedidos["status"] = pedidos["order_status"].map(STATUS)

fato_pedidos = pedidos[[
    "order_id", "customer_unique_id", "data_compra", "uf_cliente", "status",
    "qtd_itens", "receita", "frete", "valor_pago", "forma_pagamento", "parcelas",
    "entregue", "data_entrega", "data_prometida", "dias_entrega", "dias_atraso",
    "atrasado", "faixa_atraso", "ordem_faixa", "nota", "insatisfeito",
]]

# ---------------------------------------------------------------------------
# 4. Fato itens e fato pagamentos (só pedidos selecionados)
# ---------------------------------------------------------------------------

print("4. Montando fato_itens e fato_pagamentos")

# Atributos do pedido repetidos no item, para cortes por categoria e vendedor

fato_itens = items.merge(
    pedidos[["order_id", "customer_unique_id", "data_compra", "uf_cliente",
             "entregue", "atrasado", "dias_atraso", "nota", "insatisfeito"]],
    on="order_id", how="inner",
).rename(columns={"price": "preco", "freight_value": "frete"})
fato_itens = fato_itens[[
    "order_id", "order_item_id", "product_id", "seller_id", "customer_unique_id",
    "data_compra", "uf_cliente", "preco", "frete",
    "entregue", "atrasado", "dias_atraso", "nota", "insatisfeito",
]]

fato_pagamentos = payments.merge(
    pedidos[["order_id", "customer_unique_id", "data_compra", "uf_cliente"]], on="order_id", how="inner"
)
fato_pagamentos["forma_pagamento"] = fato_pagamentos["payment_type"].map(FORMAS_PAGAMENTO)
fato_pagamentos["parcelas"] = fato_pagamentos["payment_installments"].clip(lower=1)
fato_pagamentos = fato_pagamentos.rename(columns={"payment_sequential": "sequencia", "payment_value": "valor_pago"})[[
    "order_id", "sequencia", "customer_unique_id", "data_compra", "uf_cliente",
    "forma_pagamento", "parcelas", "valor_pago",
]]

# ---------------------------------------------------------------------------
# 5. Dimensões de produto, vendedor e estado
# ---------------------------------------------------------------------------

print("5. Montando dim_produto, dim_vendedor e dim_uf")

dim_produto = products.merge(traducao, on="product_category_name", how="left")
dim_produto["categoria"] = (
    dim_produto["product_category_name"].fillna("sem_categoria").str.replace("_", " ").str.capitalize()
)
dim_produto["categoria_en"] = (
    dim_produto["product_category_name_english"]
    .fillna(dim_produto["product_category_name"])
    .fillna("no_category")
    .str.replace("_", " ").str.capitalize()
)
dim_produto = dim_produto.rename(columns={"product_weight_g": "peso_g", "product_photos_qty": "qtd_fotos"})[
    ["product_id", "categoria", "categoria_en", "peso_g", "qtd_fotos"]
]

dim_vendedor = sellers.rename(columns={"seller_city": "cidade_vendedor", "seller_state": "uf_vendedor"})
dim_vendedor["cidade_vendedor"] = dim_vendedor["cidade_vendedor"].str.title()
dim_vendedor["regiao_vendedor"] = dim_vendedor["uf_vendedor"].map(lambda uf: UFS.get(uf, ("", "Não informado"))[1])
dim_vendedor = dim_vendedor[["seller_id", "cidade_vendedor", "uf_vendedor", "regiao_vendedor"]]

dim_uf = pd.DataFrame(
    [(uf, nome, regiao) for uf, (nome, regiao) in UFS.items()],
    columns=["uf", "estado", "regiao"]
)

# ---------------------------------------------------------------------------
# 6. Dimensão cliente: recompra, 1ª experiência e segmentação por valor
# ---------------------------------------------------------------------------

print("6. Montando dim_cliente")

dim_cliente = pedidos.groupby("customer_unique_id").agg(
    primeira_compra=("data_compra", "min"),
    ultima_compra=("data_compra", "max"),
    compras=("data_compra", "nunique"),  # datas distintas: pedido dividido no mesmo dia não é recompra
    pedidos=("order_id", "nunique"),
    valor=("receita", "sum"),
).reset_index()

# Estado e cidade do pedido mais recente

ultimo = pedidos.sort_values("data_compra").drop_duplicates("customer_unique_id", keep="last")
dim_cliente = dim_cliente.merge(
    ultimo[["customer_unique_id", "uf_cliente", "cidade_cliente"]], on="customer_unique_id", how="left"
)
dim_cliente["cidade_cliente"] = dim_cliente["cidade_cliente"].str.title()

# Dias até a 2ª compra

datas = pedidos[["customer_unique_id", "data_compra"]].drop_duplicates().sort_values(["customer_unique_id", "data_compra"])
datas["ordem"] = datas.groupby("customer_unique_id").cumcount()
segunda = datas[datas["ordem"] == 1].set_index("customer_unique_id")["data_compra"]
dim_cliente["segunda_compra"] = dim_cliente["customer_unique_id"].map(segunda)
dim_cliente["dias_ate_2a_compra"] = (dim_cliente["segunda_compra"] - dim_cliente["primeira_compra"]).dt.days.astype("Int64")

# Nota da 1ª compra (a pior, se houver mais de um pedido no primeiro dia)

com_primeira = pedidos.merge(dim_cliente[["customer_unique_id", "primeira_compra"]], on="customer_unique_id")
nota_primeira = (
    com_primeira[com_primeira["data_compra"] == com_primeira["primeira_compra"]]
    .groupby("customer_unique_id")["nota"].min()
)
dim_cliente["nota_1a_compra"] = dim_cliente["customer_unique_id"].map(nota_primeira).astype("Int64")

# Segmentação: RFV adaptado a uma base em que quase todos compram uma vez

dim_cliente["recencia_dias"] = (FIM - dim_cliente["ultima_compra"]).dt.days
valor_corte = dim_cliente["valor"].quantile(0.8)  # alto valor = 20% maiores gastos
alto_valor = dim_cliente["valor"] >= valor_corte
recente = dim_cliente["recencia_dias"] <= 180
dim_cliente["segmento"] = np.select(
    [dim_cliente["compras"] >= 2, alto_valor & recente, alto_valor, recente],
    SEGMENTOS[:4],
    default=SEGMENTOS[4],
)
dim_cliente["ordem_segmento"] = dim_cliente["segmento"].map({s: i for i, s in enumerate(SEGMENTOS, start=1)})
dim_cliente["voltou"] = np.where(dim_cliente["compras"] >= 2, "Sim", "Não")
dim_cliente["coorte"] = dim_cliente["primeira_compra"].dt.strftime("%Y-%m")
print(f"   corte de alto valor (percentil 80): R$ {valor_corte:,.2f}")

dim_cliente = dim_cliente[[
    "customer_unique_id", "uf_cliente", "cidade_cliente", "primeira_compra", "ultima_compra",
    "segunda_compra", "compras", "pedidos", "valor", "dias_ate_2a_compra", "nota_1a_compra",
    "recencia_dias", "voltou", "segmento", "ordem_segmento", "coorte",
]]

# ---------------------------------------------------------------------------
# 7. Retenção por coorte: % de cada coorte que comprou de novo no mês M+n
# ---------------------------------------------------------------------------

print("7. Montando agg_retencao_coorte")

base = pedidos[["customer_unique_id", "data_compra"]].merge(
    dim_cliente[["customer_unique_id", "primeira_compra", "coorte"]], on="customer_unique_id"
)
base["mes_apos"] = (
    (base["data_compra"].dt.year - base["primeira_compra"].dt.year) * 12
    + (base["data_compra"].dt.month - base["primeira_compra"].dt.month)
)
ativos = (
    base[base["mes_apos"].between(1, 12)]
    .groupby(["coorte", "mes_apos"])["customer_unique_id"].nunique()
    .rename("clientes_ativos").reset_index()
)
tamanho = dim_cliente.groupby("coorte").size().rename("tamanho_coorte").reset_index()

grade = pd.MultiIndex.from_product([tamanho["coorte"], range(1, 13)], names=["coorte", "mes_apos"]).to_frame(index=False)
grade = grade.merge(tamanho, on="coorte").merge(ativos, on=["coorte", "mes_apos"], how="left")
grade["clientes_ativos"] = grade["clientes_ativos"].fillna(0).astype(int)

# Mantém só os meses que já aconteceram até ago/2018

mes_coorte = grade["coorte"].str[:4].astype(int) * 12 + grade["coorte"].str[5:7].astype(int)
agg_retencao = grade[mes_coorte + grade["mes_apos"] <= FIM.year * 12 + FIM.month].copy()
agg_retencao["retencao"] = agg_retencao["clientes_ativos"] / agg_retencao["tamanho_coorte"]

# ---------------------------------------------------------------------------
# 9. Validações (governança): o pipeline para se alguma regra falhar
# ---------------------------------------------------------------------------

print("9. Validando")

assert fato_pedidos["order_id"].is_unique, "order_id repetido em fato_pedidos"
assert not fato_itens.duplicated(["order_id", "order_item_id"]).any(), "item repetido em fato_itens"
assert dim_cliente["customer_unique_id"].is_unique, "cliente repetido em dim_cliente"
assert dim_produto["product_id"].is_unique, "produto repetido em dim_produto"
assert fato_itens["product_id"].isin(dim_produto["product_id"]).all(), "item sem produto"
assert fato_itens["seller_id"].isin(dim_vendedor["seller_id"]).all(), "item sem vendedor"
assert np.isclose(fato_itens["preco"].sum(), fato_pedidos["receita"].sum()), "receita não reconcilia"
assert len(dim_cliente) <= len(fato_pedidos), "mais clientes do que pedidos"

print(f"   Receita: R$ {fato_itens['preco'].sum():,.2f} | Pedidos: {len(fato_pedidos):,} | "
      f"Clientes: {len(dim_cliente):,} | Voltaram: {100 * (dim_cliente['voltou'] == 'Sim').mean():.2f}%")

# ---------------------------------------------------------------------------
# 10. Gravação
# ---------------------------------------------------------------------------

print("10. Gravando em data/processed")
salvar(fato_pedidos, "fato_pedidos")
salvar(fato_itens, "fato_itens")
salvar(fato_pagamentos, "fato_pagamentos")
salvar(dim_cliente, "dim_cliente")
salvar(dim_produto, "dim_produto")
salvar(dim_vendedor, "dim_vendedor")
salvar(dim_uf, "dim_uf")
salvar(agg_retencao, "agg_retencao_coorte")
print("Concluído.")
import pandas as pd


def formatar_brl(valor_centavos):
    valor = valor_centavos / 100
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def resumo_por_categoria(df):
    despesas = df[df["tipo"] == "Despesa"]
    if despesas.empty:
        return pd.DataFrame(columns=["categoria", "valor_centavos"])
    return (
        despesas.groupby("categoria", as_index=False)["valor_centavos"]
        .sum()
        .sort_values("valor_centavos", ascending=False)
    )


def resumo_mensal(df):
    if df.empty:
        return pd.DataFrame(columns=["mes", "receitas_centavos", "despesas_centavos"])
    copia = df.copy()
    copia["mes"] = copia["data"].str.slice(0, 7)
    receitas = (
        copia[copia["tipo"] == "Receita"].groupby("mes")["valor_centavos"].sum()
    )
    despesas = (
        copia[copia["tipo"] == "Despesa"].groupby("mes")["valor_centavos"].sum()
    )
    resultado = pd.concat([receitas.rename("receitas_centavos"),
                           despesas.rename("despesas_centavos")], axis=1).fillna(0)
    resultado = resultado.astype(int).reset_index()
    return resultado.sort_values("mes")

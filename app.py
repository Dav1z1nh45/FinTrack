from datetime import date, timedelta
import pandas as pd
import streamlit as st

import database as db
from analytics import resumo_por_categoria, resumo_mensal, formatar_brl

st.set_page_config(page_title="FinTrack", page_icon="💸", layout="wide")
db.inicializar_banco()

st.title("💸 FinTrack")
st.caption("Controle simples de receitas e despesas — seus dados ficam salvos localmente.")

with st.sidebar:
    st.header("Nova transação")
    with st.form("form_nova_transacao", clear_on_submit=True):
        tipo = st.selectbox("Tipo", ["Despesa", "Receita"])
        descricao = st.text_input("Descrição", placeholder="Ex.: Mercado, salário...")
        categoria = st.selectbox(
            "Categoria",
            ["Alimentação", "Transporte", "Moradia", "Educação", "Saúde",
             "Lazer", "Salário", "Freelance", "Contas", "Compras", "Outros"]
        )
        valor = st.number_input("Valor (R$)", min_value=0.01, value=10.00, step=1.00, format="%.2f")
        data_transacao = st.date_input("Data", value=date.today())
        observacoes = st.text_area("Observações (opcional)", max_chars=500)
        enviar = st.form_submit_button("Adicionar transação", use_container_width=True)

        if enviar:
            if not descricao.strip():
                st.error("Informe uma descrição.")
            else:
                db.criar_transacao(
                    tipo=tipo,
                    descricao=descricao.strip(),
                    categoria=categoria,
                    valor_centavos=round(valor * 100),
                    data_transacao=data_transacao.isoformat(),
                    observacoes=observacoes.strip(),
                )
                st.success("Transação adicionada!")
                st.rerun()

st.subheader("Visão geral")

hoje = date.today()
inicio_padrao = hoje.replace(day=1)
with st.expander("Filtrar período", expanded=True):
    col_a, col_b = st.columns(2)
    inicio = col_a.date_input("De", value=inicio_padrao)
    fim = col_b.date_input("Até", value=hoje)

if inicio > fim:
    st.error("A data inicial precisa ser anterior ou igual à data final.")
    st.stop()

transacoes = db.listar_transacoes(inicio.isoformat(), fim.isoformat())
df = pd.DataFrame(transacoes)

if df.empty:
    st.info("Ainda não há transações nesse período. Adicione uma pela barra lateral.")
    st.metric("Saldo no período", formatar_brl(0))
else:
    df["valor_reais"] = df["valor_centavos"] / 100
    receitas = int(df.loc[df["tipo"] == "Receita", "valor_centavos"].sum())
    despesas = int(df.loc[df["tipo"] == "Despesa", "valor_centavos"].sum())
    saldo = receitas - despesas

    c1, c2, c3 = st.columns(3)
    c1.metric("Receitas", formatar_brl(receitas))
    c2.metric("Despesas", formatar_brl(despesas))
    c3.metric("Saldo no período", formatar_brl(saldo))

    st.divider()
    esquerda, direita = st.columns(2)
    with esquerda:
        st.markdown("#### Despesas por categoria")
        categorias = resumo_por_categoria(df)
        if categorias.empty:
            st.caption("Nenhuma despesa registrada no período.")
        else:
            categorias["valor_reais"] = categorias["valor_centavos"] / 100
            st.bar_chart(categorias.set_index("categoria")["valor_reais"])
    with direita:
        st.markdown("#### Movimento mensal")
        mensal = resumo_mensal(df)
        if mensal.empty:
            st.caption("Ainda não há dados para mostrar.")
        else:
            mensal["Receitas"] = mensal["receitas_centavos"] / 100
            mensal["Despesas"] = mensal["despesas_centavos"] / 100
            st.line_chart(mensal.set_index("mes")[["Receitas", "Despesas"]])

st.divider()
st.subheader("Transações")

todos = db.listar_transacoes(inicio.isoformat(), fim.isoformat())
df_todos = pd.DataFrame(todos)

if not df_todos.empty:
    col1, col2 = st.columns(2)
    tipos_disponiveis = ["Receita", "Despesa"]
    tipos_filtro = col1.multiselect("Filtrar por tipo", tipos_disponiveis, default=tipos_disponiveis)
    categorias_disponiveis = sorted(df_todos["categoria"].unique().tolist())
    categorias_filtro = col2.multiselect("Filtrar por categoria", categorias_disponiveis, default=categorias_disponiveis)

    filtrado = df_todos[
        df_todos["tipo"].isin(tipos_filtro) &
        df_todos["categoria"].isin(categorias_filtro)
    ].copy()

    exibicao = filtrado[["id", "data", "tipo", "descricao", "categoria", "valor_centavos", "observacoes"]].copy()
    exibicao["Valor (R$)"] = exibicao["valor_centavos"].map(lambda x: formatar_brl(int(x)))
    exibicao = exibicao.rename(columns={
        "id": "ID", "data": "Data", "tipo": "Tipo", "descricao": "Descrição",
        "categoria": "Categoria", "observacoes": "Observações"
    }).drop(columns=["valor_centavos"])
    st.dataframe(exibicao, use_container_width=True, hide_index=True)

    csv_df = filtrado.copy()
    csv_df["valor_reais"] = csv_df["valor_centavos"] / 100
    csv_df = csv_df.drop(columns=["valor_centavos"])
    st.download_button(
        "⬇️ Exportar transações filtradas (CSV)",
        data=csv_df.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"fintrack_{inicio.isoformat()}_{fim.isoformat()}.csv",
        mime="text/csv",
    )

    st.markdown("#### Excluir transação")
    opcoes = {
        f'#{row["id"]} — {row["data"]} — {row["descricao"]} ({formatar_brl(int(row["valor_centavos"]))})': int(row["id"])
        for _, row in filtrado.iterrows()
    }
    if opcoes:
        with st.form("excluir_transacao"):
            escolhida = st.selectbox("Selecione a transação", list(opcoes.keys()))
            confirmar = st.checkbox("Confirmo que quero excluir esta transação.")
            excluir = st.form_submit_button("Excluir selecionada")
            if excluir:
                if confirmar:
                    db.excluir_transacao(opcoes[escolhida])
                    st.success("Transação excluída.")
                    st.rerun()
                else:
                    st.warning("Marque a confirmação antes de excluir.")
else:
    st.caption("Nenhuma transação encontrada no período selecionado.")

st.caption("FinTrack é um projeto educacional de controle de registros; não fornece aconselhamento financeiro.")

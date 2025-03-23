import streamlit as st
import pandas as pd
import sqlite3
from faker import Faker
import plotly.express as px
from datetime import datetime

# Interface Streamlit
def main():
    st.title("ERP Financeiro com Streamlit")
    
    menu = ["Clientes", "Contas a Pagar", "Contas a Receber", "Lançamentos", "Relatórios"]
    choice = st.sidebar.selectbox("Selecione uma opção", menu)
    conn = sqlite3.connect("erp_finance.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    if choice == "Clientes":
        st.subheader("Cadastro de Clientes")
        df = pd.read_sql_query("SELECT * FROM clientes", conn)
        st.dataframe(df)
        
    elif choice == "Contas a Pagar":
        st.subheader("Contas a Pagar")
        df = pd.read_sql_query("SELECT * FROM contas_pagar", conn)
        st.dataframe(df)
        
    elif choice == "Contas a Receber":
        st.subheader("Contas a Receber")
        df = pd.read_sql_query("SELECT * FROM contas_receber", conn)
        st.dataframe(df)
    
    elif choice == "Lançamentos":
        st.subheader("Lançamentos Financeiros")
        df = pd.read_sql_query("SELECT * FROM lancamentos", conn)
        st.dataframe(df)
        
    elif choice == "Relatórios":
        st.subheader("Relatório de Fluxo de Caixa")
        df = pd.read_sql_query("SELECT tipo, SUM(valor) as total FROM lancamentos GROUP BY tipo", conn)
        st.dataframe(df)

        st.subheader("Distribuição das Contas a Pagar por Fornecedor")
        df = pd.read_sql_query("SELECT * FROM contas_pagar", conn)

        df_grouped = df.groupby('fornecedor', as_index=False)['valor'].sum()
        df_grouped = df_grouped.sort_values(by='valor', ascending=False)
        fig = px.pie(df_grouped, names='fornecedor', values='valor', title='Distribuição das Contas a Pagar')
        st.plotly_chart(fig)
    
        st.subheader("Top 5 Clientes com Maior Receita")
        query =  """SELECT c.nome AS Cliente, SUM(cr.valor) as total_receita
        FROM contas_receber cr
        JOIN clientes c ON cr.cliente_id = c.id
        WHERE cr.status = 'Recebido'
        GROUP BY cr.cliente_id
        ORDER BY total_receita DESC
        LIMIT 5"""
        df = pd.read_sql_query(query, conn)
        fig = px.bar(df, x="Cliente", y="total_receita", text_auto=True,
                     labels={"Receita": "Total (R$)", "Cliente": "Clientes"},
                     title="Top 5 Clientes com Maior Receita")
        
        st.plotly_chart(fig)

        st.subheader("Comparação Receita vs Despesa (Gráfico de Barras)")

        current_month = datetime.now().strftime('%Y-%m')
    
        cursor.execute("""
            SELECT SUM(valor) FROM lancamentos 
            WHERE tipo = 'Receita' AND strftime('%Y-%m', data) = ?
        """, (current_month,))
        receita = cursor.fetchone()[0] or 0
        
        cursor.execute("""
            SELECT SUM(valor) FROM lancamentos 
            WHERE tipo = 'Despesa' AND strftime('%Y-%m', data) = ?
        """, (current_month,))
        despesa = cursor.fetchone()[0] or 0
        
        df_comparacao = pd.DataFrame({
            "Categoria": ["Receita", "Despesa"],
            "Valor": [receita, despesa]
        })
        
        fig_comparacao = px.bar(df_comparacao, x="Categoria", y="Valor", text_auto=True,
                                labels={"Valor": "Total (R$)", "Categoria": "Tipo"},
                                title="Receita vs Despesa do Mês Atual")
        
        st.plotly_chart(fig_comparacao)


    conn.close()
    
if __name__ == "__main__":
    main()

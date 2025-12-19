import streamlit as st

st.header("Calculadora de Soma")

# Estes inputs são únicos para quem está com a página aberta
col1, col2 = st.columns(2)
with col1:
    n1 = st.number_input("Valor A", value=0.0)
with col2:
    n2 = st.number_input("Valor B", value=0.0)

if st.button("Calcular"):
    resultado = n1 + n2
    st.success(f"O resultado é: {resultado}")
import streamlit as st

st.title("Página 1 — Soma")

a = st.number_input("A", value=0.0, step=1.0)
b = st.number_input("B", value=0.0, step=1.0)

if st.button("Calcular", type="primary"):
    st.success(f"{a} + {b} = {a + b}")

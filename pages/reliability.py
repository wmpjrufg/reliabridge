import streamlit as st

st.title("Página 2 — Multiplicação")

x = st.number_input("X", value=0.0, step=1.0)
y = st.number_input("Y", value=0.0, step=1.0)

if st.button("Calcular", type="primary"):
    st.success(f"{x} × {y} = {x * y}")
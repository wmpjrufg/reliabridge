import streamlit as st 
import pandas as pd
from math import pi

st.title('Reliabridge')

st.write('''
         
Lorem ipsum dolor sit amet, consectetur adipiscing elit. In at dui consectetur sem maximus bibendum sed vel lectus. Donec cursus hendrerit tristique. Nullam ac ex commodo, sodales felis finibus, vulputate neque. Donec dignissim turpis vel tortor pharetra, non sollicitudin tortor consectetur. Donec non nunc dui. Cras at erat vel felis gravida posuere nec eget nunc. Proin interdum tellus eget ex vulputate fermentum. Nullam consectetur, nisl quis lacinia laoreet, augue lectus finibus lectus, quis varius tellus mauris eget enim. Cras sollicitudin eleifend tortor, vitae dignissim felis facilisis vitae. Mauris semper consequat nisi sed varius.
''')


col1, col2 = st.columns([1, 2])

with col1:
    st.image("gato.jpg", caption="Legenda da imagem", use_container_width=True)

with col2:
    st.markdown("""
    L (cm) = 15 cm
                
    a (cm) = 10 cm
    """)

col1, col2 = st.columns([1, 2])

with col1:
    st.image("gato.jpg", caption="Legenda da imagem", use_container_width=True)

with col2:
    st.markdown("""
    bw (cm) = 15 cm
                
    h (cm) = 10 cm
    """)

f_ck = st.number_input('f_ck (MPa)', 0.0)
p_load = st.number_input('permanent load (kN/m)', 0.0)

uploaded_file = st.file_uploader("Uploaded reinforcement data:")
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.table(df)

def calculate(df):
    lista = df['Asl (cm2)'].tolist()
    for item in lista:
        diam = float(item.split(",")[1])
        df['Asli'] = (((pi * diam)**2) / 4) #/ 1e6 


    return df
        

if st.button('Calculate'):
    teste = calculate(df)
    st.table(teste)
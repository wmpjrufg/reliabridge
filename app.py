import streamlit as st 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from parepy_toolbox import sampling_algorithm_structural_analysis
from obj_function import pontes

st.title('ReliaBRIDGE')

st.write(r'''
<p style="text-align: justify;">
This app evaluate reliability index in sections of reinforcement concrete bridge. You can upload your reinforcement details table and will obtain reliability index about each section.
</p>
''', unsafe_allow_html=True)

st.image("sistema_estrutural_longarina.png", caption="Structural Schema", width=500)

st.write(r'''
<p style="text-align: justify;"> You see an example of reinforcement details table in the download button below.
</p>
''', unsafe_allow_html=True)
         
with open("teste.xlsx", "rb") as file:
    st.download_button(
        label="Download example data",
        data=file,
        file_name="example_reinforcement_data.xlsx",
        mime="text/csv"
    )

l = st.number_input('$l$ (cm)', None) * 1E-2
a = st.number_input('$a$ (cm)', None) * 1E-2
bw = st.number_input('$b_w$ (cm)', None) * 1E-2
h_aux = st.number_input('$h$ (cm)', None) * 1E-2
f_c = st.number_input('$f_c$ (MPa)', None) * 1E3
p_load = st.number_input('Permanent load (kN/m)', None) 

uploaded_file = st.file_uploader("Upload reinforcement data: \n\n Reinforcement data wait to table with a values to diameter and number of steel bars")
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    if st.button('Reliability Analysis'):
        f = {'type': 'normal', 'loc': 1.22 * f_c, 'scale': 1.22 * f_c * 0.12, 'seed': None}
        p = {'type': 'gumbel max', 'loc': 0.93 * p_load, 'scale': 0.93 * p_load * 0.35, 'seed': None}
        a_s = {'type': 'normal', 'loc': 1, 'scale': 1 * 0.5/100, 'seed': None}
        b_w = {'type': 'normal', 'loc': bw, 'scale': bw * 2/100, 'seed': None}
        h = {'type': 'normal', 'loc': h_aux, 'scale': h_aux * 2/100, 'seed': None}
        f_y = {'type': 'normal', 'loc': 1.22, 'scale': 1.22 * 0.04, 'seed': None}
        var = [f, p, a_s, b_w, h, f_y]
        setup = {
                    'number of samples': 50000, 
                    'number of dimensions': len(var), 
                    'numerical model': {'model sampling': 'mcs'}, 
                    'variables settings': var, 
                    'number of state limit functions or constraints': len(df), 
                    'none variable': {'dataset': df, 'l (cm)': l},
                    'objective function': pontes,
                    'name simulation': 'pontes',
                }
        # Call algorithm
        results, pf, beta = sampling_algorithm_structural_analysis(setup)
        df['Positive bending moment - Pf'] = pf.iloc[0,:].values
        df['Positive bending moment - Beta'] = beta.iloc[0,:].values
        df['Negative bending moment - Pf'] = pf.iloc[0,:].values
        df['Negative bending moment - Beta'] = beta.iloc[0,:].values
        st.table(df)

        # plot samples
        x = df['x (cm)'].values * 1E-2
        y_pos = df['negative bending moment - number of longitudinal bars'].values * (np.pi * df['negative bending moment - diameter longitudinal bars (mm)'].values * 1e-3) ** 2 / 4 
        y_neg = -df['positive bending moment - number of longitudinal bars'].values * (np.pi * df['positive bending moment - diameter longitudinal bars (mm)'].values * 1e-3) ** 2 / 4

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(x, y_pos, color="blue")
        ax.plot(x, y_neg, color="blue")
        ax.set_xlabel("X (m)", fontsize=12, color="green")
        ax.set_ylabel("As (m)", fontsize=12, color="green")
        ax.grid(alpha=0.3)
        ax.legend(loc='upper right', fontsize=10)
        ax.set_title("Reinformcement bars envelope", fontsize=14)
        st.pyplot(fig)

else:
    st.warning('Please, upload a file')




    
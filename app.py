import streamlit as st 
import pandas as pd
from math import pi

from parepy_toolbox import sampling_algorithm_structural_analysis
from obj_function import nowak_collins_example

st.title('Sistema Estrutural Longarina')

st.write(r'''

<p style="text-align: justify;">
Lorem ipsum dolor sit amet, consectetur adipiscing elit. In at dui consectetur sem maximus bibendum sed vel lectus. Donec cursus hendrerit tristique. Nullam ac ex commodo, sodales felis finibus, vulputate neque. Donec dignissim turpis vel tortor pharetra, non sollicitudin tortor consectetur. Donec non nunc dui. Cras at erat vel felis gravida posuere nec eget nunc. Proin interdum tellus eget ex vulputate fermentum. Nullam consectetur, nisl quis lacinia laoreet, augue lectus finibus lectus, quis varius tellus mauris eget enim. Cras sollicitudin eleifend tortor, vitae dignissim felis facilisis vitae. Mauris semper consequat nisi sed varius.
</p>
''', unsafe_allow_html=True)


st.image("sistema_estrutural_longarina.png", caption="Structural Schema", width=500)

col1, col2 = st.columns([1, 2])

l = st.number_input('$l$ (cm)', None)
a = st.number_input('$a$ (cm)', None)
bw = st.number_input('$b_w$ (cm)', None)
h = st.number_input('$h$ (cm)', None)
f_c = st.number_input('$f_c$ (MPa)', None)
f_c = f_c * 1E3
p_load = st.number_input('$g$ = Permanent load (kN/m)', None)

uploaded_file = st.file_uploader("Uploaded reinforcement data: \n\n Reinforcement data wait to table with a values to diameter and number of steel bars")
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    # st.table(df)
else:
    st.warning('Please, upload a file')

if st.button('Convert my data in Steel Area'):
    st.title('Reliability Analysis')

    # Dataset
    f = {'type': 'normal', 'loc': f_c, 'scale': 0.12*f_c, 'seed': None}
    p = {'type': 'gumbel max', 'loc': 0.93 * p_load, 'scale': 1.12, 'seed': None}
    a_s = {'type': 'normal', 'loc': 1, 'scale': 1 * 0.5/100, 'seed': None}
    var = [f, p, a_s]

    # PAREpy setup
    setup = {
                'number of samples': 70000, 
                'number of dimensions': len(var), 
                'numerical model': {'model sampling': 'mcs'}, 
                'variables settings': var, 
                'number of state limit functions or constraints': len(df), 
                'none variable': {'dataset': df, 'l (cm)': l, 'bw (cm)': bw, 'h (cm)': h},
                'objective function': nowak_collins_example,
                'name simulation': 'nowak_collins_example',
            }

    # Call algorithm
    results, pf, beta = sampling_algorithm_structural_analysis(setup)

    df['Pf'] = pf.iloc[0,:].values
    df['Beta'] = beta.iloc[0,:].values
    st.table(df)
    
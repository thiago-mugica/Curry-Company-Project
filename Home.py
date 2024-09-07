import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="🎲"
)


image = Image.open('logo.png' )
st.sidebar.image( image, width=120)

st.sidebar.markdown ('### Cury Company')
st.sidebar.markdown ('## Fastest Delivery in Twon')
st.sidebar.markdown ("""---""")

st.write("# Curry Company Growth Dashboard")

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth dasshboard?
    - Visão Empresa:
        -Visão Gerencial: Métricas gerais de comportamento.
        -Visão Tática: Indicadores semanais de crescimento.
        -Visão Geográfica: Insights de geolocalização.
    - Visão Entregadores:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visao Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for Help
    - Time de Data Science no Discord
        - @meigarom
""" )
        
    
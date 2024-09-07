# Libraries 

from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import folium

#Bibliotecas necessarias
import pandas as pd
import streamlit as st
from datetime import datetime
from streamlit_folium import folium_static
from PIL import Image

st.set_page_config(page_title= 'Visão Entregadores', page_icon='🚗', layout='wide')

#=================================================
# Funções
#=================================================
def top_delivers ( df1, top_asc ): 
    df2 = (df1.loc[: , ['Delivery_person_ID', 'City', 'Time_taken(min)']] #seleção de colunas
              .groupby( ['City', 'Delivery_person_ID']) # Agrupamentos
              .mean()
              .sort_values( ['City', 'Time_taken(min)'], ascending = top_asc).reset_index()) #ordenação
                    
    df_aux01 = df2.loc[df2['City'] == 'Metropolitian' , : ].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban' , :].head(10)
                    
    df3 = pd.concat ([df_aux01, df_aux02, df_aux03]).reset_index()

    return df

def clean_code(df1):
    """ Esta função tem a responsabilidade de limpar o dataframe

        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo ( remoção do texto da variável numérica)

        Input: Dataframe
        Output: Dataframe
    """
    # 1. Convertendo a coluna Age de texto para numero
    
    linhas_selecionadas = df['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = df['Festival'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = df['City'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = df['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    
    df1.shape # ver quantas colunas e linhas eu tenho.
    
    # 2. Convertendo a coluna Ratings de texto para número decimal ( float )
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    
    # 3. Convertendo a coluna Order_date de texto para data preciso utilizar comando interno
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format = '%d-%m-%Y')
    
    # 4. Convertendo a coluna multiple_deliveries  de texto para numero inteiro (int)
    linhas_selecionadas = (df['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    
    # 7.removendo os espaços dentro de strings/textos/object
    df1.loc[: , 'ID'] = df1.loc[: , 'ID'].str.strip()
    df1.loc[: , 'Road_traffic_density'] = df1.loc[: , 'Road_traffic_density'].str.strip()
    df1.loc[: , 'Type_of_order'] = df1.loc[: , 'Type_of_order'].str.strip()
    df1.loc[: , 'Type_of_vehicle'] = df1.loc[: , 'Type_of_vehicle'].str.strip()
    df1.loc[: , 'City'] = df1.loc[: , 'City'].str.strip()
    df1.loc[: , 'Festival'] = df1.loc[: , 'Festival'].str.strip()
    
    
    df1['Time_taken(min)']= df1['Time_taken(min)'].apply(lambda x: x.split ('(min)')[1])
    
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1
# import dateset

df = pd.read_csv ('Projeto 1\\train.csv')

#Limpando os dados
df1 = clean_code (df)


# ==============================================================================
# Barra Lateral
# ==============================================================================
st.header('Marketplace - Visão Entregadores')

image = Image.open('logo.png' )
st.sidebar.image( image, width=120)

st.sidebar.markdown ('### Cury Company')
st.sidebar.markdown ('## Fastest Delivery in Twon')
st.sidebar.markdown ("""---""")

st.sidebar.markdown ('## Selecione uma data limite')

value = datetime(2022, 4, 13)
min_value = datetime(2022, 2, 11)
max_value = datetime(2022, 4, 6)

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=value,
    min_value=min_value,
    max_value=max_value,
    format='DD-MM-YYYY'
)

st.sidebar.markdown ("""---""")


traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown ("""---""")
st.sidebar.markdown('### Powered by Comunidade DS')

#Filtro de data , mexendo na barra de data ele altera os gráficos
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de Trãnsito 
#.isin passa uma lista e ele verifica se o que passou esta dentro da lista
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options)
df1 = df1.loc[linhas_selecionadas, :]


# ==============================================================================
# Layout no Streamlit
# ==============================================================================

tab1, tab2, tab3 = st.tabs ( ['Visão Gerencial', '', ''])

with tab1:
        with st.container():
            st.title('Overall Metrics')
            col1, col2, col3, col4 = st.columns(4 , gap ='large') #gap large é a distancia entre eles, criando 4 colunas
            with col1:
                # A maior idade dos entregadores
                maior_idade =  df1.loc[: , 'Delivery_person_Age'].max()
                col1.metric('Maior idade', maior_idade) # colmetri vem da documentação do streamlit
                
            with col2:
                # A menor idade dos entregadores
                menor_idade =  df1.loc[: , 'Delivery_person_Age'].min()
                col2.metric('Menor de Idade', menor_idade)
                
            with col3:
                # A maior idade dos Entregadores
                melhor_condicao = df1.loc[: , 'Vehicle_condition'].max()
                col3.metric('Melhor condicao', melhor_condicao)
            
            with col4:
                # A menor idade dos entredores
                pior_condicao = df1.loc[: , 'Vehicle_condition'].min()
                col4.metric('pior condicao', pior_condicao)
                
        with st.container():
            st.markdown("""---""")
            st.title( 'Avaliacoes')

            col1, col2 = st.columns(2)
            with col1:
                st.markdown('##### Avaliacao medias por Entregador')
                df_avg_ratings_per_deliver = (df1.loc[: ,  ["Delivery_person_Ratings" , "Delivery_person_ID"] ]            
                                                 .groupby(["Delivery_person_ID"])
                                                 .mean()
                                                 .reset_index())
                st.dataframe(  df_avg_ratings_per_deliver ) #comando para exibir o dataframe no streamlit
                                              

            with col2:
                st.markdown('##### Avaliacao media por transito')
                df_avg_std_ratings_by_traffic = (df1.loc[: , ['Delivery_person_Ratings', 'Road_traffic_density']]
                                                    .groupby('Road_traffic_density')
                                                    .agg({'Delivery_person_Ratings': ['mean', 'std']}))# chave valor ( dicionário), tenho a coluna que vou aplicar e depois as operações.

                df_avg_std_ratings_by_traffic.columns = ['delivery_mean' , 'delivery_std'] # aqui eu renomeio a coluna( mudança de colunas) porque a função agg cria dois nomes para cada colunas e aqui eu arrumo isso

                df_avg_std_ratings_by_traffic.reset_index()
                st.dataframe(  df_avg_std_ratings_by_traffic ) #comando para exibir o dataframe no streamlit
                
                st.markdown('##### Avaliacao media por clima')
                df_avg_std_ratings_by_Weatherconditions = (df1.loc[: , ['Delivery_person_Ratings', 'Weatherconditions']]
                                                              .groupby('Weatherconditions')
                                                              .agg({'Delivery_person_Ratings': ['mean', 'std']}))

                df_avg_std_ratings_by_Weatherconditions.columns = ['delivery_mean' , 'delivery_std'] # aqui eu renomeio a coluna

                df_avg_std_ratings_by_Weatherconditions.reset_index()
                #df_std_ratings_by_traffic #->esta comentado porque aqui ele vai aparecer ou da média ou do desvio padrão
                st.dataframe(  df_avg_std_ratings_by_Weatherconditions ) #comando para exibir o dataframe no streamlit


        with st.container():
            st.markdown("""---""")
            st.title('Velocidade de Entrega')

            col1, col2 = st.columns(2)

            with col1:
                st.subheader('Top Entregadores mais rápidos')
                df3 = top_delivers ( df1, top_asc=True )
                st.dataframe(df3)

            with col2:
                st.subheader('Top Entregadores mais lentos')
                df3 = top_delivers ( df1, top_asc=False )
                st.dataframe(df3)
     
# As duas funções são iguais o que muda é um TRUE e um False, logo la em cima eu chamo uma e outra e a mesma coisa aqui.

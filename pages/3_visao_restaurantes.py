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
import numpy as np
from PIL import Image

st.set_page_config(page_title= 'Visão Restaurantes', page_icon='🍽️', layout='wide')

#=================================================
# Funções
#=================================================
def avg_std_time_on_traffic( df1 ):
    df1_aux = (df1.loc[: , ["City" , "Time_taken(min)" , "Road_traffic_density"]]
                  .groupby(["City" , "Road_traffic_density"])
                  .agg ( {"Time_taken(min)" : ['mean' , 'std']}) )#como quero agrupar por cidade e tipo de pedido, meu groupby vai ser uma lista

    df1_aux.columns = ['avg_time' , 'std_time']
    df1_aux = df1_aux.reset_index()

    fig = px.sunburst(df1_aux, path=['City', 'Road_traffic_density'], values = 'avg_time',
                      color='std_time', color_continuous_scale='RdBu',
                      color_continuous_midpoint=np.average(df1_aux['std_time'] ) )
    return fig

def avg_std_time_graph( df1 ):
    st.title(" Tempo Medio de Entrega por Cidade")
    df1_aux = df1.loc[: , ['City' , 'Time_taken(min)']].groupby(['City']).agg ( {'Time_taken(min)' : ['mean' , 'std']})
    df1_aux.columns = ['avg_time' , 'std_time']
    df1_aux = df1_aux.reset_index()
    
    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control', x=df1_aux['City'], y=df1_aux['avg_time'], error_y=dict ( type='data', array=df1_aux['std_time'] ) ) ) # error y é meu desvio padrão está na documentação, se preocupe na lógica
    fig.update_layout(barmode='group')
    return fig

def avg_std_time_delivery(df1 , festival, op):
    """
        Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
        Parâmetros:
            Imput:
                -df: Dataframe com os dados necessários para o cálculo
                -op: Tipo de operação que precisa ser calculado
                   'avg_time': Calcula o tempo médio
                   'std_time': Calcula o desvio padrão do tempo.
            Output:
                - df: Dataframe com 2 colunas e 1 linha
    """
    df1_aux = (df1.loc[: , [ "Time_taken(min)" , "Festival"]]
                  .groupby("Festival")
                  .agg ( {"Time_taken(min)" : ['mean' , 'std']}))
                
    df1_aux.columns = ['avg_time' , 'std_time']
                
    df1_aux = df1_aux.reset_index() #transformando o Festival em coluna para depois fazer uma seleção.
                
    linhas_selecionadas = df1_aux["Festival"] == festival #estou criando minha condição
                
    df1_aux = np.round(df1_aux.loc[linhas_selecionadas, op],2) # quero só o tempo médio por isso uso o avg time e não todas as colunas.
    
    return df1_aux


def distance( df1, fig ):
    if fig  == False:
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
     #crio uma coluna distance
        df1['distance'] = df1.loc [:, cols].apply( lambda x: 
                                     haversine((x ['Restaurant_latitude'], x['Restaurant_longitude']), 
                                     (x['Delivery_location_latitude'], x['Delivery_location_longitude'] ) ), axis=1 )
        avg_distance = np.round(df1['distance'].mean(), 2) #aplicado a média na distância, np da biblioteca numpy é para arredondar os números.
        return avg_distance
    else:
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 
                'Restaurant_latitude', 'Restaurant_longitude']
#crio uma coluna distance
        df1['distance'] = df1.loc [:, cols].apply( lambda x: 
                                     haversine((x ['Restaurant_latitude'], x['Restaurant_longitude']), 
                                     (x['Delivery_location_latitude'], x['Delivery_location_longitude'] ) ), axis=1 ) 
        avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        fig=go.Figure(data=[ go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0,0.1,0])])
        
        return fig

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
#=========================================================
# import dateset
#=========================================================
df = pd.read_csv ('Projeto 1\\train.csv')

#Limpando os dados
df1 = clean_code (df)

# ==============================================================================
# Barra Lateral
# ==============================================================================
st.header('Marketplace - Visão Restaurantes')

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
        st.title(" Overal Metrics")
        col1, col2, col3, col4, col5, col6 = st.columns (6)
        with col1:
            delivery_unique = len(df1.loc [: , 'Delivery_person_ID'].unique()) # len faz a contagem de uma lista que eu criei
            col1.metric('Entregadores únicos', delivery_unique)

        with col2:
            avg_distance = distance ( df1, fig=False )
            col2.metric('A distancia media', avg_distance) # distancia media das entregas         
        
        with col3: #col 3 e 4 são muito parecidas, então eu crio uma função                            
            df1_aux = avg_std_time_delivery ( df1, 'Yes',  'avg_time' )
            col3.metric('Tempo médio', df1_aux)
            
        with col4:
            df1_aux = avg_std_time_delivery ( df1, 'Yes', 'std_time' )
            col4.metric('STD Entrega', df1_aux)
            
        with col5:
            df1_aux = avg_std_time_delivery ( df1, 'No', 'avg_time' )
            col5.metric('Tempo Médio ', df1_aux) # tempo médio de entrega com festival 
            
        with col6:
            df1_aux = avg_std_time_delivery ( df1, 'No', 'std_time' )
            col6.metric('STD Entrega', df1_aux) # std é o que chamo de desvio padrão com festival rolando , lembrar disso.

    with st.container():
        st.markdown("""---""")
        col1, col2 = st.columns ( 2 )

        with col1:
            fig = avg_std_time_graph ( df1 )
            st.plotly_chart(fig)
        
        with col2:
             st.title(" Tempo Medio de Entrega por Cidade")

             df1_aux = (df1.loc[: ,  ["City" , "Time_taken(min)" , "Type_of_order"]]
                          .groupby(["City" , "Type_of_order"])
                          .agg ( {"Time_taken(min)" : ['mean' , 'std']}) )#como quero agrupar por cidade e tipo de pedido, meu groupby vai ser uma lista

             df1_aux.columns = ['avg_time' , 'std_time']
             df1_aux = df1_aux.reset_index()
             st.dataframe(df1_aux)
        
    with st.container():
        st.markdown("""---""")
        st.title(" Distribuição do Tempo")

        col1, col2 = st.columns (2 )
        with col1:    
            fig= distance(df1, fig=True)
            st.plotly_chart( fig )

        with col2:
            fig = avg_std_time_on_traffic( df1 ) 
            st.plotly_chart(fig)





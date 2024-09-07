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

st.set_page_config(page_title= 'Visão Empresa', page_icon='📈', layout='wide')

#=================================================
# Funções
#=================================================
def country_maps(df1):
        
    df1_aux = df1.loc[: , ['City' , 'Road_traffic_density' , 'Delivery_location_latitude' , 'Delivery_location_longitude']].groupby (['City' , 'Road_traffic_density']).median().reset_index()
        
    df1_aux = df1_aux.loc[df1_aux['Road_traffic_density'] != 'NaN' , :] #limpeza
    df1_aux = df1_aux.loc[df1_aux['City'] != 'NaN' , :]
    
    #desenhar o mapa, vou pegar uma biblioteca chamada folium
    
    map = folium.Map()
    
    #folium.Marker coloca pontos no map


    for index, location_info in df1_aux.iterrows(): #interrows é objeto de interação
        folium.Marker([location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']], popup=location_info[['City', 'Road_traffic_density']]).add_to(map)
    folium_static(map, width=1024 , height=600)

#fazer uma nova função
def order_share_by_week(df1):
         
    #Quantidade de pedidos por semana / Número único de entregadores por semana , preciso fazer em duas partes
    
    #Primeira -> parte numero de pedidos por semana
    
    df1_aux01 = df1.loc[: , ['ID' , 'week_of_year']].groupby ('week_of_year').count().reset_index()    
    df1_aux02 = (df1.loc[: , ['Delivery_person_ID' , 'week_of_year']]
                    .groupby('week_of_year')
                    .nunique()
                    .reset_index()) # quantidade de entregadores unicos na semana
    
    #antes de dividir eu preciso juntar essas coisas (df1_aux01 e df1_aux02)
    
    #como juntar dois Data frames, vou usar a função merge que está na biblioteca pd e o comando how
    
    df1_aux = pd.merge(df1_aux01, df1_aux02, how = 'inner')
    
    #Agora eu posso dividir e criar uma nova coluna que é a Order_by_deliver
    
    df1_aux['Order_by_deliver'] = df1_aux['ID'] / df1_aux['Delivery_person_ID']
    
    #Gráfico
    
    fig = px.line(df1_aux, x='week_of_year' , y= 'Order_by_deliver')

    return fig

def order_by_week(df1):
    #Preciso Cálcular a semana
        
    #criar a coluna de semana
    #utilizo a função STRFTIME( string format time) ele vai formata a string no tempo, e o %U onde começa o início da semana. depois coloco o .dt que transformar o series em data
    df1['week_of_year'] = df1 ['Order_Date'].dt.strftime( '%U')
        
    #depois de criada a coluna eu faço a contagem
    df1_aux = df1.loc[: , ['ID' , 'week_of_year']].groupby('week_of_year').count().reset_index()
        
    #agora desenho gráfio de linhas
        
    fig = px.line(df1_aux, x='week_of_year' , y='ID')

    return fig

def traffic_order_city(df1):
    #calcular o volume de pedidos
    df1_aux = (df1.loc[: , ['ID' , 'City' , 'Road_traffic_density']]
                  .groupby( ['City' , 'Road_traffic_density'] )
                  .count()
                  .reset_index())
    
    #df1_aux = df1_aux.loc[df1_aux['City'] != 'NaN' , :]
    #gráfico
    fig = px.scatter(df1_aux, x='City', y= 'Road_traffic_density' , size='ID', color='City') #Size da o tamanho da bolha

    return fig

def traffic_order_share(df1):
#preciso cálcular aqui
    df1_aux = (df1.loc[: , ['ID', 'Road_traffic_density']]
                  .groupby('Road_traffic_density')
                  .count()
                  .reset_index())
                
#mas eu quero a % e preciso criar uma nova coluna dentro do df_aux
    df1_aux['entregas_perc'] = df1_aux['ID'] / df1_aux['ID'].sum() #aqui eu somo a coluna toda do ID e divido por cada uma das linhas e tenho uma %
    
#gráfico de pizza
    fig = px.pie(df1_aux, values = 'entregas_perc' , names= 'Road_traffic_density') #values é a coluna que a gente quer , names coluna que a gente quer
    
    return fig

def order_metric(df1): # função conta os pedidos por dias, recebe um dataframe , executa o dataframe, gera uma figura e passa a figura para mim!
    cols = ['ID', 'Order_Date'] # recebe o cols
    #selecai de linhas
    df1_aux = df1.loc[ : , cols].groupby(['Order_Date']).count().reset_index() # reseto o index para transformar o order date em coluna, faz o agrupamento com df1
    
    #desenhar o gráfico de linhas    
    #quero um gráfico de barras, mas px não funciona no streamlit, preciso usar um função específica .
        
    fig = px.bar(df1_aux, x='Order_Date' , y='ID') # dx_aux são meus dados, depois a variavel no meu eixo x e depois a variavel no meu eixo y, faz a figura

    return fig # retorna a figura

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
#=========================================Inicio da Estrutura Lógica do Código=====================
#=========================================
# import dateset
#=========================================
df = pd.read_csv ('../dataset/train.csv')

#Limpando os dados
df1 = clean_code(df)



# ==============================================================================
# Barra Lateral
# ==============================================================================
st.header('Marketplace - Visão Cliente')

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
st.dataframe(df1)

# ==============================================================================
# Layout no Streamlit
# ==============================================================================
# criar abas, comando tabs que tu passa listas dentro dele e cria paginas ali

tab1, tab2, tab3 = st.tabs ( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

#quando usar whit tudo que tiver dentro do whit vai ficar dentro dele
#tudo que estiver identado nesta tab1 vai ficar na visão gerencial
with tab1:
    with st.container():
        #Order Metric
        fig = order_metric(df1) # chamei a função la de cima passando df1, recebi a figura
        st.markdown('# Order by Day') # desenhei o titulo
        st.plotly_chart(fig, use_container_width=True) # container true é para caber dentro do espaco, coloco a figura dentro da variável fig, use a largura do container, plotamos a figura
            
    with st.container():
        col1, col2 = st.columns(2)
       
        with col1:
            fig = traffic_order_share( df1 )
            st.header('Traffic Order Share')
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            fig = traffic_order_city(df1)
            st.header("Traffic Order City")
            st.plotly_chart(fig, use_container_width=True)
    
    #dentro de tab1 vou construir colunas, e preciso do with para criar
        
with tab2:
    with st.container():
        fig = order_by_week(df1)
        st.markdown("# Order by Week")
        st.plotly_chart(fig, use_container_width=True)
        
    with st.container ():
        st.markdown("# Order Share by Week")
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

         
         
with tab3:
    st.markdown("# Country Maps")
    country_maps (df1)
    
    






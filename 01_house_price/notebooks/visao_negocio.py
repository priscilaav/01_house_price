
#Imports
from haversine import haversine
from PIL import Image
from streamlit_folium import folium_static
from branca.colormap import LinearColormap
from sklearn.ensemble import RandomForestRegressor


import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import folium
import pickle
import numpy as np

df = pd.read_csv('../data/data4.csv')


# COPIAR TODO O CÓDIGO AQUI


# ==================================
# lAYOUT NO STREAMLIT
# ==================================
st.set_page_config(
    page_title = 'Página Inicial',
    page_icon=':house_buildings:')

#image_path = 'house-for-sale.png'
#image = Image.open(image_path)
#st.sidebar.image( image, width=120)


#st.sidebar.markdown('## Vendas de Casas')
#st.sidebar.markdown('## Condado de King')
#st.sidebar.markdown("""___""")

#st.dataframe(df)

# TABELAS - CONTAINERS =================================================================================

tab1, tab2 = st.tabs(['Página Inicial','Predição'])




#TAB 1 ------------------------------------------------------------------------------------------------ 

# Função para a primeira página
#def primeira_pagina():
with tab1:    
    st.header('Bem-vindo à Análise de Preços de Casas no Condado de King, EUA!')
    st.write('Explore os preços das casas no Condado de King, Washington, e descubra onde você pode encontrar sua próxima moradia dos sonhos. Use nosso mapa interativo para filtrar casas com base no intervalo de preço desejado e na condição da casa. Encontre a casa perfeita para você no lugar que você chama de lar.')
    st.markdown('####')
    st.markdown("""___""")
    
   #------------------------------------------------------------------------------------------------ 
    st.markdown('### Conheça nossos números')
    with st.container():    
        col1, col2, col3, col4 = st.columns(4)

        #Quantidade de casas disponíveis para venda
        with col1:
            numero_casas = df['id'].nunique()
            st.metric('Casas para venda', numero_casas)

        # Calculando a minimo do preço das casas
        with col2:
            preco_min = round(df['price'].min(), 2)
            st.metric('Preço mínimo das casas', preco_min)
            
        # Calculando o preço médio das casas
        with col3:
            preco_medio = round(df['price'].mean(), 2)
            st.metric('Preço médio das casas', preco_medio) 

        # Calculando a máximo do preço das casas
        with col4:
            preco_max = round(df['price'].max(), 2)
            st.metric('Preço máximo das casas', preco_max) 

        
        st.write('Com mais de 21,000 casas disponíveis para venda, possuímos uma variedade de opções para todos os gostos e necessidades. Desde casas acessíveis a partir de 78,000.00 até luxuosas propriedades com preços de até 7,700,000.00, temos algo para todos. Explore nossa seleção e encontre a casa dos seus sonhos hoje mesmo!')
        st.markdown('####')

    
        
#TAB 2 ------------------------------------------------------------------------------------------------ 


    # Define as colunas
    coluna1, coluna2 = st.columns(2)
    altura = 250
    
    # FILTRO 1 (Preço) ------------------------------------------------------------------------------------------------ 
    
    # Define o container dentro da coluna
    with coluna1:
        with st.container(height=altura):
            st.markdown('##### Selecione o intervalo de preço da casa:')
            valor_minimo = st.number_input('Valor mínimo da casa (78,000)', min_value=78000, max_value=7700000, value=78000, step=10000)
            valor_maximo = st.number_input('Valor máximo da casa (7,700,000)', min_value=78000, max_value=7700000, value=90000, step=10000)

            # Selecionar os dados de acordo com o intervalo inserido
            df_filtrado_intervalo = df[(df['price'] >= valor_minimo) & (df['price'] <= valor_maximo)]

    # FILTRO 2 (Condição) ------------------------------------------------------------------------------------------------ 
    
    def mapear_condicao(valor):
        if valor == 1:
            return "Ruim"
        elif valor == 2:
            return "Regular"
        elif valor == 3:
            return "Média"
        elif valor == 4:
            return "Boa"
        elif valor == 5:
            return "Excelente"
        else:
            return "Desconhecido"

    # Opções para o selectbox
    opcoes_condicao = [mapear_condicao(i) for i in range(1, 6)]

    # Define o container dentro da coluna
    with coluna1:
        with st.container(height=altura):
            st.markdown('##### Selecione a condição da casa:')
            condicao_selecionada = st.selectbox(
                '(Deixe em branco para todas)',
                [''] + opcoes_condicao
            )

        # Verifica se a condição foi selecionada
        if condicao_selecionada:
            # Selecionar os dados de acordo com a condição selecionada
            condicao_numerica = opcoes_condicao.index(condicao_selecionada) + 1
            df_filtrado_intervalo = df_filtrado_intervalo[df_filtrado_intervalo['condition'] == condicao_numerica]
        else:
            # Manter todos os dados se nenhum filtro de condição for selecionado
            pass

    # FILTRO 3 (Bedrooms) ------------------------------------------------------------------------------------------------ 
    
    with coluna2:
        with st.container(height=altura):
            st.markdown('##### Selecione a quantidade de quartos:')
            quartos_selecionados = st.selectbox(
                '(Deixe em branco para todas)',
                [''] + list(df['bedrooms'].unique())
            )
        
        if quartos_selecionados:
            # Filtrar os dados com base na quantidade de quartos selecionada
            df_filtrado_intervalo = df_filtrado_intervalo[df_filtrado_intervalo['bedrooms'] == quartos_selecionados]
        else:
            # Manter todos os dados se nenhum filtro de quartos for selecionado
            pass

    # FILTRO 4 (Bathrooms) ------------------------------------------------------------------------------------------------ 
    
    with coluna2:
        with st.container(height=altura):
            st.markdown('##### Selecione a quantidade de banheiros:')
            banheiros_selecionados = st.selectbox(
                '(Deixe em branco para todas)',
                [''] + list(df['bathrooms'].unique())
            )

        if banheiros_selecionados:
            # Filtrar os dados com base na quantidade de banheiros selecionada
            df_filtrado_intervalo = df_filtrado_intervalo[df_filtrado_intervalo['bathrooms'] == banheiros_selecionados]
        else:
            # Manter todos os dados se nenhum filtro de banheiros for selecionado
            pass
        
    # MAPA ------------------------------------------------------------------------------------------------ 

    st.markdown('##### Localização do imóvel:')
    st.write('Clique no marcador para obter mais informações sobre o imóvel')

    # Criar o mapa
    mapa = folium.Map(location=[df_filtrado_intervalo['lat'].mean(), df_filtrado_intervalo['long'].mean()], zoom_start=10)

    # Adicionar marcadores ao mapa com cores variadas com base no preço
    for _, local in df_filtrado_intervalo.iterrows():
        folium.Marker(icon=folium.Icon( shadow=False),
            location=[local['lat'], local['long']],
            popup=f"Preço: ${local['price']}, Quartos: {local['bedrooms']}, Banheiros: {local['bathrooms']}, Condição: {local['condition']}"
        ).add_to(mapa)

    # Exibir o mapa atualizado
    folium_static(mapa)


    
    
# TAB 3 ------------------------------------------------------------------------------------------------ 
    
# Função para a segunda página
#def segunda_pagina():
with tab2:
    st.header('Descubra o Preço da Sua Próxima Casa!')
    st.write('Insira algumas informações sobre a casa dos seus sonhos e deixe nosso modelo preditivo estimar o preço para você. Encontre o valor estimado da sua futura casa no Condado de King, Washington, e esteja um passo mais perto de tornar seus sonhos realidade.')
    st.markdown('####')

    # Carregue o modelo treinado
    with open('C:/Users/prisc/OneDrive/Documentos/Dados/DS_prod/1_preco_casas/model/model_house_price.pkl', 'rb') as file:
        rf_model = pickle.load(file)

    def predict_price(features):
        # Faça as previsões usando o modelo
        prediction = rf_model.predict(features.reshape(1, -1))
        return prediction

    def main():
        #st.markdown('### Previsão de Preços de Casas')

        # Crie widgets para inserir valores das variáveis
        sqft_living = st.slider('Área residencial - Square feet(sqft_living)', min_value=370, max_value=13540, value=1180)
        sqft_lot = st.slider('Área do Lote - Square feet (sqft_lot)', min_value=520, max_value=1651359, value=5650)
        sqft_above = st.slider('Área acima do solo - Square feet (sqft_above)', min_value=370, max_value=9410, value=1180)
        waterfront = st.radio('Beira-mar (1 se sim, 0 se não)', [0, 1], index=0)
        view = st.slider('Vista  (maior melhor)', min_value=0, max_value=4, value=0)
        grade = st.slider('Condição da construção (maior melhor)', min_value=3, max_value=13, value=7)
        bedrooms = st.slider('Número de quartos (1 to 9)', min_value=1, max_value=9, value=3)
        bathrooms = st.slider('Número de banheiros (0.50 to 6.25, in increments of 0.25)', min_value=0.50, max_value=6.25, step=0.25, value=0.5)
        lat = st.slider('Latitude ', min_value=47.1559, max_value=47.7776, value=47.5112)
        long = st.slider('Longitude ', min_value=-122.257, max_value=-121.315, value=-122.257)
        sqft_liv15 = st.slider('Tamanho Médio da Área de Vida das 15 Casas Mais Próximas ', min_value=699, max_value=6210, value=1340)
        sqft_lot15 = st.slider('Tamanho Médio do Lote das 15 Casas Mais Próximas ', min_value=651, max_value=871200, value=5650)
        
        # Botão para fazer a previsão
        if st.button('Prever Preço'):
            # Insira os valores em um array numpy
            user_input = np.array([sqft_living, sqft_lot, sqft_above, waterfront, view, grade, bedrooms, bathrooms, lat, long, sqft_liv15, sqft_lot15])  # Adicione outros valores conforme necessário

            # Faça a previsão
            prediction = predict_price(user_input)

            # Exiba a previsão
            st.success(f'A previsão do preço é ${prediction[0]} ')

    if __name__ == '__main__':
        main()
        
        
        
   #------------------------------------------------------------------------------------------------ 
       
# Título na barra lateral
#sst.sidebar.title("# de Navegação")

# Define o estado inicial da página
#pagina = st.sidebar.radio("", ["Página Inicial", "Prevendo o Preço"])

# Renderiza o conteúdo da página selecionada
#if pagina == "Página Inicial":
#    primeira_pagina()
#elif pagina == "Prevendo o Preço":
#    segunda_pagina()

    
    
    
    
    
   
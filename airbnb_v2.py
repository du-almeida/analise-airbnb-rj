import pandas as pd
import streamlit as st
import locale
import altair as alt
import pydeck as pdk
import pandas as pd
# Definir o locale para o formato de moeda em Real Brasileiro
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Função para formatar os valores como moeda em Real
def formatar_moeda(valor):
    return locale.currency(valor, grouping=True)

# Carregar o arquivo CSV
url = 'https://data.insideairbnb.com/brazil/rj/rio-de-janeiro/2024-06-27/visualisations/listings.csv'
df = pd.read_csv(url)

# Limpeza e conversão da coluna 'price'
df['price'] = df['price'].replace('[\$,]', '', regex=True).astype(float)

# Conversão da coluna 'last_review' para o tipo datetime
df['last_review'] = pd.to_datetime(df['last_review'], errors='coerce')

# Exibir o logo na barra lateral
logo_url = "https://logodownload.org/wp-content/uploads/2016/10/airbnb-logo-0.png"
st.sidebar.image(logo_url, use_column_width=True)

st.sidebar.subheader('Filtros:')
data_min = df['last_review'].min()
data_max = df['last_review'].max()

# Seleção do intervalo de datas no menu lateral
data_inicio, data_fim = st.sidebar.date_input(
    "Selecione o intervalo de datas",
    [data_min, data_max],  # valor padrão
    min_value=data_min,
    max_value=data_max
)

# Filtro de bairros (inclui a opção "Todos")
bairros_disponiveis = ['Todos'] + sorted(df['neighbourhood'].unique())
bairro_selecionado = st.sidebar.selectbox("Selecione o Bairro", bairros_disponiveis)

# Filtro de tipo de quarto
tipos_quarto_disponiveis = sorted(df['room_type'].unique())
tipo_quarto_selecionado = st.sidebar.selectbox("Selecione o Tipo de Quarto", ['Todos'] + tipos_quarto_disponiveis)

# Filtro de preço
preco_min, preco_max = st.sidebar.slider(
    "Selecione o Intervalo de Preços (R$)",
    float(df['price'].min()), float(df['price'].max()), (float(df['price'].min()), float(df['price'].max()))
)

# Filtrar o DataFrame com base nos filtros selecionados
df_filtrado = df[
    (df['neighbourhood'].apply(lambda x: x == bairro_selecionado or bairro_selecionado == 'Todos')) &
    (df['room_type'].apply(lambda x: x == tipo_quarto_selecionado or tipo_quarto_selecionado == 'Todos')) &
    (df['price'] >= preco_min) &
    (df['price'] <= preco_max)
]

# Análise 1: Top 10 Bairros mais caros (gráfico de barras com linha do preço)
st.title('Análises Airbnb - Rio de Janeiro')
st.subheader('Top 10 Bairros Mais Caros no Rio de Janeiro')

media_preco_bairro = df_filtrado.groupby('neighbourhood')['price'].mean().sort_values(ascending=False).head(10).reset_index()

# Gráfico cruzado com barra e linha usando Altair
bar_chart = alt.Chart(media_preco_bairro).mark_bar(color='pink').encode(
    x=alt.X('neighbourhood', sort='-y', title='Bairro'),
    y=alt.Y('price', title='Preço Médio (R$)')
).properties(width=600)

line_chart = alt.Chart(media_preco_bairro).mark_line(color='red').encode(
    x=alt.X('neighbourhood', sort='-y'),
    y='price'
)

# Combinar gráficos
st.altair_chart(bar_chart + line_chart)

# Análise 2: Quantidade de avaliações (number_of_reviews) por bairro
st.subheader('Quantidade de Avaliações por Bairro')

avaliacoes_por_bairro = df_filtrado.groupby('neighbourhood')['number_of_reviews'].sum().sort_values(ascending=False).reset_index()

bar_chart_avaliacoes_bairro = alt.Chart(avaliacoes_por_bairro).mark_bar(color='pink').encode(
    x=alt.X('neighbourhood', sort='-y', title='Bairro'),
    y=alt.Y('number_of_reviews', title='Número de Avaliações')
).properties(width=600)

st.altair_chart(bar_chart_avaliacoes_bairro)

# Análise 3: Quantidade de avaliações (number_of_reviews) por tipo de quarto (gráfico de pizza)
st.subheader('Quantidade de Avaliações por Tipo de Quarto')

avaliacoes_por_tipo = df_filtrado.groupby('room_type')['number_of_reviews'].sum().sort_values(ascending=False).reset_index()

# Gráfico de pizza usando Altair
pie_chart = alt.Chart(avaliacoes_por_tipo).mark_arc().encode(
    theta=alt.Theta(field='number_of_reviews', type='quantitative', title='Número de Avaliações'),
    color=alt.Color(field='room_type', type='nominal', title='Tipo de Quarto'),
    tooltip=['room_type', 'number_of_reviews']
).properties(width=600, height=400)

st.altair_chart(pie_chart)

# Análise 4: Top 10 Anfitriões (host_name) pela quantidade de avaliações
st.subheader('Top 10 Anfitriões com Mais Avaliações')

top_anfitrioes = df_filtrado.groupby('host_name')['number_of_reviews'].sum().sort_values(ascending=False).head(10).reset_index()

bar_chart_anfitrioes = alt.Chart(top_anfitrioes).mark_bar(color='pink').encode(
    x=alt.X('host_name', sort='-y', title='Anfitrião'),
    y=alt.Y('number_of_reviews', title='Número de Avaliações')
).properties(width=600)

st.altair_chart(bar_chart_anfitrioes)

# Análise 5: Mapa de locais com avaliações

st.subheader('Mapa de Locais com Avaliações')

# Filtrar locais com pelo menos uma avaliação
df_com_avaliacoes = df_filtrado[df_filtrado['number_of_reviews'] > 0]

# Criar gráfico de mapa com pydeck
view_state = pdk.ViewState(
    latitude=-22.9068,  # Latitude central do Rio de Janeiro
    longitude=-43.1729,  # Longitude central do Rio de Janeiro
    zoom=10,
    pitch=50,
)

# Layer para exibir os pontos no mapa
layer = pdk.Layer(
    'ScatterplotLayer',
    data=df_com_avaliacoes,
    get_position='[longitude, latitude]',
    get_radius=200,
    get_color=[255, 0, 0],  # Cor vermelha
    pickable=True
)

# Renderizar o mapa
r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{name}\nNúmero de Avaliações: {number_of_reviews}"}
)

st.pydeck_chart(r)

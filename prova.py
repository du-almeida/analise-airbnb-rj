import pandas as pd
import streamlit as st
import locale
import altair as alt
import pydeck as pdk
import google.generativeai as ai
import grpc

api_key='Chave de API'
ai.configure(api_key=api_key)

# Formato de moeda em Real Brasileiro
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Função para formatar os valores como moeda em Real
def formatar_moeda(valor):
    return locale.currency(valor, grouping=True)

# CSV
url = 'https://data.insideairbnb.com/brazil/rj/rio-de-janeiro/2024-06-27/visualisations/listings.csv'
df = pd.read_csv(url)

# Limpeza e conversão da coluna 'price'
df['price'] = df['price'].replace('[\$,]', '', regex=True).astype(float)

# Conversão da coluna 'last_review' para o tipo datetime
df['last_review'] = pd.to_datetime(df['last_review'], errors='coerce')

# Logo na barra lateral
logo_url = "https://logodownload.org/wp-content/uploads/2016/10/airbnb-logo-0.png"
st.sidebar.image(logo_url, use_container_width=True)

st.sidebar.subheader('Filtros:')
data_min = df['last_review'].min()
data_max = df['last_review'].max()

# Seleção do intervalo de datas no menu lateral
data_inicio, data_fim = st.sidebar.date_input(
    "Selecione o intervalo de datas",
    [data_min, data_max],
    min_value=data_min,
    max_value=data_max
)

# Filtro de bairros
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

# DataFrame com base nos filtros selecionados
df_filtrado = df[
    (df['neighbourhood'].apply(lambda x: x == bairro_selecionado or bairro_selecionado == 'Todos')) &
    (df['room_type'].apply(lambda x: x == tipo_quarto_selecionado or tipo_quarto_selecionado == 'Todos')) &
    (df['price'] >= preco_min) &
    (df['price'] <= preco_max)
]

# Big Numbers no topo da página
total_reviews_filtrado = df_filtrado['number_of_reviews'].sum()
media_preco_filtrado = df_filtrado['price'].mean()
media_minimum_nights = df_filtrado['minimum_nights'].mean()

st.title('Análises Airbnb - Rio de Janeiro')
col1, col2, col3 = st.columns(3)
col1.metric(label="Total de Avaliações", value=total_reviews_filtrado)
col2.metric(label="Média de Preço (R$)", value=formatar_moeda(media_preco_filtrado))
col3.metric(label="Média Minima de Noites", value=int(round(media_minimum_nights)))


# Análise 1: Top 10 Bairros mais caros

st.subheader('Top 10 Bairros Mais Caros no Rio de Janeiro')

media_preco_bairro = df_filtrado.groupby('neighbourhood')['price'].mean().sort_values(ascending=False).head(10).reset_index()

# Gráfico cruzado com barra e linha
bar_chart = alt.Chart(media_preco_bairro).mark_bar(color='pink').encode(
    x=alt.X('neighbourhood', sort='-y', title='Bairro'),
    y=alt.Y('price', title='Preço Médio (R$)')
).properties(width=600)

line_chart = alt.Chart(media_preco_bairro).mark_line(color='red').encode(
    x=alt.X('neighbourhood', sort='-y'),
    y='price'
)
st.altair_chart(bar_chart + line_chart)

#Analise dos resultados com Gemini IA atarvés de API

st.subheader('Análise IA (Gemini)')

model=ai.GenerativeModel('gemini-1.5-flash')

prompt = f"Considenrando que o Dataframe {df_filtrado} se trata de uma base de avaliações do Airbnb sobre locações do Rio de Janeiro, e possui colunas as seguintes colunas: id - número de id gerado para identificar o imóvel; name - nome da propriedade anunciada; host_id - número de id do anfitrião da propriedade; host_name - Nome do anfitrião; neighbourhood_group - esta coluna não contém nenhum valor válido; neighbourhood - nome do bairro; latitude - coordenada da latitude da propriedade; longitude - coordenada da longitude da propriedade; room_type - informa o tipo de quarto que é oferecido; price - preço para alugar o imóvel; minimum_nights - quantidade mínima de noites para reservar; number_of_reviews - número de reviews que a propriedade possui; last_review - data do último review; reviews_per_month - quantidade de reviews por mês; calculated_host_listings_count - quantidade de imóveis do mesmo anfitrião; availability_365 - número de dias de disponibilidade dentro de 365 dias. Faça uma análise de no máximo 5 linhas sobre os resultados obtidos no {media_preco_bairro}"
resposta_gemini = model.generate_content(prompt)
st.write(resposta_gemini.text)


# Análise 2: Quantidade de avaliações por bairro
st.subheader('Quantidade de Avaliações por Bairro')

avaliacoes_por_bairro = df_filtrado.groupby('neighbourhood')['number_of_reviews'].sum().sort_values(ascending=False).reset_index()

bar_chart_avaliacoes_bairro = alt.Chart(avaliacoes_por_bairro).mark_bar(color='pink').encode(
    x=alt.X('neighbourhood', sort='-y', title='Bairro'),
    y=alt.Y('number_of_reviews', title='Número de Avaliações')
).properties(width=600)

st.altair_chart(bar_chart_avaliacoes_bairro)

#Analise dos resultados com Gemini IA atarvés de API

st.subheader('Análise IA (Gemini)')

model=ai.GenerativeModel('gemini-1.5-flash')

prompt = f"Considenrando que o Dataframe {df_filtrado} se trata de uma base de avaliações do Airbnb sobre locações do Rio de Janeiro, e possui colunas as seguintes colunas: id - número de id gerado para identificar o imóvel; name - nome da propriedade anunciada; host_id - número de id do anfitrião da propriedade; host_name - Nome do anfitrião; neighbourhood_group - esta coluna não contém nenhum valor válido; neighbourhood - nome do bairro; latitude - coordenada da latitude da propriedade; longitude - coordenada da longitude da propriedade; room_type - informa o tipo de quarto que é oferecido; price - preço para alugar o imóvel; minimum_nights - quantidade mínima de noites para reservar; number_of_reviews - número de reviews que a propriedade possui; last_review - data do último review; reviews_per_month - quantidade de reviews por mês; calculated_host_listings_count - quantidade de imóveis do mesmo anfitrião; availability_365 - número de dias de disponibilidade dentro de 365 dias. Faça uma análise de no máximo 5 linhas sobre os resultados obtidos no {avaliacoes_por_bairro}"
resposta_gemini = model.generate_content(prompt)
st.write(resposta_gemini.text)

# Análise 3: Quantidade de avaliações por tipo de quarto
st.subheader('Quantidade de Avaliações por Tipo de Quarto')

avaliacoes_por_tipo = df_filtrado.groupby('room_type')['number_of_reviews'].sum().sort_values(ascending=False).reset_index()

# Gráfico de pizza usando Altair
pie_chart = alt.Chart(avaliacoes_por_tipo).mark_arc().encode(
    theta=alt.Theta(field='number_of_reviews', type='quantitative', title='Número de Avaliações'),
    color=alt.Color(field='room_type', type='nominal', title='Tipo de Quarto'),
    tooltip=['room_type', 'number_of_reviews']
).properties(width=600, height=400)

st.altair_chart(pie_chart)

#Analise dos resultados com Gemini IA atarvés de API

st.subheader('Análise IA (Gemini)')

model=ai.GenerativeModel('gemini-1.5-flash')

prompt = f"Considenrando que o Dataframe {df_filtrado} se trata de uma base de avaliações do Airbnb sobre locações do Rio de Janeiro, e possui colunas as seguintes colunas: id - número de id gerado para identificar o imóvel; name - nome da propriedade anunciada; host_id - número de id do anfitrião da propriedade; host_name - Nome do anfitrião; neighbourhood_group - esta coluna não contém nenhum valor válido; neighbourhood - nome do bairro; latitude - coordenada da latitude da propriedade; longitude - coordenada da longitude da propriedade; room_type - informa o tipo de quarto que é oferecido; price - preço para alugar o imóvel; minimum_nights - quantidade mínima de noites para reservar; number_of_reviews - número de reviews que a propriedade possui; last_review - data do último review; reviews_per_month - quantidade de reviews por mês; calculated_host_listings_count - quantidade de imóveis do mesmo anfitrião; availability_365 - número de dias de disponibilidade dentro de 365 dias. Faça uma análise de no máximo 5 linhas sobre os resultados obtidos no {avaliacoes_por_tipo}"
resposta_gemini = model.generate_content(prompt)
st.write(resposta_gemini.text)

# Análise 4: Top 10 Anfitriões pela quantidade de avaliações
st.subheader('Top 10 Anfitriões com Mais Avaliações')

top_anfitrioes = df_filtrado.groupby('host_name')['number_of_reviews'].sum().sort_values(ascending=False).head(10).reset_index()

bar_chart_anfitrioes = alt.Chart(top_anfitrioes).mark_bar(color='pink').encode(
    x=alt.X('host_name', sort='-y', title='Anfitrião'),
    y=alt.Y('number_of_reviews', title='Número de Avaliações')
).properties(width=600)

st.altair_chart(bar_chart_anfitrioes)

#Analise dos resultados com Gemini IA atarvés de API

st.subheader('Análise IA (Gemini)')

model=ai.GenerativeModel('gemini-1.5-flash')

prompt = f"Considenrando que o Dataframe {df_filtrado} se trata de uma base de avaliações do Airbnb sobre locações do Rio de Janeiro, e possui colunas as seguintes colunas: id - número de id gerado para identificar o imóvel; name - nome da propriedade anunciada; host_id - número de id do anfitrião da propriedade; host_name - Nome do anfitrião; neighbourhood_group - esta coluna não contém nenhum valor válido; neighbourhood - nome do bairro; latitude - coordenada da latitude da propriedade; longitude - coordenada da longitude da propriedade; room_type - informa o tipo de quarto que é oferecido; price - preço para alugar o imóvel; minimum_nights - quantidade mínima de noites para reservar; number_of_reviews - número de reviews que a propriedade possui; last_review - data do último review; reviews_per_month - quantidade de reviews por mês; calculated_host_listings_count - quantidade de imóveis do mesmo anfitrião; availability_365 - número de dias de disponibilidade dentro de 365 dias. Faça uma análise de no máximo 5 linhas sobre os resultados obtidos no {top_anfitrioes}"
resposta_gemini = model.generate_content(prompt)
st.write(resposta_gemini.text)

# Análise 5: Mapa de locais com avaliações

st.subheader('Mapa de Locais com Avaliações')

df_com_avaliacoes = df_filtrado[df_filtrado['number_of_reviews'] > 0]

# Gráfico de mapa
view_state = pdk.ViewState(
    latitude=-22.9068,
    longitude=-43.1729,
    zoom=10,
    pitch=50,
)

layer = pdk.Layer(
    'ScatterplotLayer',
    data=df_com_avaliacoes,
    get_position='[longitude, latitude]',
    get_radius=200,
    get_color=[255, 0, 0],
    pickable=True
)

r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{name}\nNúmero de Avaliações: {number_of_reviews}"}
)

st.pydeck_chart(r)

#Analise dos resultados com Gemini IA atarvés de API
st.subheader('Análise IA (Gemini)')

model=ai.GenerativeModel('gemini-1.5-flash')

prompt = f"Considenrando que o Dataframe {df_filtrado} se trata de uma base de avaliações do Airbnb sobre locações do Rio de Janeiro, e possui colunas as seguintes colunas: id - número de id gerado para identificar o imóvel; name - nome da propriedade anunciada; host_id - número de id do anfitrião da propriedade; host_name - Nome do anfitrião; neighbourhood_group - esta coluna não contém nenhum valor válido; neighbourhood - nome do bairro; latitude - coordenada da latitude da propriedade; longitude - coordenada da longitude da propriedade; room_type - informa o tipo de quarto que é oferecido; price - preço para alugar o imóvel; minimum_nights - quantidade mínima de noites para reservar; number_of_reviews - número de reviews que a propriedade possui; last_review - data do último review; reviews_per_month - quantidade de reviews por mês; calculated_host_listings_count - quantidade de imóveis do mesmo anfitrião; availability_365 - número de dias de disponibilidade dentro de 365 dias. Faça uma análise de no máximo 5 linhas sobre os resultados obtidos no {df_com_avaliacoes}"
resposta_gemini = model.generate_content(prompt)
st.write(resposta_gemini.text)

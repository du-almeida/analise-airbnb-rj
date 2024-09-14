import pandas as pd
import streamlit as st
import locale
import altair as alt

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

# Análise 1: Top 10 Bairros mais caros (gráfico de barras com linha do preço)
st.title('Análises Airbnb - Rio de Janeiro')
st.subheader('Top 10 Bairros Mais Caros no Rio de Janeiro')

media_preco_bairro = df.groupby('neighbourhood')['price'].mean().sort_values(ascending=False).head(10).reset_index()

# Gráfico cruzado com barra e linha usando Altair
bar_chart = alt.Chart(media_preco_bairro).mark_bar().encode(
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

avaliacoes_por_bairro = df.groupby('neighbourhood')['number_of_reviews'].sum().sort_values(ascending=False).reset_index()

bar_chart_avaliacoes_bairro = alt.Chart(avaliacoes_por_bairro).mark_bar().encode(
    x=alt.X('neighbourhood', sort='-y', title='Bairro'),
    y=alt.Y('number_of_reviews', title='Número de Avaliações')
).properties(width=600)

st.altair_chart(bar_chart_avaliacoes_bairro)

# Análise 3: Quantidade de avaliações (number_of_reviews) por tipo de quarto (gráfico de pizza)
st.subheader('Quantidade de Avaliações por Tipo de Quarto')

avaliacoes_por_tipo = df.groupby('room_type')['number_of_reviews'].sum().sort_values(ascending=False).reset_index()

# Gráfico de pizza usando Altair
pie_chart = alt.Chart(avaliacoes_por_tipo).mark_arc().encode(
    theta=alt.Theta(field='number_of_reviews', type='quantitative', title='Número de Avaliações'),
    color=alt.Color(field='room_type', type='nominal', title='Tipo de Quarto'),
    tooltip=['room_type', 'number_of_reviews']
).properties(width=600, height=400)

st.altair_chart(pie_chart)

# Análise 4: Top 10 Anfitriões (host_name) pela quantidade de avaliações
st.subheader('Top 10 Anfitriões com Mais Avaliações')

top_anfitrioes = df.groupby('host_name')['number_of_reviews'].sum().sort_values(ascending=False).head(10).reset_index()

bar_chart_anfitrioes = alt.Chart(top_anfitrioes).mark_bar().encode(
    x=alt.X('host_name', sort='-y', title='Anfitrião'),
    y=alt.Y('number_of_reviews', title='Número de Avaliações')
).properties(width=600)

st.altair_chart(bar_chart_anfitrioes)

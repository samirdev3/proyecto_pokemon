import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


# Load data
CSV_PATH = Path(__file__).parent / "pokedex_enriquecida.csv"
try:
	df = pd.read_csv(CSV_PATH)
except Exception:
	df = pd.DataFrame()


st.set_page_config(page_title="Pokedex Explorer", layout="wide")

view = st.sidebar.selectbox("Vista", ["Explorador de Combate", "Geografía Pokémon"])


def show_combat_explorer(df: pd.DataFrame):
	st.title("Explorador de Combate")

	col1, col2, col3 = st.columns(3)

	if df.empty:
		st.info("No hay datos para mostrar con los filtros seleccionados.")
		return

	# KPIs (guardando por si faltan columnas)
	with col1:
		if 'Ataque' in df.columns:
			st.metric("Pokémon con mayor Ataque", int(df['Ataque'].max()), delta=None)
		else:
			st.metric("Pokémon con mayor Ataque", "N/A")

	with col2:
		if 'Velocidad' in df.columns:
			st.metric("Pokémon con mayor Velocidad", int(df['Velocidad'].max()), delta=None)
		else:
			st.metric("Pokémon con mayor Velocidad", "N/A")

	with col3:
		if 'Total' in df.columns:
			st.metric("Máximo Total", int(df['Total'].max()), delta=None)
		else:
			st.metric("Máximo Total", "N/A")

	# Scatter Attack vs Defense
	if {'Ataque', 'Defensa', 'Nombre', 'Total'}.issubset(df.columns):
		fig = px.scatter(df, x='Ataque', y='Defensa', hover_name='Nombre', size='Total', title='Ataque vs Defensa')
		st.plotly_chart(fig, use_container_width=True)

	# Histogram HP
	if 'HP' in df.columns:
		fig2 = px.histogram(df, x='HP', nbins=20, title='Distribución de HP')
		st.plotly_chart(fig2, use_container_width=True)

	# Data table
	st.dataframe(df)


def show_geography(df: pd.DataFrame):
	st.title("Geografía Pokémon")
	st.write("Mapa de fuerza promedio por país (choropleth) y distribuciones por país")

	if df.empty:
		st.info("No hay datos para mostrar en la vista Geografía.")
		return

	# compute mean total by country
	country_col = None
	if 'Pais' in df.columns:
		country_col = 'Pais'
	elif 'País' in df.columns:
		country_col = 'País'

	if country_col is None or 'Total' not in df.columns:
		st.info("La columna de país o Total no está disponible en los datos.")
		return

	group = df.groupby(country_col, as_index=False)['Total'].mean().rename(columns={'Total': 'MediaTotal'})

	# choropleth
	fig_map = px.choropleth(group, locations=country_col, locationmode='country names', color='MediaTotal', title='Fuerza promedio por país')
	st.plotly_chart(fig_map, use_container_width=True)

	# top pokemons by country
	countries = sorted(df[country_col].dropna().unique().tolist())
	country_selected = st.selectbox("Selecciona país para ver detalles", [None] + countries)
	if country_selected:
		df_country = df[df[country_col] == country_selected]
		st.subheader(f"Top Pokémon en {country_selected}")
		if 'Total' in df_country.columns:
			st.dataframe(df_country.sort_values('Total', ascending=False).head(10))
		else:
			st.dataframe(df_country.head(10))

		if 'Tipo' in df_country.columns:
			fig_types = px.histogram(df_country, x='Tipo', title=f'Distribución de Tipos en {country_selected}')
			st.plotly_chart(fig_types, use_container_width=True)


if view == "Explorador de Combate":
	show_combat_explorer(df)
elif view == "Geografía Pokémon":
	show_geography(df)

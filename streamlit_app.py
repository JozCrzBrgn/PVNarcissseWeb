import streamlit as st

#? --- PAGE SETUP ---#
st.set_page_config(layout="wide")

inventarios_page = st.Page(
    page="views/inventario.py",
    title="Inventarios",
    icon="📋",
    default=True
)

venats_page = st.Page(
    page="views/ventas.py",
    title="Ventas",
    icon="📈"
)

metas_page = st.Page(
    page="views/metas.py",
    title="Metas",
    icon="🎯"
)

pasteles_celebracion_page = st.Page(
    page="views/todos_pasteles_celebracion.py",
    title="💲Pasteles de Celebración y Abonos",
    icon="🍰"
)

pasteles_celebracion_por_entregar_page = st.Page(
    page="views/pasteles_celebracion_por_entregar.py",
    title="Past. de Celeb. por Entregar",
    icon="🎂"
)

pasteles_celebracion_prod_page = st.Page(
    page="views/pasteles_celebracion_prod.py",
    title="Past. de Celeb. Producción",
    icon="📆"
)

#? --- NAVEGATION SETUP [WITH SECTIONS] ---#
pg = st.navigation(
    {
        "Información de sucursales": [inventarios_page, venats_page],
        "Pasteles de Celebración": [pasteles_celebracion_page, pasteles_celebracion_por_entregar_page, pasteles_celebracion_prod_page],
        "Métricas": [metas_page],
    }
)

#? --- SHARE ON ALL PAGES ---#
st.logo("assets/narcisse.png")
st.sidebar.text("Made with ❤️ by Joz")

#? --- RUN NAVEGATION ---#
pg.run()
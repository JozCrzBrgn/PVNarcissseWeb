import streamlit as st

#? --- PAGE SETUP ---#
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
    page="views/pasteles_celebracion.py",
    title="Past. de Celeb. por Entregar",
    icon="🎂"
)

#? --- NAVEGATION SETUP [WITH SECTIONS] ---#
pg = st.navigation(
    {
        "Información de sucursales": [inventarios_page, venats_page, pasteles_celebracion_page],
        "Métricas": [metas_page],
    }
)

#? --- RUN NAVEGATION ---#
pg.run()
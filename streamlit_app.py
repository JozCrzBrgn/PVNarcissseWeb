import streamlit as st

#? --- PAGE SETUP ---#
inventarios_page = st.Page(
    page="views/inventario.py",
    title="Inventario",
    icon=":material/inventory:",
    default=True
)

project_1_page = st.Page(
    page="views/mermas.py",
    title="Mermas",
    icon=":material/inventory_2:"
)

project_2_page = st.Page(
    page="views/abonos.py",
    title="Abonos",
    icon=":material/smart_toy:"
)

#? --- NAVEGATION SETUP [WITH SECTIONS] ---#
pg = st.navigation(
    {
        "Info": [inventarios_page],
        "projects": [project_1_page, project_2_page],
    }
)

#? --- RUN NAVEGATION ---#
pg.run()
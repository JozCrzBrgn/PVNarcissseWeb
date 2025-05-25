import streamlit as st
from config.auth import load_authenticator

#? --- PAGE SETUP ---#
st.set_page_config(layout="wide")


#? --- AUTH LOGIN ---#
authenticator = load_authenticator()
name, auth_status, username = authenticator.login()


if auth_status:
    st.session_state["name"] = name
    st.session_state["auth_status"] = auth_status
    st.session_state["username"] = username
    col1, col2 = st.columns([4,1])
    with col1:
        st.success('Bienvenid@ {}'.format(name))
    with col2:
        authenticator.logout('Logout', 'main')
elif auth_status is False:
    st.error("Usuario o contraseña incorrectos")
    st.stop()
elif auth_status is None:
    st.warning("Por favor ingresa tus credenciales")
    st.stop()




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

ventas_filtros_page = st.Page(
    page="views/ventas_filtros.py",
    title="Filtros Ventas",
    icon="🎛️"
)

compras_sucursales_page = st.Page(
    page="views/compras_sucursales.py",
    title="Compras sucursales",
    icon="🎛️"
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

pasteles_celebracion_entregado_levantado_page = st.Page(
    page="views/levantado_entrega_abonos.py",
    title="Abonos Entregado/Levantado",
    icon="💲"
)

pasteles_celebracion_prod_page = st.Page(
    page="views/pasteles_celebracion_prod.py",
    title="Past. de Celeb. Producción",
    icon="📆"
)

pasteles_celebracion_calendar = st.Page(
    page="views/pasteles_celebracion_calendar.py",
    title="Calendario Past. de Celeb.",
    icon="📆"
)

crear_pedido_inflalandia = st.Page(
    page="views/inflalandia/crear_pedido_inflalandia.py",
    title="🆕Crear pedido inflalandia",
    icon="🦆"
)

crear_pedido_inflalandia_caro = st.Page(
    page="views/inflalandia/crear_pedido_inflalandia_caro.py",
    title="🆕Crear pedido inflalandia Nuevos",
    icon="🦆"
)

editar_pedido_inflalandia = st.Page(
    page="views/inflalandia/editar_pedido_inflalandia.py",
    title="📝Editar pedido inflalandia",
    icon="🦆"
)

abonos_inflalandia = st.Page(
    page="views/inflalandia/abonos_inflalandia.py",
    title="💵Abonos inflalandia",
    icon="🦆"
)

pdfs_inflalandia = st.Page(
    page="views/inflalandia/pdfs_inflalandia.py",
    title="⬇️PDF inflalandia",
    icon="🦆"
)

agregar_producto = st.Page(
    page="views/alta_productos/agregar_producto.py",
    title="Agregar producto",
    icon="🎂"
)

costos_distribuidores = st.Page(
    page="views/distribuidores/costos_distribuidores.py",
    title="Costos Distribuidores",
    icon="🧮"
)


#? --- DYNAMIC NAVEGATION SETUP [WITH SECTIONS] ---#
nav_dict = {
        "Información de sucursales": [inventarios_page, venats_page, ventas_filtros_page, compras_sucursales_page],
        "Pasteles de Celebración": [pasteles_celebracion_calendar, pasteles_celebracion_page, pasteles_celebracion_por_entregar_page, pasteles_celebracion_prod_page, pasteles_celebracion_entregado_levantado_page],
        "Inflalandia": [crear_pedido_inflalandia, crear_pedido_inflalandia_caro, editar_pedido_inflalandia, abonos_inflalandia, pdfs_inflalandia],
        }
# Si el usuario está autenticado y es admin, agrega secciones adicionales
if st.session_state.get("auth_status") and st.session_state.get("username") == "admin":
    nav_dict.update({
        "Distribuidores": [costos_distribuidores],
        "Alta de Productos": [agregar_producto],
        "Métricas": [metas_page]
    })
# Mostrar navegación
pg = st.navigation(nav_dict)

#? --- SHARE ON ALL PAGES ---#
st.logo("assets/narcisse.png")
st.sidebar.text("Made with ❤️ by Joz")

#? --- RUN NAVEGATION ---#
pg.run()
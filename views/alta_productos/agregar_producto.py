
import pandas as pd
import streamlit as st


# Leer del estado de sesión
name = st.session_state.get("name")
auth_status = st.session_state.get("auth_status")
username = st.session_state.get("username")


if auth_status:
    
    st.title("Agregar producto 🎂🎂🎂")

    col1, col2, col3, col4, col5 = st.columns([2,1,1,1,1])
    with col1:
        nombre_producto = st.text_input("Nombre del producto")
    with col2:
        exp_cliente = st.number_input("Días de expiración para el cliente", value=7, step=1, min_value=7)
    with col3:
        exp_sucursal = st.number_input("Días de expiración para la sucursal", value=5, step=1, min_value=5)
    with col4:
        precio_compra = st.number_input("Precio de compra", value=599, step=1, min_value=1)
    with col5:
        precio_venta = st.number_input("Precio de venta", value=599, step=1, min_value=1)

    elegir_categoria = st.radio("Elige una opción para seleccionar tu categoría", ["Seleccionar una categoría actual", "Crear una nueva categoría"])
    if elegir_categoria == "Seleccionar una categoría actual":
        categoria_producto_actual = st.segmented_control(
            "Selecciona una categoría", 
            ["Temporada", "Especiales", "Gelatina Individual", "Gelatinas", "Individual", "4 Personas", "8 Personas", 
            "10 Personas (380)", "10 Personas (399)", "20 Personas (590)", "20 Personas (520)"], 
            default="Temporada"
            )
    else:
        categoria_producto_nueva = st.text_input("Dale un nombre a la nueva categoría del producto")

    if st.button("Agregar producto"):
        data = config.supabase.table(config.LISTA_PRODUCTOS).select("id").execute().data
        ids = pd.DataFrame(data)
        if nombre_producto!="":
            values = {
                "id":int(ids.id.max()) + 1,
                "productos":str.upper(nombre_producto),
                "precio_compra":precio_compra,
                "precio_venta":precio_venta,
                "categoria":categoria_producto_actual if elegir_categoria=="Seleccionar una categoría actual" else categoria_producto_nueva,
                "activada":1,
                "time_exp_cliente":exp_cliente,
                "time_exp_sucursal":exp_sucursal,
                "precio_ingredientes":0,
            }
            config.supabase.table(config.LISTA_PRODUCTOS).insert(values).execute()
            st.success("✅️ Producto agregago correctamente ✅️")
        else:
            st.warning("⚠️ No dejes campos vacios ⚠️")
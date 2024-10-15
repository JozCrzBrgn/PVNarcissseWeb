
from io import BytesIO

import pandas as pd
from datetime import datetime as dt
from datetime import timedelta as td 

import streamlit as st
import streamlit_authenticator as stauth

from config.configuration import config, read_json_from_supabase

tabs_pedidos = {
    "Coapa":"db02_pedidos_celebracion_coapa",
    "Oceania":"db02_pedidos_celebracion_oceania",
    "Tlanepantla":"db02_pedidos_celebracion_tlane",
}
indx_pedidos = {
    "Coapa":"CO",
    "Oceania":"OC",
    "Tlanepantla":"TL",
}


#* USER AUTHENTICATION
credenciales = read_json_from_supabase(config.BUCKET_GENERAL, config.CREDENCIALES_FILE)
authenticator = stauth.Authenticate(
    credenciales,
    st.secrets["COOKIE_NAME"],
    st.secrets["COOKIE_KEY"],
    int(st.secrets["COOKIE_EXPIRY_DAYS"]),
)
name, authentication_status, username = authenticator.login()

if authentication_status is False:
    st.error('Nombre de usuario o contraseña incorrectos')
elif authentication_status is None:
    st.warning('Por favor, ingresa tu nombre de usuario y contraseña')
elif authentication_status:
    col1, col2 = st.columns([4,1])
    with col1:
        st.success('Bienvenid@ {}'.format(name))
    with col2:
        authenticator.logout('Logout', 'main')
    
    st.title("Realizar pedido inflalandia 🐤🐤🐤")

    if name=="Juan Tinajero" or name=="Sr. Silvia":
        st.text("En construcción 🏗️🚧👷🏼‍♂️...")
    else:
        num_pasteles_costo = read_json_from_supabase(config.BUCKET_GENERAL, config.COSTOS_INFLALANDIA_FILE)

        col1, col2, col3 = st.columns([1,2,1])
        with col1:
            sucursal_infla = st.selectbox("Selecciona una ubicación", ["Coapa", "Oceania", "Tlanepantla"])
        with col2:
            st.header("")
        with col3:
            past_date = dt.now() - td(days=35)
            past_date_str = past_date.strftime("%Y-%m-%d")           
            hoja_pedidos = config.supabase.table(tabs_pedidos[sucursal_infla]).select("*").gte("fecha_pedido", past_date_str).execute().data
            lista = list(set([item['clave'] for item in hoja_pedidos]))
            if lista == []:
                # Si no hay ID´s, creamos el inicial
                clave = f"{indx_pedidos[sucursal_infla]}000000001"
                st.header(f"CLAVE: {clave}")
            else:
                # Si hay ID´s, calculamos el valor del ID consecutivo
                numero = str(max([int(elemento[2:]) for elemento in lista]) + 1)
                clave = indx_pedidos[sucursal_infla] + '0'*(9-len(numero)) + numero
                st.header(f"CLAVE: {clave}")

        col1, col2 = st.columns(2)
        with col1:
            cliente_infla  = st.text_input("Nombre del cliente")
        with col2:
            leyenda_infla = st.text_input("Leyenda")

        col1, col2, col3 = st.columns(3)
        with col1:
            fecha_pedido_infla = st.date_input("Fecha del pedido")
        with col2:
            fecha_entrega_infla = st.date_input("Fecha de entrega")
        with col3:
            hora_entrega_infla = st.time_input("Hora de entrega")

        col1, col2, col3 = st.columns(3)
        with col1:
            tipos_relleno = [
                "Pan de chocolate con nutela", "Pan de vainilla con nutela", "Pan de chocolate con crema pastelera", 
                "Pan de vainilla con crema pastelera", "Pan de vainilla con durazno y crema", 
                "Pan de vainilla con fresas y crema"
                ]
            relleno_infla = st.selectbox("Relleno", tipos_relleno)
        with col2:
            numPersonas_infla = st.selectbox("Número de personas", list(num_pasteles_costo.keys()))
        with col3:
            extras_infla = st.number_input("Extras", step=100.0, min_value=0.0)
        descripcion_infla = st.text_area("Descripción/comentarios del pastel")

        costo_total = float(num_pasteles_costo[numPersonas_infla]) + extras_infla
        st.metric("COSTO TOTAL", f"$ {costo_total} MXN")
        '''values = {
                "email":"",
                "celular":"",
                "personas":"", #!
                "lugar_entrega":"",
                "empleado":"",
                "flete":"",
            }'''
        
        values = {
                "clave":clave,
                "cliente":cliente_infla,
                "fecha_entrega": dt.strftime(fecha_entrega_infla, "%Y-%m-%d"),
                "hora_entrega":str(hora_entrega_infla),
                "descuento":costo_total,
                "relleno":relleno_infla,
                "descripcion":descripcion_infla,
                "fecha_pedido":dt.strftime(fecha_pedido_infla, "%Y-%m-%d"),
                "estatus":"DANDO DE ALTA",
                "sucursal":sucursal_infla,
                "extras":extras_infla,
                "leyenda":leyenda_infla,
                "is_editable":1,
            }
        # Crear un botón
        if st.button("Crear Pedido"):
            try:
                # Simula guardar los datos en una base de datos
                config.supabase.table(tabs_pedidos[sucursal_infla]).insert(values).execute()
                st.success("✅️ Pedido creado correctamente ✅️")
            except Exception as e:
                st.error(f"Error al guardar datos: {e}")
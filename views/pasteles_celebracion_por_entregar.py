
from io import BytesIO

import pandas as pd
from datetime import datetime as dt
from datetime import timedelta as td 

import streamlit as st
import streamlit_authenticator as stauth

from config.configuration import config, read_json_from_supabase

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
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username ands password')
elif authentication_status:
    col1, col2 = st.columns([4,1])
    with col1:
        st.success('Bienvenido {}'.format(name))
    with col2:
        authenticator.logout('Logout', 'main')
    
    st.title("Pasteles de Celebración por Entregar")

    sucursal = st.radio("Selecciona un sucursal", ["Fábrica","Agrícola Oriental", "Nezahualcóyotl", "Zapotitlán", "Oaxtepec", "Pantitlán"])

    tabla_pc_db = {
        "Agrícola Oriental":"db02_pedidos_celebracion_agri", 
        "Nezahualcóyotl":"db02_pedidos_celebracion_neza", 
        "Zapotitlán":"db02_pedidos_celebracion_zapo", 
        "Oaxtepec":"db02_pedidos_celebracion_oaxt", 
        "Pantitlán":"db02_pedidos_celebracion_panti",
        "Fábrica":"db02_pedidos_celebracion_fab"
        }
    tabla_img_db = {
        "Agrícola Oriental":"agri", 
        "Nezahualcóyotl":"neza", 
        "Zapotitlán":"zapo", 
        "Oaxtepec":"oaxt", 
        "Pantitlán":"panti",
        "Fábrica":"fabrica"
        }
    
    def img_url(clave, carpeta):
        data_imgs = config.supabase.storage.from_(config.BUCKET_PASTEL_CELEBRACION).list(carpeta)
        imgs_names = [item['name'] for item in data_imgs]
        archivo = next((archivo for archivo in imgs_names if archivo.startswith(clave)), None)
        return config.supabase.storage.from_(config.BUCKET_PASTEL_CELEBRACION).get_public_url(carpeta + "/" + archivo)
    
    #? ANALISIS DE DATOS
    # Obtenemos los datos de la DB
    hoy = dt.now().strftime("%Y-%m-%d")
    cols_pc = "clave,cliente,fecha_pedido,fecha_entrega,hora_entrega"
    data_pc = config.supabase.table(tabla_pc_db[sucursal]).select('*').gte("fecha_entrega", hoy).execute().data
    # Creamos el Dataframe
    df_pc = pd.DataFrame(data_pc)

    if df_pc.empty:
        st.warning("No queda ningún pastel de celebración por entregar 😖😣😞.")
    else:
        df_pc_sort = df_pc[['clave','cliente','fecha_pedido','fecha_entrega','hora_entrega']]
        df_pc_sort = df_pc_sort.sort_values(by=['fecha_entrega'])
        st.table(df_pc_sort)
        # Seleccionar una fila basándose en la clave
        clave_seleccionada = st.selectbox("Selecciona una clave", df_pc['clave'])
        # Obtener el registro de la clave seleccionada
        registro = df_pc[df_pc['clave'] == clave_seleccionada]
        # Mostrar el registro seleccionado
        col1, col2 = st.columns([1,2])
        with col1:
            # Imagen
            st.image(img_url(clave_seleccionada, tabla_img_db[sucursal]))
        with col2:
            # Fecha y hora de entrega
            fecha = registro['fecha_entrega'].iloc[0]
            hora = registro['hora_entrega'].iloc[0]
            st.text(f"Entregar: {fecha + " " + hora}")
            # Lugar de entrega
            st.text(f"Lugar: {registro['lugar_entrega'].iloc[0]}")
            # Costos
            col21, col22, col23 = st.columns([1,1,1])
            with col21:
                st.text(f"Costo: ${registro['descuento'].iloc[0]}")
            with col22:
                st.text(f"Flete: ${registro['flete'].iloc[0]}")
            with col23:
                st.text(f"Extras: ${registro['extras'].iloc[0]}")
            # Descripcion
            st.text(f"Descripción: \n{registro['descripcion'].iloc[0]}")
            # Leyenda
            st.text(f"Leyenda: {registro['leyenda'].iloc[0]}")
            

        
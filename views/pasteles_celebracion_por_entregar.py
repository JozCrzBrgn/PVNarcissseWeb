
import pandas as pd
from datetime import datetime as dt

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
        st.success('Bienvenid@ {}'.format(name))
    with col2:
        authenticator.logout('Logout', 'main')
    
    st.title("Pasteles de Celebración por Entregar")

    lista_pc_db = [
        "db02_pedidos_celebracion_agri", 
        "db02_pedidos_celebracion_neza", 
        "db02_pedidos_celebracion_zapo",
        "db02_pedidos_celebracion_oaxt", 
        "db02_pedidos_celebracion_panti",
        "db02_pedidos_celebracion_fab",
        "db02_pedidos_celebracion_coapa",
        "db02_pedidos_celebracion_oceania",
        "db02_pedidos_celebracion_tlane"
        ]
    tabla_img_db = {
        "AG":"agri", 
        "NE":"neza", 
        "ZA":"zapo", 
        "OA":"oaxt", 
        "PA":"panti",
        "FA":"fabrica",
        "CO":"coapa",
        "OC":"oceania",
        "TL":"tlane"
        }
    
    def img_url(clave, carpeta):
        data_imgs = config.supabase.storage.from_(config.BUCKET_PASTEL_CELEBRACION).list(carpeta)
        imgs_names = [item['name'] for item in data_imgs]
        archivo = next((archivo for archivo in imgs_names if archivo.startswith(clave)), None)
        return config.supabase.storage.from_(config.BUCKET_PASTEL_CELEBRACION).get_public_url(carpeta + "/" + archivo)
    
    dfs = []
    for tab in lista_pc_db:
        # Obtener los datos de la tabla
        hoy = dt.now().strftime("%Y-%m-%d")
        data = config.supabase.table(tab).select("*").gte("fecha_entrega", hoy).execute().data
        # Crear un dataframe
        df = pd.DataFrame(data)
        # Verificamos si el dataframe esta vacio
        if df.empty:
            continue
        else:
            # Quitamos los acentos de la columna sucursal
            df['sucursal'] = df['sucursal'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
            # Agregar el dataframe a la lista
            dfs.append(df)
    if not dfs:
        st.warning("No queda ningún pastel de celebración por entregar 😖😣😞.")
    else:
        # Concatenar los dataframes
        df_pc = pd.concat(dfs)
        # Convertimos la columna de caducidad a datetime
        df_pc['fecha_entrega'] = pd.to_datetime(df_pc['fecha_entrega']).dt.date
        # Nos quedamos con las columnas que necesitamos
        df_pc_sort = df_pc[['clave','cliente','fecha_pedido','fecha_entrega','hora_entrega']]
        # Ordenamos por 'fecha_entrega'
        df_pc_sort = df_pc_sort.sort_values(by=['fecha_entrega'])
        # Checamos como quiere filtrar el cliente
        rad_btn = st.radio("Selecciona uno", ["Todos los pedidos", "Filtrar por fecha"])
        if rad_btn == "Todos los pedidos":
            df_choose = df_pc_sort
            st.table(df_choose)
        else:
            fecha = st.date_input("Selecciona una fecha")
            df_choose = df_pc_sort[df_pc_sort['fecha_entrega']==fecha]
            st.table(df_choose)
        if df_choose.empty:
            st.warning(f"Sin datos para la fecha {fecha}")
        else:
            # Seleccionar una fila basándose en la clave
            clave_seleccionada = st.selectbox("Selecciona una clave", df_choose['clave'])
            # Obtener el registro de la clave seleccionada
            registro = df_pc[df_pc['clave'] == clave_seleccionada]
            # Mostrar el registro seleccionado
            col1, col2 = st.columns([1,2])
            with col1:
                # Imagen
                st.image(img_url(clave_seleccionada, tabla_img_db[clave_seleccionada[:2]]))
            with col2:
                # Fecha y hora de entrega
                fecha = str(registro['fecha_entrega'].iloc[0])
                hora = str(registro['hora_entrega'].iloc[0])
                st.text(f"Entregar: {fecha + " " + hora}")
                # Lugar de entrega
                st.text(f"Lugar: {registro['lugar_entrega'].iloc[0]}")
                # Costos
                col11, col12, col13 = st.columns([1,1,1])
                with col11:
                    st.text(f"Costo: ${registro['descuento'].iloc[0]}")
                with col12:
                    st.text(f"Flete: ${registro['flete'].iloc[0]}")
                with col13:
                    st.text(f"Extras: ${registro['extras'].iloc[0]}")

                col31, col32 = st.columns([1,1])
                with col31:
                    st.text(f"Número de Personas: {registro['personas'].iloc[0]}")
                with col32:
                    st.text(f"Relleno: {registro['relleno'].iloc[0]}")
                # 
                col21, col22, col23 = st.columns([1,1,1])
                with col21:
                    st.text(f"Base: {registro['base'].iloc[0]}")
                with col22:
                    st.text(f"Pastel: {registro['pastel'].iloc[0]}")
                with col23:
                    st.text(f"Cobertura: {registro['cobertura'].iloc[0]}")
                # Descripcion
                st.text(f"Descripción: \n{registro['descripcion'].iloc[0]}")
                # Leyenda
                st.text(f"Leyenda: {registro['leyenda'].iloc[0]}")
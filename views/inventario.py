
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
    st.error('Nombre de usuario o contraseña incorrectos')
elif authentication_status is None:
    st.warning('Por favor, ingresa tu nombre de usuario y contraseña')
elif authentication_status:
    col1, col2 = st.columns([4,1])
    with col1:
        st.success('Bienvenid@ {}'.format(name))
    with col2:
        authenticator.logout('Logout', 'main')
    
    st.title("inventarios")
    #TODO: ["Nezahualcóyotl", "Pantitlán", "Tonanitla", "Tizayuca", "Chimalhuacán", "Chicoloapan"]

    if name=="Juan Tinajero" or name=="Sr. Silvia":
        st.text("En construcción 🏗️🚧👷🏼‍♂️...")
    else:
        sucursal = st.segmented_control(
            "Selecciona una sucursal", 
            ["Agrícola Oriental", "Zapotitlán", "Oaxtepec"], 
            default="Agrícola Oriental"
            )
        tabla_inv_db = {
            "Agrícola Oriental":"db04_inventario_agri", 
            "Nezahualcóyotl":"db04_inventario_neza", 
            "Zapotitlán":"db04_inventario_zapo", 
            "Oaxtepec":"db04_inventario_oaxt", 
            "Pantitlán":"db04_inventario_panti",
            "Tonanitla":"db04_inventario_tona",
            "Tizayuca":"db04_inventario_tiza",
            "Chimalhuacán":"db04_inventario_chim",
            "Chicoloapan":"db04_inventario_chic",
            }
        #? ANALISIS DE DATOS
        # Obtenemos los datos de la DB
        cols_inv = "clave,producto,categoria,caducidad,estatus"
        data_inv = config.supabase.table(tabla_inv_db[sucursal]).select(cols_inv).eq("estatus", "ESCANEADO").execute().data
        # Creamos el Dataframe
        df_inv = pd.DataFrame(data_inv)
        # Convertimos la columna de caducidad a datetime
        df_inv['caducidad'] = pd.to_datetime(df_inv['caducidad'])
        now = dt.now()
        # Si la columna caducidad es menor a la fecha actual, entonces se debe de cambiar el estatus a "CADUCADO"
        df_inv.loc[df_inv['caducidad'] < now, 'estatus'] = "⛔" #? CADUCADO
        # Si la columna caducidad es igual a la fecha actual, entonces se debe de cambiar el estatus a "CADUCA HOY"
        df_inv.loc[df_inv['caducidad'].dt.date == now.date(), 'estatus'] = "🔴" #? CADUCA HOY
        # Si la columna caducidad es un dia despues de la fecha actual, entonces se debe de cambiar el estatus a "CADUCA EN UN DIA"
        df_inv.loc[df_inv['caducidad'].dt.date >= (now + td(days=1)).date(), 'estatus'] = "🟠" #? CADUCA EN UN DIA
        # Si la columna caducidad es dos dias despues de la fecha actual, , entonces se debe de cambiar el estatus a "CADUCA EN DOS DIAS"
        df_inv.loc[df_inv['caducidad'].dt.date >= (now + td(days=2)).date(), 'estatus'] = "🟡" #? CADUCA EN DOS DIAS
        # Si la columna caducidad es tres dias despues de la fecha actual, entonces se debe de cambiar el estatus a "-----"
        df_inv.loc[df_inv['caducidad'].dt.date >= (now + td(days=3)).date(), 'estatus'] = "🟢" #? FALTA MUCHO PARA CADUCAR

        col1_1, col1_2  = st.columns(2)
        with col1_1:
            #? FILTROS POR CATEGORIA
            # Widget para seleccionar una categoría
            categoria_seleccionada = st.multiselect('Filtrar por categoría:', df_inv['categoria'].unique())
            if categoria_seleccionada:
                df_filtrado = df_inv[df_inv['categoria'].isin(categoria_seleccionada)]
            else:
                df_filtrado = df_inv  # Mostrar todo si no hay selección
        with col1_2:
            #? FILTROS POR PRODUCTOS
            if categoria_seleccionada:
                # Solo mostrar productos que estén dentro de las categorías seleccionadas
                productos_disponibles = df_filtrado['producto'].unique()
            else:
                # Si no hay filtro de categoría, mostrar todos los productos
                productos_disponibles = df_inv['producto'].unique()

            producto_seleccionado = st.multiselect('Filtrar por producto:', productos_disponibles)
            if producto_seleccionado:
                df_filtrado = df_filtrado[df_filtrado['producto'].isin(producto_seleccionado)]


        #? BOTON DE DESCARGA
        # Función para convertir el DataFrame a un archivo Excel en memoria
        def to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Inventario')
                writer._save()
            output.seek(0)
            return output
        # Botón de descarga de archivo Excel
        excel_data = to_excel(df_filtrado)
        st.download_button(
            label="Descargar en formato Excel",
            data=excel_data,
            file_name='Inventario.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        #? CANTIDAD DE ESTADOS
        optimo = df_filtrado[df_filtrado['estatus']=='🟢'].shape[0]
        caducado = df_filtrado[df_filtrado['estatus']=='⛔'].shape[0]
        caduca_hoy = df_filtrado[df_filtrado['estatus']=='🔴'].shape[0]
        caduca_un_dia = df_filtrado[df_filtrado['estatus']=='🟠'].shape[0]
        caduca_dos_dias = df_filtrado[df_filtrado['estatus']=='🟡'].shape[0]

        #? MARCADORES DE ESTATUS
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("ÓPTIMO", f"{optimo} 🟢")
        col2.metric("CADUCADO", f"{caducado} ⛔")
        col3.metric("CADUCA HOY", f"{caduca_hoy} 🔴")
        col4.metric("CADUCA EN UN DÍA", f"{caduca_un_dia} 🟠")
        col5.metric("CADUCA EN DOS DÍAS", f"{caduca_dos_dias} 🟡")

        st.table(df_filtrado)
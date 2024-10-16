
import pandas as pd
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
    
    st.title("Filtros en Ventas")

    if name=="Juan Tinajero" or name=="Sr. Silvia":
        st.text("En construcción 🏗️🚧👷🏼‍♂️...")
    else:
        sucursal = st.radio("Selecciona un sucursal", ["Agrícola Oriental", "Nezahualcóyotl", "Zapotitlán", "Oaxtepec", "Pantitlán", "Todas"])

        tabla_inv_db = {
            "Agrícola Oriental":"db04_inventario_agri", 
            "Nezahualcóyotl":"db04_inventario_neza", 
            "Zapotitlán":"db04_inventario_zapo", 
            "Oaxtepec":"db04_inventario_oaxt", 
            "Pantitlán":"db04_inventario_panti"
            }
        tabla_tks_db = {
            "Agrícola Oriental":"db05_tickets_agri", 
            "Nezahualcóyotl":"db05_tickets_neza", 
            "Zapotitlán":"db05_tickets_zapo", 
            "Oaxtepec":"db05_tickets_oaxt", 
            "Pantitlán":"db05_tickets_panti"
            }
        tabla_abn_db = {
            "Agrícola Oriental":"db03_abonos_celebracion_agri",
            "Nezahualcóyotl":"db03_abonos_celebracion_neza",
            "Zapotitlán": "db03_abonos_celebracion_zapo",
            "Oaxtepec":"db03_abonos_celebracion_oaxt",
            "Pantitlán": "db03_abonos_celebracion_panti"
            }
            
        
        if sucursal=="Todas":
            dfs = []
            for tab in tabla_inv_db.values():
                # Obtener los datos de la tabla
                data = config.supabase.table(tab).select("*").eq("estatus", "VENDIDO").execute().data
                # Crear un dataframe
                data_inv = pd.DataFrame(data)
                # Verificamos si el dataframe esta vacio
                if data_inv.empty:
                    continue
                else:
                    # Quitamos los acentos de la columna sucursal
                    data_inv['sucursal'] = data_inv['sucursal'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
                    # Agregar el dataframe a la lista
                    dfs.append(data_inv)
            if not dfs:
                data_inv = pd.DataFrame()
            else:
                # Concatenar los dataframes
                data_inv = pd.concat(dfs)
                # Quitamos las columnas que no necesitamos
                df_inv = data_inv[['clave', 'producto', 'categoria', 'tipo_combo','fecha_estatus', 'hora_estatus', 'costo_neto_producto']]
                # Convertimos la columna de caducidad a datetime
                df_inv['fecha_estatus'] = pd.to_datetime(df_inv['fecha_estatus'])
                # Cambiamos el nombre de la columna 'tipo_combo' a 'promocion'
                df_inv.rename(columns={'tipo_combo': 'promocion'}, inplace=True)
            
            dfs = []
            for tab in tabla_abn_db.values():
                # Obtener los datos de la tabla
                data = config.supabase.table(tab).select("*").execute().data
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
                data_abonos = pd.DataFrame()
            else:
                # Concatenar los dataframes
                data_abonos = pd.concat(dfs)
                # Quitamos las columnas que no necesitamos
                data_abonos = data_abonos[['clave', 'cantidad_abonada', 'fecha_abono','hora_abono']]
                # Convertimos la columna de fecha a datetime
                data_abonos['fecha_abono'] = pd.to_datetime(data_abonos['fecha_abono'])
        else:
            #? ANALISIS DE DATOS
            # Obtenemos los datos de la DB
            data_inv = config.supabase.table(tabla_inv_db[sucursal]).select("*").eq("estatus", "VENDIDO").execute().data
            data_abonos = config.supabase.table(tabla_abn_db[sucursal]).select("*").execute().data
            # Creamos el Dataframe
            data_inv = pd.DataFrame(data_inv)
            data_abonos = pd.DataFrame(data_abonos)
            # Quitamos las columnas que no necesitamos
            df_inv = data_inv[['clave', 'producto', 'categoria', 'tipo_combo','fecha_estatus', 'hora_estatus', 'costo_neto_producto']]
            data_abonos = data_abonos[['clave', 'cantidad_abonada', 'fecha_abono','hora_abono']]
            # Convertimos la columna de fecha a datetime
            df_inv['fecha_estatus'] = pd.to_datetime(df_inv['fecha_estatus'])
            data_abonos['fecha_abono'] = pd.to_datetime(data_abonos['fecha_abono'])
            # Cambiamos el nombre de la columna 'tipo_combo' a 'promocion'
            df_inv.rename(columns={'tipo_combo': 'promocion'}, inplace=True)

        col1_1, col1_2  = st.columns(2)
        with col1_1:
            #? FILTROS POR MES
            # Extraer los meses de la columna de fechas
            df_inv['mes'] = df_inv['fecha_estatus'].dt.month
            df_inv['dia'] = df_inv['fecha_estatus'].dt.day

            data_abonos['mes'] = data_abonos['fecha_abono'].dt.month
            data_abonos['dia'] = data_abonos['fecha_abono'].dt.day

            # Definir los nombres de los meses
            meses = {
                1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
                5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
            }

            # Filtro por mes, inicializando en enero (mes 1)
            mes_seleccionado = st.selectbox('Selecciona un mes:', options=list(meses.keys()), format_func=lambda x: meses[x], index=0)

            # Filtrar el DataFrame según el mes seleccionado
            df_filtrado = df_inv[df_inv['mes'] == mes_seleccionado]
            df_filtrado_abono = data_abonos[data_abonos['mes'] == mes_seleccionado]

        with col1_2:
            #? FILTROS POR DÍAS
            # Verificar si el DataFrame filtrado está vacío
            if df_filtrado.empty:
                st.warning(f"No hay datos disponibles para {meses[mes_seleccionado]}.")
            else:
                # Obtener los días disponibles para el mes seleccionado
                dia_min = df_filtrado['dia'].min()
                dia_max = df_filtrado['dia'].max()

                # Filtro por número de día usando un slider
                dias_seleccionados = st.slider(
                    'Filtrar por días:',
                    min_value=dia_min,
                    max_value=dia_max,
                    value=(dia_min, dia_max)
                )
                # Filtrar el DataFrame según los días seleccionados
                df_filtrado = df_filtrado[(df_filtrado['dia'] >= dias_seleccionados[0]) & (df_filtrado['dia'] <= dias_seleccionados[1])]
                df_filtrado_abono = df_filtrado_abono[(df_filtrado_abono['dia'] >= dias_seleccionados[0]) & (df_filtrado_abono['dia'] <= dias_seleccionados[1])]

        if df_filtrado.empty==False:
            col1, col2, col3, col4, col5  = st.columns(5)#[2,2,1])
            with col1:
                #? FILTROS POR CATEGORIA
                # Widget para seleccionar una categoría
                categoria_seleccionada = st.multiselect('Filtrar por categoría:', df_filtrado['categoria'].unique())
                if categoria_seleccionada:
                    df_filtrado = df_filtrado[df_filtrado['categoria'].isin(categoria_seleccionada)]
                else:
                    df_filtrado = df_filtrado  # Mostrar todo si no hay selección
            with col2:
                #? FILTROS POR PRODUCTOS
                if categoria_seleccionada:
                    # Solo mostrar productos que estén dentro de las categorías seleccionadas
                    productos_disponibles = df_filtrado['producto'].unique()
                else:
                    # Si no hay filtro de categoría, mostrar todos los productos
                    productos_disponibles = df_filtrado['producto'].unique()

                producto_seleccionado = st.multiselect('Filtrar por producto:', productos_disponibles)
                if producto_seleccionado:
                    df_filtrado = df_filtrado[df_filtrado['producto'].isin(producto_seleccionado)]
            with col3:
                #? FILTROS POR PRODUCTOS
                # Widget para seleccionar una promocion
                promocion_seleccionada = st.multiselect('Filtrar por promoción:', df_filtrado['promocion'].unique())
                if promocion_seleccionada:
                    df_filtrado = df_filtrado[df_filtrado['promocion'].isin(promocion_seleccionada)]
                else:
                    df_filtrado = df_filtrado  # Mostrar todo si no hay selección
            with col4:
                ventas = round(df_filtrado['costo_neto_producto'].sum(), 2)
                st.metric("LÍNEA", f"$ {ventas} MXN")
            with col5:
                cant = round(df_filtrado['costo_neto_producto'].count(), 2)
                st.metric("CANTIDAD", f"{cant}")

            # Mostrar tabla filtrada
            st.table(df_filtrado[['clave', 'producto', 'categoria', 'promocion', 'fecha_estatus', 'hora_estatus', 'costo_neto_producto']])
            if df_filtrado_abono.empty:
                st.warning(f"No hay abonos disponibles para {meses[mes_seleccionado]}.")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    abonos = round(df_filtrado_abono['cantidad_abonada'].sum(), 2)
                    st.metric("ABONOS", f"$ {abonos} MXN")
                with col2:
                    total = ventas + abonos
                    st.metric("VENTA TOTAL", f"$ {total} MXN")
                st.table(df_filtrado_abono[["clave", "cantidad_abonada", "fecha_abono", "hora_abono"]])

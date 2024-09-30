
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
        sucursal = st.radio("Selecciona un sucursal", ["Agrícola Oriental", "Nezahualcóyotl", "Zapotitlán", "Oaxtepec", "Pantitlán"])

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
        #? ANALISIS DE DATOS
        # Obtenemos los datos de la DB
        data_inv = config.supabase.table(tabla_inv_db[sucursal]).select("*").eq("estatus", "VENDIDO").execute().data
        # Creamos el Dataframe
        data_inv = pd.DataFrame(data_inv)
        # Quitamos las columnas que no necesitamos
        df_inv = data_inv[['clave', 'producto', 'categoria', 'tipo_combo','fecha_estatus', 'hora_estatus', 'costo_neto_producto']]
        # Convertimos la columna de caducidad a datetime
        df_inv['fecha_estatus'] = pd.to_datetime(df_inv['fecha_estatus'])
        # Cambiamos el nombre de la columna 'tipo_combo' a 'promocion'
        df_inv.rename(columns={'tipo_combo': 'promocion'}, inplace=True)

        col1_1, col1_2  = st.columns(2)
        with col1_1:
            #? FILTROS POR MES
            # Extraer los meses de la columna de fechas
            df_inv['mes'] = df_inv['fecha_estatus'].dt.month
            df_inv['dia'] = df_inv['fecha_estatus'].dt.day

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

        if df_filtrado.empty==False:
            col1_1, col1_2, col2_2, col1_3  = st.columns([1,1,1,2])#[2,2,1])
            with col1_1:
                #? FILTROS POR CATEGORIA
                # Widget para seleccionar una categoría
                categoria_seleccionada = st.multiselect('Filtrar por categoría:', df_filtrado['categoria'].unique())
                if categoria_seleccionada:
                    df_filtrado = df_filtrado[df_filtrado['categoria'].isin(categoria_seleccionada)]
                else:
                    df_filtrado = df_filtrado  # Mostrar todo si no hay selección
            with col1_2:
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
            with col2_2:
                #? FILTROS POR PRODUCTOS
                # Widget para seleccionar una promocion
                promocion_seleccionada = st.multiselect('Filtrar por promoción:', df_filtrado['promocion'].unique())
                if promocion_seleccionada:
                    df_filtrado = df_filtrado[df_filtrado['promocion'].isin(promocion_seleccionada)]
                else:
                    df_filtrado = df_filtrado  # Mostrar todo si no hay selección
            with col1_3:
                ventas = round(df_filtrado['costo_neto_producto'].sum(), 2)
                st.metric("VENDIDO", f"$ {ventas} MXN")

            # Mostrar tabla filtrada
            st.table(df_filtrado[['clave', 'producto', 'categoria', 'promocion', 'fecha_estatus', 'hora_estatus', 'costo_neto_producto']])


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
        st.success('Bienvenid@ {}'.format(name))
    with col2:
        authenticator.logout('Logout', 'main')
    
    st.title("Fechas de Pedido y Entrega de Abonos")

    if name=="Juan Tinajero" or name=="Sr. Silvia":
        st.text("En construcción 🏗️🚧👷🏼‍♂️...")
    else:
        ls_pc_ab = [
            ["db02_pedidos_celebracion_agri","db03_abonos_celebracion_agri"],
            ["db02_pedidos_celebracion_neza","db03_abonos_celebracion_neza"],
            ["db02_pedidos_celebracion_zapo", "db03_abonos_celebracion_zapo"],
            ["db02_pedidos_celebracion_oaxt","db03_abonos_celebracion_oaxt"],
            ["db02_pedidos_celebracion_panti", "db03_abonos_celebracion_panti"],
            ["db02_pedidos_celebracion_fab","db03_abonos_celebracion_fab"],
            ]
        ls_pc = []
        ls_ab = []
        for tabs in ls_pc_ab:
            # Obtener los datos de la tabla
            data_pc = config.supabase.table(tabs[0]).select("*").execute().data
            data_ab = config.supabase.table(tabs[1]).select("*").execute().data
            # Crear un dataframe
            df_celeb = pd.DataFrame(data_pc)
            df_abono = pd.DataFrame(data_ab)
            # Verificamos si el dataframe esta vacio
            if not df_celeb.empty:
                # Quitamos los acentos de la columna sucursal
                df_celeb['sucursal'] = df_celeb['sucursal'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
                # Agregar el dataframe a la lista
                ls_pc.append(df_celeb)
            if not df_abono.empty:
                # Quitamos los acentos de la columna sucursal
                df_abono['sucursal'] = df_abono['sucursal'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
                # Agregar el dataframe a la lista
                ls_ab.append(df_abono)
        if not ls_pc:
            st.warning("No tienes ningún pastel de celebración 😖😣😞.")
        else:
            # Concatenar los dataframes
            df_pc = pd.concat(ls_pc)
            # Convertimos la columna de caducidad a datetime
            df_pc['fecha_entrega'] = pd.to_datetime(df_pc['fecha_entrega'])
            df_pc['fecha_pedido'] = pd.to_datetime(df_pc['fecha_pedido'])
            # Obtenemos el 10% de la comisión
            df_pc['comision_empleado'] = (df_pc['descuento']*0.10).astype(int)
            # Nos quedamos con las columnas que necesitamos
            df_pc_sort = df_pc[['clave','cliente','fecha_pedido','fecha_entrega','hora_entrega','empleado','comision_empleado','descuento','flete','extras']]
        
        # Checamos como quiere filtrar el cliente
        rad_btn = st.radio("Selecciona un filtro", ["Fecha de pedido", "Fecha de entrega"])
        if rad_btn == "Fecha de pedido":
            col1_1, col1_2  = st.columns(2)
            with col1_1:
                #? FILTROS POR MES
                # Extraer los meses de la columna de fechas
                df_pc_sort['mes'] = df_pc_sort['fecha_pedido'].dt.month
                df_pc_sort['dia'] = df_pc_sort['fecha_pedido'].dt.day

                # Definir los nombres de los meses
                meses = {
                    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
                    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
                }

                # Filtro por mes, inicializando en enero (mes 1)
                mes_seleccionado = st.selectbox('Selecciona un mes:', options=list(meses.keys()), format_func=lambda x: meses[x], index=0)
                print(mes_seleccionado)
                # Filtrar el DataFrame según el mes seleccionado
                df_filtrado = df_pc_sort[df_pc_sort['mes'] == mes_seleccionado]

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
            df_filtrado = df_filtrado[['clave','cliente','fecha_pedido','fecha_entrega','hora_entrega','empleado','comision_empleado','descuento','flete','extras']]
            df_filtrado.rename(columns={'descuento': 'costo_pastel'}, inplace=True)
            st.table(df_filtrado)
        else:
            col1_1, col1_2  = st.columns(2)
            with col1_1:
                #? FILTROS POR MES
                # Extraer los meses de la columna de fechas
                df_pc_sort['mes'] = df_pc_sort['fecha_entrega'].dt.month
                df_pc_sort['dia'] = df_pc_sort['fecha_entrega'].dt.day

                # Definir los nombres de los meses
                meses = {
                    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
                    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
                }

                # Filtro por mes, inicializando en enero (mes 1)
                mes_seleccionado = st.selectbox('Selecciona un mes:', options=list(meses.keys()), format_func=lambda x: meses[x], index=0)

                # Filtrar el DataFrame según el mes seleccionado
                df_filtrado = df_pc_sort[df_pc_sort['mes'] == mes_seleccionado]

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
            df_filtrado = df_filtrado[['clave','cliente','fecha_pedido','fecha_entrega','hora_entrega','empleado','comision_empleado','descuento','flete','extras']]
            df_filtrado.rename(columns={'descuento': 'costo_pastel'}, inplace=True)
            st.table(df_filtrado)

        # Concatenar los dataframes
        df_abonos_desglosado = pd.concat(ls_ab)
        # Crear una columna con el efectivo total
        df_abonos_desglosado['efectivo2'] = df_abonos_desglosado['efectivo'] - df_abonos_desglosado['cambio']
        # Quitamos las columnas que no necesitamos
        df_abonos = df_abonos_desglosado[['clave','sucursal','fecha_abono','hora_abono','efectivo2','tarjeta','transferencia','cantidad_abonada']]
        # Renombramos las columnas
        df_abonos.columns = ['clave','sucursal','fecha','hora','efectivo','tarjeta','transferencia','total_dia']
        df_abonos['fecha'] = pd.to_datetime(df_abonos['fecha'])
        # Filtramos por clave
        abonos_tbl = df_abonos[df_abonos['fecha'].dt.month == mes_seleccionado]
        abonos_tbl = abonos_tbl[(abonos_tbl['fecha'].dt.day >= dias_seleccionados[0]) & (abonos_tbl['fecha'].dt.day <= dias_seleccionados[1])]
        # Mostramos el total
        col41, col42 = st.columns([4,1])
        with col41:
            st.text(f"")
        with col42:
            st.metric("Total abonado", f"$ {abonos_tbl['total_dia'].sum().round(0)} 💵")
        # Mostramos la tabla
        st.table(abonos_tbl)
        
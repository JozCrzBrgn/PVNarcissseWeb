import pandas as pd
import numpy as np
import streamlit as st
from config.configuration import config

# Leer del estado de sesión
name = st.session_state.get("name")
auth_status = st.session_state.get("auth_status")
username = st.session_state.get("username")
if auth_status:
    
    st.title("Filtros en Ventas")

    if name=="Juan Tinajero" or name=="Sr. Silvia":
        st.text("En construcción 🏗️🚧👷🏼‍♂️...")
    else:
        sucursal = st.segmented_control(
            "Selecciona una sucursal", 
            ["Agrícola Oriental", "Nezahualcóyotl", "Zapotitlán", "Oaxtepec", "Pantitlán", "Iztapalapa", "Tonanitla", "Todas"], 
            default="Agrícola Oriental"
            )

        tabla_inv_db = {
            "Agrícola Oriental":"db04_inventario_agri", 
            "Nezahualcóyotl":"db04_inventario_neza", 
            "Zapotitlán":"db04_inventario_zapo", 
            "Oaxtepec":"db04_inventario_oaxt", 
            "Pantitlán":"db04_inventario_panti",
            "Tonanitla":"db04_inventario_tona",
            "Iztapalapa":"db04_inventario_iztapalapa",
            }
        tabla_tks_db = {
            "Agrícola Oriental":"db05_tickets_agri", 
            "Nezahualcóyotl":"db05_tickets_neza", 
            "Zapotitlán":"db05_tickets_zapo", 
            "Oaxtepec":"db05_tickets_oaxt", 
            "Pantitlán":"db05_tickets_panti",
            "Tonanitla":"db05_tickets_tona",
            "Iztapalapa":"db05_tickets_iztapalapa",
            }
        tabla_abn_db = {
            "Agrícola Oriental":"db03_abonos_celebracion_agri",
            "Nezahualcóyotl":"db03_abonos_celebracion_neza",
            "Zapotitlán": "db03_abonos_celebracion_zapo",
            "Oaxtepec":"db03_abonos_celebracion_oaxt",
            "Pantitlán": "db03_abonos_celebracion_panti",
            "Tonanitla":"db03_abonos_celebracion_tona",
            "Iztapalapa":"db03_abonos_celebracion_iztapalapa",
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
                # Sí el tipo de combo es COMPENSACION se hará cero el costo
                data_inv['costo_neto_producto'] = np.where(data_inv['tipo_combo'] == 'COMPENSACION', 0, data_inv['costo_neto_producto'])
                # Quitamos las columnas que no necesitamos
                df_inv = data_inv[['clave', 'producto', 'categoria', 'tipo_combo','fecha_estatus', 'hora_estatus', 'costo_neto_producto']]
                # Convertimos la columna de 'fecha_estatus' a datetime
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

            if data_inv.empty:
                st.warning("No tienes ningún pastel de celebración 😖😣😞.")
            else:
                # Sí el tipo de combo es COMPENSACION se hará cero el costo
                data_inv['costo_neto_producto'] = np.where(data_inv['tipo_combo'] == 'COMPENSACION', 0, data_inv['costo_neto_producto'])
                # Quitamos las columnas que no necesitamos
                df_inv = data_inv[['clave', 'producto', 'categoria', 'tipo_combo','fecha_estatus', 'hora_estatus', 'costo_neto_producto']]
                # Convertimos la columna de fecha a datetime
                df_inv['fecha_estatus'] = pd.to_datetime(df_inv['fecha_estatus'])
                # Cambiamos el nombre de la columna 'tipo_combo' a 'promocion'
                df_inv.rename(columns={'tipo_combo': 'promocion'}, inplace=True)

            if data_abonos.empty:
                st.warning("No tienes ningún abono 😖😣😞.")
            else:
                data_abonos = data_abonos[['clave', 'cantidad_abonada', 'fecha_abono','hora_abono']]
                # Convertimos la columna de fecha a datetime
                data_abonos['fecha_abono'] = pd.to_datetime(data_abonos['fecha_abono'])
                

        col1_1, col1_2  = st.columns(2)
        # Mensajes si los DataFrames están vacíos
        if df_inv.empty:
            st.warning("No tienes ningún pastel de celebración 😖😣😞.")
        if data_abonos.empty:
            st.warning("No tienes ningún abono 😖😣😞.")

        # Continuar si al menos uno tiene datos
        if not df_inv.empty or not data_abonos.empty:
            with col1_1:
                #? FILTROS POR AÑO
                if not df_inv.empty:
                    df_inv['anio'] = df_inv['fecha_estatus'].dt.year
                if not data_abonos.empty:
                    data_abonos['anio'] = data_abonos['fecha_abono'].dt.year

                # Calcular rango de años disponibles
                anios = []
                if not df_inv.empty:
                    anios.append(df_inv['anio'].min())
                    anios.append(df_inv['anio'].max())
                if not data_abonos.empty:
                    anios.append(data_abonos['anio'].min())
                    anios.append(data_abonos['anio'].max())

                anio_min = min(anios)
                anio_max = max(anios)

                anio_seleccionado = st.slider(
                    'Filtrar por año:',
                    min_value=anio_min,
                    max_value=anio_max,
                    value=(anio_min, anio_max)
                )

                if not df_inv.empty:
                    df_inv = df_inv[(df_inv['anio'] >= anio_seleccionado[0]) & (df_inv['anio'] <= anio_seleccionado[1])]
                if not data_abonos.empty:
                    data_abonos = data_abonos[(data_abonos['anio'] >= anio_seleccionado[0]) & (data_abonos['anio'] <= anio_seleccionado[1])]

                #? FILTROS POR MES
                meses = {
                    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
                    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
                }

                if not df_inv.empty:
                    df_inv['mes'] = df_inv['fecha_estatus'].dt.month
                    df_inv['dia'] = df_inv['fecha_estatus'].dt.day
                if not data_abonos.empty:
                    data_abonos['mes'] = data_abonos['fecha_abono'].dt.month
                    data_abonos['dia'] = data_abonos['fecha_abono'].dt.day

                mes_seleccionado = st.selectbox('Selecciona un mes:', options=list(meses.keys()), format_func=lambda x: meses[x], index=0)

                df_filtrado = df_inv[df_inv['mes'] == mes_seleccionado] if not df_inv.empty else pd.DataFrame()
                df_filtrado_abono = data_abonos[data_abonos['mes'] == mes_seleccionado] if not data_abonos.empty else pd.DataFrame()

            with col1_2:
                if df_filtrado.empty and df_filtrado_abono.empty:
                    st.warning(f"No hay datos disponibles para {meses[mes_seleccionado]}.")
                else:
                    dias = []
                    if not df_filtrado.empty:
                        dias.append(df_filtrado['dia'].min())
                        dias.append(df_filtrado['dia'].max())
                    if not df_filtrado_abono.empty:
                        dias.append(df_filtrado_abono['dia'].min())
                        dias.append(df_filtrado_abono['dia'].max())

                    dia_min = min(dias)
                    dia_max = max(dias)

                    dias_seleccionados = st.slider(
                        'Filtrar por días:',
                        min_value=dia_min,
                        max_value=dia_max,
                        value=(dia_min, dia_max)
                    )

                    if not df_filtrado.empty:
                        df_filtrado = df_filtrado[(df_filtrado['dia'] >= dias_seleccionados[0]) & (df_filtrado['dia'] <= dias_seleccionados[1])]
                    if not df_filtrado_abono.empty:
                        df_filtrado_abono = df_filtrado_abono[(df_filtrado_abono['dia'] >= dias_seleccionados[0]) & (df_filtrado_abono['dia'] <= dias_seleccionados[1])]

            # Mostrar paneles solo si hay datos
            if not df_filtrado.empty:
                col1, col2, col3, col4, col5 = st.columns(5)

                with col1:
                    categoria_seleccionada = st.multiselect('Filtrar por categoría:', df_filtrado['categoria'].unique())
                    if categoria_seleccionada:
                        df_filtrado = df_filtrado[df_filtrado['categoria'].isin(categoria_seleccionada)]

                with col2:
                    productos_disponibles = df_filtrado['producto'].unique()
                    producto_seleccionado = st.multiselect('Filtrar por producto:', productos_disponibles)
                    if producto_seleccionado:
                        df_filtrado = df_filtrado[df_filtrado['producto'].isin(producto_seleccionado)]

                with col3:
                    promocion_seleccionada = st.multiselect('Filtrar por promoción:', df_filtrado['promocion'].unique())
                    if promocion_seleccionada:
                        df_filtrado = df_filtrado[df_filtrado['promocion'].isin(promocion_seleccionada)]

                with col4:
                    ventas = round(df_filtrado['costo_neto_producto'].sum(), 2)
                    st.metric("LÍNEA", f"$ {ventas} MXN")

                with col5:
                    cant = round(df_filtrado['costo_neto_producto'].count(), 2)
                    st.metric("CANTIDAD", f"{cant}")

                st.table(df_filtrado[['clave', 'producto', 'categoria', 'promocion', 'fecha_estatus', 'hora_estatus', 'costo_neto_producto']])

            if not df_filtrado_abono.empty:
                col1, col2 = st.columns(2)
                with col1:
                    abonos = round(df_filtrado_abono['cantidad_abonada'].sum(), 2)
                    st.metric("ABONOS", f"$ {abonos} MXN")
                with col2:
                    ventas = ventas if 'ventas' in locals() else 0
                    total = ventas + abonos
                    st.metric("VENTA TOTAL", f"$ {total} MXN")

                st.table(df_filtrado_abono[["clave", "cantidad_abonada", "fecha_abono", "hora_abono"]])
            elif not data_abonos.empty:
                st.warning(f"No hay abonos disponibles para {meses[mes_seleccionado]}.")

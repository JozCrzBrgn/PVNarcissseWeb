import pandas as pd
import numpy as np
import streamlit as st
from config.configuration import config

# Leer del estado de sesión
name = st.session_state.get("name")
auth_status = st.session_state.get("auth_status")
username = st.session_state.get("username")
if auth_status:
    
    st.title("Reporte de Ventas")

    if name=="Juan Tinajero" or name=="Sr. Silvia":
        st.text("En construcción 🏗️🚧👷🏼‍♂️...")
    else:
        sucursal = st.segmented_control(
            "Selecciona una sucursal", 
            ["Agrícola Oriental", "Nezahualcóyotl", "Zapotitlán", "Oaxtepec", "Pantitlán", "Iztapalapa", "Tonanitla"], 
             default="Agrícola Oriental"
            )
        fecha = st.date_input("Selecciona una fecha")

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
        #? ANALISIS DE DATOS
        # Obtenemos los datos de la DB
        cols_inv = "*"#!"clave,producto,costo_neto_producto,fecha_estatus,hora_estatus,no_ticket,tipo_combo"
        data_inv = config.supabase.table(tabla_inv_db[sucursal]).select(cols_inv).eq("fecha_estatus", fecha).eq("estatus", "VENDIDO").execute().data
        cols_tks = "no_ticket,nombre_cajero"
        data_tks = config.supabase.table(tabla_tks_db[sucursal]).select(cols_tks).eq("fecha", fecha).execute().data
        # Creamos los Dataframe
        df_inv = pd.DataFrame(data_inv)
        df_tks = pd.DataFrame(data_tks)
        # Renombrar la columna 'fecha_estatus' a 'fecha_venta' y 'hora_estatus' a 'hora_venta'
        df_inv.rename(columns={'fecha_estatus': 'fecha_venta', 'hora_estatus': 'hora_venta'}, inplace=True)
        if df_inv.empty!=False:
            st.warning(f"La sucursal de {sucursal} no tiene ventas para la fecha {fecha}.")
        else:
            # Sí el tipo de combo es COMPENSACION se hará cero el costo
            df_inv['costo_neto_producto'] = np.where(df_inv['tipo_combo'] == 'COMPENSACION', 0, df_inv['costo_neto_producto'])
            # Realizar el merge entre df_inv y df_ventas en base a la columna 'no_ticket'
            df_new = pd.merge(df_inv, df_tks, on='no_ticket')
            # Venta total
            sum_venta = df_new['costo_neto_producto'].sum()
            col1, col2 = st.columns([4,1])
            with col1:
                st.title('')
            with col2:
                st.metric("VENTA", f"$ {sum_venta}")
            # Seleccionar las columnas del nuevo DataFrame
            df_new = df_new[['clave', 'nombre_cajero', 'producto', 'fecha_venta', 'hora_venta']]
            # Asegurarse de que la columna esté en formato de tiempo
            df_new['hora_venta'] = pd.to_datetime(df_new['hora_venta'], format='%H:%M:%S').dt.time
            # Ordenamos por hora de venta
            df_sorted = df_new.sort_values(by=['hora_venta'])
            st.table(df_sorted)
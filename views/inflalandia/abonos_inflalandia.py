import pandas as pd
from datetime import datetime as dt
from time import gmtime, strftime
import streamlit as st
from config.configuration import config


tabs_pedidos = {
    "Coapa":"db02_pedidos_celebracion_coapa",
    "Oceania":"db02_pedidos_celebracion_oceania",
    "Tlanepantla":"db02_pedidos_celebracion_tlane",
}
tabs_abonos = {
    "Coapa":"db03_abonos_celebracion_coapa",
    "Oceania":"db03_abonos_celebracion_oceania",
    "Tlanepantla":"db03_abonos_celebracion_tlane",
}
indx_pedidos = {
    "Coapa":"CO",
    "Oceania":"OC",
    "Tlanepantla":"TL",
}

# Leer del estado de sesión
name = st.session_state.get("name")
auth_status = st.session_state.get("auth_status")
username = st.session_state.get("username")
if auth_status:
    
    st.title("Abonos inflalandia 🦆🦆🦆")

    if name=="Juan Tinajero" or name=="Sr. Silvia":
        st.text("En construcción 🏗️🚧👷🏼‍♂️...")
    else:
        col1, col2, col3 = st.columns([1,2,1])
        with col1:
            sucursal_infla = st.selectbox("Selecciona una ubicación", ["Tlanepantla", "Coapa", "Oceania"])
        with col2:
            st.header("")
        with col3:          
            hoja_pedidos = config.supabase.table(tabs_pedidos[sucursal_infla]).select("*").execute().data
            lista_ids = list(set([item['clave'] for item in hoja_pedidos]))
            lista_ids.sort()
            if lista_ids == []:
                # Si no hay ID´s, no hay nada que editar
                st.warning('Esta sucursal no tiene ningún pedido que abonar!')
            else:
                # Si hay ID's, desplegamos la lista con los ID's
                ids_celeb = st.selectbox("Selecciona una clave", lista_ids)

        #* Validamos que si tenga pedidos
        if lista_ids != []:
            #* Mostramos los datos relevantes del pedido
            col1, col2, col3 = st.columns(3)
            with col1:
                fecha_abono = st.date_input("Fecha del abono", value="default_value_today", disabled=True)
            with col2:
                df_pedidos_celeb = pd.DataFrame(hoja_pedidos)
                df_pedido = df_pedidos_celeb[df_pedidos_celeb['clave']==ids_celeb]
                cto_tot_db = df_pedido['descuento'] + df_pedido['flete'] + df_pedido['extras']
                cto_tot_fl = float(cto_tot_db.values[0])
                costo_total = st.number_input("Costo total", value=cto_tot_fl, step=100.0, min_value=0.0, disabled=True)
            with col3:
                data_abonos = config.supabase.table(tabs_abonos[sucursal_infla]).select("*").execute().data
                df_abonos_celeb = pd.DataFrame(data_abonos)
                if df_abonos_celeb.empty:
                    deuda_actual = st.number_input("Deuda actual", value=0.0, step=100.0, min_value=0.0, disabled=True)
                else:
                    df_abono = df_abonos_celeb[df_abonos_celeb['clave']==ids_celeb]
                    sum_abono_fl = float(df_abono['cantidad_abonada'].sum())
                    deuda_fl = cto_tot_fl - sum_abono_fl
                    deuda_actual = st.number_input("Deuda actual", value=deuda_fl, step=100.0, min_value=0.0, disabled=True)
            #* Mosrtamos los campos a ingresar
            col1, col2, col3 = st.columns(3)
            with col1:
                efectivo = st.number_input("Efectivo", value=0.0, step=100.0, min_value=0.0)
            with col2:
                tarjeta = st.number_input("Tarjeta", value=0.0, step=100.0, min_value=0.0)
            with col3:          
                transferencia = st.number_input("Transferenia", value=0.0, step=100.0, min_value=0.0)
            #* 
            cantidad_abonada = efectivo + tarjeta + transferencia
            if st.button("Agregar Abono 💸"):
                    if cantidad_abonada <= deuda_actual:
                        values = {
                            "clave":ids_celeb,
                            "fecha_abono":dt.strftime(fecha_abono, "%Y-%m-%d"),
                            "cantidad_abonada":cantidad_abonada,
                            "empleado":"Elvia Castillo",
                            "comentarios":"",
                            "sucursal":sucursal_infla,
                            "hora_abono":strftime("%H:%M:%S",gmtime()),
                            "efectivo":efectivo,
                            "tarjeta":tarjeta,
                            "transferencia":transferencia,
                            "cambio":0.0
                        }
                        config.supabase.table(tabs_abonos[sucursal_infla]).insert(values).execute()
                        st.success("✅️ Pedido abonado correctamente ✅️")
                    else:
                        st.warning("⚠️ No puedes abonar más de lo que debes ⚠️")
            if df_abonos_celeb.empty:
                st.info("Aun no hay abonos para este pedido")
            else:
                st.table(df_abono[['clave', 'fecha_abono', 'hora_abono', 'efectivo', 'tarjeta', 'transferencia']])
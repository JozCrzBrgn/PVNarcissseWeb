import pandas as pd
from datetime import datetime as dt
from datetime import timedelta as td 
import streamlit as st
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

# Leer del estado de sesión
name = st.session_state.get("name")
auth_status = st.session_state.get("auth_status")
username = st.session_state.get("username")
if auth_status:
    
    st.title("Editar pedido inflalandia 🦆🦆🦆")

    if name=="Juan Tinajero" or name=="Sr. Silvia":
        st.text("En construcción 🏗️🚧👷🏼‍♂️...")
    else:
        col1, col2, col3 = st.columns([1,2,1])
        with col1:
            sucursal_infla = st.selectbox("Selecciona una ubicación", ["Tlanepantla", "Coapa", "Oceania"])
        with col2:
            st.header("")
        with col3:
            past_date = dt.now() - td(days=35)
            past_date_str = past_date.strftime("%Y-%m-%d")           
            hoja_pedidos = config.supabase.table(tabs_pedidos[sucursal_infla]).select("*").gte("fecha_pedido", past_date_str).execute().data
            lista_ids = list(set([item['clave'] for item in hoja_pedidos]))
            lista_ids.sort()
            if lista_ids == []:
                # Si no hay ID´s, no hay nada que editar
                st.warning(f'La sucursal {sucursal_infla} no tiene ningún pedido que editar!')
            else:
                # Si hay ID's, desplegamos la lista con los ID's
                ids_celeb = st.selectbox("Selecciona una clave", lista_ids)
        
        if lista_ids != []:
            # Creamos el Dataframe
            df = pd.DataFrame(hoja_pedidos)
            df_celeb = df[df['clave']==ids_celeb]

            edit_prop = st.radio("¿Qué quieres editar?", ["Nombre del cliente", "Leyenda", "Fecha del pedido", "Fecha de entrega", "Hora de entrega", "Relleno", "Número de personas", "Extras", "Descripción/comentarios del pastel", "Entregado"])

            if edit_prop == "Nombre del cliente":
                cliente_infla  = st.text_input("Nombre del cliente", value=df_celeb['cliente'].values[0])
                # Crear un botón
                if st.button("Editar: Nombre del cliente"):
                    config.supabase.table(tabs_pedidos[sucursal_infla]).update({"cliente": cliente_infla}).eq("clave", ids_celeb).execute()
                    st.success("✅️ Pedido editado correctamente ✅️")
            if edit_prop == "Leyenda":
                leyenda_infla = st.text_input("Leyenda", value=df_celeb['leyenda'].values[0])
                # Crear un botón
                if st.button("Editar: Leyenda"):
                    config.supabase.table(tabs_pedidos[sucursal_infla]).update({"leyenda": leyenda_infla}).eq("clave", ids_celeb).execute()
                    st.success("✅️ Pedido editado correctamente ✅️")
            if edit_prop == "Fecha del pedido":
                fecha_pedido_infla = st.date_input("Fecha del pedido", value="default_value_today")
                # Crear un botón
                if st.button("Editar: Fecha del pedido"):
                    config.supabase.table(tabs_pedidos[sucursal_infla]).update({"fecha_pedido": dt.strftime(fecha_pedido_infla, "%Y-%m-%d")}).eq("clave", ids_celeb).execute()
                    st.success("✅️ Pedido editado correctamente ✅️")
            if edit_prop == "Fecha de entrega":
                fecha_entrega_infla = st.date_input("Fecha de entrega", value="default_value_today")
                # Crear un botón
                if st.button("Editar: Fecha de entrega"):
                    config.supabase.table(tabs_pedidos[sucursal_infla]).update({"fecha_entrega": dt.strftime(fecha_entrega_infla, "%Y-%m-%d")}).eq("clave", ids_celeb).execute()
                    st.success("✅️ Pedido editado correctamente ✅️")
            if edit_prop == "Hora de entrega":
                hora_entrega_infla = st.time_input("Hora de entrega", value="now")
                # Crear un botón
                if st.button("Editar: Hora de entrega"):
                    config.supabase.table(tabs_pedidos[sucursal_infla]).update({"hora_entrega": str(hora_entrega_infla)}).eq("clave", ids_celeb).execute()
                    st.success("✅️ Pedido editado correctamente ✅️")
            if edit_prop == "Relleno":
                tipos_relleno = [
                "Pan de chocolate con nutela", "Pan de vainilla con nutela", "Pan de chocolate con crema pastelera", 
                "Pan de vainilla con crema pastelera", "Pan de vainilla con durazno y crema", 
                "Pan de vainilla con fresas y crema"
                ]
                relleno_infla = st.selectbox("Relleno", tipos_relleno)
                # Crear un botón
                if st.button("Editar: Relleno"):
                    config.supabase.table(tabs_pedidos[sucursal_infla]).update({"relleno": relleno_infla}).eq("clave", ids_celeb).execute()
                    st.success("✅️ Pedido editado correctamente ✅️")
            if edit_prop == "Número de personas":
                pasteles_costo_json = read_json_from_supabase(config.BUCKET_GENERAL, config.COSTOS_INFLALANDIA_FILE)
                num_pasteles_costo = pasteles_costo_json['pasteles']
                personas_infla = pasteles_costo_json['personas']
                numPersonas_infla = st.selectbox("Número de personas", list(num_pasteles_costo.keys()))
                costo_total = float(num_pasteles_costo[numPersonas_infla]) + float(df_celeb['extras'].values[0])
                # Crear un botón
                if st.button("Editar: Número de personas"):
                    values_to_update = {
                        "descuento":costo_total,
                        "costo_total":costo_total,
                        "personas":int(personas_infla[numPersonas_infla]),
                    }
                    config.supabase.table(tabs_pedidos[sucursal_infla]).update(values_to_update).eq("clave", ids_celeb).execute()
                    st.success("✅️ Pedido editado correctamente ✅️")
            if edit_prop == "Extras":
                #? Extras
                extras_infla = st.number_input("Extras", value=float(df_celeb['extras'].values[0]), step=100.0, min_value=0.0)
                #? Costos por personas
                num_pers = str(df_celeb['personas'].values[0])
                pasteles_costo_json = read_json_from_supabase(config.BUCKET_GENERAL, config.COSTOS_INFLALANDIA_FILE)
                personas_map_extras = pasteles_costo_json['personas_map_extras']
                #? Costo total
                costo_total = int(personas_map_extras[num_pers]) + float(extras_infla)
                # Crear un botón
                if st.button("Editar: Extras"):
                    values_to_update = {
                        "extras":extras_infla,
                        "descuento":costo_total,
                        "costo_total":costo_total
                    }
                    config.supabase.table(tabs_pedidos[sucursal_infla]).update(values_to_update).eq("clave", ids_celeb).execute()
                    st.success("✅️ Pedido editado correctamente ✅️")
            if edit_prop == "Descripción/comentarios del pastel":
                descripcion_infla = st.text_area("Descripción/comentarios del pastel", value=df_celeb['descripcion'].values[0])
                # Crear un botón
                if st.button("Editar: Descripción/comentarios del pastel"):
                    config.supabase.table(tabs_pedidos[sucursal_infla]).update({"descripcion": descripcion_infla}).eq("clave", ids_celeb).execute()
                    st.success("✅️ Pedido editado correctamente ✅️")
            if edit_prop == "Entregado":
                # Crear un botón
                if st.button("Editar: El pedido cambiará a entregado"):
                    config.supabase.table(tabs_pedidos[sucursal_infla]).update({"estatus": "VENDIDO"}).eq("clave", ids_celeb).execute()
                    st.success("✅️ Pedido editado correctamente ✅️")

        # Obtenemos la tabla con el pedido selecionado
        hoja_pedidos = config.supabase.table(tabs_pedidos[sucursal_infla]).select("*").execute().data
        df_pedidos_celeb = pd.DataFrame(hoja_pedidos)
        if df_pedidos_celeb.empty:
            st.error('No hay pedidos aun', icon="🚨")
        else:
            df_pedido = df_pedidos_celeb[df_pedidos_celeb['clave']==ids_celeb]
            st.table(df_pedido[["cliente", "leyenda", "fecha_pedido", "fecha_entrega", "hora_entrega", "relleno", "personas", "extras", "descripcion"]])
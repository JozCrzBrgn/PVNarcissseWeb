import os
import pandas as pd
import streamlit as st
from config.configuration import config
from views.inflalandia.my_pdf import CrearPDF

tabs_pedidos = {
    "Coapa":"db02_pedidos_celebracion_coapa",
    "Oceania":"db02_pedidos_celebracion_oceania",
    "Tlanepantla":"db02_pedidos_celebracion_tlane",
}
imgs_pedidos = {
    "Coapa":"./assets/coapa.png",
    "Oceania":"./assets/oceania.png",
    "Tlanepantla":"./assets/tlalpan.png",
}
dir_pedidos = {
    "Coapa":"Calz Acoxpa 610, Coapa, Equipamiento Plaza Coapa, Tlalpan, 14390 Ciudad de México, CDMX",
    "Oceania":"Av del peñón, Del Rosal 355, col. Moctezuma, 15530 Ciudad de México, CDMX",
    "Tlanepantla":"Perif. Blvd. Manuel Ávila Camacho 2610, San Andres Atenco, 54040 Tlalnepantla, Méx.",
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
    
    st.title("Descargar pedido inflalandia 🦆🦆🦆")

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

        #* Validamos que si tenga pedidos
        if lista_ids != []:
            #locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')
            def formatear_fecha(fecha):
                fecha_new = fecha.strftime("%A %d, %B").upper()
                fecha_sin_acentos = fecha_new.replace("Á","A").replace("É","E").replace("Í","I").replace("Ó","O").replace("Ú","U")
                return fecha_sin_acentos
            
            pedidos_imprimir = st.multiselect("Selecciona los pedidos a imprimir", lista_ids)

            if st.button("Generar PDF 📑"):
                data_celeb = config.supabase.table(tabs_pedidos[sucursal_infla]).select("clave,cliente,fecha_entrega,hora_entrega,personas,relleno,costo_total,leyenda").execute().data
                df_pedidos_celeb = pd.DataFrame(data_celeb)
                df_pedidos_seleccionados = df_pedidos_celeb[df_pedidos_celeb['clave'].isin(pedidos_imprimir)]
                df_pedidos_seleccionados['fecha_entrega'] = pd.to_datetime(df_pedidos_seleccionados['fecha_entrega'])
                df_pedidos_seleccionados['fecha_formateda'] = df_pedidos_seleccionados['fecha_entrega'].apply(formatear_fecha)
                df_pdf = df_pedidos_seleccionados[['clave', 'cliente', 'personas', 'fecha_formateda', 'hora_entrega', 'relleno', 'costo_total', 'leyenda']]
                file = CrearPDF(df_pdf, sucursal_infla, imgs_pedidos[sucursal_infla], dir_pedidos[sucursal_infla])
                # Proporcionar un botón para descargar el PDF
                with open(file, "rb") as f:
                    st.download_button(
                        label="Descargar PDF",
                        data=f,
                        file_name=file,
                        mime="application/pdf"
                    )
                os.remove(file)
            
        st.divider()
        st.divider()
        # Obtenemos la tabla con todos los pedidos
        df_pedidos_celeb = pd.DataFrame(hoja_pedidos)
        if df_pedidos_celeb.empty:
            st.error('No hay pedidos aun', icon="🚨")
        else:
            st.table(df_pedidos_celeb[["clave", "cliente", "leyenda", "fecha_pedido", "fecha_entrega", "hora_entrega", "relleno", "personas", "extras", "descripcion"]])

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
    
    st.title("Pasteles de Celebración y Abonos")

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
            ["db02_pedidos_celebracion_coapa","db03_abonos_celebracion_coapa"],
            ["db02_pedidos_celebracion_oceania","db03_abonos_celebracion_oceania"],
            ["db02_pedidos_celebracion_tlane","db03_abonos_celebracion_tlane"],
            ["db02_pedidos_celebracion_tona","db03_abonos_celebracion_tona"],
            ["db02_pedidos_celebracion_tiza","db03_abonos_celebracion_tiza"],
            ["db02_pedidos_celebracion_chim","db03_abonos_celebracion_chim"],
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
            "TL":"tlane",
            "TO":"tona",
            "TI":"tiza",
            "CH":"chim",
            }
        
        def img_url(clave, carpeta):
            data_imgs = config.supabase.storage.from_(config.BUCKET_PASTEL_CELEBRACION).list(carpeta)
            imgs_names = [item['name'] for item in data_imgs]
            archivo = next((archivo for archivo in imgs_names if archivo.startswith(clave)), None)
            return config.supabase.storage.from_(config.BUCKET_PASTEL_CELEBRACION).get_public_url(carpeta + "/" + archivo)
        
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
            df_pc['fecha_entrega'] = pd.to_datetime(df_pc['fecha_entrega']).dt.date
            # Obtenemos el 10% de la comisión
            df_pc['comision_empleado'] = (df_pc['descuento']*0.10).astype(int)
            # Nos quedamos con las columnas que necesitamos
            df_pc_sort = df_pc[['clave','cliente','fecha_pedido','fecha_entrega','hora_entrega','empleado','comision_empleado']]
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
                    try:
                        st.image(img_url(clave_seleccionada, tabla_img_db[clave_seleccionada[:2]]))
                    except:
                        st.info('Esta imagen es muy antigua y se retiró de la base de datos', icon="ℹ️")
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
                if not ls_ab:
                    st.warning(f"No tienes ningún abono 💸💲💰 para la clave {clave_seleccionada}.")
                else:
                    # Concatenar los dataframes
                    df_abonos_desglosado = pd.concat(ls_ab)
                    # Crear una columna con el efectivo total
                    df_abonos_desglosado['efectivo2'] = df_abonos_desglosado['efectivo'] - df_abonos_desglosado['cambio']
                    # Quitamos las columnas que no necesitamos
                    df_abonos = df_abonos_desglosado[['clave','sucursal','fecha_abono','hora_abono','efectivo2','tarjeta','transferencia','cantidad_abonada']]
                    # Renombramos las columnas
                    df_abonos.columns = ['clave','sucursal','fecha','hora','efectivo','tarjeta','transferencia','total_dia']
                    # Filtramos por clave
                    abonos_tbl = df_abonos[df_abonos['clave']==clave_seleccionada]
                    # Mostramos el total
                    col41, col42 = st.columns([4,1])
                    with col41:
                        st.text(f"")
                    with col42:
                        st.metric("Total abonado", f"$ {abonos_tbl['total_dia'].sum().round(0)} 💵")
                    # Mostramos la tabla
                    st.table(abonos_tbl)
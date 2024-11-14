
from io import BytesIO
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
    
    st.title("Compras en Sucursales")

    if name=="Juan Tinajero" or name=="Sr. Silvia":
        st.text("En construcción 🏗️🚧👷🏼‍♂️...")
    else:
        sucursal = st.segmented_control("Selecciona un sucursal", ["Agrícola Oriental", "Nezahualcóyotl", "Zapotitlán", "Oaxtepec", "Pantitlán", "Tonanitla", "Tizayuca", "Chimalhuacán"])
        
        
        tabla_inv_db = {
            "Agrícola Oriental":"db04_inventario_agri", 
            "Nezahualcóyotl":"db04_inventario_neza", 
            "Zapotitlán":"db04_inventario_zapo", 
            "Oaxtepec":"db04_inventario_oaxt", 
            "Pantitlán":"db04_inventario_panti",
            "Tonanitla":"db04_inventario_tona",
            "Tizayuca":"db04_inventario_tiza",
            "Chimalhuacán":"db04_inventario_chim",
            }

        if sucursal!=None:
            # Filtro de Fechas
            col1, col2 = st.columns(2)
            with col1:
                fecha_ini = st.date_input("Fecha inicial del filtro")
            with col2:
                fecha_fin = st.date_input("Fecha final del filtro")

            # Obtener los datos de la tabla
            data = config.supabase.table(tabla_inv_db[sucursal]).select("clave, producto, categoria").gte("fecha_entrega", fecha_ini).lte("fecha_entrega", fecha_fin).execute().data
            # Crear un dataframe
            data_inv = pd.DataFrame(data)
            # Verificamos si el dataframe esta vacio
            if data_inv.empty:
                st.warning("No hay datos en el rango de fechas seleccionado")
            else:
                # Obtener los precios de los productos
                data_precios = config.supabase.table("00_ListaProductos").select("productos, categoria, precio_venta").execute().data
                df_precios_compra = pd.DataFrame(data_precios)
                df_precios_compra.columns =  ['producto', 'categoria', 'precio_compra']
                # quitamos las categorias que no necesitamos
                data_inv = data_inv[~data_inv['categoria'].isin(['VELAS','HELADO SENCILLO', 'AMERICANO','HELADO DOBLE', 
                                    'CAPUCHINOS', 'FRAPPES', 'FRAPUCHINO','PALETAS','SODAS', 'CHOCOLATES', 'MALTEADAS', 
                                    'HELADO MEDIO LITRO', 'LATTES','EXPRESSOS', 'BOLSAS', 'HELADO LITRO','MOKACHINO',
                                    'MOKA','EXTRA UBER', 'Envios Uber'])]
                if data_inv.empty:
                    st.warning("No hay datos en el rango de fechas seleccionado")
                else:
                    # Mapeamos los precios de compra
                    data_inv = pd.merge(data_inv, df_precios_compra, on=['producto', 'categoria'], how='left')
                    col1, col2 = st.columns(2)#[2,2,1])
                    with col1:
                        #? FILTROS POR CATEGORIA
                        # Widget para seleccionar una categoría
                        categoria_seleccionada = st.multiselect('Filtrar por categoría:', data_inv['categoria'].unique())
                        if categoria_seleccionada:
                            df_filtrado = data_inv[data_inv['categoria'].isin(categoria_seleccionada)]
                        else:
                            df_filtrado = data_inv  # Mostrar todo si no hay selección
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
                        else:
                            df_filtrado = df_filtrado

                    #? BOTON DE DESCARGA
                    # Función para convertir el DataFrame a un archivo Excel en memoria
                    def to_excel(df):
                        df=df[['clave', 'producto', 'categoria','precio_compra']]
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df.to_excel(writer, index=False, sheet_name='Ventas')
                            writer._save()
                        output.seek(0)
                        return output
                    # Botón de descarga de archivo Excel
                    excel_data = to_excel(df_filtrado)
                    st.download_button(
                        label="Descargar en formato Excel",
                        data=excel_data,
                        file_name='Compras.xlsx',
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )

                    # Mostramos el dataframe    
                    st.table(df_filtrado[['clave', 'producto', 'categoria','precio_compra']])

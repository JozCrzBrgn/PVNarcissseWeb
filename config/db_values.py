


from config.configuration import config
import pandas as pd
from datetime import datetime as dt
import unicodedata
import time
import httpx

def metas_sucursales():
    data = config.supabase.table(config.TAB_SECRETOS).select("*").execute().data
    data = {d['clave']: d['item2'] for d in data}
    metas_dic = {
        'Agri': float(data['meta_agri']),
        'Neza': float(data['meta_neza']),
        'Zapo': float(data['meta_zapo']),
        'Oaxte': float(data['meta_oaxt']),
        'Panti': float(data['meta_panti']),
        'Iztapa': float(data['meta_iztapalapa']),
        'Tona': float(data['meta_tona']),
    }
    return metas_dic

def ventas_sucursales():
    # Obtener los nombres de las tablas
    list_tk = ['db05_tickets_agri', 'db05_tickets_zapo', 'db05_tickets_oaxt', 'db05_tickets_panti', 'db05_tickets_iztapalapa', 'db05_tickets_tona']
    list_ab = ['db03_abonos_celebracion_agri', 'db03_abonos_celebracion_zapo', 'db03_abonos_celebracion_oaxt', 'db03_abonos_celebracion_panti', 'db03_abonos_celebracion_iztapalapa', 'db03_abonos_celebracion_tona']
    # Obtenemos las fechas del mes
    dia_hoy = dt.now().strftime("%Y-%m-%d")
    inicio_mes = dt.now().strftime("%Y-%m-01")
    #* Realizar ETL
    dfs_ab = []
    dfs_tk = []
    for num,tab_tk in enumerate(list_tk):
        tab_ab = list_ab[num]
        # Obtener los datos de la tabla
        data_ab = config.supabase.table(tab_ab).select("*").gte("fecha_abono", inicio_mes).lte("fecha_abono", dia_hoy).execute().data
        data_tk = config.supabase.table(tab_tk).select("*").gte("fecha", inicio_mes).lte("fecha", dia_hoy).execute().data
        # Crear un dataframe
        df_ab = pd.DataFrame(data_ab)
        df_tk = pd.DataFrame(data_tk)
        # Verificamos si el dataframe esta vacio
        if df_ab.empty == False:
            # Quitamos los acentos de la columna sucursal
            df_ab['sucursal'] = df_ab['sucursal'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
            # Agregar el dataframe a la lista
            dfs_ab.append(df_ab)
        # Verificamos si el dataframe esta vacio
        if df_tk.empty == False:
            # Quitamos los acentos de la columna sucursal
            df_tk['sucursal'] = df_tk['sucursal'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
            # Agregar el dataframe a la lista
            dfs_tk.append(df_tk)

    if not dfs_ab:
        df_abonos = pd.DataFrame()
    else:
        # Concatenar los dataframes
        df_abonos_desglosado = pd.concat(dfs_ab)
        # Quitamos las columnas que no necesitamos
        df_abonos = df_abonos_desglosado[['fecha_abono', 'sucursal', 'cantidad_abonada']]
        # Renombramos las columnas
        df_abonos.columns = ['Fecha', 'sucursal', 'total_abono']
        # pasamos la columna fecha a datetime
        df_abonos['Fecha'] = pd.to_datetime(df_abonos['Fecha'])
        # Sumamos los totales de las fechas iguales
        df_abonos = df_abonos.groupby(['Fecha', 'sucursal'], as_index=False)['total_abono'].sum()

    if not dfs_tk:
        df_tickets = pd.DataFrame()
    else:
        # Concatenar los dataframes
        df_tickets_desglosado = pd.concat(dfs_tk)
        # Quitamos las columnas que no necesitamos
        df_tickets = df_tickets_desglosado[['fecha', 'sucursal', 'costo_total']]
        # Renombramos las columnas
        df_tickets.columns = ['Fecha', 'sucursal', 'total_ticket']
        # pasamos la columna fecha a datetime
        df_tickets['Fecha'] = pd.to_datetime(df_tickets['Fecha'])
        # Sumamos los totales de las fechas iguales
        df_tickets = df_tickets.groupby(['Fecha', 'sucursal'], as_index=False)['total_ticket'].sum()

    # Asegurarse de que los DataFrames tengan las columnas necesarias si están vacíos
    if df_abonos.empty:
        df_abonos = pd.DataFrame(columns=['Fecha', 'sucursal', 'total_abono'])

    if df_tickets.empty:
        df_tickets = pd.DataFrame(columns=['Fecha', 'sucursal', 'total_ticket'])
    
    # unimos los dataframes con el mismo dia
    df = pd.merge(df_abonos, df_tickets, on=['Fecha', 'sucursal'], how='outer')
    # rellenamos los valores nulos con 0
    df.fillna(0, inplace=True)
    # Obtenemos el total
    df['Ventas'] = df['total_abono'] + df['total_ticket']
    # Quitamos las columnas que no necesitamos
    df = df[['Fecha', 'sucursal', 'Ventas']]
    # Separamos las sucursales
    df_agri = df[df['sucursal']=='Agricola Oriental']
    df_neza = df[df['sucursal']=='Nezahualcoyotl']
    df_zapo = df[df['sucursal']=='Zapotitlan']
    df_oaxt = df[df['sucursal']=='Oaxtepec']
    df_panti = df[df['sucursal']=='Pantitlan']
    df_iztapa = df[df['sucursal']=='Iztapalapa']
    df_tona = df[df['sucursal']=='Tonanitla']
    ventas_df_dic = {
        'Agri': df_agri,
        'Neza': df_neza,
        'Zapo': df_zapo,
        'Oaxte': df_oaxt,
        'Panti': df_panti,
        'Iztapa': df_iztapa,
        'Tona': df_tona
    }
    ventas_sum_dic = {
        'Agri': df_agri['Ventas'].sum(),
        'Neza': df_neza['Ventas'].sum(),
        'Zapo': df_zapo['Ventas'].sum(),
        'Oaxte': df_oaxt['Ventas'].sum(),
        'Panti': df_panti['Ventas'].sum(),
        'Iztapa': df_iztapa['Ventas'].sum(),
        'Tona': df_tona['Ventas'].sum()
    }
    return ventas_df_dic, ventas_sum_dic

'''
def diccionario_categorias():
    # Obtener los valores de las tablas
    data = config.supabase.table(config.TAB_PRODUCTOS).select("productos, categoria").execute().data
    # lo hacemos diccionario
    data_dic = {d['productos']: d['categoria'] for d in data}
    # Crear un nuevo diccionario para agrupar productos por categorías
    productos_por_categoria = {}
    # Agrupar productos por categorías
    for producto, categoria in data_dic.items():
        if categoria not in productos_por_categoria:
            productos_por_categoria[categoria] = []
        productos_por_categoria[categoria].append(producto)
    return productos_por_categoria


def quitar_acentos(serie):
    return serie.apply(lambda x: unicodedata.normalize('NFKD', x).encode('ascii', errors='ignore').decode('utf-8'))

def obtener_datos(tabla, columna_fecha, inicio, fin, retries=3, delay=2):
    for intento in range(retries):
        try:
            data = config.supabase.table(tabla).select("*").gte(columna_fecha, inicio).lte(columna_fecha, fin).execute().data
            return pd.DataFrame(data)
        except (httpx.ReadError, Exception) as e:
            print(f"[{tabla}] Error al obtener datos: {e}. Reintentando {intento + 1}/{retries}...")
            time.sleep(delay)
    print(f"[{tabla}] No se pudo obtener datos después de {retries} intentos.")
    return pd.DataFrame()

def procesar_dataframe(df, col_fecha, col_valor, nuevo_nombre_valor):
    if df.empty:
        return df
    df['sucursal'] = quitar_acentos(df['sucursal'])
    df = df[[col_fecha, 'sucursal', col_valor]].copy()
    df.columns = ['Fecha', 'sucursal', nuevo_nombre_valor]
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    return df.groupby(['Fecha', 'sucursal'], as_index=False)[nuevo_nombre_valor].sum()

def ventas_sucursales():
    list_tk = ['db05_tickets_agri', 'db05_tickets_neza', 'db05_tickets_zapo', 'db05_tickets_oaxt', 'db05_tickets_panti']
    list_ab = ['db03_abonos_celebracion_agri', 'db03_abonos_celebracion_neza', 'db03_abonos_celebracion_zapo', 'db03_abonos_celebracion_oaxt', 'db03_abonos_celebracion_panti']
    dia_hoy = dt.now().strftime("%Y-%m-%d")
    inicio_mes = dt.now().strftime("%Y-%m-01")

    dfs_ab, dfs_tk = [], []

    for tab_ab, tab_tk in zip(list_ab, list_tk):
        df_ab = obtener_datos(tab_ab, 'fecha_abono', inicio_mes, dia_hoy)
        df_tk = obtener_datos(tab_tk, 'fecha', inicio_mes, dia_hoy)
        if not df_ab.empty:
            dfs_ab.append(df_ab)
        if not df_tk.empty:
            dfs_tk.append(df_tk)

    df_abonos = procesar_dataframe(pd.concat(dfs_ab) if dfs_ab else pd.DataFrame(), 'fecha_abono', 'cantidad_abonada', 'total_abono')
    df_tickets = procesar_dataframe(pd.concat(dfs_tk) if dfs_tk else pd.DataFrame(), 'fecha', 'costo_total', 'total_ticket')

    # Asegurarse de que los DataFrames tengan las columnas necesarias si están vacíos
    if df_abonos.empty:
        df_abonos = pd.DataFrame(columns=['Fecha', 'sucursal', 'total_abono'])

    if df_tickets.empty:
        df_tickets = pd.DataFrame(columns=['Fecha', 'sucursal', 'total_ticket'])

    df = pd.merge(df_abonos, df_tickets, on=['Fecha', 'sucursal'], how='outer').fillna(0)
    df['Ventas'] = df['total_abono'] + df['total_ticket']
    df = df[['Fecha', 'sucursal', 'Ventas']]

    sucursales = {
        'Agri': 'Agricola Oriental',
        'Neza': 'Nezahualcoyotl',
        'Zapo': 'Zapotitlan',
        'Oaxte': 'Oaxtepec',
        'Panti': 'Pantitlan'
    }

    ventas_df_dic = {k: df[df['sucursal'] == v] for k, v in sucursales.items()}
    ventas_sum_dic = {k: v['Ventas'].sum() for k, v in ventas_df_dic.items()}

    return ventas_df_dic, ventas_sum_dic'''
from config.configuration import config
import pandas as pd
from datetime import datetime as dt

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
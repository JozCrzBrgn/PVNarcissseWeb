import streamlit as st
import streamlit_authenticator as stauth

from config.configuration import config, read_json_from_supabase
from config.custom_widgets import meta, grafico_barras, grafico_velocimetro
from config.db_values import metas_sucursales, ventas_sucursales

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
    
    st.title("Metas")

    if name=="Juan Tinajero" or name=="Sr. Silvia":
        st.text("En construcción 🏗️🚧👷🏼‍♂️...")
    else:
        #? Datos de la DB
        metas_dic = metas_sucursales()
        ventas_df_dic, ventas_sum_dic = ventas_sucursales()

        #? Renderizacion de widgets

        #* ###################
        #* AGRICOLA ORIENTAL #
        #* ###################
        st.header("Agrícola Oriental")
        # Marcador de métas
        meta(metas_dic['Agri'], int(ventas_sum_dic['Agri']-metas_dic['Agri']))
        # Ventas por día
        grafico_barras(ventas_df_dic['Agri'])
        # Meta a alcanzar
        grafico_velocimetro(ventas_sum_dic['Agri'], metas_dic['Agri'])

        #* ############
        #* ZAPOTITLAN #
        #* ############
        st.header("Zapotitlán")
        # Marcador de métas
        meta(metas_dic['Zapo'], int(ventas_sum_dic['Zapo']-metas_dic['Zapo']))
        # Ventas por día
        grafico_barras(ventas_df_dic['Zapo'])
        # Meta a alcanzar
        grafico_velocimetro(ventas_sum_dic['Zapo'], metas_dic['Zapo'])

        #* ##########
        #* OAXTEPEC #
        #* ##########
        st.header("Oaxtepec")
        # Marcador de métas
        meta(metas_dic['Oaxte'], int(ventas_sum_dic['Oaxte']-metas_dic['Oaxte']))
        # Ventas por día
        grafico_barras(ventas_df_dic['Oaxte'])
        # Meta a alcanzar
        grafico_velocimetro(ventas_sum_dic['Oaxte'], metas_dic['Oaxte'])
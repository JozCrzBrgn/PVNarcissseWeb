import streamlit as st 
from config.custom_widgets import meta, grafico_barras, grafico_velocimetro
from config.db_values import metas_sucursales, ventas_sucursales


# Leer del estado de sesión
name = st.session_state.get("name")
auth_status = st.session_state.get("auth_status")
username = st.session_state.get("username")

if auth_status:

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
        grafico_barras(ventas_df_dic['Agri'], key="ventas_agri")
        # Meta a alcanzar
        grafico_velocimetro(ventas_sum_dic['Agri'], metas_dic['Agri'], key="velocimetro_agri")

        #* ############
        #* ZAPOTITLAN #
        #* ############
        st.header("Zapotitlán")
        # Marcador de métas
        meta(metas_dic['Zapo'], int(ventas_sum_dic['Zapo']-metas_dic['Zapo']))
        # Ventas por día
        grafico_barras(ventas_df_dic['Zapo'], key="ventas_zapo")
        # Meta a alcanzar
        grafico_velocimetro(ventas_sum_dic['Zapo'], metas_dic['Zapo'], key="velocimetro_zapo")

        #* ##########
        #* OAXTEPEC #
        #* ##########
        st.header("Oaxtepec")
        # Marcador de métas
        meta(metas_dic['Oaxte'], int(ventas_sum_dic['Oaxte']-metas_dic['Oaxte']))
        # Ventas por día
        grafico_barras(ventas_df_dic['Oaxte'], key="ventas_oaxte")
        # Meta a alcanzar
        grafico_velocimetro(ventas_sum_dic['Oaxte'], metas_dic['Oaxte'], key="velocimetro_oaxte")

        #* ###########
        #* PANTITLAN #
        #* ###########
        st.header("Pantitlán")
        # Marcador de métas
        meta(metas_dic['Panti'], int(ventas_sum_dic['Panti']-metas_dic['Panti']))
        # Ventas por día
        grafico_barras(ventas_df_dic['Panti'], key="ventas_panti")
        # Meta a alcanzar
        grafico_velocimetro(ventas_sum_dic['Panti'], metas_dic['Panti'], key="velocimetro_panti")

        #* ############
        #* IZTAPALAPA #
        #* ############
        st.header("Iztapalapa")
        # Marcador de métas
        meta(metas_dic['Iztapa'], int(ventas_sum_dic['Iztapa']-metas_dic['Iztapa']))
        # Ventas por día
        grafico_barras(ventas_df_dic['Iztapa'], key="ventas_iztapa")
        # Meta a alcanzar
        grafico_velocimetro(ventas_sum_dic['Iztapa'], metas_dic['Iztapa'], key="velocimetro_iztapa")

        #* ###########
        #* TONANITLA #
        #* ###########
        #!st.header("Tonanitla")
        # Marcador de métas
        #!meta(metas_dic['Tona'], int(ventas_sum_dic['Tona']-metas_dic['Tona']))
        # Ventas por día
        #!grafico_barras(ventas_df_dic['Tona'], key="ventas_tona")
        # Meta a alcanzar
        #!grafico_velocimetro(ventas_sum_dic['Tona'], metas_dic['Tona'], key="velocimetro_tona")

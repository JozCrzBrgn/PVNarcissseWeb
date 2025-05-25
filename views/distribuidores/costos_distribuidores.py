import streamlit as st

# Leer del estado de sesión
name = st.session_state.get("name")
auth_status = st.session_state.get("auth_status")
username = st.session_state.get("username")


if auth_status:
    # Continúa con tu app
    st.write("Aquí va el resto del código...")

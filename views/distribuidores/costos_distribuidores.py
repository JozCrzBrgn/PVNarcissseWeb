import streamlit as st
from config.auth import authenticate_user

name, auth_status, username = authenticate_user()

if auth_status:
    # Continúa con tu app
    st.write("Aquí va el resto del código...")

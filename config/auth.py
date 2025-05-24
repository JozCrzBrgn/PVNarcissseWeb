# archivo: config/auth.py

import streamlit as st
import streamlit_authenticator as stauth
from config.configuration import config, read_json_from_supabase

def authenticate_user():
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
        return None, False, None
    elif authentication_status is None:
        st.warning('Please enter your username and password')
        return None, None, None
    elif authentication_status:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.success(f'Bienvenid@ {name}')
        with col2:
            authenticator.logout('Logout', 'main')
        return name, authentication_status, username

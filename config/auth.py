import streamlit as st
import streamlit_authenticator as stauth
from config.configuration import config, read_json_from_supabase


def load_authenticator():
    credenciales = read_json_from_supabase(config.BUCKET_GENERAL, config.CREDENCIALES_FILE)
    authenticator = stauth.Authenticate(
        credenciales,
        st.secrets["COOKIE_NAME"],
        st.secrets["COOKIE_KEY"],
        int(st.secrets["COOKIE_EXPIRY_DAYS"])
    )
    return authenticator

import json

import streamlit as st
from supabase import create_client

class Configuracion:
    def __init__(self):
        #? Conexión a la base de datos
        self.supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
        self.BUCKET_GENERAL = st.secrets["BUCKET_GENERAL"]
        self.CREDENCIALES_FILE = st.secrets["CREDENCIALES_FILE"]
        self.TAB_SECRETOS = st.secrets["TAB_SECRETOS"]
        self.BUCKET_PASTEL_CELEBRACION = st.secrets["BUCKET_PASTEL_CELEBRACION"]
        self.COSTOS_INFLALANDIA_FILE = st.secrets["COSTOS_INFLALANDIA_FILE"]
        self.COSTOS_INFLALANDIA_FILE_CARO = st.secrets["COSTOS_INFLALANDIA_FILE_CARO"]
        self.LISTA_PRODUCTOS = st.secrets["LISTA_PRODUCTOS"]
config = Configuracion()


def read_json_from_supabase(bucket_name, file_name):
        # Descarga el archivo desde el almacenamiento de Supabase
        response = config.supabase.storage.from_(bucket_name).download(file_name)
        # Carga el contenido del archivo JSON
        json_data = json.loads(response)
        return json_data

import streamlit as st
import streamlit_authenticator as stauth


def crear_credenciales(names=['Alice', 'Bob', 'Charlie'], usernames=['alice123', 'bob456', 'charlie789'], passwords=['pass1', 'pass2', 'pass3']):
    def guardar_sin_comentarios_espacios(contenido):
        lineas = contenido.split('\n')  # Dividir el contenido en líneas
        # Filtrar las líneas que no son comentarios ni espacios en blanco
        lineas_filtradas = [linea for linea in lineas if not linea.strip().startswith("#") and linea.strip()]
        # Unir las líneas filtradas de nuevo en un solo texto
        contenido_sin_comentarios_espacios = '\n'.join(lineas_filtradas)
        return contenido_sin_comentarios_espacios

    hashed_passwords = stauth.Hasher(passwords).generate()

    contenido = f"""{{
        "usernames": {{
            "{usernames[0]}": {{
                "failed_login_attempts": 0, 
                "logged_in": "False", 
                "name": "{names[0]}", 
                "password": "{hashed_passwords[0]}"
            }}, 
            "{usernames[1]}": {{
                "failed_login_attempts": 0, 
                "logged_in": "False", 
                "name": "{names[1]}", 
                "password": "{hashed_passwords[1]}"
            }}, 
            "{usernames[2]}": {{
                "failed_login_attempts": 0, 
                "logged_in": "False", 
                "name": "{names[2]}", 
                "password": "{hashed_passwords[2]}"
            }}
        }}
    }}"""

    contenido_sin_comentarios_espacios = guardar_sin_comentarios_espacios(contenido)
    # Ruta del archivo de salida
    ruta_archivo = 'ENV/credenciales.json'
    # Escribir el contenido en el archivo
    with open(ruta_archivo, "w", encoding="utf-8") as archivo:
        archivo.write(contenido_sin_comentarios_espacios)
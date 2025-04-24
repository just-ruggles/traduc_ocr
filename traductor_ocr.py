import streamlit as st
import os
import time
import glob
import cv2
import numpy as np
import pytesseract
from PIL import Image
from gtts import gTTS
from googletrans import Translator

st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://wallpapers.com/images/hd/black-carbon-fiber-1biekffyzs37csto.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Eliminar archivos viejos
def remove_files(n):
    mp3_files = glob.glob("temp/*mp3")
    if mp3_files:
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)

remove_files(7)

# Crear carpeta temporal si no existe
try:
    os.mkdir("temp")
except:
    pass

# --- TITULO PRINCIPAL ---
st.markdown("<h1 style='color: red;'>Reconocimiento Óptico de Caracteres</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='color: blue;'>Elige la fuente de la imagen, esta puede venir de la cámara o cargando un archivo</h3>", unsafe_allow_html=True)

# OPCIÓN DE CÁMARA
cam_ = st.checkbox("Usar Cámara")

if cam_:
    img_file_buffer = st.camera_input("Toma una Foto")
else:
    img_file_buffer = None

# --- SIDEBAR OPCIONES PARA CÁMARA ---
with st.sidebar:
    st.markdown("<h3 style='color: blue;'>Procesamiento para Cámara</h3>", unsafe_allow_html=True)
    filtro = st.radio("Filtro para imagen con cámara", ('Sí', 'No'))

# PROCESAMIENTO DE IMAGEN CARGADA
text = ""

bg_image = st.file_uploader("Cargar Imagen:", type=["png", "jpg"])
if bg_image is not None:
    uploaded_file = bg_image
    st.image(uploaded_file, caption='Imagen cargada.', use_column_width=True)
    
    with open(uploaded_file.name, 'wb') as f:
        f.write(uploaded_file.read())

    st.success(f"Imagen guardada como {uploaded_file.name}")

    img_cv = cv2.imread(f'{uploaded_file.name}')
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)
    st.write(text)

# PROCESAMIENTO DE IMAGEN DESDE LA CÁMARA
if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    if filtro == 'Sí':
        cv2_img = cv2.bitwise_not(cv2_img)

    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)
    st.write(text)

# --- SIDEBAR TRADUCCIÓN ---
with st.sidebar:
    st.markdown("<h3 style='color: blue;'>Parámetros de traducción</h3>", unsafe_allow_html=True)
    translator = Translator()

    in_lang = st.selectbox(
        "Seleccione el lenguaje de entrada",
        ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"),
    )
    input_language = {
        "Inglés": "en", "Español": "es", "Bengali": "bn",
        "Coreano": "ko", "Mandarín": "zh-cn", "Japonés": "ja"
    }[in_lang]

    out_lang = st.selectbox(
        "Seleccione el lenguaje de salida",
        ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"),
    )
    output_language = {
        "Inglés": "en", "Español": "es", "Bengali": "bn",
        "Coreano": "ko", "Mandarín": "zh-cn", "Japonés": "ja"
    }[out_lang]

    english_accent = st.selectbox(
        "Seleccione el acento",
        ("Default", "India", "Reino Unido", "Estados Unidos", "Canadá", "Australia", "Irlanda", "Sudáfrica")
    )
    tld_map = {
        "Default": "com", "India": "co.in", "Reino Unido": "co.uk",
        "Estados Unidos": "com", "Canadá": "ca", "Australia": "com.au",
        "Irlanda": "ie", "Sudáfrica": "co.za"
    }
    tld = tld_map.get(english_accent, "com")

    display_output_text = st.checkbox("Mostrar texto traducido")

# --- FUNCION PARA TEXTO A AUDIO ---
def text_to_speech(input_language, output_language, text, tld):
    translation = translator.translate(text, src=input_language, dest=output_language)
    trans_text = translation.text
    tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
    try:
        my_file_name = text[0:20].strip().replace(" ", "_")
    except:
        my_file_name = "audio"
    tts.save(f"temp/{my_file_name}.mp3")
    return my_file_name, trans_text

# --- BOTÓN PARA CONVERTIR ---
if st.button("Convertir Texto a Voz"):
    if text.strip() == "":
        st.warning("⚠️ No se encontró texto para traducir. Por favor carga o captura una imagen con texto claro.")
    else:
        result, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown("<h2 style='color: red;'>Tu audio:</h2>", unsafe_allow_html=True)
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        if display_output_text:
            st.markdown("<h3 style='color: blue;'>Texto de salida:</h3>", unsafe_allow_html=True)
            st.write(output_text)

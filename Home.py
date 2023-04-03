import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime, date
from functions import check_password



if not firebase_admin._apps:
    cred = credentials.Certificate('firestore-key.json')
    firebase_admin.initialize_app(cred)
db = firestore.client()

st.set_page_config(page_title='Le Bon Ton', layout = 'wide', page_icon = "", initial_sidebar_state = 'auto')
hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)



if check_password():
    def add_bg_from_url():
            st.markdown(
                f"""
                <style>
                .stApp {{
                    background-image: url("https://www.olioevinilenardon.it/wp-content/uploads/2022/07/AdobeStock_283777992.jpeg");
                    background-attachment: fixed;
                    background-size: cover
                }}
                </style>
                """,
                unsafe_allow_html=True
            )

    add_bg_from_url()
    

    st.markdown('# <span style="color:  #FFFFFF;">Armando per Le Bon Ton</span>', unsafe_allow_html=True)






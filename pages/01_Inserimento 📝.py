
import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime, date, timedelta
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
import pandas as pd
import time
from functions import check_password

# --- Layout comune a tutte le pagine
st.set_page_config(page_title='Le Bon Ton', layout = 'wide', page_icon = '', initial_sidebar_state = 'auto')
hide_streamlit_style = """
	            <style>
	            #MainMenu {visibility: hidden;}
	            footer {visibility: hidden;}
	            </style>
	            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

if check_password():

# --- Importazione firebase, necessario if per evitare errore streamlit ---
	if not firebase_admin._apps:
		cred = credentials.Certificate('firestore-key.json')
		firebase_admin.initialize_app(cred)
	db = firestore.client()


	


	st.markdown('# <span style="color: #983C8E;">Inserisci i vini nel magazzino</span>', unsafe_allow_html=True)

	# --- Inserimento campi del prodotto ---
	prod_nome = st.text_input('Nome')
	prod_ann = st.text_input("Annata")
	prod_quant = st.number_input('Quantità', step=1, min_value=1, value=1)
	prod_prezzo_p = st.number_input('Prezzo di vendita al privato', min_value=0.00)
	prod_prezzo_g = st.number_input('Prezzo di vendita al grossista', min_value=0.00)
	prod_prezzo_ac = st.number_input('Prezzo di acquisto', min_value=0.00)
	soglia = st.number_input('Soglia di avvertimento', min_value=0, step=1)


	# --- controllo se è presente una quantità precedente ---
	query = db.collection(u'vini').where(u'nome', u'==', prod_nome).where('annata', '==', prod_ann)
	docs = query.stream()
	old_prod_quant = 0
	for doc in docs:
		old_prod_quant = doc.to_dict()['quant']
		
		



	# --- Aggiunta prodotto al database ---
	if st.button('Aggiungi'):
		# l'id (chiave univoca) 
		prod_id = prod_nome + '-' + prod_ann

		doc_ref = db.collection("vini").document(prod_id)
		doc = doc_ref.get()
		current_date = datetime.now().strftime("%Y-%m-%d")
		if prod_nome == '':
			st.warning('⚠️ Inserisci un nome valido')
		else:
			doc_ref.set({
			'nome': prod_nome,
			'quant': old_prod_quant + prod_quant,
			'prezzo_vp' : prod_prezzo_p,
			'prezzo_vg' : prod_prezzo_g,
			'prezzo_a' : prod_prezzo_ac,
			'annata': prod_ann,
			'soglia': soglia 

		})
			# time.sleep(1) serve a bloccare l'applicazione un secondo prima di runnarla nuovamente
			# per permettere di visualizzare il messaggio di successo
			st.success(f'Aggiunte/i {prod_quant} {prod_nome} al magazzino')
			time.sleep(1)
			st.experimental_rerun()









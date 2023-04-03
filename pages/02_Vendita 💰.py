import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime, date
import time
from zoneinfo import ZoneInfo
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


	

	# --- Creazione barra di ricerca per i prodotti ---
	docs = db.collection(u'vini').stream()
	prodotti = ['']
	for doc in docs:
		if doc.to_dict()['quant'] != 0:
			# crea un array di nomi (non sono presenti duplicati)
			prodotti.append(doc.id)
	st.markdown('# <span style="color: #983C8E;">Vendi i vini</span>', unsafe_allow_html=True)
	option = st.selectbox('Seleziona il vino', prodotti)
	if option:
		option_ac = st.selectbox('Vendi a privato o grossista', ['Privato', 'Grossista'])


	# --- Selezione del prodotto ---
	# tramite l'array info, estraggo il nome e l'annata del vino 
	if option and option != '':
		info = option.split('-')
		query = db.collection(u'vini').where(u'nome', u'==', info[0]).where('annata', '==', info[1])
		docs = query.stream()
		for doc in docs:
			nome = doc.to_dict()['nome']
			annata = doc.to_dict()['annata']
			prezzo_vg = doc.to_dict()['prezzo_vg']
			prezzo_a = doc.to_dict()['prezzo_a']
			prezzo_vp = doc.to_dict()['prezzo_vp']
			quant = doc.to_dict()['quant']
			soglia = doc.to_dict()['soglia']
		
		
		if option_ac == 'Grossista':
			vendita = prezzo_vg
		else:
			vendita = prezzo_vp
		
		st.markdown(f'> Sono presenti <span style="color: #37519F;">{quant}</span>  <span style="color: #983C8E;">{option}</span>', unsafe_allow_html=True)
		st.markdown(f'> Il prezzo consigliato di vendita è {vendita} euro')
		vendita= st.number_input('Vendi a questo prezzo', min_value=0.0, value=vendita)


		# seleziono quantità da vendere
		quant_vendita = st.number_input('Quantità da vendere', step=1, min_value=0, max_value=quant)

		vendi = st.button('Vendi')


		# --- Vendita del prodotto ---
		if vendi and quant_vendita!=0 and quant_vendita<=quant:
			
			# aggiorno il prodotto con la nuova quantità attuale
			id_prodotto = nome + '-' + annata 
			db.collection(u'vini').document(id_prodotto).update({

			'quant': quant - quant_vendita,
			})
			# aggiungo vendita e ricavo alla sezione vendite del database

			db.collection(u'vendite').document().set({

			'annata': annata,
			'nome': nome,
			'quant': quant_vendita,
			'data': datetime.now(ZoneInfo("Europe/Rome")).strftime("%d/%m/%Y %H:%M:%S"),
			'ricavo' : float(quant_vendita) * float(vendita),
			'guadagno': (float(quant_vendita) * float(vendita)) - (float(quant_vendita) * float(doc.to_dict()['prezzo_a'])),
			'prezzo_vg': prezzo_vg,
			'prezzo_a' : prezzo_a,
			'prezzo_vp' : prezzo_vp,
			'reso' : '',
			'acquirente': option_ac,
			'soglia': soglia
			})
			
			# time.sleep(1) serve a bloccare l'applicazione un secondo prima di runnarla nuovamente
			# per permettere di visualizzare il messaggio di successo
			st.success(f'Hai venduto con successo {quant_vendita} {nome}')
			time.sleep(1)
			st.experimental_rerun()

		elif vendi:
			# errore se la quantià non è valida
			st.warning('Inserisci una quantità valida', icon="⚠️")
		



import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime, date, timedelta
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
import time
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
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

	if not firebase_admin._apps:
		cred = credentials.Certificate('firestore-key.json')
		firebase_admin.initialize_app(cred)
	db = firestore.client()

	

	st.markdown('# <span style="color: #983C8E;">Grafici</span>', unsafe_allow_html=True)



	option = st.selectbox(
	    'Seleziona la categoria',
	    (' ', 'Vendite', 'Ricevimenti'))


	if option == "Pagina principale":
		pass

	if option == "Vendite":
		st.header("Grafici vendite a grossisti e privati 📈")
		current_month = datetime.now().strftime("%m")
		current_year =  datetime.now().strftime("%Y")
		mesi = ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno', 'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre']
		mese_drop = st.selectbox('Seleziona mese di riferimento', mesi)
		sel_mese = mesi.index(mese_drop) + 1
		sel_anno = st.number_input('Seleziona anno di riferimento', step=1, min_value=2000, max_value=int(current_year), value=int(current_year))
		
		col1, col2 = st.columns(2)

		#---------------------------VENDITE e GUADAGNI------------------------------------
		with col1:
			doc_ref = db.collection("vendite")
			docs = doc_ref.stream()
			st.markdown('# <span style="color: #983C8E;">Grafico delle vendite</span>', unsafe_allow_html=True)
			new_data = {'prodotti': [], 'quantità': []}
			for doc in docs:
				nome = doc.to_dict()['nome']
				quant = doc.to_dict()['quant']
				data = doc.to_dict()['data']
				mese = data.split('/')[1]
				anno = data.split('/')[2][0:4]
				
				if str(int(mese)) == str(sel_mese) and str(int(anno)) == str(sel_anno):
					if not nome in new_data['prodotti']:
						new_data['prodotti'].append(nome)
						new_data['quantità'].append(quant)
					
					else:
						pos = 0
						for i in range(len(new_data['prodotti'])):
							if nome == new_data['prodotti'][i]:
								pos = i
						temp = new_data['quantità'][pos]
						new_quant = temp + quant
						new_data['quantità'][pos] = new_quant
			
			plt.rcdefaults()
			fig, ax = plt.subplots()
			ax.barh(new_data['prodotti'], new_data['quantità'], color = "#983C8E")
			ax.set_xlabel('quantità')
			ax.invert_yaxis()
			plt.grid(axis = 'x', linestyle = '--', linewidth = 0.5)
			st.pyplot(fig)


			#--------------vino più venduto----------------
			doc_refg = db.collection("vendite")
			docsg = doc_ref.stream()
			new_datagg = {'prodotti': [], 'quantità': []} #lista vini grossista
			new_datagp = {'prodotti': [], 'quantità': []} #lista vini privato
			vino_grossista = ''
			vino_privato = ''
			for doc in docsg:
				nome = doc.to_dict()['nome']
				quant = doc.to_dict()['quant']
				data = doc.to_dict()['data']
				mese = data.split('/')[1]
				anno = data.split('/')[2][0:4]
				acq = doc.to_dict()['acquirente']

				if str(int(mese)) == str(sel_mese) and str(int(anno)) == str(sel_anno) and 'Grossista' == str(acq):
					if not nome in new_datagg['prodotti']:
						new_datagg['prodotti'].append(nome)
						new_datagg['quantità'].append(quant)
					
					else:
						pos = 0
						for i in range(len(new_datagg['prodotti'])):
							if nome == new_datagg['prodotti'][i]:
								pos = i
						temp = new_datagg['quantità'][pos]
						new_quant = temp + quant
						new_datagg['quantità'][pos] = new_quant

				if str(int(mese)) == str(sel_mese) and str(int(anno)) == str(sel_anno) and 'Privato' == str(acq):
					if not nome in new_datagp['prodotti']:
						new_datagp['prodotti'].append(nome)
						new_datagp['quantità'].append(quant)
					
					else:
						pos = 0
						for i in range(len(new_datagp['prodotti'])):
							if nome == new_datagp['prodotti'][i]:
								pos = i
						temp = new_datagp['quantità'][pos]
						new_quant = temp + quant
						new_datagp['quantità'][pos] = new_quant


			st.markdown('---')
			if new_datagp['quantità'] != []:
				max_quant = max(new_datagp['quantità'])
				for t in range(len(new_datagp['quantità'])):
					gg = new_datagp['quantità'][t]
					if gg == max_quant:
						vino_privato = vino_privato + ", " + (new_datagp['prodotti'][t])
				
				vp = vino_privato[2:]
				if ',' in vp:
					st.markdown(f'- I vini più venduti a privati sono: {vp}')
				else:
					st.markdown(f'- Il vino più venduto a privati è: {vp}')
			
			if new_datagp['quantità'] == []:
				st.markdown(f'- Non sono stati venduti vini a privati')

			if new_datagg ['quantità'] != []:
				max_quant = max(new_datagg['quantità'])
				for t in range(len(new_datagg['quantità'])):
					gg = new_datagg['quantità'][t]
					if gg == max_quant:
						vino_grossista = vino_grossista + ", " + (new_datagg['prodotti'][t])
				
				vg = vino_grossista[2:]
				if ',' in vg:
					st.markdown(f'- I vini più venduti a grossisti sono: {vg}')
				else:
					st.markdown(f'- Il vino più venduto a grossisti è: {vg}')
			
			if new_datagg['quantità'] == []:
				st.markdown(f'- Non sono stati venduti vini a grossisti')		




			st.markdown('# <span style="color: #983C8E;">Grafico dei guadagni</span>', unsafe_allow_html=True)
			doc_ref2 = db.collection("vendite")
			docs2 = doc_ref.stream()
			new_data2 = {'prodotti': [], 'guadagni': []}
			
			for doc in docs2:
				nome = doc.to_dict()['nome']
				guadagno = doc.to_dict()['guadagno']
				data = doc.to_dict()['data']
				mese = data.split('/')[1]
				anno = data.split('/')[2][0:4]
				
				if str(int(mese)) == str(sel_mese) and str(int(anno)) == str(sel_anno):
					if not nome in new_data2['prodotti']:
						new_data2['prodotti'].append(nome)
						new_data2['guadagni'].append(guadagno)
						
					else:
						pos = 0
						for i in range(len(new_data2['prodotti'])):
							if nome == new_data2['prodotti'][i]:
								pos = i
						temp = new_data2['guadagni'][pos]
						new_guadagno = temp + guadagno
						new_data2['guadagni'][pos] = new_guadagno

			plt.rcdefaults()		
			fig3, ax3 = plt.subplots()
			ax3.barh(new_data2['prodotti'], new_data2['guadagni'],  color = "#983C8E")
			ax3.set_xlabel('guadagno in euro')
			ax3.invert_yaxis()
			plt.grid(axis = 'x', linestyle = '--', linewidth = 0.5)
			st.pyplot(fig3)



		#---------------------------RESI e RICAVI------------------------------------
		with col2:
			st.markdown('# <span style="color: #983C8E;">Grafico dei resi</span>', unsafe_allow_html=True)
			doc_ref4 = db.collection("vendite")
			docs4 = doc_ref.stream()
			new_data4 = {'prodotti': [], 'quantità': []}

			for doc in docs4:
				#'reso': str(new_quant) + ';' + datetime.now().strftime("%Y-%m-%d")
				nome = doc.to_dict()['nome']
				quant = doc.to_dict()['quant']
				res = doc.to_dict()['reso']
				res_quant = res.split(';', 1)[0]
				temp1 = res.split(';', 1)[-1]
				temp2 = temp1.split('-')
				anno = temp2[0]

				if anno != '' and res != '':
					mese = temp2[1]
					if str(int(mese)) == str(sel_mese) and str(int(anno)) == str(sel_anno):
						if not nome in new_data4['prodotti']:
							new_data4['prodotti'].append(nome)
							new_data4['quantità'].append(int(res_quant))
							
						else:
							pos = 0
							for i in range(len(new_data4['prodotti'])):
								if nome == new_data4['prodotti'][i]:
									pos = i
							temp = int(new_data4['quantità'][pos])
							new_quant = temp + int(res_quant)
							new_data4['quantità'][pos] = new_quant

			plt.rcdefaults()
			fig4, ax = plt.subplots()
			ax.barh(new_data4['prodotti'], new_data4['quantità'], color = "#983C8E")
			ax.set_xlabel('quantità')
			ax.invert_yaxis()
			plt.grid(axis = 'x', linestyle = '--', linewidth = 0.5)
			st.pyplot(fig4)

			#--------------------------vino più reso----------------
			doc_ref5 = db.collection("vendite")
			docs5 = doc_ref.stream()
			new_datarg = {'prodotti': [], 'quantità': []} #lista vini grossista
			new_datarp = {'prodotti': [], 'quantità': []} #lista vini privato
			vino_privato = ''
			vino_grossista = ''
			for doc in docs5:
				nome = doc.to_dict()['nome']
				quant = doc.to_dict()['quant']
				res = doc.to_dict()['reso']
				res_quant = res.split(';', 1)[0]
				temp1 = res.split(';', 1)[-1]
				temp2 = temp1.split('-')
				anno = temp2[0]
				acq = doc.to_dict()['acquirente']

				if anno != '' and res != '':
					mese = temp2[1]
					if str(int(mese)) == str(sel_mese) and str(int(anno)) == str(sel_anno) and 'Grossista' == str(acq):
						if not nome in new_datarg['prodotti']:
							new_datarg['prodotti'].append(nome)
							new_datarg['quantità'].append(int(res_quant))
							
						else:
							pos = 0
							for i in range(len(new_datarg['prodotti'])):
								if nome == new_datarg['prodotti'][i]:
									pos = i
							temp = int(new_datarg['quantità'][pos])
							new_quant = temp + int(res_quant)
							new_datarg['quantità'][pos] = new_quant

					if str(int(mese)) == str(sel_mese) and str(int(anno)) == str(sel_anno) and 'Privato' == str(acq):
						if not nome in new_datarp['prodotti']:
							new_datarp['prodotti'].append(nome)
							new_datarp['quantità'].append(int(res_quant))
							
						else:
							pos = 0
							for i in range(len(new_datarp['prodotti'])):
								if nome == new_datarp['prodotti'][i]:
									pos = i
							temp = int(new_datarp['quantità'][pos])
							new_quant = temp + int(res_quant)
							new_datarp['quantità'][pos] = new_quant


			st.markdown('---')

			if new_datarp['quantità'] != []:
				max_quant = max(new_datarp['quantità'])
				for t in range(len(new_datarp['quantità'])):
					gg = new_datarp['quantità'][t]
					if gg == max_quant:
						vino_privato = vino_privato + ", " + (new_datarp['prodotti'][t])

				vp = vino_privato[2:]
				if ',' in vp:
					st.markdown(f'- I vini più resi da privati sono: {vp}')
				else:
					st.markdown(f'- Il vino più reso da privati è: {vp}')

			if new_datarp['quantità'] == []:
				st.markdown(f'- Non sono stati resi vini da privati')

			if new_datarg['quantità'] != []:
				max_quant = max(new_datarg['quantità'])
				for t in range(len(new_datarg['quantità'])):
					gg = new_datarg['quantità'][t]
					if gg == max_quant:
						vino_grossista = vino_grossista + ", " + (new_datarg['prodotti'][t])
				
				vg = vino_grossista[2:]
				if ',' in vg:
					st.markdown(f'- I vini più resi da grossisti sono: {vg}')
				else:
					st.markdown(f'- Il vino più reso da grossisti è: {vg}')
			
			else:
				st.markdown(f'- Non sono stati resi vini da grossisti')





			st.markdown('# <span style="color: #983C8E;">Grafico dei ricavi</span>', unsafe_allow_html=True)
			doc_ref2 = db.collection("vendite")
			docs2 = doc_ref.stream()
			new_data2 = {'prodotti': [], 'ricavi': []}
			
			for doc in docs2:
				nome = doc.to_dict()['nome']
				ricavo = doc.to_dict()['ricavo']
				data = doc.to_dict()['data']
				mese = data.split('/')[1]
				anno = data.split('/')[2][0:4]
				
				if str(int(mese)) == str(sel_mese) and str(int(anno)) == str(sel_anno):
					if not nome in new_data2['prodotti']:
						new_data2['prodotti'].append(nome)
						new_data2['ricavi'].append(ricavo)
					
					else:
						pos = 0
						for i in range(len(new_data2['prodotti'])):
							if nome == new_data2['prodotti'][i]:
								pos = i
						temp = new_data2['ricavi'][pos]
						new_ricavo = temp + ricavo
						new_data2['ricavi'][pos] = new_ricavo
			
			plt.rcdefaults()
			fig2, ax2 = plt.subplots()
			ax2.barh(new_data2['prodotti'], new_data2['ricavi'], color = "#983C8E")
			ax2.set_xlabel('ricavo in euro')
			ax2.invert_yaxis()
			plt.grid(axis = 'x', linestyle = '--', linewidth = 0.5)
			st.pyplot(fig2)
			

	if option == "Ricevimenti":
		st.header("Grafici ricevimenti 📉")
		current_month = datetime.now().strftime("%m")
		current_year =  datetime.now().strftime("%Y")
		mesi = ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno', 'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre']
		mese_drop = st.selectbox('Seleziona mese di riferimento', mesi)
		sel_mese = mesi.index(mese_drop) + 1
		sel_anno = st.number_input('Seleziona anno di riferimento', step=1, min_value=2000, max_value=int(current_year), value=int(current_year))
		doc_ref = db.collection("vendite")
		docs = doc_ref.stream()
		
		col1, col2 = st.columns(2)
		#--------------USCITE------------------
		with col1:
			st.markdown('# <span style="color: #983C8E;">Grafico delle uscite</span>', unsafe_allow_html=True)
			doc_ref = db.collection("ordini")
			docs = doc_ref.stream()
			new_data = {'prodotti': [], 'quantità': []}
			for doc in docs:
				data = doc.to_dict()['data evento']
				mese = data.split('-')[1]
				anno = data.split('-')[0]
				temp = doc.to_dict()['ordinato']
				if str(int(mese)) == str(sel_mese) and str(int(anno)) == str(sel_anno):
					for i in temp:
						nome_vino = i.split('-')[0]
						if nome_vino not in new_data['prodotti']:
							new_data['prodotti'].append(nome_vino)
							new_data['quantità'].append(int(temp[i][0]))
						
						else:
							pos = 0
							for g in range(len(new_data['prodotti'])):
								if nome_vino == new_data['prodotti'][g]:
									pos = g
							temp1 = int(new_data['quantità'][pos])
							new_quant = temp1 + int(temp[i][0])
							new_data['quantità'][pos] = new_quant

			plt.rcdefaults()		
			fig, ax = plt.subplots()
			ax.barh(new_data['prodotti'], new_data['quantità'],  color = "#983C8E")
			ax.set_xlabel('quantità')
			ax.invert_yaxis()
			plt.grid(axis = 'x', linestyle = '--', linewidth = 0.5)
			st.pyplot(fig)	



		#--------------RESI--------------------
		with col2:
			st.markdown('# <span style="color: #983C8E;">Grafico dei resi</span>', unsafe_allow_html=True)
			doc_ref = db.collection("resi_ordini")
			docs = doc_ref.stream()
			new_data = {'prodotti': [], 'quantità': []}
			for doc in docs:
				reso = doc.to_dict()['reso']
				data = doc.to_dict()['data']
				mese = data.split('-')[1]
				anno = data.split('-')[0]
				if str(int(mese)) == str(sel_mese) and str(int(anno)) == str(sel_anno):
					for i in reso:
						nome_vino = i.split('-')[0]
						if nome_vino not in new_data['prodotti']:
							new_data['prodotti'].append(nome_vino)
							new_data['quantità'].append(int(reso[i]))
						
						else:
							pos = 0
							for g in range(len(new_data['prodotti'])):
								if nome_vino == new_data['prodotti'][g]:
									pos = g
							temp = int(new_data['quantità'][pos])
							new_quant = temp + int(reso[i])
							new_data['quantità'][pos] = new_quant

			plt.rcdefaults()		
			fig, ax = plt.subplots()
			ax.barh(new_data['prodotti'], new_data['quantità'],  color = "#983C8E")
			ax.set_xlabel('quantità')
			ax.invert_yaxis()
			plt.grid(axis = 'x', linestyle = '--', linewidth = 0.5)
			st.pyplot(fig)	



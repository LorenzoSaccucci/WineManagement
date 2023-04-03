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

  

  st.markdown('# <span style="color: #983C8E;">Gestione degli ordini per eventi e ricevimenti</span>', unsafe_allow_html=True)

  tab1, tab2 = st.tabs(['Registrazione ordini per ricevimenti', 'Gestione degli ordini per ricevimenti'])

  # --- Pagina per l'inserimento di ordini relativi a eventi e ricevimenti ---
  with tab1:

    docs_vini = db.collection(u'vini').stream()
    prodotti = ['']
    for doc in docs_vini:
      if doc.to_dict()['quant'] != 0:
        prodotti.append(doc.id)

    #informazioni evento
    ord_nome = st.text_input('Inserisci il nome dell\'evento')
    ord_data = st.date_input('Inserisci la data dell\' evento', value=date.today())

    #codice identificativo per ogni singolo evento
    ord_id = ord_nome + str(ord_data)

    #informazioni relative ai vini che si vogliono prendere per l'evento
    option = st.multiselect('Seleziona uno o più vini', prodotti)


    # selezione del prodotto con comparsa iterativa di widget come il number input q_vino
    dict_vino = {}
    if option and option != '':
      for vino in option:
        info = vino.split('-')
        # query = db.collection(u'vini').where(u'nome', u'==', info[0]).where('annata', '==', info[1])
        query = db.collection(u'vini').document(vino).get()
        quant = query.to_dict()['quant']

        q_ord = st.number_input('Quante bottiglie di {}'.format(' '.join(vino.split('-'))), key=str(vino), step=1, min_value=0)

        # creazione di un dizionario con le chiavi che sono i vini ordinati, i valori sono q in magazzino e q ordinata
        dict_vino[vino]=[quant, q_ord]


    ordine = st.button('Registra ordine per ricevimento')

    if ordine and option!=[]:

      control = 0                     # contatore di controllo per verificare le disponibilità in magazzino di ogni ivno
      for i in dict_vino:
        q_iniziale = dict_vino[i][0]
        q_evento = dict_vino[i][1]

        if q_evento < q_iniziale:
          control += 1

        else:
          st.warning('⚠️ La quantità di {} non è disponibile in magazzino. La scorta attuale è pari a: {}'.format(' '.join(i.split('-')),q_iniziale))

      if control == len(dict_vino):
        for i in dict_vino:
          q_iniziale = dict_vino[i][0]
          q_evento = dict_vino[i][1]
          db.collection(u'vini').document(i).update({'quant': q_iniziale - q_evento})
          dict_vino[i].remove(dict_vino[i][0])

        db.collection(u'ordini').document(ord_id).set({
          'nome ordine': ord_nome,
          'data evento': str(ord_data),
          'ordinato': dict_vino
          })
          
        st.success('Ordine registrato con successo')
        time.sleep(1)
        st.experimental_rerun()

  with tab2:
    docs_ordini = db.collection('ordini').stream()

    ordini = []
    for doc in docs_ordini:
      ordinato = doc.to_dict()['ordinato']
      lista_vini = sorted(ordinato.keys())

      vini_ord = ''   
      for i in lista_vini:
        vini_ord += str(i) + ' = ' + str(ordinato[i][0]) + ';   '


      ordini.append({'Nome ordine': doc.to_dict()['nome ordine'], 'Data evento':doc.to_dict()['data evento'], 'Vini ordinati': vini_ord}) 

    st.markdown('> Seleziona un ordine per effettuare un reso')
    if ordini != []:
      data = pd.DataFrame(ordini)
      gd = GridOptionsBuilder.from_dataframe(data)
      gd.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=6)
      gd.configure_selection(selection_mode='single', use_checkbox=True)
      gridOptions = gd.build()


      table = AgGrid(data, gridOptions=gridOptions, update_mode=GridUpdateMode.SELECTION_CHANGED, enable_enterprise_modules=False, fit_columns_on_grid_load=True)

      selected = table['selected_rows']

      col1, col2 = st.columns(2)

      

      
      docs_ordini = db.collection('ordini').stream()

      if selected != []:
        reso_id = selected[0]['Nome ordine'] + selected[0]['Data evento']

        query = db.collection(u'ordini').document(reso_id).get()
        vini_ordinato_dic = query.to_dict()['ordinato']
        vini_ordinato_list = sorted(vini_ordinato_dic.keys()) 

        vini_resi = col2.multiselect('Scegli il prodotto da rendere', vini_ordinato_list)

        if vini_resi and vini_resi !=[]:
          dict_resi = {}
          for vino in vini_resi:
            dict_resi[vino] = col2.number_input('Quantità di reso di {}'.format(' '.join(vino.split('-'))), min_value=0, step=1)

        aggiorna_reso = col2.button('Registra reso')

        docs_vini = db.collection(u'vini').stream()

        if aggiorna_reso:
          controllo_q_resi = 0    # contatore di controllo per verificare le quantità da rendere
          for vino in vini_resi:
            if vini_ordinato_dic[vino][0] < dict_resi[vino]:
              controllo_q_resi = controllo_q_resi
              col2.warning('⚠️ Quantità da rendere non disponibile per {}'.format(' '.join(vino.split('-'))))
            else:
              controllo_q_resi += 1
            
          if controllo_q_resi == len(vini_resi):
            reso_nome = selected[0]['Nome ordine']
            db.collection(u'resi_ordini').document(reso_id).set({'nome': reso_nome,'data': str(date.today()),'reso': dict_resi})

            for vino in vini_resi:
              for doc in docs_vini:
                if vino == doc.id:
                  q_iniziale = doc.to_dict()['quant']
                  db.collection(u'vini').document(vino).update({'quant': q_iniziale + dict_resi[vino]})

              col2.success('Reso registrato con successo')
              time.sleep(1)
              st.experimental_rerun()
      
      

  # --- Resi ---
    doc_ref = db.collection(u"resi_ordini")
    docs_resi = doc_ref.stream()

    resi = []
    for doc in docs_resi:
      reso = doc.to_dict()['reso']
      for i in reso:
        resi.append({"Ordine reso" : doc.to_dict()['nome'],"Data reso": doc.to_dict()['data'],  "Vino": i , "Quantità": reso[i]}) 


    if resi != []:
      data2 = pd.DataFrame(resi)
      gd2 = GridOptionsBuilder.from_dataframe(data2)
      gd2.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=6)
      gridOptions2 = gd2.build()

      table2 = AgGrid(data2, gridOptions=gridOptions2, update_mode=GridUpdateMode.SELECTION_CHANGED, enable_enterprise_modules=False, fit_columns_on_grid_load=False)
    else:
      st.write("Nessun reso registrato")
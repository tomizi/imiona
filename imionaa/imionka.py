import os
import openpyxl
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

#st.set_page_config(page_title='Analiza imion nadanym dzieciom w latach 2000-2021', page_icon = ':family:', layout='wide')

sekcja = st.sidebar.radio(
    'Wybierz sekcję:',
    ('Strona główna','Wyniki analizy statystycznej','Analiza korespondencji')
 )

im = pd.read_excel(io='imionaa/imiona.xlsx',engine='openpyxl',dtype={'Rok':str})

if sekcja == 'Strona główna':
    new_title = '<b style="color:rgb(0, 80, 170); font-size: 62px;">Analiza imion nadanym dzieciom w latach 2000-2021</p>'
    st.markdown(new_title, unsafe_allow_html=True)
    st.markdown('---')
    st.title('Strona główna')
    st.subheader('Wybór imienia dla dziecka to niełatwa decyzja. Powinna być świadomym wyborem obojga partnerów' +
		 'Niektórzy rodzice kierują się modą, inni rodzinną tradycją,'  +
	      'kolejni łatwością do zdrobnienia. Są też tacy, którzy zwracają uwagę na oryginalność lub po prostu brzmienie imienia.')

    #st.title(':baby: Analiza imion nadanym dzieciom w latach 2000-2021')
       
    imie = st.text_input('Podaj imię: ','Martyna')
    imie = imie.upper()
    st.header('Liczba dzieci o nadanym imieniu {} na przestrzeni lat 2000-2021'.format(imie))
    st.plotly_chart(px.line(im[im['Imię']==imie],x='Rok',y='Liczba',color='Płeć',markers=True,width=1100, height=600))

    st.header('Część dzieci o nadanym imieniu {} na przestrzeni lat 2000-2021'.format(imie))
    st.plotly_chart(px.line(im[im['Imię']==imie],x='Rok',y='Proporcja%',color='Płeć',markers=True,width=1100, height=600))


st.balloons()
    
        


        
  
        



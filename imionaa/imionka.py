# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 16:20:59 2022

@author: User
"""

import openpyxl
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title='Analiza imion dzieci', page_icon = ':family:', layout='wide')

st.title(':baby: Analiza imion dzieci')

imiona = st.sidebar.file_uploader(label='Wprwadź plik z imionami', type=['xlsx'])


if imiona is not None:
    try:
        im = pd.read_excel(imiona)
        imie = st.text_input('Podaj imię: ','Martyna')
        imie = imie.upper()
        st.header('Wykres liniowy liczby dzieci o imieniu {} w zależnosci od czasu'.format(imie))
        st.plotly_chart(px.line(im[im['Imię']==imie],x='Rok',y='Liczba',color='Płeć',markers=True,width=1100, height=600))
        st.balloons()
    except Exception as e:
        st.write('Czekam na dane')
        st.write(e)
        


        st.header('Wykres liniowy liczby dzieci o imieniu {} w zależnosci od czasu'.format(imie))
        st.plotly_chart(px.line(im[im['Imię']==imie],x='Rok',y='Proporcja',color='Płeć',markers=True,width=1100, height=600))
    except Exception as f:
        st.write('Czekam na dane')
        st.write(f)
        
        



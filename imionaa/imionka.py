import os
import openpyxl
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title='Analiza imion nadanym dzieciom w latach 2000-2021', page_icon = ':family:', layout='wide')

sekcja = st.sidebar.radio(
    'Wybierz sekcję:',
    ('Strona główna','Wyniki analizy statystycznej','Analiza korespondencji')
 )



im = pd.read_excel(io='imionaa/imiona.xlsx',engine='openpyxl',dtype={'Rok':str})



#PRZYDATNE FUNKCJE
#top 500	
def the_top500(group):
    	return group.sort_values(by='Liczba', ascending=False)[:500]
grouped=im.groupby(['Rok','Płeć'])
top500=grouped.apply(the_top500)
top500.reset_index(inplace=True, drop=True)

#Ile imion wystarczy, żeby objąć 50% obserwacji (posortowane od najbardziej do najmnije popularnych)
def dla_kazdego_roku(group,q=0.5):
	group=group.sort_values(by='Proporcja',ascending=False)
	return group.Proporcja.cumsum().values.searchsorted(q)+1

diversity = top500.groupby(['Rok','Płeć']).apply(dla_kazdego_roku)
diversity = diversity.unstack('Płeć')
	
#pierwsza litera imienia
#Wyciągamy pierwszą literę z kolumny imion
imiona_k=im[im.Płeć=='K']
imiona_m=im[im.Płeć=='M']
wyciagam_pierwsza_litere = lambda x: x[0]
pierwsza_litera_k = imiona_k.Imię.map(wyciagam_pierwsza_litere)
pierwsza_litera_m = imiona_m.Imię.map(wyciagam_pierwsza_litere)

tabelka_k= im.pivot_table('Liczba', index=pierwsza_litera_k, columns=['Rok'], aggfunc=sum)
tabelka_m= im.pivot_table('Liczba', index=pierwsza_litera_m, columns=['Rok'], aggfunc=sum)

litera_ulamek_k = tabelka_k/tabelka_k.sum()


litera_ulamek_m = tabelka_m/tabelka_m.sum()




if sekcja == 'Strona główna':
    new_title = '<b style="color:rgb(0, 80, 170); font-size: 62px;">Analiza imion nadanym dzieciom w latach 2000-2021</p>'
    st.markdown(new_title, unsafe_allow_html=True)
    st.markdown('---')
    st.title('Strona główna')
    st.subheader('Wybór imienia dla dziecka to niełatwa decyzja. Powinna być świadomym wyborem obojga partnerów. ' +
		 'Niektórzy rodzice kierują się modą, inni rodzinną tradycją, kolejni łatwością do zdrobnienia. ' +
		 'Są też tacy, którzy zwracają uwagę na oryginalność lub po prostu brzmienie imienia.')
       
    imie = st.text_input('Podaj imię: ','Martyna')
    imie = imie.upper()
    st.subheader('Liczba dzieci o nadanym imieniu {i} na przestrzeni lat 2000-2021'.format(i=str(imie)))
    st.plotly_chart(px.line(im[im['Imię']==imie],x='Rok',y='Liczba',color='Płeć',markers=True,width=1100, height=600))

    st.subheader('Część dzieci o nadanym imieniu {} na przestrzeni lat 2000-2021'.format(imie))
    st.plotly_chart(px.line(im[im['Imię']==imie],x='Rok',y='Proporcja%',color='Płeć',markers=True,width=1100, height=600))
	

	
if sekcja == 'Wyniki analizy statystycznej':
    new_title = '<b style="color:rgb(0, 80, 170); font-size: 62px;">Analiza imion nadanym dzieciom w latach 2000-2021</p>'
    st.markdown(new_title, unsafe_allow_html=True)
    st.markdown('---')
    st.title('Wyniki analizy statystycznej')
    
    #łączna ilość urodzeń
    total_ur=im.pivot_table('Liczba', index='Rok', columns='Płeć', aggfunc=sum)	
    total_ur=pd.DataFrame(total_ur, columns=['K','M'])
    st.subheader('Łączna liczba dzieci urodzonych w latach 2000-2021 z podziałem na płeć')
    st.line_chart(total_ur)
 
    #top 100
    def the_top100(group):
    	return group.sort_values(by='Liczba', ascending=False)[:100]
    grouped=im.groupby(['Rok','Płeć'])
    top100=grouped.apply(the_top100)
    top100.reset_index(inplace=True, drop=True)
	
    tabelka=top100.pivot_table('Proporcja',index='Rok',columns='Płeć',aggfunc=sum)
    tabelka=pd.DataFrame(tabelka, columns=['K','M'])
    st.subheader('Część urodzonych dzieci, którym nadaje się imiona należące do listy 100 najpopularniejszych imion')
    st.line_chart(tabelka)
	
	
    diversity = pd.DataFrame(diversity, columns=['K','M'])
    st.subheader('Liczba imion tworzących 50% zbioru najpopularniejeszych imion')
    st.line_chart(diversity)
	
   
    rok=st.selectbox("Wybierz rok", list(range(2000,2022)))
    st.plotly_chart(px.bar(litera_ulamek_k[str(rok)],y=str(rok)).update_xaxes(title_text='Pierwsza litera').update_yaxes(title_text='czesc'
		).update_layout(plot_bgcolor='white'))
    
    uni=pd.DataFrame({'litera':list(map(lambda x: x[0],im[im['Rok']==str(rok)].sort_values(by='Imię')['Imię'].unique()))}).groupby(['litera'])['litera'].count()
    st.plotly_chart(px.bar(uni,y='litera'))
    


st.balloons()
    
        


        
  
        



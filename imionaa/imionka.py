import os
import openpyxl
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json

st.set_page_config(page_title='Analiza imion nadanych dzieciom w latach 2000-2021', page_icon = ':family:', layout='wide')

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

#ostatnia litera imienia
wyciagam_ostatnia_litere = lambda x: x[-1]
ostatnia_litera_k = imiona_k.Imię.map(wyciagam_ostatnia_litere)
ostatnia_litera_m = imiona_m.Imię.map(wyciagam_ostatnia_litere)

tabelka_k1=im.pivot_table('Liczba', index=ostatnia_litera_k,columns=['Rok'], aggfunc=sum)
tabelka_m1=im.pivot_table('Liczba', index=ostatnia_litera_m,columns=['Rok'], aggfunc=sum)



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
    st.subheader('Liczba imion tworzących 50% zbioru najpopularniejszych imion')
    st.line_chart(diversity)
	
   
    # PIERWSZA LITERA
	#liczba dziewczynek
    rok=st.selectbox("Wybierz rok", list(range(2000,2022)))
    st.header('Pierwsza litera - imiona żeńskie')
    c1, c2 = st.columns(2)
    with c1:
    	st.subheader('Liczba dziewczynek o imieniu rozpoczynającym się na daną literę')
    	st.plotly_chart(px.bar(tabelka_k[str(rok)],y=str(rok)).update_xaxes(title_text='Pierwsza litera').update_yaxes(title_text='Liczba'
		).update_layout(plot_bgcolor='white'))
    
	#liczba imion żeńskich
    with c2:
    	uni=pd.DataFrame({'litera':list(map(lambda x: x[0],im[(im['Rok']==str(rok)) & (im['Płeć']=='K')].sort_values(by='Imię')['Imię'].unique()))}).groupby(['litera'])['litera'].count()
    	st.subheader('Liczba imion żeńskich rozpoczynających się na daną literę')
    	st.plotly_chart(px.bar(uni,y='litera').update_xaxes(title_text='Litera').update_yaxes(title_text='Liczba'
		).update_layout(plot_bgcolor='white'))
    
	#liczba chłopców
    st.header('Pierwsza litera - imiona męskie')
    c3, c4 = st.columns(2)
    with c3:
    	st.subheader('Liczba chłopców o imieniu rozpoczynającym się na daną literę')
    	st.plotly_chart(px.bar(tabelka_m[str(rok)],y=str(rok)).update_xaxes(title_text='Pierwsza litera').update_yaxes(title_text='Liczba'
		).update_layout(plot_bgcolor='white'))
    
	#liczba imion męskich
    with c4:
    	uni=pd.DataFrame({'litera':list(map(lambda x: x[0],im[(im['Rok']==str(rok)) & (im['Płeć']=='M')].sort_values(by='Imię')['Imię'].unique()))}).groupby(['litera'])['litera'].count()
    	st.subheader('Liczba imion męskich rozpoczynających się na daną literę')
    	st.plotly_chart(px.bar(uni,y='litera').update_xaxes(title_text='Litera').update_yaxes(title_text='Liczba'
		).update_layout(plot_bgcolor='white'))
	
    st.header('Ostatnia litera - imiona męskie')
    c5, c6 = st.columns(2)
    with c5:
    	st.subheader('Liczba chłopców o imieniu kończącym się na daną literę')
    	st.plotly_chart(px.bar(tabelka_m1[str(rok)],y=str(rok)).update_xaxes(title_text='Ostatnia litera').update_yaxes(title_text='Liczba'
		).update_layout(plot_bgcolor='white'))
    
	#liczba imion męskich
    with c6:
    	uni=pd.DataFrame({'litera':list(map(lambda x: x[-1],im[(im['Rok']==str(rok)) & (im['Płeć']=='M')].sort_values(by='Imię')['Imię'].unique()))}).groupby(['litera'])['litera'].count()
    	st.subheader('Liczba imion męskich kończących się na daną literę')
    	st.plotly_chart(px.bar(uni,y='litera').update_xaxes(title_text='Litera').update_yaxes(title_text='Liczba'
		).update_layout(plot_bgcolor='white'))
    
	
    #PORÓWNANIE TRENDÓW DLA DWÓCH IMION
    st.subheader('Porównanie trendów dla dwóch imion')
    imie1 = st.text_input('Podaj pierwsze imię: ','Martyna')
    imie1 = imie1.upper()
    imie2 = st.text_input('Podaj drugie imię: ','Joanna')
    imie2 = imie2.upper()

    imionka1=im[im.Imię==str(imie1)]
    imionka2=im[im.Imię==str(imie2)]
    imionka=pd.concat([imionka1,imionka2], ignore_index=True, sort=False)
    #st.dataframe(imionka)
    st.plotly_chart(px.line(imionka,x='Rok',y='Liczba',color='Imię',markers=True,width=1100, height=600))

    
    #IMIONA JEDNOCZEŚNIE MĘSKIE I ŻEŃSKIE
    chłopcy=im[im.Płeć=='M']
    dziewczynki=im[im.Płeć=='K']
    dziwne=['ADEL','ADI','ALEX','ALEXIS','AMAL','AMIT','ANDREA','ANGEL','ARIEL','BAO AN','CHEN','DANIEL','EDEN','ELI','ELIA','EZRA','FABIAN','GIA',
	    'IGOR','ILIA','IMAN','ISA','KAREN','LAUREN','LILIAN','MICHAL','MIKA','MILENA','MINH','MINH ANH','MORGAN','NICOLA','NIKITA','NIKOLA',
	    'NOA','NOAM','OMER','ORI','PARIS','RILEY','RONI','SASHA','SIMONE','SZYMON','TAL','THIEN AN','YARDEN','YUVAL']
    st.subheader('Imiona dla dzieci, które były nadawane zarówno chłopcom jak i dziewczynkom')
    st.dataframe(dziwne)
	
	#Mapka polski
    with urlopen('https://raw.githubusercontent.com/ppatrzyk/polska-geojson/master/wojewodztwa/wojewodztwa-min.geojson') as response:
        counties = json.load(response)
    dff = pd.DataFrame({"Województwo":['dolnośląskie','kujawsko-pomorskie','lubelskie','lubuskie','łódzkie','małopolskie','mazowieckie',
                                   'opolskie','podkarpackie','podlaskie','pomorskie','śląskie','świętokrzyskie','warmińsko-mazurskie',
                                   'wielkopolskie','zachodniopomorskie'],'kolor':['lightgray']*16})
    mies = st.selectbox('Wybierz województwo: ',['dolnośląskie','kujawsko-pomorskie','lubelskie','lubuskie','łódzkie','małopolskie','mazowieckie',
                                   'opolskie','podkarpackie','podlaskie','pomorskie','śląskie','świętokrzyskie','warmińsko-mazurskie',
                                   'wielkopolskie','zachodniopomorskie'])
    dff['kolor']=dff['kolor'].where(dff['Województwo']!=mies,'red')
    fig = px.choropleth(dff,
                    locations="Województwo",
                    geojson=counties,
                    featureidkey="properties.nazwa",
                    color='Województwo',
                    color_discrete_sequence=dff['kolor'],
                    range_color=(400, 1900),
                   projection="mercator")
    
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(height=650,showlegend=False,title="Mapa Polski",title_x=0.5)
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig)
    # top 10
    DF = pd.DataFrame({"Województwo":['dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie',
				      'kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie',
				      'lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie',
				      'lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie',
				      'małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie',
				      'mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie',
				      'opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie',
				      'podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie',
				      'podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie',
				      'pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie',
				      'śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie',
				      'świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie',
				      'warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie',
				      'wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie',
				      'zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie',
				     'łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie'],
		       'Imię':['ZUZANNA','HANNA','ZOFIA','MAJA','JULIA','LAURA','OLIWIA','POLA','ALICJA','LENA',
			       'ZOFIA','ZUZANNA','MAJA','JULIA','LAURA','POLA','ALICJA','LENA','OLIWIA','HANNA',
			       'ZUZANNA','JULIA','HANNA','LAURA','ALICJA','ZOFIA','OLIWIA','LENA','MAJA','POLA',
			       'HANNA','ZUZANNA','MAJA','POLA','JULIA','ZOFIA','LAURA','LENA','OLIWIA','MARIA',
			       'ZUZANNA','JULIA','ZOFIA','EMILIA','HANNA','LAURA','MAJA','ALICJA','OLIWIA','LENA',
			       'ZOFIA','ALICJA','ZUZANNA','JULIA','HANNA','LAURA','MAJA','MARIA','OLIWIA','POLA',
			       'HANNA','ZOFIA','ZUZANNA','JULIA','LENA','MAJA','LAURA','POLA','EMILIA','OLIWIA',
			       'JULIA','LAURA','HANNA','ZUZANNA','ZOFIA','MAJA','EMILIA','LENA','OLIWIA','ALEKSANDRA',
			       'ZUZANNA','HANNA','LAURA','ZOFIA','JULIA','OLIWIA','MAJA','MARIA','MARCELINA','ALICJA',
			       'ZUZANNA','ZOFIA','LAURA','HANNA','MAJA','JULIA','POLA','OLIWIA','LENA','MARIA',
			       'ZUZANNA','HANNA','JULIA','MAJA','EMILIA','ZOFIA','LAURA','ALICJA','LENA','OLIWIA',
			       'HANNA','ZUZANNA','ZOFIA','LENA','LAURA','JULIA','MAJA','MARIA','ALICJA','OLIWIA',
			       'ZUZANNA','HANNA','ZOFIA','JULIA','MAJA','LAURA','MARIA','POLA','OLIWIA','ALICJA',
			       'ZOFIA','ZUZANNA','MAJA','JULIA','LAURA','HANNA','LENA','POLA','OLIWIA','MARIA',
			       'MAJA','ZUZANNA','HANNA','JULIA','ZOFIA','POLA','LAURA','LENA','MARIA','OLIWIA',
			       'HANNA','ZUZANNA','ZOFIA','MAJA','JULIA','LAURA','OLIWIA','ALICJA','LENA','MARIA'],
		       'Liczba imion':[497,489,428,416,405,365,362,346,309,301,
				       363,326,286,285,276,273,263,258,230,227,
				       330,316,287,282,277,258,247,245,238,219,
				       167,161,141,137,132,124,120,100,100,90,
				       686,670,660,591,586,573,554,512,510,444,
				       1136,983,983,938,909,901,828,767,758,714,
				       145,134,128,128,118,115,111,109,99,86,
				       353,353,352,346,316,313,300,286,272,230,
				       226,219,201,185,180,167,159,153,152,137,
				       454,438,398,369,363,350,339,286,279,273,
				       730,706,677,618,597,585,581,559,538,531,
				       189,182,178,172,157,157,156,135,124,124,
				       268,237,229,192,191,166,160,159,152,144,
				       675,581,570,559,521,519,480,454,454,450,
				       263,258,249,248,230,228,203,180,177,161,
				       414,403,386,374,362,355,329,315,279,275]}
				       
		     )
    col2.plotly_chart(px.bar(x=DF[DF['Województwo']==mies]['Liczba imion'][::-1],y=DF[DF['Województwo']==mies]['Imię'][::-1],
			     orientation='h',text=DF[DF['Województwo']==mies]['Liczba imion'][::-1],color=["red"]*10,
			     color_discrete_map="identity",
			     title='Top 10 imon żeńskich').update_xaxes(title_text='Liczba imion').update_yaxes(title_text='Imię'
				).update_layout(plot_bgcolor='white',title_x=0.5,height=600))

  

      #chłopcy
  
    # top 10
    DF_c = pd.DataFrame({"Województwo":['dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie',
				      'kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie',
				      'lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie',
				      'lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie',
				      'małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie',
				      'mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie',
				      'opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie',
				      'podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie',
				      'podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie',
				      'pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie',
				      'śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie',
				      'świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie',
				      'warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie',
				      'wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie',
				      'zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie',
				     'łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie'],
		       'Imię':['Antoni','Jakub','Jan','Aleksander','Leon','Franciszek','Filip','Mikołaj','Ignacy','Stanisław',
			       'Antoni','Jakub','Aleksander','Franciszek','Jan','Leon','Nikodem','Mikołaj','Tymon','Szymon',
			       'Antoni','Aleksander','Jan','Jakub','Mikołaj','Franciszek','Szymon','Nikodem','Filip','Ignacy',
			       'Antoni';'Leon';'Franciszek';'Aleksander';'Jan';'Jakub';'Szymon';'Nikodem';'Filip';'Ignacy',
			       'Jan','Aleksander','Antoni','Franciszek','Jakub','Stanisław','Mikołaj','Ignacy','Szymon','Filip',
			       'Antoni','Franciszek','Jan','Jakub','Aleksander','Szymon','Mikołaj','Leon','Filip','Nikodem',
			       'Antoni','Jakub','Jan','Leon','Franciszek','Szymon','Filip','Wojciech','Aleksander','Nikodem',
			       'Antoni','Jakub','Szymon','Franciszek','Aleksander','Jan','Nikodem','Mikołaj','Filip','Tymon',
			       'Aleksander','Antoni','Jakub','Franciszek','Jan','Szymon','Mikołaj','Filip','Michał','Marcel',
			       'Antoni','Jan','Aleksander','Franciszek','Leon','Jakub','Ignacy','Mikołaj','Stanisław','Nikodem',
			       'Aleksander','Antoni','Jan','Franciszek','Nikodem','Jakub','Szymon','Stanisław','Mikołaj','Filip',
			       'Antoni','Jan','Franciszek','Leon','Aleksander','Stanisław','Wojciech','Jakub','Ignacy','Mikołaj',
			       'Antoni','Jan','Franciszek','Leon','Aleksander','Jakub','Mikołaj','Nikodem','Filip','Stanisław',
			       'Antoni','Aleksander','Jan','Franciszek','Jakub','Mikołaj','Szymon','Leon','Wojciech','Filip',
			       'Jakub','Antoni','Franciszek','Jan','Filip','Leon','Mikołaj','Aleksander','Szymon','Wojciech',
			       'Antoni','Aleksander','Jan','Franciszek','Jakub','Mikołaj','Nikodem','Marcel','Szymon','Stanisław'],
		       'Liczba imion':[539,467,450,435,435,431,391,387,332,330,
				       410,367,366,360,342,290,289,284,249,249,
				       409,394,336,336,320,299,293,260,253,233,
				       192,132,127,124,124,119,115,113,109,105,
				       1372,1312,1255,1143,986,935,852,786,774,752,
				       758,715,715,714,683,554,537,505,492,452,
				       147,132,126,123,120,109,108,105,101,98,
				       459,408,367,366,357,330,298,289,286,274,
				       262,222,215,194,189,173,168,143,142,138,
				       475,456,456,450,423,397,357,347,346,329,
				       276,247,242,221,191,186,171,167,161,158,
				       808,710,694,651,632,624,553,518,484,442,
				       347,271,261,246,245,236,201,192,189,186,
				       509,478,458,395,372,316,307,307,293,287,
				       801,763,653,650,636,594,574,572,533,502,
				       279,223,200,198,172,142,139,130,127,122]}
				       
		     )
    col2.plotly_chart(px.bar(x=DF_c[DF_c['Województwo']==mies]['Liczba imion'][::-1],y=DF_c[DF_c['Województwo']==mies]['Imię'][::-1],
			     orientation='h',text=DF_c[DF_c['Województwo']==mies]['Liczba imion'][::-1],color=["red"]*10,
			     color_discrete_map="identity",
			     title='Top 10 imon męskich').update_xaxes(title_text='Liczba imion').update_yaxes(title_text='Imię'
				).update_layout(plot_bgcolor='white',title_x=0.5,height=600))
 

    
st.balloons()
    
        


        
  
        



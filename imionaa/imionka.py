import os
import openpyxl
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json




st.set_page_config(page_title='Imiona nadawane dzieciom w Polsce - analiza', page_icon = ':family:', layout='wide')

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
    new_title = '<b style="color:rgb(0, 80, 170); font-size: 62px;">Imiona nadawane dzieciom w Polsce - analiza </p>'
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
    new_title = '<b style="color:rgb(0, 80, 170); font-size: 62px;">Imiona nadawane dzieciom w Polsce - analiza</p>'
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
    st.header('Analiza pierwszej i ostatniej litery imienia')
    rok=st.selectbox("Wybierz rok:", list(range(2000,2022)))
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
	
	
	
	
	
	
	
	
	#Mapka Polski
    st.subheader('Najczęściej nadawane dzieciom imiona w X roku w podziale na województwa')
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
    st.subheader('Imiona żeńskie')
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig)
    
	
	
     #chłopcy
    with urlopen('https://raw.githubusercontent.com/ppatrzyk/polska-geojson/master/wojewodztwa/wojewodztwa-min.geojson') as response:
        counties = json.load(response)
    dff = pd.DataFrame({"Województwo":['dolnośląskie','kujawsko-pomorskie','lubelskie','lubuskie','łódzkie','małopolskie','mazowieckie',
                                   'opolskie','podkarpackie','podlaskie','pomorskie','śląskie','świętokrzyskie','warmińsko-mazurskie',
                                   'wielkopolskie','zachodniopomorskie'],'kolor':['lightgray']*16})
    
    dff['kolor']=dff['kolor'].where(dff['Województwo']!=mies,'red')
    fig = px.choropleth(dff,
                    locations="Województwo",
                    geojson=counties,
                    featureidkey="properties.nazwa",
                    color='Województwo',
                    color_discrete_sequence=dff['kolor'],
                    range_color=(400, 1900),
                   projection="mercator")
    st.subheader('Imiona męskie')
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(height=650,showlegend=False,title="Mapa Polski",title_x=0.5)
    st.subheader('Imiona męskie')
    col1.plotly_chart(fig)
    #col1.plotly_chart(fig)
    # top 10
    DF = pd.DataFrame({"Województwo":['dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie',
				      'kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie',
				      'lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie',
				      'lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie',
				      'mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie',
				      'małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie',
				      'opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie',
				      'podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie',
				      'podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie',
				      'pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie',
				      'warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie',
				      'wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie',
				      'zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie',
				      'łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie',
				      'śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie',
				     'świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie'],
				    
		       'Imię':['Zuzanna','Hanna','Zofia','Maja','Julia','Laura','Oliwia','Pola','Alicja','Lena',
			       'Zofia','Zuzanna','Maja','Julia','Laura','Pola','Alicja','Lena','Oliwia','Hanna',
			       'Zuzanna','Julia','Hanna','Laura','Alicja','Zofia','Oliwia','Lena','Maja','Pola',
			       'Hanna','Zuzanna','Maja','Pola','Julia','Zofia','Laura','Lena','Oliwia','Maria',
			       'Zofia','Alicja','Zuzanna','Julia','Hanna','Laura','Maja','Maria','Oliwia','Pola',
			       'Zuzanna','Julia','Zofia','Emilia','Hanna','Laura','Maja','Alicja','Oliwia','Lena',
			       'Hanna','Zofia','Zuzanna','Julia','Lena','Maja','Laura','Pola','Emilia','Oliwia',
			       'Julia','Laura','Hanna','Zuzanna','Zofia','Maja','Emilia','Lena','Oliwia','Aleksandra',
			       'Zuzanna','Hanna','Laura','Zofia','Julia','Oliwia','Maja','Maria','Marcelina','Alicja',
			       'Zuzanna','Zofia','Laura','Hanna','Maja','Julia','Pola','Oliwia','Lena','Maria',
			       'Zuzanna','Hanna','Zofia','Julia','Maja','Laura','Maria','Pola','Oliwia','Alicja',
			       'Zofia','Zuzanna','Maja','Julia','Laura','Hanna','Lena','Pola','Oliwia','Maria',
			       'Maja','Zuzanna','Hanna','Julia','Zofia','Pola','Laura','Lena','Maria','Oliwia',
			       'Hanna','Zuzanna','Zofia','Maja','Julia','Laura','Oliwia','Alicja','Lena','Maria',
			       'Zuzanna','Hanna','Julia','Maja','Emilia','Zofia','Laura','Alicja','Lena','Oliwia',
			       'Hanna','Zuzanna','Zofia','Lena','Laura','Julia','Maja','Maria','Alicja','Oliwia'],
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
	
    DF_c = pd.DataFrame({"Województwo":['dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie',
				      'kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie',
				      'lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie',
				      'lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie',
				      'mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie',
				      'małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie',
				      'opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie',
				      'podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie',
				      'podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie',
				      'pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie',
				      'warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie',
				      'wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie',
				      'zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie',
				      'łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie',
				      'śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie',
				     'świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie'],
		       'Imię':['Antoni','Jakub','Jan','Aleksander','Leon','Franciszek','Filip','Mikołaj','Ignacy','Stanisław',
			       'Antoni','Jakub','Aleksander','Franciszek','Jan','Leon','Nikodem','Mikołaj','Tymon','Szymon',
			       'Antoni','Aleksander','Jan','Jakub','Mikołaj','Franciszek','Szymon','Nikodem','Filip','Ignacy',
			       'Antoni','Leon','Franciszek','Aleksander','Jan','Jakub','Szymon','Nikodem','Filip','Ignacy',
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
	
	

	
    DF_2020_z=pd.DataFrame({"Województwo":['dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie',
				      'kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie',
				      'lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie',
				      'lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie',
				      'mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie',
				      'małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie',
				      'opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie',
				      'podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie',
				      'podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie',
				      'pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie',
				      'warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie',
				      'wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie',
				      'zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie',
				      'łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie',
				      'śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie',
				     'świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie'],
				    
		       'Imię':['Hanna','Julia','Zofia','Zuzanna','Maja','Oliwia','Lena','Alicja','Pola','Laura',
			       'Zuzanna','Zofia','Julia','Lena','Maja','Hanna','Alicja','Laura','Oliwia','Maria',
			       'Zuzanna','Hanna','Julia','Alicja','Maja','Zofia','Lena','Laura','Oliwia','Maria',
			       'Maja','Zuzanna','Hanna','Julia','Zofia','Lena','Oliwia','Pola','Maria','Wiktoria',
			       'Zofia','Julia','Zuzanna','Hanna','Alicja','Maja','Maria','Oliwia','Laura','Marcelina',
			       'Julia','Zuzanna','Zofia','Emilia','Hanna','Maja','Lena','Laura','Oliwia','Alicja',
			       'Zuzanna','Hanna','Julia','Zofia','Maja','Emilia','Lena','Alicja','Amelia','Maria',
			       'Julia','Zuzanna','Emilia','Maja','Hanna','Zofia','Lena','Oliwia','Aleksandra','Laura',
			       'Zofia','Julia','Zuzanna','Hanna','Maja','Laura','Lena','Oliwia','Aleksandra','Maria',
			       'Zuzanna','Zofia','Maja','Julia','Hanna','Lena','Laura','Pola','Oliwia','Antonina',
			       'Zuzanna','Zofia','Hanna','Julia','Maja','Pola','Lena','Oliwia','Alicja','Maria',
			       'Zofia','Zuzanna','Maja','Julia','Hanna','Lena','Maria','Laura','Oliwia','Antonina',
			       'Zofia','Zuzanna','Hanna','Julia','Maja','Pola','Lena','Maria','Laura','Oliwia',
			       'Julia','Hanna','Maja','Zuzanna','Zofia','Lena','Alicja','Maria','Oliwia','Laura',
			       'Julia','Zuzanna','Hanna','Maja','Emilia','Alicja','Zofia','Lena','Laura','Oliwia',
			       'Zuzanna','Hanna','Maja','Julia','Zofia','Lena','Alicja','Oliwia','Maria','Laura'],
		       'Liczba imion':[572,548,529,506,465,378,369,360,329,322,
				       403,385,361,352,318,296,276,268,247,238,
				       409,356,339,325,302,298,287,259,245,215,
				       179,168,168,166,157,126,120,115,111,94,
				       1207,1180,1121,1004,985,965,884,820,800,724,
				       810,736,664,644,627,624,532,503,501,499,
				       185,166,161,156,146,132,114,103,96,95,
				       480,421,363,351,337,330,328,320,293,293,
				       239,238,222,205,181,174,167,166,165,164,
				       503,481,481,431,376,354,353,318,295,294,
				       276,268,253,248,237,175,171,171,167,165,
				       809,655,642,633,579,548,516,473,460,442,
				       301,288,285,284,274,246,212,211,196,177,
				       456,443,428,425,411,388,361,323,321,303,
				       829,817,775,705,685,669,666,645,545,523,
				      215,214,210,186,166,158,154,144,125,125]}
			   
	 	     )
			   
    DF_2020_m=pd.DataFrame({"Województwo":['dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie',
				      'kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie',
				      'lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie',
				      'lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie',
				      'mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie',
				      'małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie',
				      'opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie',
				      'podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie',
				      'podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie',
				      'pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie',
				      'warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie',
				      'wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie',
				      'zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie',
				      'łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie',
				      'śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie',
				     'świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie'],
				    
		       'Imię':['Antoni','Jakub','Jan','Aleksander','Franciszek','Szymon','Mikołaj','Filip','Leon','Stanisław',
			       'Antoni','Jan','Aleksander','Jakub','Franciszek','Szymon','Mikołaj','Stanisław','Tymon','Marcel',
			       'Antoni','Szymon','Jan','Aleksander','Franciszek','Jakub','Mikołaj','Filip','Wojciech','Nikodem',
			       'Antoni','Jan','Aleksander','Jakub','Leon','Franciszek','Szymon','Mikołaj','Filip','Nikodem',
			       'Antoni','Jan','Aleksander','Franciszek','Jakub','Stanisław','Szymon','Mikołaj','Adam','Filip',
			       'Antoni','Jan','Jakub','Franciszek','Szymon','Aleksander','Filip','Mikołaj','Adam','Leon',
			       'Antoni','Jakub','Filip','Szymon','Franciszek','Jan','Adam','Leon','Michał','Aleksander',
			       'Antoni','Szymon','Jakub','Franciszek','Aleksander','Jan','Filip','Mikołaj','Kacper','Nikodem',
			       'Jakub','Aleksander','Jan','Antoni','Szymon','Filip','Marcel','Franciszek','Mikołaj','Kacper',
			       'Antoni','Jan','Jakub','Franciszek','Aleksander','Leon','Stanisław','Szymon','Filip','Nikodem',
			       'Aleksander','Antoni','Franciszek','Jan','Jakub','Szymon','Mikołaj','Stanisław','Filip','Nikodem',
			       'Antoni','Franciszek','Jan','Stanisław','Aleksander','Leon','Wojciech','Jakub','Marcel','Filip',
			       'Antoni','Jan','Aleksander','Franciszek','Jakub','Leon','Filip','Mikołaj','Szymon','Tymon',
			       'Jan','Antoni','Aleksander','Franciszek','Jakub','Szymon','Mikołaj','Wojciech','Stanisław','Filip',
			       'Jakub','Antoni','Franciszek','Jan','Filip','Szymon','Wojciech','Aleksander','Leon','Mikołaj',
			       'Antoni','Aleksander','Jan','Franciszek','Jakub','Szymon','Tymon','Adam','Filip','Mikołaj'],
		       'Liczba imion':[543,506,482,457,437,424,421,393,392,353,
				       404,398,389,366,344,316,291,278,265,261,
				       462,393,390,377,363,353,315,277,232,231,
				       159,158,152,149,132,131,124,122,122,110,
				       1413,1384,1337,1255,1055,963,907,856,819,802,
				       847,843,819,720,673,654,569,552,531,513,
				       181,159,158,140,138,121,119,114,105,104,
				       530,483,440,423,396,381,335,316,283,279,
				       267,249,236,223,211,195,160,160,148,145,
				       510,494,457,434,422,417,386,350,337,326,
				       327,319,249,243,234,225,201,177,176,172,
				       857,794,791,674,671,619,618,588,498,462,
				       338,290,287,287,262,224,218,217,194,184,
				       529,511,509,457,457,358,342,328,327,323,
				       851,800,730,707,702,667,621,592,578,563,
				      269,240,210,199,198,159,157,155,148,147]}

		     )
    DF_2019_z=pd.DataFrame({"Województwo":['dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie',
				      'kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie',
				      'lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie',
				      'lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie',
				      'mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie',
				      'małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie',
				      'opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie',
				      'podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie',
				      'podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie',
				      'pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie',
				      'warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie',
				      'wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie',
				      'zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie',
				      'łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie',
				      'śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie',
				     'świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie'],
				    
		       'Imię':['Zuzanna','Hanna','Julia','Maja','Zofia','Lena','Maria','Amelia','Alicja','Oliwia',
			       'Zuzanna','Lena','Maja','Julia','Zofia','Hanna','Alicja','Amelia','Maria','Oliwia',
			       'Zuzanna','Hanna','Julia','Maja','Zofia','Lena','Alicja','Aleksandra','Maria','Oliwia',
			       'Zuzanna','Hanna','Maja','Zofia','Julia','Lena','Maria','Alicja','Laura','Oliwia',
			       'Zofia','Julia','Zuzanna','Hanna','Maja','Alicja','Maria','Lena','Oliwia','Helena',
			       'Julia','Zuzanna','Zofia','Hanna','Maja','Emilia','Lena','Aleksandra','Oliwia','Alicja',
			       'Hanna','Zuzanna','Maja','Julia','Zofia','Lena','Emilia','Wiktoria','Amelia','Alicja',
			       'Zuzanna','Julia','Maja','Lena','Hanna','Emilia','Zofia','Aleksandra','Oliwia','Wiktoria',
			       'Julia','Zofia','Zuzanna','Lena','Hanna','Maja','Aleksandra','Maria','Oliwia','Amelia',
			       'Zofia','Zuzanna','Julia','Maja','Lena','Hanna','Maria','Oliwia','Antonina','Amelia',
			       'Zuzanna','Zofia','Hanna','Maja','Lena','Julia','Maria','Alicja','Pola','Wiktoria',
			       'Zofia','Julia','Maja','Zuzanna','Lena','Hanna','Maria','Oliwia','Antonina','Amelia',
			       'Hanna','Zuzanna','Julia','Zofia','Maja','Lena','Alicja','Maria','Antonina','Pola',
			       'Julia','Zuzanna','Maja','Zofia','Hanna','Lena','Alicja','Maria','Amelia','Oliwia',
			       'Zuzanna','Hanna','Julia','Maja','Zofia','Lena','Alicja','Emilia','Amelia','Oliwia',
			       'Zuzanna','Julia','Lena','Maja','Zofia','Hanna','Maria','Oliwia','Alicja','Amelia'],
		       'Liczba imion':[602,594,571,521,505,400,338,331,329,326,
				       474,435,430,427,424,317,283,259,256,253,
				       489,380,378,368,343,332,328,245,242,241,
				       216,208,207,199,197,171,117,106,106,101,
				       1384,1310,1266,1098,1083,1024,977,932,768,689,
				       876,790,695,685,680,636,610,541,531,496,
				       218,194,186,180,173,148,126,117,113,109,
				       556,497,442,427,360,346,343,306,289,270,
				       283,261,250,228,220,206,197,191,161,159, 
				       511,510,506,491,427,424,369,323,318,305,
				       316,308,288,288,282,254,201,186,176,175,
				       818,746,738,706,699,674,571,484,480,470,
				       378,349,326,320,319,291,206,196,192,180,
				       547,510,460,460,459,438,337,337,301,297,
				       944,880,856,797,793,759,687,686,599,523,
				      280,235,234,215,197,195,146,143,141,138]}
			  
		     )   
			   
    DF_2019_m=pd.DataFrame({"Województwo":['dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie',
				      'kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie','kujawsko-pomorskie',
				      'lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie','lubelskie',
				      'lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie','lubuskie',
				      'mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie','mazowieckie',
				      'małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie','małopolskie',
				      'opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie','opolskie',
				      'podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie','podkarpackie',
				      'podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie','podlaskie',
				      'pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie','pomorskie',
				      'warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie','warmińsko-mazurskie',
				      'wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie','wielkopolskie',
				      'zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie','zachodniopomorskie',
				      'łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie','łódzkie',
				      'śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie','śląskie',
				     'świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie','świętokrzyskie'],
				    
		       'Imię':['Antoni','Jakub','Jan','Filip','Szymon','Aleksander','Franciszek','Mikołaj','Wojciech','Michał',
			       'Aleksander','Jakub','Antoni','Jan','Szymon','Franciszek','Mikołaj','Filip','Wojciech','Adam',
			       'Antoni','Szymon','Jakub','Aleksander','Jan','Mikołaj','Franciszek','Filip','Marcel','Wojciech',
			       'Antoni','Szymon','Jakub','Jan','Aleksander','Filip','Michał','Franciszek','Marcel','Leon',
			       'Jan','Aleksander','Antoni','Jakub','Franciszek','Szymon','Mikołaj','Stanisław','Adam','Filip',
			       'Jakub','Antoni','Szymon','Jan','Franciszek','Filip','Aleksander','Mikołaj','Kacper','Adam',
			       'Jakub','Antoni','Wojciech','Szymon','Jan','Franciszek','Filip','Adam','Aleksander','Kacper',
			       'Antoni','Szymon','Jakub','Aleksander','Jan','Filip','Mikołaj','Franciszek','Kacper','Michał',
			       'Jakub','Szymon','Jan','Aleksander','Antoni','Filip','Franciszek','Kacper','Michał','Mikołaj',
			       'Jan','Aleksander','Jakub','Franciszek','Antoni','Leon','Szymon','Mikołaj','Stanisław','Filip',
			       'Antoni','Aleksander','Jan','Jakub','Szymon','Franciszek','Filip','Nikodem','Mikołaj','Kacper',
			       'Antoni','Jan','Wojciech','Franciszek','Aleksander','Jakub','Stanisław','Leon','Filip','Mikołaj',
			       'Antoni','Jakub','Aleksander','Jan','Filip','Szymon','Franciszek','Mikołaj','Nikodem','Leon',
			       'Antoni','Jan','Aleksander','Jakub','Szymon','Franciszek','Filip','Wojciech','Mikołaj','Stanisław',
			       'Jakub','Antoni','Franciszek','Filip','Szymon','Jan','Wojciech','Mikołaj','Aleksander','Kacper',
			       'Antoni','Aleksander','Jakub','Jan','Franciszek','Szymon','Filip','Wojciech','Marcel','Mikołaj'],
		       'Liczba imion':[637,551,519,477,475,465,415,396,377,359,
				       448,429,425,377,374,364,339,333,292,268,
				       464,464,448,393,362,331,330,300,288,267,
				       199,183,171,162,161,155,123,122,113,110,
				       1629,1439,1419,1175,1161,1117,959,957,934,871,
				       890,802,798,783,661,624,597,583,546,534,
				       201,176,165,162,158,139,134,127,127,118,
				       544,544,505,414,401,388,382,371,322,295,
				       263,253,235,230,219,188,186,178,173,160, 
				       556,503,487,473,465,377,377,370,363,353,
				       324,317,279,249,243,233,218,201,182,178,
				       868,818,741,740,702,678,678,596,585,575,
				       350,321,303,282,251,250,227,227,216,215,
				       583,533,494,441,421,411,358,358,321,307,
				       921,793,766,757,756,713,628,582,579,544,
				      280,257,233,224,203,189,175,174,166,158]}

				       
				       
		     )
	
    col2.plotly_chart(px.bar(x=DF[DF['Województwo']==mies]['Liczba imion'][::-1],y=DF[DF['Województwo']==mies]['Imię'][::-1],
			     orientation='h',text=DF[DF['Województwo']==mies]['Liczba imion'][::-1],color=["red"]*10,
			     color_discrete_map="identity",
			     title='Top 10 imon żeńskich').update_xaxes(title_text='Liczba imion').update_yaxes(title_text='Imię'
				).update_layout(plot_bgcolor='white',title_x=0.5,height=600))

  

      

    col1, col2 = st.columns(2)
    
    # top 10
    
   
    col2.plotly_chart(px.bar(x=DF_c[DF_c['Województwo']==mies]['Liczba imion'][::-1],y=DF_c[DF_c['Województwo']==mies]['Imię'][::-1],
			     orientation='h',text=DF_c[DF_c['Województwo']==mies]['Liczba imion'][::-1],color=["red"]*10,
			     color_discrete_map="identity",
			     title='Top 10 imon męskich').update_xaxes(title_text='Liczba imion').update_yaxes(title_text='Imię'
				).update_layout(plot_bgcolor='white',title_x=0.5,height=600))
 













if sekcja == 'Analiza korespondencji':
    new_title = '<b style="color:rgb(0, 80, 170); font-size: 62px;">Imiona nadawane dzieciom w Polsce - analiza</p>'
    st.markdown(new_title, unsafe_allow_html=True)
    st.markdown('---')
    st.title('Analiza korespondencji')
    roczek_opcje=["2019","2020","2021"]
    roczek_wybrany = st.selectbox("Wybierz rok:", roczek_opcje)
    if roczek_wybrany == "2019":
        st.subheader("Analiza korespondencji dla chłopców")
        st.write("Skumulowana proporcja bezwładności dla 2 wymiarów wynosi 0.459")
        st.image('imionaa/AK/f2_chl2019.png')
        st.subheader("Analiza korespondencji dla dziewczynek")
        st.write("Skumulowana proporcja bezwładności dla 2 wymiarów wynosi 0.464")
        st.image('imionaa/AK/f2_dzi2019.png')
    if roczek_wybrany == "2020":
        st.subheader("Analiza korespondencji dla chłopców")
        st.write("Skumulowana proporcja bezwładności dla 2 wymiarów wynosi 0.402")
        st.image('imionaa/AK/f2_chl2020.png')
        st.subheader("Analiza korespondencji dla dziewczynek")
        st.write("Skumulowana proporcja bezwładności dla 2 wymiarów wynosi 0.447")
        st.image('imionaa/AK/f2_dzi2020.png')
    if roczek_wybrany == "2021":
        st.subheader("Analiza korespondencji dla chłopców")
        st.write("Skumulowana proporcja bezwładności dla 2 wymiarów wynosi 0.511")
        st.image('imionaa/AK/f2_chl2021.png')
        st.subheader("Analiza korespondencji dla dziewczynek")
        st.write("Skumulowana proporcja bezwładności dla 2 wymiarów wynosi 0.654")
        st.image('imionaa/AK/f2_dzi2021.png')
	#st.subheader('Imiona żeńskie')
        #st.image('imionaa/PI1/PI1/zk1.png')
	
   
    

    
    
    
st.balloons()
    
        


        
  
        



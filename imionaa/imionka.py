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
    ('Strona główna','Trendy','Litery w imionach', 'Najczęściej nadawane imiona','Analiza korespondencji')
 )


tabs_font_css = """
<style>
div[class*="stTextInput"] label {
  font-size: 26px;
  color: black;
}
div[class*="stSelectbox"] label {
  font-size: 26px;
  color: black;
}
</style>
"""

st.write(tabs_font_css, unsafe_allow_html=True)

kol = {'K':'rgb(255, 0, 255)','M':'rgb(0,70,180)'}
kol1 = {'KK':['rgb(255, 0, 255)','rgb(200, 0, 25)'],'MM':['rgb(0,70,180)','rgb(0,0,205)'],'KM':['rgb(255, 0, 255)','rgb(0,70,180)'],'MK':['rgb(0,70,180)','rgb(255, 0, 255)']}
kol2 = {'K0K1M2M3':['rgb(255,0,205)','red','rgb(0,70,180)','blue'],'K0M1M2K3':['rgb(255,0,205)','rgb(0,70,180)','blue','red'],
       'K0M1K2M3':['rgb(255,0,205)','rgb(0,70,180)','red','blue'],'M0K1M2K3':['rgb(0,70,180)','red','blue','rgb(255,0,205)'],
       'M0M1K2K3':['rgb(0,70,180)','blue','red','rgb(255,0,205)'],'M0K1K2M3':['rgb(0,70,180)','red','rgb(255,0,205)','blue'],
       'M0M1K2':['rgb(0,70,180)','blue','rgb(255,0,205)'],'M0K1K2':['rgb(0,70,180)','red','rgb(255,0,205)'],
       'M0K1M2':['rgb(0,70,180)','rgb(255,0,205)','blue'],'K0M1K2':['rgb(255,0,205)','rgb(0,70,180)','red'],
       'K0M1M2':['rgb(255,0,205)','rgb(0,70,180)','blue'],'K0K1M2':['rgb(255,0,205)','red','rgb(0,70,180)'],
       'K0K1':['rgb(255,0,205)','red'],'K0M1':['rgb(255,0,205)','rgb(0,70,180)'],'M0K1':['rgb(0,70,180)','rgb(255,0,205)'],
       'M0M1':['rgb(0,70,180)','blue']}
im = pd.read_excel(io='imionaa/PI/imiona.xlsx',engine='openpyxl',dtype={'Rok':str})
alf = {'A':0, 'B':1, 'C':2, 'D':3, 'E':4, 'F':5, 'G':6, 'H':7, 'I':8, 'J':9, 'K':10, 'L':11, 'Ł':12, 'M':13, 'N':14, 'O':15, 'Ó':16, 'P':17, 'Q':18, 'R':19, 'S':20, 'Ś':21, 'T':22, 'U':23, 'V':24, 'W':25, 'X':26, 'Y':27, 'Z':28, 'Ź':29, 'Ż':30}


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
tabelka_k = tabelka_k.sort_index(key= lambda x : x.map(alf))
tabelka_m= im.pivot_table('Liczba', index=pierwsza_litera_m, columns=['Rok'], aggfunc=sum)
tabelka_m = tabelka_m.sort_index(key= lambda x : x.map(alf))

litera_ulamek_k = tabelka_k/tabelka_k.sum()

litera_ulamek_m = tabelka_m/tabelka_m.sum()

#ostatnia litera imienia
wyciagam_ostatnia_litere = lambda x: x[-1]
ostatnia_litera_k = imiona_k.Imię.map(wyciagam_ostatnia_litere)
ostatnia_litera_k = ostatnia_litera_k.sort_index(key= lambda x : x.map(alf))
ostatnia_litera_m = imiona_m.Imię.map(wyciagam_ostatnia_litere)
ostatnia_litera_m = ostatnia_litera_m.sort_index(key= lambda x : x.map(alf))


tabelka_k1=im.pivot_table('Liczba', index=ostatnia_litera_k,columns=['Rok'], aggfunc=sum)
tabelka_k1 = tabelka_k1.sort_index(key= lambda x : x.map(alf))
tabelka_m1=im.pivot_table('Liczba', index=ostatnia_litera_m,columns=['Rok'], aggfunc=sum)
tabelka_m1 = tabelka_m1.sort_index(key= lambda x : x.map(alf))


if sekcja == 'Strona główna':
    new_title = '<b style="color:rgb(0, 80, 170); font-size: 62px;">Imiona nadawane dzieciom w Polsce - analiza </p>'
    st.markdown(new_title, unsafe_allow_html=True)
    st.markdown('---')
    st.title('Strona główna')
    st.write('Ustalenie imienia dla dziecka to niełatwa decyzja. Powinna być świadomym wyborem obojga partnerów. ' +
		 'Niektórzy rodzice kierują się modą, inni rodzinną tradycją, kolejni łatwością do zdrobnienia. ' +
		 'Są też tacy, którzy zwracają uwagę na oryginalność lub po prostu brzmienie imienia. ' +
		'Niniejsza strona prezentuje trendy w popularności imion nadawanych dzieciom w Polsce w latach 2000-2022. ' +
	    'Aplikację należy dostosować sobie do szerokości ekranu za pomocą kombinacji klawiszy Ctrl Shift + lub Ctrl Shift -.')

    st.subheader('Źródło danych')
    st.write('Dane do analizy pobrane zostały ze strony Ministerstwa Cyfryzacji. Były one w postaci piętnastu plików formatu xlsx.')
    st.write('Link do strony: https://dane.gov.pl/pl/dataset/219,imiona-nadawane-dzieciom-w-polsce')
    st.write('Dane z lat 2000-2021 - dostęp z dnia 29.05.2022 r.')
    st.write('Dane z roku 2022 - dostęp z dnia 03.02.2023 r.')
    st.write('Dane z lat 2000–2012 zawierają imiona, których liczba wystąpień wynosi co najmniej 5. ' +
	     'Od roku 2013 dane zawierają imiona, których liczba wystąpień jest większa od 1. ' + 
	     'W związku z tym łączna liczba zarejestrowanych dzieci w rzeczywistości oznacza łączną liczbę zarejestrowanych dzieci o imionach występujących na liście, ' +
	     'czyli tych, które nie są unikalne. Ta liczba służy też do wyznaczenia wszystkich wartości względnych (procentowych).')
       
    imie = st.text_input('Podaj imię:  ','Martyna')
    imie = imie.upper()
    if imie in list(im['Imię']):
        st.subheader('Liczba dzieci o nadanym imieniu {i} na przestrzeni lat 2000-2022'.format(i=str(imie)))
        st.plotly_chart(px.line(im[im['Imię']==imie].sort_values(['Rok','Płeć']),x='Rok',y='Liczba',color='Płeć',markers=True,width=1100, height=600,
			    color_discrete_sequence=list(map(lambda x: kol[x],[np.array(im[im['Imię']==imie].sort_values(['Rok','Płeć'])['Płeć'])[index] for index in sorted(np.unique(np.array(im[im['Imię']==imie].sort_values(['Rok','Płeć'])['Płeć']), return_index=True)[1])])))
		    .update_yaxes(rangemode='tozero').update_traces(line_width=2))
        st.subheader('Procent dzieci danej płci o nadanym imieniu {} na przestrzeni lat 2000-2022'.format(imie))
        st.write('Wykres prezentuje liczbę dzieci o danym imieniu w ujęciu procentowym względem liczby zarejestrowanych dzieci, która mogła być różna w kolejnych latach. ')
        st.plotly_chart(px.line(im[im['Imię']==imie].sort_values(['Rok','Płeć']),x='Rok',y='Proporcja%',color='Płeć',markers=True,width=1100, height=600,color_discrete_sequence=list(map(lambda x: kol[x],im[im['Imię']==imie].sort_values(['Rok','Płeć'])['Płeć'].unique()))).update_yaxes(title_text='Procent',rangemode='tozero'))
        
    else:
        st.write("*Brak danych o wybranym imieniu")
    #st.subheader('Liczba dzieci o nadanym imieniu {i} na przestrzeni lat 2000-2021'.format(i=str(imie)))
    #st.plotly_chart(px.line(im[im['Imię']==imie].sort_values(['Rok','Płeć']),x='Rok',y='Liczba',color='Płeć',markers=True,width=1100, height=600,
	#		    color_discrete_sequence=list(map(lambda x: kol[x],[np.array(im[im['Imię']==imie].sort_values(['Rok','Płeć'])['Płeć'])[index] for index in sorted(np.unique(np.array(im[im['Imię']==imie].sort_values(['Rok','Płeć'])['Płeć']), return_index=True)[1])])))
		#    .update_yaxes(rangemode='tozero').update_traces(line_width=2))
    #
    #st.dataframe(im[im['Imię']==imie].sort_values(['Rok','Płeć']))
    #st.write(im[im['Imię']==imie]['Płeć'].groupby('Rok')['Płeć'].astype(int).agg(np.min))
	#st.dataframe(im[im['Imię']==imie].sort_values(['Płeć','Rok']))
	
     #IMIONA JEDNOCZEŚNIE MĘSKIE I ŻEŃSKIE
    chłopcy=im[im.Płeć=='M']
    dziewczynki=im[im.Płeć=='K']
    dziwne=pd.DataFrame({"Imię":['ADEL','ADI','ALEX','ALEXIS','AMAL','AMELIA','AMIT','ANDREA','ANGEL','ARIEL','BAO AN','CHEN','DANIEL','EDEN',
				 'ELI','ELIA','EZRA','FABIAN','GIA','IGOR','ILIA','ILLIA','IMAN','ISA','KAREN','LAUREN','LILIAN','MICHAL','MIKA',
				 'MILENA','MINH','MINH ANH','MORGAN','NICOLA','NIKITA','NIKOLA','NOA','NOAM','OLIVIA','OMER','ORI','PARIS','RAJA',
				 'RILEY','RONI','SASHA','SIMONE','SZYMON','TAL','THIEN AN','YARDEN','YUVAL'],
			"Liczba wystąpień imienia jako imię żeńskie":['37','19','2','6','5','116606','6','331','5','6','3','2','2','2','3','9','2','2',
								      '5','2','8','2','90','2','141','29','56','5','178','45893',
								      '8','14','2','7936','63','71691','132','9','9431','3','4','7','4','2','77','26','18','2',
								      '10','2','2','20'],
			"Liczba wystąpień imienia jako imię męskie":['2', '2', '8811', '2', '2','2', '32', '149', '20', '400', '2', '2', '32540', '2',
								     '31', '2', '11', '29196', '2', '73629', 
								     '41', '205', '2', '3', '2', '2', '6',
								     '211', '2', '2', '24', '4', '11', '34', '380', '9', '15', '76', '2', '54', '39', '2',
								     '2', '2', '18', '33', '153', '162375', 
								     '12', '2', '4', '47']
			})
    st.subheader('Imiona, które były nadawane zarówno chłopcom jak i dziewczynkom')
    st.dataframe(dziwne)
	
	
	
    
    

	

	
if sekcja == 'Trendy':
    new_title = '<b style="color:rgb(0, 80, 170); font-size: 62px;">Imiona nadawane dzieciom w Polsce - analiza</p>'
    st.markdown(new_title, unsafe_allow_html=True)
    st.markdown('---')
    st.title('Trendy')
    
    #łączna ilość urodzeń
    total_ur=im.pivot_table('Liczba', index='Rok', columns='Płeć', aggfunc=sum)	
    total_ur=pd.DataFrame(total_ur, columns=['K','M'])
    st.subheader('Łączna liczba dzieci zarejestrowanych w latach 2000-2022 z podziałem na płeć')
    st.write('Po wzroście liczby rejestrowanych dzieci w latach 2008-2010 i w roku 2017 w ostatnich latach zauważalny jest znaczny spadek.')
    #st.dataframe(total_ur.index)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=total_ur.index,y=total_ur['K'],line_color=kol['K'],name='Dziewczynki'))
    fig.add_trace(go.Scatter(x=total_ur.index,y=total_ur['M'],line_color=kol['M'],name='Chłopcy'))
    fig.update_xaxes(title_text='Rok')
    fig.update_yaxes(title_text='Liczba',rangemode='tozero')
    fig.update_layout(legend_title_text='Płeć',width=1000,height=400)
    st.plotly_chart(fig)
    
	
    #top 100
    def the_top100(group):
    	return group.sort_values(by='Liczba', ascending=False)[:100]
    grouped=im.groupby(['Rok','Płeć'])
    top100=grouped.apply(the_top100)
    top100.reset_index(inplace=True, drop=True)
	
    tabelka=top100.pivot_table('Proporcja%',index='Rok',columns='Płeć',aggfunc=sum)
    tabelka=pd.DataFrame(tabelka, columns=['K','M'])
    st.subheader('Procent zarejestrowanych dzieci, którym nadaje się imiona należące do listy 100 najpopularniejszych imion')
    st.write('Wykres ten pokazuje, że rodzice coraz rzadziej sięgają po najpopularniejsze imiona. Trend ten zmienił się chwilowo w latach 2016-2018, być może ze względu na dużą popularność w tych latach takich imion jak Antoni czy Zofia. ')
    #st.plotly_chart(px.line(tabelka).update_yaxes(title_text='Rok').update_yaxes(title_text='Procent'))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tabelka.index,y=tabelka['K'],line_color=kol['K'],name='Dziewczynki'))
    fig.add_trace(go.Scatter(x=tabelka.index,y=tabelka['M'],line_color=kol['M'],name='Chłopcy'))
    fig.update_xaxes(title_text='Rok')
    fig.update_yaxes(title_text='Procent',rangemode='tozero')
    fig.update_layout(legend_title_text='Płeć',width=1000,height=400)
    st.plotly_chart(fig)
	
	
    diversity = pd.DataFrame(diversity, columns=['K','M'])
    st.subheader('Liczba imion z listy najpopularniejszych w Polsce nadanych łącznie przynajmniej 50% zarejestrowanych dzieci danej płci')
    st.write(' Mimo że na liście imion nadawanych dzieciom w Polsce w latach 2000-2022 jest 2055 imion żeńskich i 2144 imion męskich, ' +
	     'ponad połowie dzieci nadano imię z listy 12-20 najpopularniejszych. '+
        'O ile różnorodność imion męskich jest od lat na mniej więcej stałym poziomie, to różnorodność imion żeńskich stale rośnie.')
    #st.plotly_chart(px.line(diversity).update_yaxes(title_text='Rok').update_yaxes(title_text='Liczba',rangemode='tozero'))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=diversity.index,y=diversity['K'],line_color=kol['K'],name='Dziewczynki'))
    fig.add_trace(go.Scatter(x=diversity.index,y=diversity['M'],line_color=kol['M'],name='Chłopcy'))
    fig.update_xaxes(title_text='Rok')
    fig.update_yaxes(title_text='Liczba',rangemode='tozero')
    fig.update_layout(legend_title_text='Płeć',width=1000,height=400)
    st.plotly_chart(fig)
   

	
   

    
	
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
    #st.write(kol1[str(im[im['Imię']==imie1]['Płeć'].iloc[0])+str(im[im['Imię']==imie2]['Płeć'].iloc[0])])
    #st.dataframe(imionka)
    imionka2 = imionka
    imionka2['Nowa'] = imionka2[['Imię','Płeć']].apply(lambda x: x['Imię']+str('  ')+x['Płeć'],axis=1)
    imionka2['Nowa2'] = imionka2[['Imię','Płeć']].apply(lambda x: x['Płeć']+str('  ')+x['Imię'],axis=1)
    #st.dataframe(imionka2)
    #st.dataframe(imionka2.sort_values(['Rok','Nowa2']))
    koly = list(map(lambda x, y: x[0]+str(y),list(imionka2.sort_values(['Rok','Nowa2'])['Nowa2'].unique()),list(range(len(list(list(imionka2.sort_values(['Rok','Nowa2'])['Nowa2'].unique()))) ))) )
    koly0 = ''.join(str(x) for x in koly)
    
    #st.dataframe(imionka2.sort_values(['Rok','Nowa2']))
    imionka3 = imionka2.groupby(by=['Rok','Imię']).sum().reset_index()
    #st.dataframe(imionka3['Rok'].apply(lambda x: str(x)+'-12'))
    #imionka3['Rok'] = imionka3['Rok'].apply(lambda x: str(x)+'-12')
    imionka2['Rok'] = imionka2['Rok'].apply(lambda x: str(x)+'-1')
    #st.write(koly0)
    #if (imie1 in list(im['Imię']))  and (imie2 in list(im['Imię']) )
    #if (np.min(list(im[im['Imię']==imie1]['Liczba']))>100)  and (np.min(list(im[im['Imię']==imie2]['Liczba']))>100) :
    #st.plotly_chart(px.line(imionka3.sort_values(['Rok','Imię']),x=sorted(list(imionka3['Rok'])),y='Liczba',color='Imię',width=1100, height=600, markers=True).update_xaxes(tickmode='array').update_yaxes(rangemode='tozero'))
    #st.plotly_chart(px.line(imionka2.sort_values(['Rok','Nowa2']),x='Rok',y='Liczba',color='Nowa2',markers=True,width=1100, height=600,color_discrete_sequence=kol2[koly0]).update_xaxes(dtick='M12').update_yaxes(rangemode='tozero'))
    if (imie1 in list(im['Imię']))  and (imie2 in list(im['Imię']) ):
	    st.plotly_chart(px.line(imionka2.sort_values(['Rok','Nowa2']),x='Rok',y='Liczba',color='Nowa2',markers=True,width=1100, height=600,color_discrete_sequence=kol2[koly0]).update_xaxes(dtick='M12').update_yaxes(rangemode='tozero').update_layout(legend_title_text='Płeć oraz imię'),legend={'traceorder':'normal'})
    else:
	    st.write('*Brak danych dla wybranych imion')
    
   
	
	
	
if sekcja == 'Litery w imionach':	
    # PIERWSZA LITERA
	#liczba dziewczynek
    st.header('Analiza pierwszej i ostatniej litery imienia')
    rok=st.selectbox("Wybierz rok:", list(range(2000,2023))[::-1])
    st.header('Pierwsza litera - imiona żeńskie')
    c1, c2 = st.columns(2)
    with c1:
    	st.subheader('Liczba dziewczynek o imieniu rozpoczynającym się daną literą')
    	st.plotly_chart(px.bar(tabelka_k[str(rok)],y=str(rok),color_discrete_sequence=['rgb(255,0,205)']*len(tabelka_k[str(rok)])).update_xaxes(title_text='Litera').update_yaxes(title_text='Liczba'
		).update_layout(plot_bgcolor='white'))
	
	#liczba imion żeńskich	
    with c2:
        uni=pd.DataFrame({'litera':list(map(lambda x: x[0],im[(im['Rok']==str(rok)) & (im['Płeć']=='K')].sort_values(by='Imię')['Imię'].unique()))}).groupby(['litera'])['litera'].count()
        uni = uni.sort_index(key= lambda x : x.map(alf))
        st.subheader('Liczba imion żeńskich rozpoczynających się daną literą')
        st.plotly_chart(px.bar(uni,y='litera',color_discrete_sequence=['rgb(255,0,205)']*len(uni)).update_xaxes(title_text='Litera').update_yaxes(title_text='Liczba'
		    ).update_layout(plot_bgcolor='white'))
    
	#liczba chłopców
    st.header('Pierwsza litera - imiona męskie')
    c3, c4 = st.columns(2)
    with c3:
    	st.subheader('Liczba chłopców o imieniu rozpoczynającym się daną literą')
    	st.plotly_chart(px.bar(tabelka_m[str(rok)],y=str(rok),color_discrete_sequence=['rgb(0,70,180)']*len(tabelka_m[str(rok)])).update_xaxes(title_text='Litera').update_yaxes(title_text='Liczba'
		).update_layout(plot_bgcolor='white'))
    
	#liczba imion męskich
    with c4:
        uni=pd.DataFrame({'litera':list(map(lambda x: x[0],im[(im['Rok']==str(rok)) & (im['Płeć']=='M')].sort_values(by='Imię')['Imię'].unique()))}).groupby(['litera'])['litera'].count()
        uni = uni.sort_index(key= lambda x : x.map(alf))
        st.subheader('Liczba imion męskich rozpoczynających się daną literą')
        st.plotly_chart(px.bar(uni,y='litera',color_discrete_sequence=['rgb(0,70,180)']*len(uni)).update_xaxes(title_text='Litera').update_yaxes(title_text='Liczba'
		   ).update_layout(plot_bgcolor='white'))
	
    st.header('Ostatnia litera - imiona żeńskie')
    c7, c8 = st.columns(2)
    with c7:
        st.subheader('Liczba dziewczynek o imieniu kończącym się daną literą')
        st.plotly_chart(px.bar(tabelka_k1[str(rok)],y=str(rok),color_discrete_sequence=['rgb(255,0,205)']*len(tabelka_k1[str(rok)])).update_xaxes(title_text='Litera').update_yaxes(title_text='Liczba'
		).update_layout(plot_bgcolor='white'))
	
	#liczba imion żeńskich
    with c8:
        uni=pd.DataFrame({'litera':list(map(lambda x: x[-1],im[(im['Rok']==str(rok)) & (im['Płeć']=='K')].sort_values(by='Imię')['Imię'].unique()))}).groupby(['litera'])['litera'].count()
        uni = uni.sort_index(key= lambda x : x.map(alf))
        st.subheader('Liczba imion żeńskich kończących się daną literą')
        st.plotly_chart(px.bar(uni,y='litera',color_discrete_sequence=['rgb(255,0,205)']*len(uni)).update_xaxes(title_text='Litera').update_yaxes(title_text='Liczba'
        		).update_layout(plot_bgcolor='white'))
	
	
	
    st.header('Ostatnia litera - imiona męskie')
    c5, c6 = st.columns(2)
    with c5:
    	st.subheader('Liczba chłopców o imieniu kończącym się daną literą')
    	st.plotly_chart(px.bar(tabelka_m1[str(rok)],y=str(rok),color_discrete_sequence=['rgb(0,70,180)']*len(tabelka_m1[str(rok)])).update_xaxes(title_text='Litera').update_yaxes(title_text='Liczba'
		).update_layout(plot_bgcolor='white'))
    
	#liczba imion męskich
    with c6:
        uni=pd.DataFrame({'litera':list(map(lambda x: x[-1],im[(im['Rok']==str(rok)) & (im['Płeć']=='M')].sort_values(by='Imię')['Imię'].unique()))}).groupby(['litera'])['litera'].count()
        uni = uni.sort_index(key= lambda x : x.map(alf))  	
        st.subheader('Liczba imion męskich kończących się daną literą')
        st.plotly_chart(px.bar(uni,y='litera',color_discrete_sequence=['rgb(0,70,180)']*len(uni)).update_xaxes(title_text='Litera').update_yaxes(title_text='Liczba'
        		).update_layout(plot_bgcolor='white'))
    


if sekcja == 'Najczęściej nadawane imiona':
	#Najczęsciej nadawane imiona dzieciom w Polsce
    st.subheader("Imiona najczęściej nadawane dzieciom w Polsce w latach 2000-2022")
    dowyboru=list(range(2000,2023)[::-1])
    cos=st.selectbox("Wybierz rok:     ", dowyboru)
    def the_top10(group):
        return group.sort_values(by='Liczba', ascending=False)[:10]
    grouped=im.groupby(['Rok','Płeć'])
    top10=grouped.apply(the_top10)
    top10.reset_index(inplace=True, drop=True)
    top10_k=top10[top10.Płeć=='K']
    top10_m=top10[top10.Płeć=='M']
    c1, c2 = st.columns(2)
    top10_k=top10_k[top10_k.Rok==str(cos)]
    top10_k = top10_k.sort_values(by='Liczba', ascending = True)
    #st.dataframe(top10_k)
    c1.plotly_chart(px.bar(top10_k, x="Liczba", y="Imię", orientation='h',color='Płeć',color_discrete_sequence=['rgb(255,0,205)'],
             height=600,
             title='Top 10 najczęściej nadawanych imion żeńskich w roku {i}'.format(i=str(cos))))
    top10_m=top10_m[top10_m.Rok==str(cos)]
    top10_m=top10_m.sort_values(by="Liczba", ascending = True)
    #st.dataframe(top10_m)
    c2.plotly_chart(px.bar(top10_m, x="Liczba", y="Imię", orientation='h',color='Płeć',color_discrete_sequence=['rgb(0,70,180)'],
             height=600,
             title='Top 10 najczęściej nadawanych imion męskich w roku {i}'.format(i=str(cos))))

	
	
	
	
	
	
	#Najczęściej nadawane imiona dzieciom w podziale na województwa
    st.subheader('Imiona najczęściej nadawane dzieciom w Polsce w latach 2019-2022 w podziale na województwa')
    latka_opcje=["2019","2020","2021","2022"][::-1]
    wybrany = st.selectbox("Wybierz rok:", latka_opcje)
    
        #Mapka
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
    
    #col1.plotly_chart(fig)
    
	
	
     #chłopcy
    with urlopen('https://raw.githubusercontent.com/ppatrzyk/polska-geojson/master/wojewodztwa/wojewodztwa-min.geojson') as response:
        counties = json.load(response)
    dff = pd.DataFrame({"Województwo":['dolnośląskie','kujawsko-pomorskie','lubelskie','lubuskie','łódzkie','małopolskie','mazowieckie',
                                   'opolskie','podkarpackie','podlaskie','pomorskie','śląskie','świętokrzyskie','warmińsko-mazurskie',
                                   'wielkopolskie','zachodniopomorskie'],'kolor':['lightgray']*16})
    
    dff['kolor']=dff['kolor'].where(dff['Województwo']!=mies,'rgb(255,0,205)')
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
    dff1=dff
    dff1['kolor']=dff1['kolor'].where(dff1['Województwo']!=mies,'rgb(0,70,180)')
    fig1 = px.choropleth(dff1,
                    locations="Województwo",
                    geojson=counties,
                    featureidkey="properties.nazwa",
                    color='Województwo',
                    color_discrete_sequence=dff1['kolor'],
                    range_color=(400, 1900),
                   projection="mercator")
   
    fig1.update_geos(fitbounds="locations", visible=False)
    fig1.update_layout(height=650,showlegend=False,title="Mapa Polski",title_x=0.5)
    
    #col1.plotly_chart(fig)
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





    DF_2022_m=pd.DataFrame({"Województwo":['dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie',
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
				    
		       'Imię':['Antoni','Jan','Nikodem','Jakub','Leon','Aleksander','Franciszek','Mikołaj','Filip','Stanisław',
			       'Nikodem','Jan','Antoni','Aleksander','Franciszek','Leon','Mikołaj','Stanisław','Ignacy','Szymon',
			       'Antoni','Nikodem','Aleksander','Jan','Jakub','Franciszek','Mikołaj','Szymon','Filip','Ignacy',
			       'Leon','Antoni','Nikodem','Franciszek','Jan','Aleksander','Jakub','Mikołaj','Stanisław','Tymon',
			       'Jan','Aleksander','Antoni','Franciszek','Nikodem','Jakub','Stanisław','Mikołaj','Ignacy','Leon',
			       'Antoni','Jan','Jakub','Aleksander','Nikodem','Franciszek','Leon','Szymon','Mikołaj','Filip',
			       'Antoni','Leon','Nikodem','Franciszek','Jan','Jakub','Filip','Szymon','Wojciech','Mikołaj',
			       'Antoni','Nikodem','Aleksander','Jakub','Jan','Franciszek','Szymon','Filip','Kacper','Michał',
			       'Aleksander','Jakub','Antoni','Jan','Franciszek','Nikodem','Mikołaj','Szymon','Michał','Filip',
			       'Antoni','Nikodem','Aleksander','Leon','Franciszek','Jan','Jakub','Stanisław','Ignacy','Mikołaj',
			       'Nikodem','Antoni','Aleksander','Jan','Jakub','Franciszek','Leon','Mikołaj','Szymon','Ignacy',
			       'Jan','Antoni','Leon','Franciszek','Aleksander','Stanisław','Ignacy','Nikodem','Wojciech','Jakub',
			       'Antoni','Nikodem','Leon','Franciszek','Aleksander','Jan','Jakub','Mikołaj','Stanisław','Ignacy',
			       'Aleksander','Nikodem','Jan','Antoni','Franciszek','Jakub','Leon','Stanisław','Mikołaj','Wojciech',
			       'Antoni','Jakub','Nikodem','Filip','Franciszek','Leon','Mikołaj','Jan','Aleksander','Szymon',
			       'Aleksander','Antoni','Jan','Nikodem','Jakub','Franciszek','Marcel','Szymon','Mikołaj','Adam'],
		       'Liczba imion':[438,435,434,433,422,368,342,331,309,301,
				       366,350,339,314,306,302,244,228,223,217,
				       377,353,344,304,278,267,252,245,217,214,
				       150,140,131,130,124,116,115,109,99,85,
				       1238,1172,1099,1023,960,905,805,746,729,701,
				       722,673,644,629,621,603,540,501,479,430,
				       137,127,126,126,126,120,97,94,87,87,
				       418,404,370,366,362,334,314,255,248,245,
				       228,210,207,202,180,170,153,148,132,126,
				       392,387,382,382,356,355,336,312,293,275,
				       270,252,250,217,194,187,157,153,147,141,
				       638,623,622,598,579,513,492,487,481,444,
				       277,273,226,209,204,203,180,166,163,162,
				       453,393,392,391,350,336,299,298,278,253,
				       628,611,577,571,552,517,501,499,476,421,
				      228,226,216,202,152,133,125,120,117,117]}

				       
				       
		     )
	
	
	
			   
    DF_2022_z=pd.DataFrame({"Województwo":['dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie','dolnośląskie',
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
				    
		       'Imię':['Zuzanna','Hanna','Zofia','Maja','Julia','Oliwia','Pola','Laura','Maria','Alicja',
			       'Zuzanna','Laura','Zofia','Maja','Alicja','Pola','Lena','Oliwia','Julia','Maria',
			       'Zuzanna','Hanna','Zofia','Laura','Alicja','Maja','Oliwia','Julia','Pola','Lena',
			       'Maja','Zofia','Zuzanna','Hanna','Laura','Pola','Oliwia','Lena','Maria','Michalina',
			       'Zofia','Julia','Alicja','Laura','Hanna','Zuzanna','Maja','Pola','Maria','Oliwia',
			       'Zuzanna','Julia','Laura','Emilia','Zofia','Hanna','Maja','Oliwia','Alicja','Lena',
			       'Hanna','Julia','Zuzanna','Zofia','Maja','Laura','Emilia','Alicja','Lena','Oliwia',
			       'Zuzanna','Laura','Julia','Hanna','Maja','Zofia','Oliwia','Lena','Emilia','Pola',
			       'Zuzanna','Laura','Zofia','Julia','Oliwia','Hanna','Aleksandra','Maja','Lena','Maria',
			       'Zuzanna','Zofia','Maja','Laura','Hanna','Oliwia','Pola','Julia','Maria','Lena',
			       'Zofia','Hanna','Maja','Zuzanna','Laura','Pola','Oliwia','Lena','Maria','Julia',
			       'Zofia','Maja','Laura','Pola','Hanna','Zuzanna','Julia','Oliwia','Lena','Maria',
			       'Hanna','Zofia','Maja','Zuzanna','Pola','Laura','Julia','Oliwia','Lena','Maria',
			       'Hanna','Zofia','Zuzanna','Laura','Maja','Alicja','Julia','Oliwia','Maria','Lena',
			       'Hanna','Zuzanna','Zofia','Maja','Julia','Laura','Emilia','Oliwia','Alicja','Lena',
			       'Hanna','Zofia','Julia','Zuzanna','Laura','Oliwia','Maja','Alicja','Lena','Liliana'],
		       'Liczba imion':[419,408,405,343,341,317,297,295,284,268,
				       305,284,283,263,231,228,223,221,219,192,
				       286,258,258,254,243,241,220,215,197,178,
				       129,129,124,116,113,111,106,99,93,87,
				       996,871,858,833,795,781,693,685,684,676,
				       596,591,560,533,527,517,503,475,458,404,
				       141,130,130,125,112,103,101,83,82,80,
				       351,312,306,287,283,282,269,266,244,214,
				       193,186,175,167,164,150,143,142,142,133, 
				       385,385,361,314,302,279,270,262,232,227,
				       222,213,204,180,175,171,151,150,150,146,
				       588,485,472,458,452,446,439,397,383,376,
				       244,243,212,211,208,196,167,160,159,152,
				       372,366,365,325,313,300,298,288,256,252,
				       637,626,558,550,533,520,514,494,486,397,
				      175,171,163,159,147,143,140,125,117,115]}
			  
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

       
			   
    if wybrany == "2022":     
        col1.plotly_chart(fig)
        col2.plotly_chart(px.bar(x=DF_2022_z[DF_2020_z['Województwo']==mies]['Liczba imion'][::-1],y=DF_2022_z[DF_2022_z['Województwo']==mies]['Imię'][::-1],
			         orientation='h',text=DF_2022_z[DF_2022_z['Województwo']==mies]['Liczba imion'][::-1],color=["rgb(255,0,205)"]*10,
			         color_discrete_map="identity",
			         title='Top 10 imion żeńskich').update_xaxes(title_text='Liczba imion').update_yaxes(title_text='Imię'
				    ).update_layout(plot_bgcolor='white',title_x=0.5,height=600))
        
        col1.plotly_chart(fig1)
        col2.plotly_chart(px.bar(x=DF_2022_m[DF_2022_m['Województwo']==mies]['Liczba imion'][::-1],y=DF_2022_m[DF_2022_m['Województwo']==mies]['Imię'][::-1],
			     orientation='h',text=DF_2022_m[DF_2020_m['Województwo']==mies]['Liczba imion'][::-1],color=["rgb(0,70,180)"]*10,
			     color_discrete_map="identity",
			     title='Top 10 imion męskich').update_xaxes(title_text='Liczba imion').update_yaxes(title_text='Imię'
				).update_layout(plot_bgcolor='white',title_x=0.5,height=600))
			   
   
			   
    if wybrany == "2021":
       
        col1.plotly_chart(fig)
        col2.plotly_chart(px.bar(x=DF[DF['Województwo']==mies]['Liczba imion'][::-1],y=DF[DF['Województwo']==mies]['Imię'][::-1],
			         orientation='h',text=DF[DF['Województwo']==mies]['Liczba imion'][::-1],color=["rgb(255,0,205)"]*10,
			         color_discrete_map="identity",
			         title='Top 10 imion żeńskich').update_xaxes(title_text='Liczba imion').update_yaxes(title_text='Imię'
				    ).update_layout(plot_bgcolor='white',title_x=0.5,height=600))
     
        col1.plotly_chart(fig1)
        col2.plotly_chart(px.bar(x=DF_c[DF_c['Województwo']==mies]['Liczba imion'][::-1],y=DF_c[DF_c['Województwo']==mies]['Imię'][::-1],
			     orientation='h',text=DF_c[DF_c['Województwo']==mies]['Liczba imion'][::-1],color=["rgb(0,70,180)"]*10,
			     color_discrete_map="identity",
			     title='Top 10 imion męskich').update_xaxes(title_text='Liczba imion').update_yaxes(title_text='Imię'
				).update_layout(plot_bgcolor='white',title_x=0.5,height=600))
	
    if wybrany == "2020":
        
        col1.plotly_chart(fig)
        col2.plotly_chart(px.bar(x=DF_2020_z[DF_2020_z['Województwo']==mies]['Liczba imion'][::-1],y=DF_2020_z[DF_2020_z['Województwo']==mies]['Imię'][::-1],
			         orientation='h',text=DF_2020_z[DF_2020_z['Województwo']==mies]['Liczba imion'][::-1],color=["rgb(255,0,205)"]*10,
			         color_discrete_map="identity",
			         title='Top 10 imion żeńskich').update_xaxes(title_text='Liczba imion').update_yaxes(title_text='Imię'
				    ).update_layout(plot_bgcolor='white',title_x=0.5,height=600))
        
        col1.plotly_chart(fig1)
        col2.plotly_chart(px.bar(x=DF_2020_m[DF_2020_m['Województwo']==mies]['Liczba imion'][::-1],y=DF_2020_m[DF_2020_m['Województwo']==mies]['Imię'][::-1],
			     orientation='h',text=DF_2020_m[DF_2020_m['Województwo']==mies]['Liczba imion'][::-1],color=["rgb(0,70,180)"]*10,
			     color_discrete_map="identity",
			     title='Top 10 imion męskich').update_xaxes(title_text='Liczba imion').update_yaxes(title_text='Imię'
				).update_layout(plot_bgcolor='white',title_x=0.5,height=600))
    if wybrany == "2019":
        
        col1.plotly_chart(fig)
        col2.plotly_chart(px.bar(x=DF_2019_z[DF_2019_z['Województwo']==mies]['Liczba imion'][::-1],y=DF_2019_z[DF_2019_z['Województwo']==mies]['Imię'][::-1],
			         orientation='h',text=DF_2019_z[DF_2019_z['Województwo']==mies]['Liczba imion'][::-1],color=["rgb(255,0,205)"]*10,
			         color_discrete_map="identity",
			         title='Top 10 imion żeńskich').update_xaxes(title_text='Liczba imion').update_yaxes(title_text='Imię'
				    ).update_layout(plot_bgcolor='white',title_x=0.5,height=600))
      
        col1.plotly_chart(fig1)
        col2.plotly_chart(px.bar(x=DF_2019_m[DF_2019_m['Województwo']==mies]['Liczba imion'][::-1],y=DF_2019_m[DF_2019_m['Województwo']==mies]['Imię'][::-1],
			     orientation='h',text=DF_2019_m[DF_2019_m['Województwo']==mies]['Liczba imion'][::-1],color=["rgb(0,70,180)"]*10,
			     color_discrete_map="identity",
			     title='Top 10 imion męskich').update_xaxes(title_text='Liczba imion').update_yaxes(title_text='Imię'
				).update_layout(plot_bgcolor='white',title_x=0.5,height=600))
	
    

    
   #ANALIZA KORESPONDENCJI
   
if sekcja == 'Analiza korespondencji':
    new_title = '<b style="color:rgb(0, 80, 170); font-size: 62px;">Imiona nadawane dzieciom w Polsce - analiza</p>'
    st.markdown(new_title, unsafe_allow_html=True)
    st.markdown('---')
    st.title('Analiza korespondencji')
    st.subheader('Analizę korespondencji wykonano w oprogramowaniu PS IMAGO PRO 28 opartym o silnik analityczny IBM SPSS Statistics 28.')
    st.subheader('Poniższe wykresy są proste do interpretacji - obiekty położone blisko siebie są podobne, obiekty położone daleko od siebie są od siebie różne.')
    st.subheader('Aby wykres był bardziej czytelny, zamiast nazw województw widzimy liczby odpowiadające indentyfikatorom poszczególnego terytorium z ' +
		 'Wykazu identyfikatorów i nazw jednostek podziału terytorialnego kraju. Wyjaśnienie przedstawia niżej umieszczona tabelka: ')

    st.image('imionaa/PII/tabelka.png')

    roczek_opcje=["2019","2020","2021"][::-1]
    roczek_wybrany = st.selectbox("Wybierz rok:", roczek_opcje)
    if roczek_wybrany == "2019":
        st.subheader("Analiza korespondencji najczęściej nadawanych imion męskich (TOP 10 Z każdego województwa) i województw")
        st.write("Skumulowana proporcja bezwładności dla 2 wymiarów wynosi 0.459")
        st.image('imionaa/PII/chl2019.png', width=1000)
        st.subheader("Analiza korespondencji najczęściej nadawanych imion żeńskich (TOP 10 Z każdego województwa) i województw")
        st.write("Skumulowana proporcja bezwładności dla 2 wymiarów wynosi 0.464")
        st.image('imionaa/PII/dz2019.png', width=1000)
    if roczek_wybrany == "2020":
        st.subheader("Analiza korespondencji najczęściej nadawanych imion męskich (TOP 10 Z każdego województwa) i województw")
        st.write("Skumulowana proporcja bezwładności dla 2 wymiarów wynosi 0.402")
        st.image('imionaa/PII/chl2020.png', width=1000)
        st.subheader("Analiza korespondencji najczęściej nadawanych imion żeńskich (TOP 10 Z każdego województwa) i województw")
        st.write("Skumulowana proporcja bezwładności dla 2 wymiarów wynosi 0.447")
        st.image('imionaa/PII/dz2020.png', width=1000)
    if roczek_wybrany == "2021":
        st.subheader("Analiza korespondencji najczęściej nadawanych imion męskich (TOP 10 Z każdego województwa) i województw")
        st.write("Skumulowana proporcja bezwładności dla 2 wymiarów wynosi 0.511")
        st.image('imionaa/PII/ch2021.png', width=1000)
        st.subheader("Analiza korespondencji najczęściej nadawanych imion żeńskich (TOP 10 Z każdego województwa) i województw")
        st.write("Skumulowana proporcja bezwładności dla 2 wymiarów wynosi 0.654")
        st.image('imionaa/PII/dz2021.png', width=1000)

	
   
    

    
    
    
st.balloons()
    
        


        
  
        



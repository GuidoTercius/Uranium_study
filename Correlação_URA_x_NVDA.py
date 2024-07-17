'''
Contexto:
Tese de Urânio que consiste em aproveitar da assimetria de oferta e demanda. 
No meio da realização da tese (comprado em urânio), aparece uma variável que não era levada em conta:
IA. Com intuito de mitigar a tese a um possível risco de expectativas/realidade com as empresas de IA impactando na demanda enérgica. 
Ideia hedge estratégico as IA de forma que evite exposição short IA constante.

Cálculos e estudos 
1- Correlação empresas de IA com empresas do mercado de urânio. Exemplo simples: URA x NVDIA 
Feito, conclusão:
A correlação entre ambos não é muito alta, talvez a ideia não faça sentido.. em outras palvaras a industria de energia nuclear não é tão sensível a IA/chips, testar com XLK em vez de NVDA

2- beta entre os ativos 
3- tempo de entrada. Exemplo simples: pós alta de 15% do valor da NVDIA em 1 a 5 dias

Execução
1- Ao apitar o tempo de entrada (3° estudo) entrar short em NVDA com tamanho proporcional ao beta com URA. mitigando perdas de realização.

'''

from matplotlib import pyplot as plt 
from matplotlib import dates as mpl_date

plt.style.use('Solarize_Light2') # escolher estilo de plot # 'Solarize_Light2' , 'bmh' , dark_background 
from io import StringIO
import yfinance as yf
import datetime as dt
import seaborn as sns
import pandas as pd
import requests
import numpy as np
import sys

'/Users/GuidoImpactus/Documents/GitHub/Risk-in-Class/Guido_risk_in_Class.py'

#Definir os ativos

ativos  = ['URA', 'NVDA','NLR','SPY']

# Definir começo e fim

def correlation(ativo1='URA' , ativo2 = 'NVDA', começo = dt.datetime.today() - dt.timedelta(360*21), fim =dt.datetime.today() ):
    ndc_retroativos = 360*21 #numero de dias corridos retroativos para baixar a serie historica

    começo = dt.datetime.today() - dt.timedelta(ndc_retroativos)

    fim = dt.datetime.today()
    ativos = [ativo1 , ativo2]
    # Importar historico dos ativos

    historico_preços = yf.download(tickers= ativos , start  = começo ,end = fim)['Adj Close'].dropna()

    #  Variação em dias

    dias_var = 1
    janela_movel=14


    h_c = (historico_preços/historico_preços.shift(dias_var)-1).dropna()

    # Correlação

    # correlação = h_c.corr() # Correlação Histórica
    c_UxN = h_c[ativo1].rolling(janela_movel).corr(h_c[ativo2]) # Correlação Movel
    return c_UxN

def chartlayers(Largurax = 3 ,Alturay = 1 , tamanhox = 16 , tamanhoy = 9 , dataframcomcorrel = np.nan, a1 = 'URA',a2 = 'NVDA',maxy = 1,miny = -1,arquivoname = ' '
          , Titulo = ''):

# Criar subplots
    fig, axs = plt.subplots(Largurax, Alturay, figsize=(tamanhox, tamanhoy))

    # Primeiro período: Desde o início até 2015
    axs[0].plot(dataframcomcorrel[dataframcomcorrel.index <= '2015-12-31'])
    axs[0].axhline(0, color='red', linestyle='--', linewidth=1)
    axs[0].set_title(Titulo)
    axs[0].set_ylim(miny, maxy)
    axs[0].legend()
    # axs[0].set_xlabel('Date')
    # axs[0].set_ylabel('Rolling Correlation')

    # Segundo período: 2016 a 2019
    axs[1].plot(dataframcomcorrel[(dataframcomcorrel.index  >= '2016-01-01') & (dataframcomcorrel.index <= '2019-12-31')])
    axs[1].axhline(0, color='red', linestyle='--', linewidth=1)
    axs[1].set_title(Titulo)
    axs[1].set_ylim(miny, maxy)
    axs[1].legend()    
    # axs[1].set_xlabel('Date')
    # axs[1].set_ylabel('Rolling Correlation')

    # Terceiro período: 2019 até o presente
    axs[2].legend()    
    axs[2].axhline(0, color='red', linestyle='--', linewidth=1)
    axs[2].plot(dataframcomcorrel[dataframcomcorrel.index >= '2020-01-01'])
    axs[2].set_title(Titulo)
    axs[2].set_ylim(miny, maxy)
    # axs[2].set_xlabel('Date')
    # axs[2].set_ylabel('Rolling Correlation')

    plt.tight_layout()
    if arquivoname == " ":
        pass
    else:   
        plt.savefig(arquivoname)
    plt.show()

def chart(dataframcomcorrel = np.nan, a1 = 'URA',a2 = 'NVDA',maxy = 1,miny = -1,arquivoname = ' ', Titulo = ''):
    

    dataframcomcorrel.plot()
    plt.axhline(0, color='red', linestyle='--', linewidth=1)
    plt.title(Titulo)
    plt.ylim(miny, maxy)
    plt.legend()
    plt.xlabel('Date')
    plt.ylabel('Rolling Correlation')

    plt.tight_layout()
    if arquivoname == ' ':
        pass
    else:   
        plt.savefig(arquivoname)
    plt.show()

def retorno(ativos = [''], começo = dt.datetime.today() - dt.timedelta(360*21), fim =dt.datetime.today(), daydiff=1):
    ndc_retroativos = 360*21 #numero de dias corridos retroativos para baixar a serie historica


    # Importar historico dos ativos

    historico_preços = yf.download(tickers= ativos , start  = começo ,end = fim)['Adj Close'].dropna()

    #  Variação em dias

    dias_var = daydiff

    # h_c = (historico_preços/historico_preços.shift(dias_var)-1).dropna()
    h_c = (historico_preços/historico_preços.iloc[0]-1).dropna()  
    print(h_c)      
    return h_c

def getcdi():
    url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=csv"
    response = requests.get(url,)

    data = StringIO(response.text)

    cdi = pd.read_csv(data, sep=';')  
    cdi['data'] = pd.to_datetime(cdi['data'],format='%d/%m/%Y')
    cdi['valor'] = (pd.to_numeric(cdi['valor'].str.replace(",", "."), errors='coerce')/100+1)**252-1
    return cdi

### Retornos

# chart(dataframcomcorrel = retorno(ativos=['URA'],daydiff=1, começo = '2024-06-01', fim = '2024-06-30')
#       , a1 = 'URA',a2 = 'NVDA',maxy = 1,miny = -1,arquivoname= f' '
#        ,Titulo='URAxNVDA Retornos')
chart(dataframcomcorrel = retorno(ativos=['URA','NVDA','NXE'],daydiff=1, começo = '2024-06-01', fim = '2024-06-30')
      , a1 = 'URA',a2 = 'NVDA',maxy = 0.2,miny = -0.1,arquivoname= f' '
       ,Titulo='URA Retornos Mês de Junho')

## Correlação em janelas

# chartlayers(Largurax = 3 ,Alturay = 1 , tamanhox = 16 , tamanhoy = 9 , 
#       dataframcomcorrel = correlation(ativo1='URA' , ativo2 = 'NVDA', começo = dt.datetime.today() - dt.timedelta(360*21), fim =dt.datetime.today() )
#       , a1 = 'URA',a2 = 'NVDA',maxy = 1,miny = -1,arquivoname= f' ', Titulo= 'URAxNVDA Correlação')

### Correlação Historica Heatmap

# cr = retorno(ativos = ['URA','XLK','NVDA','NLR']).corr()
# sns.heatmap(cr ,annot=True)
# plt.show()

# Média das Correlações### Média das correlções em janelas

# chartlayers(Largurax = 3 ,Alturay = 1 , tamanhox = 16 , tamanhoy = 9 , 
# dataframcomcorrel = correlation(ativo1='URA' , ativo2 = 'NVDA', começo = dt.datetime.today() - dt.timedelta(360*21), fim =dt.datetime.today() ).rolling(14).mean(),
# a1 = 'URA',a2 = 'NVDA',maxy = 1,miny = -1,arquivoname= f'URAxNVDA_correlaçãomédia',Titulo = 'URAxNVDA Correlação média')

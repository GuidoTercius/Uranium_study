'''
Contexto:
Tese de Urânio que consiste em aproveitar da assimetria de oferta e demanda. 
No meio da realização da tese (comprado em urânio), aparece uma variável que não era levada em conta:
IA. Com intuito de mitigar a tese a um possível risco de expectativas/realidade com as empresas de IA impactando na demanda enérgica. 
Ideia hedge estratégico as IA de forma que evite exposição short IA constante.

Cálculos e estudos 
1- Correlação empresas de IA com empresas do mercado de urânio. Exemplo simples: URA x NVDIA 
2- beta entre os ativos 
3- tempo de entrada. Exemplo: pós alta de 15% do valor da NVDIA em 1 a 5 dias

Execução
1- Ao apitar o tempo de entrada (3° estudo) entrar short em NVDA com tamanho proporcional ao beta com URA. mitigando perdas de realização.

'''

from matplotlib import pyplot as plt 
from matplotlib import dates as mpl_date

plt.style.use('Solarize_Light2') # escolher estilo de gráfico # 'Solarize_Light2' , 'bmh' , dark_background 

from io import StringIO
import yfinance as yf
import datetime as dt
import seaborn as sns
import pandas as pd
import requests
import numpy as np
import sys

# Função para puxar a correlação
def rolling_correlation(ativo1='URA' , ativo2 = 'NVDA', começo = dt.datetime.today() - dt.timedelta(360*21), fim =dt.datetime.today(),dias_var = 1,janela_movel = 14 ):
    
    # ndc_retroativos = 360*21 #numero de dias corridos retroativos para baixar a serie historica
    # começo = dt.datetime.today() - dt.timedelta(ndc_retroativos)
    # fim = dt.datetime.today()
    ativos = [ativo1 , ativo2]
    
    # # Importar historico dos ativos

    historico_preços = yf.download(tickers= ativos , start  = começo ,end = fim)['Adj Close'].dropna()

    h_c = (historico_preços/historico_preços.shift(dias_var)-1).dropna() ### Retorno diario
    CM = h_c[ativo1].rolling(janela_movel).corr(h_c[ativo2]) # Correlação Movel
    return CM

def chartlayers(Largurax = 3 ,Alturay = 1 , tamanhox = 16 , tamanhoy = 9 , dataframcomcorrel = np.nan, maxy = 1,miny = -1,arquivoname = ' '
          , Titulo = ''):

# Criar subplots
    fig, axs = plt.subplots(Largurax, Alturay, figsize=(tamanhox, tamanhoy))

    # Primeiro período: Desde o início até 2015
    axs[0].plot(dataframcomcorrel[dataframcomcorrel.index <= '2015-12-31'],label=dataframcomcorrel.columns)
    axs[0].axhline(0, color='black', linestyle='--', linewidth=1)
    axs[0].set_title(Titulo)
    axs[0].set_ylim(miny, maxy)
    axs[0].legend()
    # axs[0].set_xlabel('Date')
    # axs[0].set_ylabel('Rolling Correlation')

    # Segundo período: 2016 a 2019
    axs[1].plot(dataframcomcorrel[(dataframcomcorrel.index  >= '2016-01-01') & (dataframcomcorrel.index <= '2019-12-31')],label=dataframcomcorrel.columns)
    axs[1].axhline(0, color='black', linestyle='--', linewidth=1)
    # axs[1].set_title(Titulo)
    axs[1].set_ylim(miny, maxy)
    axs[1].legend()    
    # axs[1].set_xlabel('Date')
    # axs[1].set_ylabel('Rolling Correlation')

    # Terceiro período: 2019 até o presente

    axs[2].plot(dataframcomcorrel[dataframcomcorrel.index >= '2020-01-01'],label=dataframcomcorrel.columns)
    axs[2].legend()    
    axs[2].axhline(0, color='black', linestyle='--', linewidth=1)    
    # axs[2].set_title(Titulo)
    axs[2].set_ylim(miny, maxy)
    # axs[2].set_xlabel('Date')
    # axs[2].set_ylabel('Rolling Correlation')

    plt.tight_layout()
    if arquivoname == " ":
        pass
    else:   
        plt.savefig(arquivoname)
    plt.show()

def chart(dataframcomcorrel = np.nan, maxy = 1,miny = -1,arquivoname = ' ', Titulo = ''):
    

    dataframcomcorrel.plot()
    plt.axhline(0, color='black', linestyle='--', linewidth=1)
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

def retorno(ativos = [''], começo = dt.datetime.today() - dt.timedelta(360*21), fim =dt.datetime.today(), dias_var=1,tipo = 'diario'):
    # Importar historico dos ativos

    historico_preços = yf.download(tickers= ativos , start  = começo ,end = fim)['Adj Close'].dropna()

    if tipo == 'diario':
        h_c = (historico_preços/historico_preços.shift(dias_var)-1).dropna()
    elif tipo == 'acumulado':
        h_c = (historico_preços/historico_preços.iloc[0]-1).dropna()  
    else:
        f'Incluir tipo de retrono ""{tipo}""'        
    # print(h_c)      
    return h_c

def getcdi():
    url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=csv"
    response = requests.get(url,)

    data = StringIO(response.text)

    cdi = pd.read_csv(data, sep=';')  
    cdi['data'] = pd.to_datetime(cdi['data'],format='%d/%m/%Y')
    cdi['valor'] = (pd.to_numeric(cdi['valor'].str.replace(",", "."), errors='coerce')/100+1)**252-1
    cdi = cdi.rename(columns={'data':'Date','valor':'CDI'}).reset_index(drop=True).set_index('Date')
    return cdi

def Beta(df= np.nan,ativo1='',ativo2=''):
    beta_result =(df[ativo1].cov(df[ativo2]))/df[ativo2].var()
    return beta_result



############################################################ EXERCICIO 1 ############################################################
############################################################  CORRELAÇÃO ############################################################
'''Correlação em janelas'''

correlation_roll = pd.DataFrame() ### Criando DF
list_correl = ['NVDA','ARKG' , 'ROBO' , 'AIQ', 'IGV','XLK'] ### Lista dos ativos para analisar correlção contra 'URA' ; Robo Global Robotics and Automation Index ETF (ROBO) , Global X Artificial Intelligence & Technology ETF (AIQ) ; iShares Expanded Tech-Software Sector ETF (IGV)

for ativo in list_correl: ### Criando Looping que pega cada ativo da lista e calcula a correlação móvel com a função criada anteriormente
    correlation_roll[f'URA_{ativo}'] = rolling_correlation(ativo1='URA' , ativo2 = ativo, começo = dt.datetime.today() - dt.timedelta(360*24), fim =dt.datetime.today(),dias_var=1,janela_movel=50)

chartlayers(Largurax = 3 ,Alturay = 1 , tamanhox = 16 , tamanhoy = 9 , 
      dataframcomcorrel = correlation_roll,
       maxy = 1,miny = -1,arquivoname= f'Correlação em Janelas móveis', Titulo= f'URAxIA Correlação (Janela móvel de 50 dias)')

'''Correlação Historica Heatmap'''

list_correl2 = ['NLR','URA','ARKG' , 'ROBO' , 'AIQ', 'IGV','XLK','NVDA'] 
cr = retorno(ativos = list_correl2,         tipo = 'diario').corr()
sns.heatmap(cr ,cmap="Reds",annot=True) #Pastel1 & 2 RdGy Greys
plt.title('Correlação Histórica')
plt.tight_layout()
plt.savefig('Correlação Histórica')
plt.show()

## NVDA mostrou mais momentos de descorrelção nas janelas móveis e no geral (0.39 NLR e 0.41), coerente por não ser um ETF
## Robo Global Robotics and Automation Index ETF (ROBO): Demonstrou a maior correlação entre todos (0.59 com URA e 0.64 com NLR) e menor período de descorrelação em 2017-2018 , 
## Global X Artificial Intelligence & Technology ETF (AIQ): Apresentou correlação levemente mais fraca do que a do ROBO (0.54), porém parece ser o ativo mais condizente para a estratégia por ser de IA
## URA X NLR o NLR se mostra mais correlacionado com os ativos de tech e IA que o URA ; Deve ocorrer pela distribuição mais concentrada em emrpesas de enrgia 

############################################################ Final do Exercicio 1 ############################################################

############################################################ EXERCICIO 2 ############################################################
############################################################    Beta     ############################################################

Betas = {}

### Retornos

list_retorno= ['URA','ARKG' , 'ROBO' , 'AIQ', 'IGV','XLK','NVDA'] 
returns = retorno(ativos= list_retorno,dias_var=1, começo = '2024-06-01', fim = dt.datetime.today() ,tipo='diario')

for ativo in list_retorno:
    Betas[f'{ativo}'] = Beta(df = returns,ativo1='URA',ativo2=ativo)

Betas = dict(sorted(Betas.items(), key=lambda item: item[1])) #ordenando
colunas = list(Betas.keys())                                  #eixo x 
valores = list(Betas.values())                                #eixo y

### Plotando

bars = plt.bar(colunas,valores)
plt.title('Beta URA x IA & Techs')
plt.tick_params(axis='x', colors='black')
plt.tick_params(axis='y', colors='black')
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), ha='center', va='bottom')
plt.tight_layout()
plt.savefig('Beta URA x IA & Techs')    

plt.show()

### Betas: URA tem sensibilidade muito próxima de 1 para os ETFs ROBO (1.16) e AIQ (0.97) apontando para uma similiaridade na grandeza de seus movimetnos. 
### Para os outros ETFs o URA tende a se mexer mais passivamente a eles, faz sentindo visto a volatilidade dos ativos de IA e Tech tem tido recentemente.

############################################################ Final do Exercicio 2 ############################################################

############################################################      EXERCICIO 3     ############################################################
############################################################    Time de entrada   ############################################################

list_retorno= ['URA','ARKG' , 'ROBO' , 'AIQ', 'IGV','XLK','NVDA'] 
returns = retorno(ativos= list_retorno,dias_var=5, começo = '2024-06-01', fim = dt.datetime.today() ,tipo='diario') #analisar os retornos a cada 5 dias

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

def chart(dataframcomcorrel = np.nan, maxy = 1,miny = -1,arquivoname = ' ', Titulo = '',linha=0,xlabeltext='Date',ylabeltext='Rolling Correlation',show=True):
    

    dataframcomcorrel.plot()
    plt.axhline(linha, color='black', linestyle='--', linewidth=1)
    plt.title(Titulo)
    plt.ylim(miny, maxy)
    plt.legend()
    plt.xlabel(xlabeltext)
    plt.ylabel(ylabeltext)

    plt.tight_layout()
    if arquivoname == ' ':
        pass
    else:   
        plt.savefig(arquivoname)
    if show == True:
        plt.show()
    else:
        pass        

def retorno(ativos = [''], começo = dt.datetime.today() - dt.timedelta(360*21), fim =dt.datetime.today(), dias_var=1,tipo = 'diario'):
    
    # Importar historico dos ativos
    historico_preços = yf.download(tickers= ativos , start  = começo ,end = fim)['Adj Close'].dropna()

    if tipo == 'diario':
        retorno = (historico_preços/historico_preços.shift(dias_var)-1).dropna()
    elif tipo == 'acumulado':
        retorno = (historico_preços/historico_preços.iloc[0]-1).dropna()  
    else:
        f'Incluir tipo de retrono ""{tipo}""'        
    # print(retorno)      
    return retorno

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

def backtest(ativomain = 'URA',ativohedge = 'XLK' ,beta=0.5,pontamain = 'C', pontahedge = 'V',exposição=1,stopgain = 0.05,stoploss=-0.03,começo = "2024-05-08 00:00:00", fim =dt.datetime.today(), dias_var=1,tipo = 'acumulado'):
    
    começo = pd.to_datetime(começo).strftime('%Y-%m-%d')
    fim = pd.to_datetime(fim).strftime('%Y-%m-%d')
    # Importar historico dos ativos
    historico_preços = yf.download(tickers= [ativomain,ativohedge] , start  = começo ,end = fim)['Adj Close'].dropna()


    if tipo == 'diario':
        retorno = (historico_preços/historico_preços.shift(dias_var)-1).dropna()
    elif tipo == 'acumulado':
        retorno = (historico_preços/historico_preços.iloc[0]-1).dropna()  
    else:
        f'Incluir tipo de retrono ""{tipo}""'        

    ### Definindo a ponta do Hedge
    if pontamain.upper() == 'C' or pontamain.upper() == 'COMPRA':
        pontamain = 1
    elif pontamain.upper() == 'V' or pontamain.upper() == 'VENDA':
        pontamain = -1        
    else:
        pontamain = 1
    if pontahedge.upper() == 'C' or pontahedge.upper() == 'COMPRA':
        pontahedge = 1
    elif pontahedge.upper() == 'V' or pontahedge.upper() == 'VENDA':
        pontahedge = -1        
    else:
        pontahedge = -1

    
    retorno[ativohedge] = retorno[ativohedge] * beta * pontahedge
    retorno[ativomain] = retorno[ativomain] * beta * pontamain
    retorno['Estratégia'] = (retorno[ativohedge]+retorno[ativomain])*exposição
    try:
        try:
            retorno[f'{ativohedge} trigger end'] = (retorno[ativohedge] >= stopgain)         
            retorno = (retorno[retorno.index < retorno[retorno[f'{ativohedge} trigger end']].index[0]])[[ativomain,ativohedge,'Estratégia']] ### retorno[(index < Data do primeiro True)]
        except :
            retorno[f'{ativohedge} trigger end'] = (retorno[ativohedge] <= stoploss)        
            retorno = (retorno[retorno.index < retorno[retorno[f'{ativohedge} trigger end']].index[0]])[[ativomain,ativohedge,'Estratégia']]
    except:
        retorno  
    
    return retorno

############################################################ EXERCICIO 1 ############################################################
############################################################  CORRELAÇÃO ############################################################
# '''Correlação em janelas'''

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

### Inputs importantes para o back teste

diasvar =1 ### retorno movel em quantas dias
começo = '2020-01-01' ### começo da busca por momentos de entrada
tiporetorno ='diario' ### Tipo de retorno ; na formula de retorno ele so aborda o retorno em janelas moveis se for diario

list_retorno = ['URA','ARKG' , 'ROBO' , 'AIQ', 'IGV','XLK','NVDA'] ### ativos no geral ; usado mais tarde para o Beta
list_flag = ['ROBO','AIQ','XLK'] ### ativos que irão disparar trigger do Hedge e serão usados como hedges

returns = retorno(ativos = list_retorno,dias_var = diasvar, começo = começo, fim = dt.datetime.today() ,tipo = tiporetorno)
flag = retorno(ativos = list_flag,dias_var = diasvar, começo = começo, fim = dt.datetime.today() ,tipo = tiporetorno) # retorno dos ativos triggers

flagtrigger =pd.DataFrame() ### DataFrame para os ativos/datas que serão triggados

for ativo in flag:
    flag[f'Trigger {ativo}'] = flag[ativo]>=0.05 ### Colunas pra trigar ponta de entrada do Hedge 

for name in flag.columns:
    if name.startswith('Trigger'):
        nametrigger = name.split(" ")[-1] # Nome das colunas original
        flagtrigger[f'{nametrigger}']=flag[f'{name}'] # nome dos ativos, mas com as flags de entrada nas linhas (True and False)
    else:
        pass
    
flagtrigger  = flagtrigger[flagtrigger.any(axis=1)]    # Filtrando os Trues das colunas triggers e pegando só as datas (index) ; usar futuramente para serem os pontos de entrada
datastrigger = {}
for ativo in list_flag:
    datastrigger[ativo] = list(flagtrigger[flagtrigger[ativo] == True].index) ### keys and values para triggar back test ; nome de um ativo corresponde a x datas

for chave in datastrigger: ### para ativo no dict de ativo: datas
    for valor in datastrigger[chave]: ### para datas de trigger do determinado ativo
        valor = pd.to_datetime(valor).strftime('%Y-%m-%d') ### formatando a data
        chart(backtest(ativomain = 'URA',ativohedge = chave ,
            beta= Beta(df = returns,ativo1='URA',ativo2=chave), ### usando o beta para ponderar a exposição ao ativo hedge
            pontamain = 'C', pontahedge = 'V',                  ### Ponta do Hedge
            exposição=1,stopgain=0.03,stoploss= -0.03 ,começo = valor, ### atenção para o stop gain e loss, eles que são os trigerres para sair da posição
            fim =dt.datetime.today(), tipo = 'acumulado'),
            maxy=0.035,miny=-0.035,linha=0,Titulo=f'Buy_URA x short_{chave}_{valor}',arquivoname=f'Buy_URA x short_{chave}_{valor}',show=False)

# chart(flag,maxy=0.25,miny=-0.1,linha=0.05,ylabeltext='Retorno a cada 5 dias',Titulo='Retorno em janela móvel de 5 dias') #plotando retornos acumulados de 5 dias    



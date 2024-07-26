import pandas as pd
import datetime as dt
from urllib import parse, request
from bs4 import BeautifulSoup
import sys
import matplotlib.pyplot as plt
plt.style.use('Solarize_Light2') ### Estilo do Gráfico

Source = request.urlopen(request.Request(url="https://www.cameco.com/invest/markets/uranium-price")).read()
u3o8 = pd.read_html(Source,decimal='.')[0]

u3o8 = u3o8.rename(columns={'Unnamed: 0':'Data', 'Uranium Spot Price':'Spot Price','Long-term Uranium Price':'Term Price'}).reset_index(drop=True).set_index('Data')

u3o8['Spread'] = u3o8['Spot Price']-u3o8['Term Price']

# print(u3o8.head(150))

# u3o8 = u3o8[u3o8.index>="2020-01-01"] ### Filtrando momento pos pandemia

u3o8.plot()
plt.title('Uranium Price (monthly)')
plt.legend()
plt.xlabel('Date')
plt.ylabel('Price (USD)')
plt.axhline(0, color='red', linestyle='--', linewidth=1)
plt.gcf().autofmt_xdate()
plt.tight_layout()
plt.savefig('U3O8_term_x_spot')
plt.show()


import pandas as pd
import json
from pandas import json_normalize
import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=UCO&interval=1min&apikey=XMBXF0SOTIPN8P3B'
# url = 'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=UCO&apikey=XMBXF0SOTIPN8P3B'
r = requests.get(url)
data = r.json()
dict = json.loads(data)
df = json_normalize(dict['technologies'])
# df2 = pd.read_json(jsonStr, orient ='index')
print(data)
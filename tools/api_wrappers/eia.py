import requests
import json
import pandas as pd

api_key = "JkhKVqmaPUA3DnaGCO3obVnLls0SshYbmhYnCPnk"
url = f'https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={api_key}&frequency=weekly&data[0]=value\
&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000'

r = requests.get(
    url=url
)

full_data = json.loads(r.content.decode('utf-8'))
data = pd.json_normalize(full_data['response']['data']).T
data = data.T
data = data.loc[data['area-name']=='U.S.']
data = data.loc[data['series']=='WCRSTUS1'][['period','value']]

print('')
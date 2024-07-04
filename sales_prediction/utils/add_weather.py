import requests
import json

key='8yP3ASnh3nWzg35DS8EWkpFIn8B2/G4usrZ4STZmvf1fptCKIws6eAZQrTddRNDlRvhH3LHpaupWUAGjBj8tew=='
url = 'http://apis.data.go.kr/1360000/MidFcstInfoService/getMidFcst'
params ={'serviceKey' : key, 'pageNo' : '1', 'numOfRows' : '10', 'dataType' : 'JSON', 'stnId' : '108', 'tmFc' : '202407041200' }

response = requests.get(url, params=params)
response.encoding='utf-8'
print(response.content)

# data=response.json()
# print(data)
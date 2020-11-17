import requests

URL = ''

response = requests.get(url= URL)
print(response.encoding)
a = response.text

with open('shit.py', 'w', encoding=response.encoding) as f:
    f.write(a)
import requests
from bs4 import BeautifulSoup
import json

url = "https://localfirstbank.com/article/budgeting-101-personal-budget-categories/"

r=requests.get(url)
soup= BeautifulSoup(r.text, 'html.parser')

ptag=soup.find_all('p')
utag= soup.find_all('ul')

d={}
ptag=ptag[9:24]
utag=utag[72:87]
for p,u in zip(ptag,utag):
    for li in u.find_all('li'):
        a,b=str(li.text),str(p.text)
        if "\xa0" in a:
            a=a.replace("\xa0"," ")
        if "\xa0" in b:
            b=b.replace("\xa0"," ")
        a=a.strip()
        b=b.strip()
        d[a]=b

with open("mapping.json", "w") as outfile:
    json.dump(d, outfile,indent=4)
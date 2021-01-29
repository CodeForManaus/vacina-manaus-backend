"""
    Code from https://towardsdatascience.com/how-to-web-scrape-with-python-in-4-minutes-bc49186a8460
"""

import requests
import urllib.request
import time
from bs4 import BeautifulSoup


url = 'https://semsa.manaus.am.gov.br/sala-de-situacao/novo-coronavirus/'

response = requests.get(url)

# Parse HTML and save to BeautifulSoup object¶
soup = BeautifulSoup(response.text, "html.parser")


for one_a_tag in soup.findAll('a'):
    link = one_a_tag['href']
    if "Vacinados" in link:
        urllib.request.urlretrieve(link, 'raw_db/' + link.split("/")[-1])

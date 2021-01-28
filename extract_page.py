"""
    Code from https://towardsdatascience.com/how-to-web-scrape-with-python-in-4-minutes-bc49186a8460
"""

# Import libraries
import requests
import urllib.request
import time
from bs4 import BeautifulSoup


# Set the URL you want to webscrape from
url = 'https://semsa.manaus.am.gov.br/sala-de-situacao/novo-coronavirus/'

# Connect to the URL
response = requests.get(url)

# Parse HTML and save to BeautifulSoup object¶
soup = BeautifulSoup(response.text, "html.parser")


# To download the whole data set, let's do a for loop through all a tags
line_count = 1 #variable to track what line you are on
for one_a_tag in soup.findAll('a'):  #'a' tags are for links
    link = one_a_tag['href']
    if "Vacinados" in link:
        urllib.request.urlretrieve(link, 'raw_db/newest_Vacinados.pdf')
    #add 1 for next line
    line_count +=1

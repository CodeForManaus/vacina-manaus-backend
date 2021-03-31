"""
    Code from https://towardsdatascience.com/how-to-web-scrape-with-python-in-4-minutes-bc49186a8460
"""

from datetime import datetime
from glob import glob
import hashlib
import hmac
import os
import sys
import urllib.request

from bs4 import BeautifulSoup
import pytz
import requests

from progress_download import ProgressDownload


class PdfDownloader:

    def __init__(self, url):
        self.url = url
        self.filename = None

    def __sha1file(self, filepath):
        sha1sum = hashlib.sha1()
        with open(filepath, "rb") as fd:
            for chunk in iter(lambda: fd.read(4096), b''):
                sha1sum.update(chunk)
        return sha1sum

    def __get_latest_file(self):
        files = glob('data/raw/*.pdf')
        return max(files, key=os.path.getctime)

    def download(self):
        response = requests.get(self.url)

        # Parse HTML and save to BeautifulSoup object¶
        soup = BeautifulSoup(response.text, "html.parser")

        amt = pytz.timezone('America/Manaus')
        now = datetime.now(amt)
        filename = ''
        filepath = ''
        for one_a_tag in soup.findAll('a'):
            link = one_a_tag['href']
            if "Vacinados" in link:
                filename = link.split("/")[-1]
                filepath = 'data/raw/' + filename
                latest_filepath = self.__get_latest_file()
                current_file_checksum = self.__sha1file(latest_filepath)

                if filepath == latest_filepath:
                    current_file_checksum = self.__sha1file(filepath)
                    timestamp = now.strftime('%Y%m%d%H%M')
                    basename, ext = filename.split(".")
                    filename = f'{basename}-{timestamp}.{ext}'
                    filepath = 'data/raw/' + filename

                urllib.request.urlretrieve(link, filepath, ProgressDownload())

                downloaded_file_checksum = self.__sha1file(filepath)
                if current_file_checksum and hmac.compare_digest(
                    downloaded_file_checksum.hexdigest(),
                        current_file_checksum.hexdigest()):
                    os.remove(filepath)
                    sys.exit('File already downloaded!')

        self.filename = filename
        today = now.strftime('%d/%m/%Y')
        fd = open('data/analyzed/last_update_date.csv', 'w+')
        fd.writelines(['last_update_date\n', today])
        fd.close()

        print(f'Download da lista {filepath} foi finalizado!')

    def get_filename(self):
        return self.filename


if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = 'https://semsa.manaus.am.gov.br/' \
              'sala-de-situacao/novo-coronavirus/lista-de-vacinados-covid-19/'
    pdfDownloader = PdfDownloader(url)
    pdfDownloader.download()

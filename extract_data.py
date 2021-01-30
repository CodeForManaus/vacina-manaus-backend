# coding: utf-8
import os
import sys


import json
import pdfplumber
from validate_docbr import CPF

from progressDownload import ProgressDownload

paths = os.listdir('raw_db')

# Add absolute path to get information about tha last modification to max method
_paths = list(map(lambda x: 'raw_db/{}'.format(x), paths))

filename = max(_paths, key=os.path.getctime).replace(
    'raw_db/', '').replace('.pdf', '')

input_path = "raw_db/{}.pdf".format(filename)

def getNewestFilename():
    paths = os.listdir('raw_db')

    # Add absolute path to get information about tha last modification to max method
    _paths = list(map(lambda x: 'raw_db/{}'.format(x), paths))

    return max(_paths, key=os.path.getctime)

class PdfExtractor:

    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.header = [
                        'full_name',
                        'cpf',
                        'vaccine_date',
                        'vaccination_site',
                        'priority_group',
                        'service_group',
                        'workplace',
                        'role'
                    ]

    def __formatCPF(self, cpf):
        if len(cpf) < 11:
            cpf = cpf.zfill(11)
        return '{}.{}.{}-{}'.format(cpf[:3], cpf[3:6], cpf[6:9], cpf[9:])

    def __extra_attribs(self, dictio_):
        cpf_validator = CPF()
        dictio_.update(
            {
                'area': dictio_['vaccination_site'].split('-', 1)[0].strip(),
                'vaccination_site': dictio_['vaccination_site'].split('-', 1)[1].strip(),
                'cpf': self.__formatCPF(dictio_['cpf'].replace('\'', '')),
                'valid_cpf': cpf_validator.validate(dictio_['cpf'].replace('\'', ''))
            }
        )

        return dictio_


    def __remove_line_breaks(self,arr):
        return list(map(lambda v: v.replace('\n', ''), arr))


    def __get_dict(self,header_, record_):
        if len(header_) != len(record_):
            # TODO: Specify exception

            raise Exception

        return {header_[i]: record_[i] for i in range(len(header_))}

    def process(self):
        i = 1
        data = []
        header = self.header
        output_file = open(self.output_path, 'w')
        pdf = pdfplumber.open(self.input_path)
        
        count = 1
        sizePages = len(pdf.pages)
        progressDownload = ProgressDownload()
        for page in range(len(pdf.pages)):
            table = pdf.pages[page].extract_table()

            if page == 0:
                if not header:
                    header = self.__remove_line_breaks(table.pop(0))
                else:
                    table.pop(0)

            for record in table:
                dictio = self.__get_dict(header, self.__remove_line_breaks(record))
                self.__extra_attribs(dictio)

                dictio['id'] = i

                data.append(dictio)

                i += 1
            progressDownload(count,1,sizePages)
            count +=1

        json.dump(data, output_file)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fileName = sys.argv[1]
    else:
        fileName = getNewestFilename()

    pdfExtractor = PdfExtractor(fileName, fileName.replace("raw_db","db").replace("pdf", "json"))
    pdfExtractor.process()

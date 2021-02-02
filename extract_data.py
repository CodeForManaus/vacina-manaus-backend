# coding: utf-8
import os
import sys

import json
import pdfplumber
from validate_docbr import CPF

from progress_download import ProgressDownload

paths = os.listdir('raw_db')

# Add absolute path to get information about tha last modification to max method
_paths = list(map(lambda x: 'raw_db/{}'.format(x), paths))

filename = max(_paths, key=os.path.getctime).replace(
    'raw_db/', '').replace('.pdf', '')

input_path = "raw_db/{}.pdf".format(filename)


def get_latest_filename():
    paths = os.listdir('raw_db')

    # Add absolute path to get information about tha last modification to max method
    _paths = list(map(lambda x: 'raw_db/{}'.format(x), paths))

    return max(_paths, key=os.path.getctime)


class PdfExtractor:

    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path

        self.raw_header_first_word = 'Nome Completo'

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

    def __find_header_index(self, table):
        for i in range(len(table)):
            if self.raw_header_first_word in table[i]:
                return i

        # TODO: Specify exception

        raise Exception

    @staticmethod
    def __format_cpf(cpf):
        if len(cpf) < 11:
            cpf = cpf.zfill(11)
        return '{}.{}.{}-{}'.format(cpf[:3], cpf[3:6], cpf[6:9], cpf[9:])

    def __extra_attribs(self, dictio_):
        cpf_validator = CPF()
        dictio_.update(
            {
                'area': dictio_['vaccination_site'].split('-', 1)[0].strip(),
                'vaccination_site': dictio_['vaccination_site'].split('-', 1)[1].strip(),
                'cpf': self.__format_cpf(dictio_['cpf'].replace('\'', '')),
                'valid_cpf': cpf_validator.validate(dictio_['cpf'].replace('\'', ''))
            }
        )

        return dictio_

    @staticmethod
    def __remove_line_breaks(arr):
        return list(map(lambda v: v.replace('\n', ''), arr))

    @staticmethod
    def __get_dict(header_, record_):
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
        size_pages = len(pdf.pages)
        progress_download = ProgressDownload()

        for page in range(len(pdf.pages)):
            table = pdf.pages[page].extract_table(
                table_settings={
                    "vertical_strategy": "explicit",
                    "horizontal_strategy": "lines",

                    # TODO: Automatically identify columns (even if they are not delimited)
                    "explicit_vertical_lines": [35, 210, 270, 315, 450, 520, 585, 660, 760],
                }
            )

            if page == 0:
                table = table[self.__find_header_index(table):]

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
            progress_download(count, 1, size_pages)
            count += 1

        json.dump(data, output_file)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        fileName = sys.argv[1]
    else:
        fileName = get_latest_filename()

    pdfExtractor = PdfExtractor(fileName, fileName.replace("raw_db", "db").replace("pdf", "json"))
    pdfExtractor.process()

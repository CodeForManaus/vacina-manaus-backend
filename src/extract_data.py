# coding: utf-8

from concurrent.futures import ThreadPoolExecutor
import copy
import csv
from datetime import datetime
import fnmatch
import gc
import os
import re
import sys

from decimal import Decimal

import pdfplumber

from column_finder import find_columns_positions
from validate_docbr import CPF

paths = os.listdir('data/raw')

# Add absolute path to get information about tha last modification to max method
_paths = list(map(lambda x: 'data/raw/{}'.format(x), paths))
filename = max(_paths, key=os.path.getctime).replace(
    'data/raw/', '').replace('.pdf', '')
input_path = "data/raw/{}.pdf".format(filename)

regex_str = r'([\d]{1,2})/([\d]{1,2})/([\d]{2,4})'
regex = re.compile(regex_str)


pdf_header = [
    'full_name',
    'cpf',
    'vaccine_date',
    'vaccination_site',
    'priority_group',
    'service_group',
    'workplace',
    'role'
]


def get_latest_filename():
    paths = os.listdir('data/raw')

    # Add absolute path to get information about tha last modification to max method
    _paths = list(map(lambda x: 'data/raw/{}'.format(x), paths))

    return max(_paths, key=os.path.getctime)


class PdfExtractor:

    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.raw_header_first_word = 'Nome Completo'

        chunk_list = fnmatch.filter(os.listdir('tmp/pdf'), '*.pdf')
        regex = re.compile('page-[0]*1.pdf')
        first_chunk = list(filter(regex.match, chunk_list))[0]

        self.__columns = find_columns_positions(f'tmp/pdf/{first_chunk}')
        # FIXME: Find the end column
        self.__columns.append(Decimal('763.599'))

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

    @staticmethod
    def __get_area_by_vaccination_site(vaccination_site):
        area = 'NÃO ESPECIFICADA'

        data = vaccination_site.split('-', 1)

        if len(data) == 2:
            area = data[0].strip()

        return area

    @staticmethod
    def __get_vaccination_site_name(vaccination_site):
        data = vaccination_site.split('-', 1)

        if len(data) == 2:
            vaccination_site = data[1].strip()

        return vaccination_site

    def __extra_attribs(self, dictio_):
        cpf_validator = CPF()

        dictio_.update(
            {
                'area': self.__get_area_by_vaccination_site(dictio_['vaccination_site']),
                'vaccination_site': self.__get_vaccination_site_name(dictio_['vaccination_site']),
                'cpf': self.__format_cpf(dictio_['cpf'].replace('\'', '')),
                'valid_cpf': cpf_validator.validate(dictio_['cpf'].replace('\'', ''))
            }
        )

        return dictio_

    @staticmethod
    def __row_blank(data):
        for key in pdf_header:
            if data[key].strip():
                return False

        return True

    @staticmethod
    def __try_fix_date(date_str):
        match = regex.match(date_str)
        if match:
            day, month, year = match.groups()
            if len(year) != 4:
                year = '2021'
            return f'{day}/{month}/{year}'

        return date_str

    @staticmethod
    def __validate_date(date_str):
        try:
            datetime.strptime(date_str, '%d/%m/%Y')
        except ValueError:
            return False

        return True

    @staticmethod
    def __remove_line_breaks(arr):
        return list(map(lambda v: v.replace('\n', ''), arr))

    @staticmethod
    def __get_dict(header_, record_):
        if len(header_) != len(record_):
            # TODO: Specify exception

            raise Exception

        return {header_[i]: record_[i] for i in range(len(header_))}

    def __extract_chunk_data(self, chunk):
        print(f'Processing chunk {chunk}...')
        csv_chunk_filepath = 'tmp/csv/{}'.format(chunk.replace('pdf', 'csv'))
        fd = open(csv_chunk_filepath, 'w')

        headers_csv = [
            'full_name',
            'cpf',
            'valid_cpf',
            'vaccine_date',
            'vaccination_site',
            'priority_group',
            'service_group',
            'workplace',
            'role',
            'area'
        ]
        writer = csv.DictWriter(fd, fieldnames=headers_csv)
        if chunk.endswith('-1.pdf'):
            writer.writeheader()

        pdf_chunk_filepath = f'tmp/pdf/{chunk}'
        with pdfplumber.open(pdf_chunk_filepath) as pdf:
            for page in range(len(pdf.pages)):
                table = pdf.pages[page].extract_table(
                    table_settings={
                        "vertical_strategy": "explicit",
                        "horizontal_strategy": "lines",
                        "explicit_vertical_lines": self.__columns,
                    }
                )

                header = copy.deepcopy(pdf_header)
                if chunk.endswith('-1.pdf') and page == 0:
                    table = table[self.__find_header_index(table):]

                    if not header:
                        header = self.__remove_line_breaks(table.pop(0))
                    else:
                        table.pop(0)

                for record in table:
                    dictio = self.__get_dict(header, self.__remove_line_breaks(record))
                    if self.__row_blank(dictio):
                        continue
                    self.__extra_attribs(dictio)
                    if not self.__validate_date(dictio['vaccine_date']):
                        dictio['vaccine_date'] = self.__try_fix_date(dictio['vaccine_date'])
                    writer.writerow(dictio)

                pdf.pages[page].flush_cache()

            gc.collect()

        print(f'Saving result chunk {csv_chunk_filepath}...')
        fd.close()

    def process(self):
        print('Processing file...')

        chunks = fnmatch.filter(os.listdir('tmp/pdf'), '*.pdf')

        os.makedirs('tmp/csv', exist_ok=True)

        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            executor.map(
                self.__extract_chunk_data,
                chunks
            )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        fileName = sys.argv[1]
    else:
        fileName = get_latest_filename()

    pdfExtractor = PdfExtractor(fileName, fileName.replace("data/raw", "data/cleaned").replace("pdf", "csv"))
    pdfExtractor.process()

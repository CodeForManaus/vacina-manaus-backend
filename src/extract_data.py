# coding: utf-8
import os
import sys

import json
from decimal import Decimal

import pdfplumber
from validate_docbr import CPF

from progress_download import ProgressDownload

paths = os.listdir('data/raw')

# Add absolute path to get information about tha last modification to max method
_paths = list(map(lambda x: 'data/raw/{}'.format(x), paths))

filename = max(_paths, key=os.path.getctime).replace(
    'data/raw/', '').replace('.pdf', '')

input_path = "data/raw/{}.pdf".format(filename)


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

        self.__open_file()

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

    def __open_file(self):

        print('Opening file...')

        self.pdf = pdfplumber.open(self.input_path)
        self.columns = [
            Decimal('38.904'),
            Decimal('210.530'),
            Decimal('273.050'),
            Decimal('315.890'),
            Decimal('455.110'),
            Decimal('520.900'),
            Decimal('586.300'),
            Decimal('662.020'),
            Decimal('763.599')
        ]

    def __find_columns(self):
        candidate_cols = {}
        num_cols_to_find = len(self.header)+1
        allowed_minimum_distance_between_cols = 25  # pixels

        progress_download = ProgressDownload()

        pages = len(self.pdf.pages)

        print('Analyzing file to find columns...')

        for page in range(pages):
            progress_download(page + 1, 1, pages)

            table = self.pdf.pages[page].find_tables(
                {
                    "vertical_strategy": "text",
                    "horizontal_strategy": "lines",
                    "keep_blank_chars": True,
                    "text_tolerance": 1,
                }
            )[0]

            # Gets all left/right cell delimiters as a sorted tuple of unique delimiters
            cols = tuple(
                sorted(set([cell[0] for cell in table.cells])) +
                sorted(
                    set([cell[2] for cell in table.cells]) - set([cell[0] for cell in table.cells])
                )
            )

            if len(cols) != num_cols_to_find:
                continue

            minimum_distance_between_cols = min([cols[i] - cols[i-1] for i in range(1, len(cols))])

            if minimum_distance_between_cols < allowed_minimum_distance_between_cols:
                continue

            if cols in candidate_cols.keys():
                candidate_cols[cols] += 1
            else:
                candidate_cols[cols] = 1

        # Sort candidate columns by number of appearances
        candidate_cols = dict(sorted(candidate_cols.items(), key=lambda value: value[1], reverse=True))

        elected = list(next(iter(candidate_cols)))

        print('Elected: {}'.format(elected))

        # Returns the one that appeared most times
        return elected

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

        progress_download = ProgressDownload()

        pages = len(self.pdf.pages)

        print('Processing file...')

        for page in range(pages):
            table = self.pdf.pages[page].extract_table(
                table_settings={
                    "vertical_strategy": "explicit",
                    "horizontal_strategy": "lines",
                    "explicit_vertical_lines": self.columns,
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

            progress_download(page+1, 1, pages)

        print('Saving output file...')

        json.dump(data, output_file)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        fileName = sys.argv[1]
    else:
        fileName = get_latest_filename()

    pdfExtractor = PdfExtractor(fileName, fileName.replace("data/raw", "data/cleaned").replace("pdf", "json"))
    pdfExtractor.process()

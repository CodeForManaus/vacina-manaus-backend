# coding: utf-8

import json
import pdfplumber
from validate_docbr import CPF
 
input = "raw_db/007_Vacinados_2021_01_23_17_17_00.pdf"
output = "db/007_Vacinados_2021_01_23_17_17_00.json"

pdf = pdfplumber.open(input)
output_file = open(output, 'w')
cpf_validator = CPF()

header = [
    'full_name',
    'cpf',
    'vaccine_date',
    'vaccination_site',
    'priority_group',
    'service_group',
    'workplace',
    'role'
]

data = []


def extra_attribs(dictio_):
    dictio_.update(
        {
            'area': dictio['vaccination_site'].split('-', 1)[0].strip(),
            'vaccination_site': dictio['vaccination_site'].split('-', 1)[1].strip(),
            'cpf': dictio['cpf'].replace('\'', ''),
            'valid_cpf': cpf_validator.validate(dictio['cpf'].replace('\'', ''))
        }
    )

    return dictio_


def remove_line_breaks(arr):
    return list(map(lambda v: v.replace('\n', ''), arr))


def get_dict(header_, record_):
    if len(header_) != len(record_):
        # TODO: Specify exception

        raise Exception

    return {header_[i]: record_[i] for i in range(len(header_))}


i = 1

for page in range(len(pdf.pages)):
    table = pdf.pages[page].extract_table()

    if page == 0:
        if not header:
            header = remove_line_breaks(table.pop(0))
        else:
            table.pop(0)

    for record in table:
        dictio = get_dict(header, remove_line_breaks(record))
        extra_attribs(dictio)

        dictio['id'] = i

        data.append(dictio)

        i += 1

json.dump(data, output_file)

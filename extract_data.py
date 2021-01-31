# coding: utf-8
import os

import json
import pdfplumber
from validate_docbr import CPF

paths = os.listdir('raw_db')

# Add absolute path to get information about tha last modification to max method
_paths = list(map(lambda x: 'raw_db/{}'.format(x), paths))

filename = max(_paths, key=os.path.getctime).replace(
    'raw_db/', '').replace('.pdf', '')

input_path = "raw_db/{}.pdf".format(filename)

output_path = "db/{}.json".format(filename)

output_file = open(output_path, 'w')
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


def formatCPF(cpf):
    if len(cpf) < 11:
        cpf = cpf.zfill(11)
    return '{}.{}.{}-{}'.format(cpf[:3], cpf[3:6], cpf[6:9], cpf[9:])

def extra_attribs(dictio_):
    dictio_.update(
        {
            'area': dictio['vaccination_site'].split('-', 1)[0].strip(),
            'vaccination_site': dictio['vaccination_site'].split('-', 1)[1].strip(),
            'cpf': formatCPF(dictio['cpf'].replace('\'', '')),
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

pdf = pdfplumber.open(input_path)

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

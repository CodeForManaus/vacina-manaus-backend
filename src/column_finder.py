from decimal import Decimal

from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator

keys = [
    'full_name',
    'cpf',
    'vaccine_date',
    'vaccination_site',
    'priority_group',
    'service_group',
    'workplace',
    'role'
]

pdf_header = [
    'Nome Completo',
    'CPF',
    'Data da Vacina',
    'Local de Vacinação',
    'Grupo Prioritário',
    'Grupo de Atendimento',
    'Local onde exerce a função',
    'Cargo/Função'
]


def sanitize_text(text):
    name = text.strip() \
        .replace('\n', '') \
        .replace('\t', '')
    return ' '.join(name.split())


def find_header_in_text(text):
    text = sanitize_text(text)
    if text in pdf_header:
        return text

    for item in pdf_header:
        if text.startswith(item):
            return item

    return None


def find_columns_positions(filepath):
    fp = open(filepath, 'rb')
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    pages = PDFPage.get_pages(fp)

    page = next(pages)
    interpreter.process_page(page)
    layout = device.get_result()
    header_y_pos = 0
    header_x_positions = {}

    for lobj in layout:
        if isinstance(lobj, LTTextBox):
            x, y, text = lobj.bbox[0], lobj.bbox[3], lobj.get_text()
            name = find_header_in_text(text)
            if name == pdf_header[0]:
                header_y_pos = y

            if y == header_y_pos or name:
                header_x_positions[name] = x

    return [Decimal(header_x_positions[item]) for item in pdf_header]


if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    print(find_columns_positions(filename))

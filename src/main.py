from download_data import PdfDownloader
from extract_data import PdfExtractor
from process_data import DataProcessor
import logging


def main():
    url = 'https://semsa.manaus.am.gov.br/sala-de-situacao/novo-coronavirus/'

    logging.info("INIT DOWNLOAD")
    pdfDownloader = PdfDownloader(url)
    pdfDownloader.download()
    fileName = pdfDownloader.get_filename()

    logging.info("INIT Extracting")
    input_paths = "data/raw/{}".format(fileName)
    print(input_paths)
    pdfExtractor = PdfExtractor(input_paths, "data/cleaned/{}".format(fileName.replace("pdf", "json")))
    pdfExtractor.process()

    logging.info("INIT processing")
    dataProcessor = DataProcessor(pdfExtractor.output_path, 'analyzed')
    dataProcessor.process_all()

    logging.info("FINISH")


if __name__ == "__main__":
    main()

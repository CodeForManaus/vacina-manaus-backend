from download_data import PdfDownloader
from extract_data import PdfExtractor
from process_data import DataProcessor
import logging


def main():
    url = 'https://semsa.manaus.am.gov.br/sala-de-situacao/novo-coronavirus/'

    logging.info("INIT DOWNLOAD")
    pdfDownloader = PdfDownloader(url)
    pdfDownloader.download()
    fileName = pdfDownloader.filename

    logging.info("INIT Extracting")
    input_paths = "raw_db/{}".format(fileName)
    print(input_paths)
    pdfExtractor = PdfExtractor(input_paths, "db/{}".format(fileName.replace("pdf", "json")))
    pdfExtractor.process()

    logging.info("INIT processing")
    dataProcessor = DataProcessor(pdfExtractor.output_path, 'analytics')
    dataProcessor.process_all()

    logging.info("FINISH")


if __name__ == "__main__":
    main()

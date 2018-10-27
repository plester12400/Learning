import logging
import csv
from src.dl.flaskapp.transactions.parsers.csv_readers import CMCUDataReader, CapitalOneDataReader, WeatherDataReader
from src.dl.flaskapp.transactions.parsers.xml_readers import HealthDataReader

logger = logging.getLogger(__name__)


class TransactionReaderFactory:
    @classmethod
    def get_transaction_reader(cls, input_file):
        """
        Evaluate file, based on content, and return the proper parser for it.
        :param input_file:
        :return:
        """
        with open(input_file, "rt") as f:
            if input_file[-4:] == '.csv':
                reader = csv.DictReader(f)
                for r in reader:
                    if r.get('category', None) and r.get('account', None):
                        logger.info("Returning CMCUTransactionReader")
                        return CMCUDataReader()
                    elif r.get('Posted Date', None) and r.get('Card No.', None):
                        logger.info("Returning CapitalOneTransactionReader")
                        return CapitalOneDataReader()
                    elif r.get('STATION_NAME', None):
                        logger.info("Returning WeatherDataReader")
                        return WeatherDataReader()
            elif input_file[-4:] == '.xml':
                for line in f:
                    if 'HealthData' in line:
                        return HealthDataReader()

        logger.info("Unknown file type!")
        return None

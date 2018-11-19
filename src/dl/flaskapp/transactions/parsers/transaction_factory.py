import logging
import csv
from src.dl.flaskapp.transactions.parsers.csv_readers import CMCUDataReader, CapitalOneDataReader, WeatherDataReader, \
    VanguardTransactionReader, CapitalOneAutoDataReader
from src.dl.flaskapp.transactions.parsers.xml_readers import HealthDataReader

logger = logging.getLogger(__name__)


class TransactionReaderFactory:
    @classmethod
    def has_all(cls, elements, input_line):
        return all(map(lambda x: x in input_line, elements))

    @classmethod
    def get_transaction_reader(cls, input_file):
        """
        Evaluate file, based on content, and return the proper parser for it.
        :param input_file:
        :return:
        """
        with open(input_file, "rt") as f:
            if input_file[-4:] == '.csv':
                line = f.readline()
                if cls.has_all(['category', 'account'], line):
                    logger.info("Returning CMCUTransactionReader")
                    return CMCUDataReader()
                elif cls.has_all(['Posted Dat', 'account'], line):
                    logger.info("Returning CapitalOneTransactionReader")
                    return CapitalOneDataReader()
                elif cls.has_all(['STATION_NAME'], line):
                    logger.info("Returning WeatherDataReader")
                    return WeatherDataReader()
                elif cls.has_all(['Settlement Date'], line):
                    logger.info("Returning Vanguard")
                    return VanguardTransactionReader()
                elif cls.has_all(['Principal', 'Interest'], line):
                    logger.info('Returning Capital One Auto Reader')
                    return CapitalOneAutoDataReader()
            elif input_file[-4:] == '.xml':
                for line in f:
                    if 'HealthData' in line:
                        return HealthDataReader()

        logger.info("Unknown file type!")
        return None

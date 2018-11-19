import csv
import logging
from src.dl.flaskapp.transactions.parsers.abstract_readers import AbstractCSVReader
from src.dl.flaskapp.transactions.parsers.transaction_types import CapitalOneTransaction, CMCUTransaction, \
    WeatherData, VanguardTransaction, CapitalOneAutoTransaction

logger = logging.getLogger(__name__)


class CapitalOneDataReader(AbstractCSVReader):

    def _get_transaction(self, data):
        return CapitalOneTransaction(data)

    def _get_document_type(self):
        return 'capital-one-document-v2'


class CapitalOneAutoDataReader(AbstractCSVReader):
    def load_data(self, from_location, post_to_queue=None):
        try:
            with open(from_location, "rt") as f:
                lines = f.readlines()
                lines = list(map(lambda x: x.replace('-$', ''), lines))
                lines = list(map(lambda x: x.replace('---', '0.0'), lines))
                lines = list(map(lambda x: x.replace(',0', '0'), lines))
                reader = csv.DictReader(lines, delimiter='\t')
                self._post_it(reader, post_to_queue)
        except FileNotFoundError:
            logger.warning("File not found. Returning nothingness")

    def _get_transaction(self, data):
        return CapitalOneAutoTransaction(data)

    def _get_document_type(self):
        return 'capital-one-auto-document'


class VanguardTransactionReader(AbstractCSVReader):

    def _get_transaction(self, data):
        return VanguardTransaction(data)

    def _get_document_type(self):
        return 'vanguard-account-document'


class CMCUDataReader(AbstractCSVReader):

    def load_data(self, from_location, post_to_queue=None):
        try:
            with open(from_location, "rt") as f:
                lines = f.readlines()
                header = lines[0]
                lines = lines[1:]
                lines.reverse()
                lines.insert(0,header)
                reader = csv.DictReader(lines)
                self._post_it(reader, post_to_queue)
        except FileNotFoundError:
            logger.warning("File not found. Returning nothingness")

    def _get_transaction(self, data):
        return CMCUTransaction(data)

    def _get_document_type(self):
        return 'cmcu-account-document'


class WeatherDataReader(AbstractCSVReader):

    def _get_transaction(self, data):
        return WeatherData(data)

    def _get_document_type(self):
        return 'weather-data-document'

import csv
from src.dl.flaskapp.transactions.parsers.abstract_readers import AbstractCSVReader
from src.dl.flaskapp.transactions.parsers.transaction_types import CapitalOneTransaction, CMCUTransaction, \
    WeatherData, VanguardTransaction


class CapitalOneDataReader(AbstractCSVReader):

    def _get_transaction(self, data):
        return CapitalOneTransaction(data)

    def _get_document_type(self):
        return 'capital-one-document-v2'


class VanguardTransactionReader(AbstractCSVReader):

    def _get_transaction(self, data):
        return VanguardTransaction(data)

    def _get_document_type(self):
        return 'vanguard-account-document'


class CMCUDataReader(AbstractCSVReader):

    def _get_transaction(self, data):
        return CMCUTransaction(data)

    def _get_document_type(self):
        return 'cmcu-account-document'


class WeatherDataReader(AbstractCSVReader):

    def _get_transaction(self, data):
        return WeatherData(data)

    def _get_document_type(self):
        return 'weather-data-document'



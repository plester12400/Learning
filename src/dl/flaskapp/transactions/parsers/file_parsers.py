import csv
from dateutil.parser import parse
import logging
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AbstractDataReader(ABC):
    @abstractmethod
    def load_data(self, from_location, post_to_queue=None):
        pass

    @abstractmethod
    def _get_document_type(self):
        pass


class CapitalOneDataReader(AbstractDataReader):

    def load_data(self, from_location, post_to_queue=None):
        try:
            with open(from_location, "rt") as f:
                index = 1
                reader = csv.DictReader(f)
                for d in reader:
                    shit_to_do = {
                        'doc_type': self._get_document_type(),
                        'data': CapitalOneTransaction(d),
                        'index': index
                    }
                    post_to_queue.put(shit_to_do)
                    index += 1
        except FileNotFoundError:
            logger.warning("File not found. Returning nothingness")

    def _get_document_type(self):
        return 'capital-one-document-v2'


class CapitalOneTransaction:
    def __init__(self, transaction):
        self.account = transaction['Card No.']
        self.date = parse(transaction['Posted Date'])
        self.year = self.date.year
        self.month = self.date.month
        self.day_of_month = self.date.day
        self.description = transaction['Description']
        self.category = transaction['Category']
        if transaction['Debit']:
            self.debit = float(transaction['Debit'])
        if transaction['Credit']:
            self.credit = float(transaction['Credit'])

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return self.__dict__


class CMCUDataReader(AbstractDataReader):

    def load_data(self, from_location, post_to_queue=None):
        try:
            index = 1
            with open(from_location, "rt") as f:
                reader = csv.DictReader(f)
                for d in reader:
                    shit_to_do = {
                        'index': index,
                        'doc_type': self._get_document_type(),
                        'data': CMCUTransaction(d)
                    }
                    post_to_queue.put(shit_to_do)
                    index += 1
        except FileNotFoundError:
            logger.warning("File not found. Returning nothingness")

    def _get_document_type(self):
        return 'cmcu-account-document'


class CMCUTransaction:
    debit_none_remap = {
        'AutoLoan': ['AUTO'],
        'Auto': ['Oil', 'Tire', 'Tint'],
        'Fuel': ['CONOCO', 'SUNOCO', 'Love'],
        'Credit Card': ['Capital One Card', 'CC'],
        'Utilities': ['CITY OF', 'PIEDMONT', 'Water', 'PNG', 'Duke'],
        'Cell Phone': ['Cell Phone'],
        'Fee': ['Simply Elite'],
        'PayPal': ['PAYPAL'],
        'Insurance': ['STATE FARM'],
        'Taxes': ['MECKLENBURG TAX', 'NC DEPT REVENUE'],
        'Health': ['PLANET FIT', 'MASSAGE ENVY', 'Radiology', 'Gastro', 'Surgical', 'Medical', 'Novant', 'Dr.', 'LCI'],
        'Investments': ['VANGUARD', 'TROWE'],
        'Misc Purchase': ['POS Withdrawal'],
        'Entertainment': ['Netflix', 'HULU'],
        'Wages': ['Deposit'],
        'Transfer To Checking': ['From Share'],
        'From Checking': ['Online Withdrawal']

    }

    def __init__(self, transaction):
        self.account = transaction['account']
        self.amount = self._normalize_amount(transaction['amount'])
        self.date = str(parse(transaction['date']))
        self.balance = self._normalize_amount(transaction['balance'])
        self.description = transaction['description']
        self.memo = transaction['memo']
        self.category = self._recategorize(transaction['category'])
        self.deposit = False

    def _normalize_amount(self, amount):
        if amount:
            is_negative = '(' in amount
            stripped_amount = amount.strip('(').strip(')').strip('$')
            if is_negative:
                self.deposit = False
                return -1 * float(stripped_amount)
            else:
                self.deposit = True
                return float(stripped_amount)
        return None

    def _recategorize(self, category_in):
        if category_in in ['DebitNone', 'CreditNone', 'CreditTransfer']:
            for k, v in self.debit_none_remap.items():
                found_in_desc = any(kw.upper() in self.description.upper() for kw in v)
                found_in_memo = any(kw.upper() in self.memo.upper() for kw in v)
                if found_in_desc or found_in_memo:
                    return k
        else:
            return category_in
        return 'Misc'

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return self.__dict__


class HealthDataReader(AbstractDataReader):

    def load_data(self, from_location, post_to_queue=None):
        try:
            root = ET.parse(from_location).getroot()
            index = 1
            for c in root.iter(tag='Record'):
                shit_to_do = {
                    'doc_type': self._get_document_type(),
                    'data': HealthData(c),
                    'index': index
                }
                post_to_queue.put(shit_to_do)
                if index % 100 == 0:
                    logger.info("Record {}".format(index))
                index += 1
        except FileNotFoundError:
            logger.warning("File not found. Returning nothingness")

    def _get_document_type(self):
        return 'health-data-document'


class HealthData:
    def __init__(self, record):
        data_dict = record.attrib
        self.type = data_dict['type'][24:]
        self.unit = data_dict['unit']
        self.value = float(data_dict['value'])
        the_date = parse(data_dict['creationDate'])
        self.date = the_date.replace(hour=0, minute=0, second=0, microsecond=0)

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return self.__dict__


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
            elif input_file[-4:] == '.xml':
                for line in f:
                    if 'HealthData' in line:
                        return HealthDataReader()

        logger.info("Unknown file type!")
        return None

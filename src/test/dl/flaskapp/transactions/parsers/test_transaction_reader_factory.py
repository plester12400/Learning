import unittest
from src.dl.flaskapp.transactions.parsers.transaction_factory import TransactionReaderFactory
from src.dl.flaskapp.transactions.parsers.csv_readers import CapitalOneAutoDataReader


class TransactionFactoryTest(unittest.TestCase):
    def test_is_capital_one_auto_trans(self):
        the_reader = TransactionReaderFactory.get_transaction_reader("/Users/Paul/Downloads/data/coa.csv")
        self.assertIsNotNone(the_reader)
        self.assertTrue(isinstance(the_reader, CapitalOneAutoDataReader))

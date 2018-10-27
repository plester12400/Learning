import xml.etree.ElementTree as ET
from src.dl.flaskapp.transactions.parsers.transaction_types import HealthData
from src.dl.flaskapp.transactions.parsers.abstract_readers import AbstractDataReader
import logging

logger = logging.getLogger(__name__)


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

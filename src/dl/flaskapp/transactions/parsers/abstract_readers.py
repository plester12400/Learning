from abc import ABC, abstractmethod
import csv
import logging

logger = logging.getLogger(__name__)


class AbstractDataReader(ABC):
    @abstractmethod
    def load_data(self, from_location, post_to_queue=None):
        pass

    @abstractmethod
    def _get_document_type(self):
        pass


class AbstractCSVReader(AbstractDataReader):
    def load_data(self, from_location, post_to_queue=None):
        try:
            index = 1
            with open(from_location, "rt") as f:
                reader = csv.DictReader(f)
                for d in reader:
                    shit_to_do = {
                        'index': index,
                        'doc_type': self._get_document_type(),
                        'data': self._get_transaction(d)
                    }
                    post_to_queue.put(shit_to_do)
                    index += 1
        except FileNotFoundError:
            logger.warning("File not found. Returning nothingness")

    @abstractmethod
    def _get_document_type(self):
        pass

    @abstractmethod
    def _get_transaction(self, data):
        pass

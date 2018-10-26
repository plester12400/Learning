from elasticsearch import Elasticsearch
import redis
import hashlib
import time
import logging
from os import listdir, rename
from os.path import isfile, join
from datetime import datetime
from src.dl.flaskapp.transactions.parsers.file_parsers import TransactionReaderFactory
import queue
from threading import Thread

logger = logging.getLogger(__name__)
worker_queue = queue.Queue()


def es_worker():
    while True:
        shit_to_do = worker_queue.get()
        r = es_client.index(index='{}-index'.format(shit_to_do['doc_type']),
                            doc_type=shit_to_do['doc_type'],
                            id=shit_to_do['index'],
                            body=shit_to_do['data'].to_dict())
        print(r)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    cache = redis.Redis(host='localhost', port=6379)
    es_client = Elasticsearch(hosts=['localhost:9200'])

    DATA_DIRECTORY = "/Users/Paul/Downloads/data/"

    workers = []
    # four cores
    for w in range(0, 4):
        t = Thread(target=es_worker)
        t.start()
        workers.append(t)

    while True:
        csvfiles = [f for f in listdir(DATA_DIRECTORY) if
                    isfile(join(DATA_DIRECTORY, f)) and f[-4:] in ['.csv', '.xml']]
        for file in csvfiles:
            try:
                full_path = join(DATA_DIRECTORY, file)
                logger.info("Processing file: {}".format(full_path))
                transaction_reader = TransactionReaderFactory.get_transaction_reader(full_path)
                if not transaction_reader:
                    logger.warning("Unknown file type for {}. Skipping".format(full_path))
                    continue
            except Exception as e:
                logger.exception(e)
                continue

            el_hash = hashlib.md5(open(full_path, 'rb').read()).hexdigest()
            hash_exists = cache.exists(full_path)
            stored_hash = cache.get(full_path).decode('utf-8') if cache.get(full_path) else None
            hashes_match = el_hash == stored_hash
            load_file = not hashes_match
            hashes_match = False
            if not hashes_match:
                logger.info("Hash does not match. Reading file {}".format(full_path))
                transaction_reader.load_data(from_location=full_path, post_to_queue=worker_queue)
                cache.set(full_path, el_hash)
                rename(full_path, '{}_{}'.format(full_path, datetime.now().strftime('%Y_%m_%d_%H_%M_%s')))
            else:
                logger.info("File hasn't changed. Not loading")
        logger.info("Sleeping one minute until next round")
        time.sleep(60)

from datetime import datetime, timedelta
import requests
import random
import collections
import time
import asyncio
from requests.auth import HTTPBasicAuth
from elasticsearch import Elasticsearch, helpers


class ExecutionTimeDecorator:
    def __init__(self, function):
        self.function = function

    def __call__(self, *args, **kwargs):
        st = datetime.now().timestamp()
        res = self.function(*args, **kwargs)
        print("[%s Function Run-Time : %0.4fsec" % (self.function.__name__, datetime.now().timestamp()-st))
        return res


@ExecutionTimeDecorator
async def es_insert(es, doc, st):
    # for i, (ok, res) in enumerate(helpers.streaming_bulk(es, doc)):
    for i, (ok, res) in enumerate(helpers.parallel_bulk(es, doc, thread_count=8, queue_size=8, chunk_size=10000)):
        if i % 100000 == 0:
            print(datetime.now() - st, ok, res)

while 1:
    cmd = int(input("Select the Command : "))

    es = Elasticsearch(["218.55.23.206", "218.55.23.207", "218.55.23.208"],
                       http_auth=('elastic', 'i8OfnpTPBnRzCfX0IHWq'),
                       port=9200, retry_on_timeout=True, max_retries=10, timeout=30)
    # if es.indices.exists(index='test-index'):
    #     es.indices.delete(index='test-index')
    es_host = es.info()['name']
    es_cls = es.info()['cluster_name']
    sst = datetime.now()
    doc = [{"_index": "test-index3",
            "_type": "_doc",
            "_source": {
                "reqTime": datetime.now() - timedelta(days=random.randint(0, 200),
                                                                     hours=random.randint(0, 24),
                                                                     minutes=random.randint(0, 60),
                                                                     seconds=random.randint(0, 60)),
                "a": random.choices(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"]),
                "b": random.choices(["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k"]),
                "c": random.randint(0, 10000),
                "d": es_cls,
                "e": es_host
            }
            } for _ in range(30000000)]
    print(datetime.now() - sst)
    st = datetime.now()
    collections.Counter().elements()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(es_insert(es, doc, st))
    print("end : {}".format(datetime.now() - st))
    if cmd == 444:
        loop.close()
        break





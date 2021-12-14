import os

import redis
from rq import Worker, Queue, Connection
import datetime

from rq import get_current_job
from pathlib import Path
import openpyxl as openpyxl
import xlrd
from app import app


listen = ['upload_file_tasks']

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', '6379')
redis_url = "redis://{0}:{1}".format(REDIS_HOST, REDIS_PORT)

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()

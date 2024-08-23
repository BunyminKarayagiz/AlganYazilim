import time
import logging
from multiprocessing import Process, Queue
from logging.handlers import QueueHandler, QueueListener

def setup_logging(queue):
    root = logging.getLogger()
    h = QueueHandler(queue)
    root.addHandler(h)
    root.setLevel(logging.DEBUG)

def log_listener(queue):
    listener = QueueListener(queue, logging.FileHandler('yki.log'))
    listener.start()
    try:
        while True:
            time.sleep(0.1) 
    except KeyboardInterrupt:
        pass
    finally:
        listener.stop()

def start_log_listener():
    log_queue = Queue()
    listener_process = Process(target=log_listener, args=(log_queue,))
    listener_process.start()
    return log_queue, listener_process

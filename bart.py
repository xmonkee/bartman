import json
import logging
import signal
import smbus
import sys
import time
import threading
import urllib2
from datetime import datetime
from logging.handlers import RotatingFileHandler

from Adafruit_LED_Backpack import SevenSegment


URL = 'http://api.bart.gov/api/etd.aspx?cmd=etd&orig={}&key=MW9S-E7SL-26DU-VV8V&json=y'


display = SevenSegment.SevenSegment()
display.begin()
DEFAULT_VAL = '8888'
VAL = [DEFAULT_VAL]
LOCK = threading.Lock()
STOP_EVENT = threading.Event()


def init_logger():
    handler = RotatingFileHandler('bart.log', maxBytes=10000, backupCount=0)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger = logging.getLogger("Bart Log")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger


logger = init_logger()


def signal_handler(signal, frame):
    STOP_EVENT.set()
    display.clear()
    display.write_display()
    sys.exit(0)


def pad_zero(n):
    if len(n) == 2:
        return n
    if len(n) == 1:
        return '0' + n
    raise Exception('Received a value with too many digits')


def get_etds(origin, destinations):
    logger.info('Getting ETDs')
    response = urllib2.urlopen(URL.format(origin))
    data = json.load(response)
    all_dests = data['root']['station'][0]['etd']
    etds = [etd
        for dest in all_dests
        if dest['abbreviation'] in destinations
        for train in dest['estimate']
        for etd in [train['minutes']]
        if etd.isdigit()
        for etd in [int(etd)]
    ]
    logger.info('Found ETDs: {}'.format(etds))
    return etds


def get_for_fruitvale():
    return get_etds('FTVL', [
        'DALY', 'GLEN', 'POWL', 'SFIA', 'SSAN', 'UCTY', 'MLBR',
        '16TH', '19TH', 'CIVC', 'BALB',
    ])


def filter_sort_and_pad(etds):
    # sort and filter
    etds = sorted([etd for etd in etds if etd >= 10 and etd < 100])
    # take first two
    etds = etds[:2]
    # pad with zeros
    etds = [0] * (2 - len(etds)) + etds
    return etds


def make_string(e1, e2):
    s = '{}{}'.format(e1, e2)
    assert len(s) == 4
    return s


def get_val():
    etds = get_for_fruitvale()
    e1, e2 = filter_sort_and_pad(etds)
    return make_string(e1, e2)


def try_to_get_val():
    try:
        return get_val()
    except Exception as e:
        logger.exception(e)
        return DEFAULT_VAL


def set_val():
    with LOCK:
        VAL[0] = try_to_get_val()


def display_val(val, colon):
    logger.info('Writing to display')
    display.clear()
    display.set_colon(colon)
    display.print_number_str(val)
    display.write_display()


def try_to_display(val, colon):
    try:
        display_val(val, colon)
    except Exception as e:
        logger.exception(e)


def update_etd():
    while True:
        set_val()
        for i in xrange(10):
            if STOP_EVENT.is_set():
                return
            time.sleep(1)


THREAD = threading.Thread(target=update_etd).start()


def show_etd():
    with LOCK:
        try_to_display(VAL[0], False)


def show_time():
    now = datetime.now()
    hour = pad_zero(str(now.hour))
    minute = pad_zero(str(now.minute))
    try_to_display(hour + minute, True)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    threading.Thread(target=update_etd).start()
    is_show_time = False
    while True:
        if is_show_time: show_time()
        else: show_etd()
        is_show_time = not is_show_time
        time.sleep(1)

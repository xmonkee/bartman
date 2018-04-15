import json
import time
import threading
import urllib2

from logger import logger


URL = 'http://api.bart.gov/api/etd.aspx?cmd=etd&orig={}&key=MW9S-E7SL-26DU-VV8V&json=y'
DEFAULT_VAL = '8888'


class FetchError(Exception):
    pass


def get_etds(origin, destinations):
    logger.info('Getting ETDs')
    try:
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
    except Exception as e:
        logger.exception(e)
        raise FetchError(e)


def get_for_fruitvale():
    return get_etds('FTVL', [
        'DALY', 'GLEN', 'POWL', 'SFIA', 'SSAN', 'UCTY', 'MLBR',
        '16TH', '19TH', 'CIVC', 'BALB',
    ])


def to_display_string(etds):
    # sort and filter
    etds = sorted([etd for etd in etds if etd >= 10 and etd < 100])
    # take first two
    etds = etds[:2]
    # pad with zeros
    e1, e2 = [0] * (2 - len(etds)) + etds
    # Format as a single 4 digit string
    # Will appear as t1:t2
    s = '{:02d}{:02d}'.format(e1, e2)
    assert len(s) == 4, '%s is not a valid string' % s
    return s


def get_fresh_val():
    try:
        etds = get_for_fruitvale()
        return to_display_string(etds)
    except FetchError as e:
        logger.exception(e)
        return DEFAULT_VAL


class Bart(threading.Thread):
    def __init__(self):
        super(Bart, self).__init__()
        self.val = DEFAULT_VAL
        self.lock = threading.Lock()
        self.event = threading.Event()
        self.refresh()
        self.start()

    def set(self, val):
        with self.lock:
            self.val = val

    def get(self, ):
        with self.lock:
            return self.val

    def refresh(self):
        self.set(get_fresh_val())

    def stop(self):
        logger.info('Shutting down BART api')
        self.event.set()

    def run(self):
        counter = 0
        while True:
            if (counter + 1) % 10 == 0:
                self.refresh()
                conter = 0
            if self.event.is_set():
                logger.info('BART api terminated')
                return
            counter += 1
            time.sleep(1)


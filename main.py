#!/usr/bin/env python
import signal
import sys
import time

from clock import Clock
from bart import Bart
from display import Display
from logger import logger


class Main(object):
    def __init__(self):
        logger.info('Starting Bart service')
        self.clock = Clock()
        self.bart = Bart()
        self.display = Display()
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signal, frame):
        logger.info('Caught signal {}. Shutting down.'.format(signal))
        self.clock.stop()
        self.bart.stop()
        self.display.stop()
        sys.exit(0)

    def run(self):
        show_clock = False
        while True:
            if show_clock: 
                self.display.display(self.clock.get(), True) 
            else:
                self.display.display(self.bart.get(), False) 
            show_clock = not show_clock
            time.sleep(1)


if __name__ == '__main__':
    main = Main()
    main.run()

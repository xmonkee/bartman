import smbus
from logger import logger


ADDR = 0x70
# Each write operations is of the form bus.write_byte_data(ADDR, cmd, val)
# cmd refers a memory location and val refers to the value in that location
# val_array[i] corresponds to the value that needs to be set to show 'i' on the display
# The last value means blank
val_array = [63, 6, 91, 79, 102, 109, 125, 7, 127, 111, 0]
# cmd_array[i] corresponds to the cmd for position i
cmd_array = [0, 2, 6, 8, 4]
# Example, '0 18' would be values [63, 0, 6, 127] in cmds [0, 2, 6, 8]


class Bus(object):
    def __init__(self):
        self.bus = smbus.SMBus(1)
        
    def clear(self):
        for pos in range(5):
            self.bus.write_byte_data(ADDR, cmd_array[pos], 0) 

    def set_colon(self, colon):
        if colon:
            self.bus.write_byte_data(ADDR, cmd_array[4], 0b10)

    def print_number_str(self, val):
        for pos, digit in enumerate(val):
            digit = 10 if digit == ' ' else int(digit)
            self.bus.write_byte_data(ADDR, cmd_array[pos], val_array[digit])


class Display(object):
    def __init__(self):
        self.d = Bus()

    def _display(self, val, colon):
        logger.info('Writing to display: {}. Colon: {}'.format(val, colon))
        self.d.clear()
        self.d.set_colon(colon)
        self.d.print_number_str(val)

    def display(self, val, colon):
        try:
            self._display(val, colon)
        except Exception as e:
            logger.exception(e)

    def stop(self):
        logger.info('Shutting down display')
        try:
            self.d.clear()
            logger.info('Display terminated')
        except Exception as e:
            logger.exception(e)


import logging
from logging.handlers import RotatingFileHandler


class Logger(object):
    logger = None

    @classmethod
    def get_logger(cls):
        if cls.logger:
            return cls.logger

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)

        fh = RotatingFileHandler('/var/log/bart.log', maxBytes=10000, backupCount=0)
        fh.setFormatter(formatter)

        logger = logging.getLogger('bart')
        logger.setLevel(logging.INFO)

        logger.addHandler(fh)
        logger.addHandler(ch)

        cls.logger = logger
        return logger

logger = Logger.get_logger()

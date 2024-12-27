import logging

class CustomFormatter(logging.Formatter):
    def __init__(self, count):
        super().__init__()

        self.log_formats = {
            logging.DEBUG: logging.Formatter(
                f'\x1b[35m[\U0001F527 DEBUG]\x1b[0m %(message)s'
            ),
            logging.INFO: logging.Formatter(
                f'\x1b[36m[\U00002139\U0000FE0F INFO ]\x1b[0m %(message)s'
            ),
            logging.WARNING: logging.Formatter(
                f'\x1b[33m[\U000026A0\U0000FE0F WARN ]\x1b[0m %(message)s'
            ),
            logging.ERROR: logging.Formatter(
                f'\x1b[31m[\U0001F635 ERROR]\x1b[0m %(message)s'
            ),
            logging.CRITICAL: logging.Formatter(
                f'\x1b[37;41m[\U0001F62D CRIT ]\x1b[0m %(message)s'
            ),
            'unknown': logging.Formatter(
                f'\x1b[32m[\U00002753 UNKWN]\x1b[0m %(message)s'
            )
        }

    def format(self, log):
        useformat = self.log_formats.get(log.levelno)
        if not useformat:
            useformat = self.log_formats.get('unknown')

        if log.exc_info:
            text = useformat.formatException(log.exc_info)
            log.exc_text = f'\x1b[31m{text}\x1b[0m'
            output = useformat.format(log)
            log.exc_text = None
        else:
            output = useformat.format(log)

        return output

def buildlogger(package, name, level, handler=None):
    if not handler:
        handler = logging.StreamHandler()

    handler.setLevel(level)
    handler.setFormatter(CustomFormatter(len(package) + 15))
    library, _, _ = __name__.partition('.')
    logger = logging.getLogger(package + '.' + name)

    # Prevent duplicate output
    while logger.hasHandlers():
        try:
            logger.removeHandler(logger.handlers[0])
        except:
            break

    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

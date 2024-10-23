import logging


def setup_logging():
    """
    Configures the logging settings.
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s: %(message)s')

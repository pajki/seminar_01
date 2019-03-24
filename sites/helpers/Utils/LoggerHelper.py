import logging


def init_logger(debug):
    """
    Init logging level. Pass debug as True to class to enable info output
    :return:
    """
    if debug:
        logging.basicConfig(format='%(message)s', level=logging.INFO)
    else:
        logging.basicConfig(format='%(message)s', level=logging.NOTSET)


def log(content):
    """
    Log content
    :param content: content to log
    """
    logging.info(content)


import logging
logging.basicConfig(level=logging.INFO)

def lprint(msg, status="error"):
    if status == "warning":
        logging.warning(str(msg))
    elif status == "error":
        logging.error(str(msg))
    else:
        logging.info(str(msg))

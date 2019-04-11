import logging

def set_loglevel(
    loglevel,
    modulename=None, 
):
    logging.basicConfig(
        format="%(asctime)-5.5s %(name)-20.20s %(levelname)-7.7s %(message)s",
        datefmt="%H:%M",
        level=logging.WARNING,
    )

    logging.getLogger(__name__ if modulename is None else modulename).setLevel(loglevel)

def get_logger(
    name
):
    logging.basicConfig(
        format="%(asctime)-5.5s %(name)-20.20s %(levelname)-7.7s %(message)s",
        datefmt="%H:%M",
        level=logging.WARNING,
    )
    logging.getLogger(name).addHandler(logging.NullHandler())
    return logging.getLogger(name)

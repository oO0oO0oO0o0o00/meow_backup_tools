from datetime import datetime


def to66(x=None):
    if x is None:
        x = datetime.now()
    return x.strftime("%y%m%d-%H%M%S")

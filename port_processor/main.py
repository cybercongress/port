from processor import processor
from config import *


if __name__ == '__main__':
    print(POSTGRES_DB)
    print(POSTGRES_USER)
    print(RECEIVER)
    processor()

